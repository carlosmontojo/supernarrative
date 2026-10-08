#!/usr/bin/env python3
"""
SuperNarrative — Linter de prosa
Mide lo que los LLMs (y los humanos cansados) hacen mal al escribir ficción,
con números en vez de opiniones:

  - Regresión a la voz robot: varianza de longitud de frase baja, ritmo uniforme
  - Densidad de recursos: símiles, adverbios en -mente, construcciones "no X, sino Y"
  - Léxico quemado ("slop"): frases hechas de la ficción generada por IA
  - Muletillas propias: n-gramas repetidos dentro del capítulo y ENTRE capítulos
  - Arranques de frase repetidos, frases-fragmento efectistas en exceso
  - Deriva respecto al ancla de estilo del proyecto (si está fijada)
  - Anti-poeta: símiles en boca de personajes (aparte de los del narrador) y léxico de
    poeta-matemático (arithmetic, geometry, grammar, ledger, "a kind of"...), con extractos

Uso:
  python3 supernarrative.py prose --file cap05.md                  # analizar un fichero
  python3 supernarrative.py prose --chapter 5                      # vía file_path de la DB
  python3 supernarrative.py prose --set-anchor pasaje_ejemplar.md  # fijar el ancla de estilo
"""

import argparse
import json
import re
import sys
import os
from collections import Counter

from _common import connect, fail, get_project_id, require_db

# Frases quemadas de la ficción LLM (ampliable; español + inglés)
SLOP_LEXICON = [
    "una oleada de", "no pudo evitar", "se le encogió el", "una mezcla de",
    "respiró hondo", "soltó el aire que no sabía", "el silencio se hizo",
    "esbozó una sonrisa", "en ese momento supo", "nada volvería a ser",
    "un escalofrío le recorrió", "el corazón le dio un vuelco",
    "los ojos se le llenaron", "apretó los puños", "tragó saliva",
    "el aire olía a", "como si el mundo", "sintió un nudo en",
    "a wave of", "couldn't help but", "a mix of", "took a deep breath",
    "let out a breath", "heart skipped", "sent shivers down",
    "a mixture of", "breath he didn't know", "breath she didn't know",
    "eyes widened", "knuckles whitened", "unreadable expression",
    "the ghost of a smile", "heart hammered", "stomach dropped",
    "time seemed to slow", "the world narrowed", "in that moment",
    "little did", "despite himself", "despite herself", "if he was being honest",
    "something flickered", "a beat passed", "couldn't shake the feeling",
    "white-knuckled", "released a breath", "let out a long breath",
]

# Léxico de "poeta-matemático": abstracciones y metáforas de oficio que los personajes
# (y el narrador cercano) NO usan. Un chaval de dieciséis años no habla de aritmética,
# geometría ni gramática para describir una pelea o un sentimiento. Cero tolerancia.
POET_LEXICON = [
    "arithmetic", "geometry", "geometric", "geometrical", "equation", "algebra", "calculus",
    "mathematics", "mathematical", "theorem", "formula", "the sum", "did the sum", "do the sum",
    "does the sum", "doing the sum", "a sum", "the maths", "the math",
    "ledger", "liturgy", "liturgical", "currency", "economy of", "the economy", "economics",
    "grammar", "syntax", "vocabulary", "punctuation", "a sentence that", "the sentence",
    "the physics", "the logic of", "the language of", "the music of", "the architecture of",
    "the shape of", "the weight of", "the colour of", "the color of", "the texture of",
    "a kind of", "kind of thing", "the kind of thing", "which is to say", "the particular",
    "a thing that", "a thing with", "a thing the", "is a place", "not a time", "is a time",
    "the opposite of", "a version of", "the version of",
    "a question with", "the answer to a", "a word for", "the word for", "what it costs", "the cost of",
    "a tax", "a tithe", "the price of", "a debt to", "in the currency",
    "aritmética", "geometría", "ecuación", "gramática", "sintaxis", "liturgia", "la suma de",
    "una especie de", "la forma de", "el peso de", "el color de", "lo que cuesta",
]

# Patrones de símil/comparación (inglés + español). Se cuentan aparte en diálogo y en narración.
SIMILE_PATTERNS = [
    r"\blike (?:a|an|the|some|something|someone|somebody) \b", r"\bas (?:if|though)\b",
    r"\bthe way (?:a|an|the|you|he|she|they|we|it|somebody|someone) \b",
    r"\b(?:is|was|are|were|'s) a kind of\b", r"\bthe sound of (?:a|an|the)\b",
    r"\bcomo (?:si|un|una|el|la|los|las) \b", r"\ba la manera de\b",
]

# Registro de epigrama: la gente no habla en sentencias. Patrones de "frase redonda" que
# delatan al poeta aunque no haya símil: antítesis "That's not X. That's Y.", definiciones
# "That's what an arena is", "the only thing that helps", "there's a word for it",
# "people like us... people like us", fragmentos-sentencia "Not fear. Arithmetic."
EPIGRAM_PATTERNS = [
    r"\bthat's not (?:a |an |the )?[^.?!\"]{1,40}\. that's\b",
    r"\bit's not (?:a |an |the )?[^.?!\"]{1,40}\. it's\b",
    r"\b(?:isn't|aren't|wasn't) (?:a |an |the )?[^.?!\"]{1,40}\. (?:it's|they're|it was|that's)\b",
    r"\bthe only (?:thing|one|part|question|rule) (?:that|is|was|which)\b",
    r"\bthere's a (?:word|name) for\b", r"\bthe word (?:for it|doesn't|isn't|is|was)\b",
    r"\bthe thing (?:is|about|that|with|was)\b", r"\bthe part (?:that|where|of it)\b",
    r"\bthe kind that\b", r"\bthat's what (?:a |an |the )?\w+ (?:is|are|does|do|means)\b",
    r"\bthat's (?:the whole|the only|the first|the real|the one) (?:thing|rule|trick|point|of it|question)\b",
    r"\b(?:is|are|was|were) the (?:useful|only|whole|real|hard|easy|interesting|dangerous) part\b",
    r"\bthat's (?:not )?(?:a|an) (?:fact|rule|promise|question|answer|limit|number|clock|formula|lie|choice|decision|punishment|threat|offer)\b\.",
    r"(?:^|[.!?] )not (?:a |an |the )?\w+\. (?:a |an |the )?\w+\.",
    r"\bpeople like (?:us|you|me|him|her|them)\b[^\"]{0,80}\bpeople like (?:us|you|me|him|her|them)\b",
    r"\bthat's (?:how|where|why|when) (?:you|it|they|we|he|she) \w+\. that's\b",
]

def epigram_report(text):
    """Frases redondas en diálogo (y fragmentos-sentencia en narración), con extractos."""
    low = text.lower(); spans = dialogue_spans(text)
    def in_dialogue(i): return any(a <= i < b for a, b in spans)
    def excerpt(i, j):
        a = max(0, i - 50); b = min(len(text), j + 50)
        return re.sub(r"\s+", " ", text[a:b]).strip()
    hits_d, hits_n, examples = 0, 0, []
    for pat in EPIGRAM_PATTERNS:
        for m in re.finditer(pat, low):
            where = "dialogue" if in_dialogue(m.start()) else "narration"
            if where == "dialogue": hits_d += 1
            else: hits_n += 1
            examples.append({"where": where, "hit": m.group(0).strip()[:60], "text": excerpt(m.start(), m.end())})
    # anáfora retórica dentro de una réplica: TRES frases seguidas con las mismas dos palabras de
    # arranque (regla de tres). Dos seguidas es habla normal ("You were scary. You were actually
    # scary.") y no cuenta desde la pasada de voces v3.
    for a, b in spans:
        sents = [x.strip() for x in re.split(r"(?<=[.!?])\s+", text[a + 1:b - 1]) if len(x.split()) >= 3]
        for s1, s2, s3 in zip(sents, sents[1:], sents[2:]):
            w1, w2, w3 = s1.lower().split()[:2], s2.lower().split()[:2], s3.lower().split()[:2]
            if w1 == w2 == w3:
                hits_d += 1
                examples.append({"where": "dialogue", "hit": "anaphora x3: " + " ".join(w1), "text": excerpt(a, min(b, a + 160))})
                break
    return hits_d, hits_n, examples

# Marcadores de ingenio de narrador (v2.3): remates "which was X", "For X that was a lot",
# "That was the Horno for you", hipérboles y resúmenes-sentencia. No mide la densidad real
# (eso lo juzga la lectura) pero delata el tic.
WIT_PATTERNS = [
    r", which (?:from|showed|counted as|in the \w+ (?:was|meant)) [^.]{2,60}\.",
    r", which was (?:what (?:he|she|they)'d wanted|rare for|a lot for|more than|her way of|his way of|the point|the trouble|the problem)\b",
    r"\bfor \w+,? that was (?:a lot|something|a speech|a parade|a wreath|a medal)\b",
    r"\bthat was the \w+ for you\b", r"\bit was that or\b", r"\bwhich was (?:the whole|most of|its own|how)\b",
    r"\bdoing what \w+ do, which\b", r"\bsame as it did everything\b", r"\bthe only free\b",
    r"\bwhich (?:he|she|they) (?:thought|found|considered) was\b", r"\bin that order\b",
    r"\b(?:so|too) \w+ (?:that|you could) [^.]{0,40}\b(?:complained|see your thumb|two streets)\b",
]

# Las instituciones y los objetos no tienen ojos (cuarta corrección del autor): "the levy didn't
# look at medical notes", "the room looked at Dex", "the machine had looked", "the office was lying".
# Sujeto institucional/colectivo/objeto + verbo de percepción, pensamiento, sentimiento o habla.
PERSON_SUBJECTS = r"(?:levy|empire|school|collegium|censo|censorate|office|house|senate|company|genetrix|drusa|valerii|physici|tabularium|record|file|annex|catalogue|rules?|form|order|paper|letter|strip|slate|board|machine|bracelet|armilla|tree|numbers?|chart|book|post room|council|district|horno|orb|room|hall|yard|block|mess|arena|sand|wall|line|tunnel|ladder|bracket|draw|clock|lamp|oven|dough|bunk|tanks?|pit|chair|door|gate|stone|water|dark|cold|quiet|silence|loud feeling|bird|oak|arrow|fever|warning|view|crowd|benches|stands)"
PERSON_VERBS = r"(?:look(?:s|ed)?|see(?:s)?|saw|seen|think(?:s)?|thought|care(?:s|d)?|know(?:s)?|knew|known|want(?:s|ed)?|remember(?:s|ed)?|like(?:s|d)?|hate(?:s|d)?|forgive(?:s)?|forgave|forgiven|believe(?:s|d)?|notice(?:s|d)?|expect(?:s|ed)?|learn(?:s|ed)?|mean(?:s|t)?|need(?:s|ed)?|watch(?:es|ed)?|listen(?:s|ed)?|understand(?:s)?|understood|allow(?:s|ed)?|refuse(?:s|d)?|apologi[sz]e(?:s|d)?|ask(?:s|ed)?|answer(?:s|ed)?|agree(?:s|d)?|argue(?:s|d)?|lie(?:s|d)?|lying|wait(?:s|ed)?|prefer(?:s|red)?|mind(?:s|ed)?|worr(?:y|ies|ied)|hope(?:s|d)?|forg(?:et|ets|ot|otten)|decide(?:s|d)?|tell(?:s)?|told|complain(?:s|ed)?|sleep(?:s)?|slept|breathe(?:s|d)?|flinch(?:es|ed)?|trust(?:s|ed)?|respect(?:s|ed)?|love(?:s|d)?|enjoy(?:s|ed)?|pretend(?:s|ed)?|insist(?:s|ed)?|promise(?:s|d)?|intend(?:s|ed)?|try|tries|tried|feel(?:s)?|felt|had opinions|has opinions|have opinions|wasn't interested|isn't interested|didn't mind|doesn't mind|went quiet|go quiet|held its breath|stopped breathing)"
PERSON_PATTERN = re.compile(r"\bthe " + PERSON_SUBJECTS + r"(?:'s \w+)? (?:(?:didn't|doesn't|don't|never|always|had|has|have|would|wouldn't|could|couldn't|still|just|only|also|hadn't|hasn't|was|were|is|are|wasn't|weren't) )?(?:not )?" + PERSON_VERBS + r"\b", re.I)

def personification_report(text):
    spans = dialogue_spans(text); hits = []
    for m in PERSON_PATTERN.finditer(text):
        where = "dialogue" if any(a <= m.start() < b for a, b in spans) else "narration"
        a = max(0, m.start() - 50); b = min(len(text), m.end() + 50)
        hits.append({"where": where, "hit": m.group(0), "text": re.sub(r"\s+", " ", text[a:b]).strip()})
    return hits

def wit_report(text):
    low = text.lower(); spans = dialogue_spans(text); hits = []
    for pat in WIT_PATTERNS:
        for m in re.finditer(pat, low):
            where = "dialogue" if any(a <= m.start() < b for a, b in spans) else "narration"
            a = max(0, m.start() - 50); b = min(len(text), m.end() + 40)
            hits.append({"where": where, "hit": m.group(0).strip()[:60], "text": re.sub(r"\s+", " ", text[a:b]).strip()})
    # párrafos-remate de narración: una sola frase de 6 palabras o menos, sin comillas
    for para in text.split("\n\n"):
        t = para.strip()
        if t and '"' not in t and not t.startswith(("#", ">", "-")) and 1 <= len(t.split()) <= 6 and t[-1] in ".!" and not t.isupper():
            hits.append({"where": "narration", "hit": "one-line zinger", "text": t})
    return hits

# Remates (quinta corrección del autor, 4-oct): frases que solo están para "quedar bien" y hacen
# repelentes a los personajes. "The shiny ones are in eights too, they just don't know why",
# "People always do", "Everybody says that", "So what", "Obviously.", un "Sir." suelto al final
# de una pulla, "nobody wrote it down". Se miden por frase dentro de cada réplica.
PUNCHLINE_PATTERNS = [
    r"^(?:people|everyone|everybody|nobody|no one|they|girls|boys|houses|patricians|the shiny ones) (?:always|never|just) ",
    r"\b(?:they always do|people always do|always do\.|never do\.|every single time|ask anyone|just don'?t know (?:it|why|that)|nobody (?:wrote|writes|asked|asks|counts|counted) (?:it|that|them|me)\b|so what\b|which is the point|that'?s the point|that'?s the joke|you'?ll see\.|trust me\.|everybody says that|everyone says that|people say that|said nobody|famous last words)",
    r"^(?:obviously|naturally|apparently|clearly|famously)\.$",
    r"^sir\.$",
]

def punchline_report(text):
    hits = []
    for a, b in dialogue_spans(text):
        inner = text[a + 1:b - 1]
        for sent in [x.strip() for x in re.split(r"(?<=[.!?])\s+", inner) if x.strip()]:
            low = sent.lower()
            if any(re.search(p_, low) for p_ in PUNCHLINE_PATTERNS):
                hits.append({"hit": sent[:80], "text": re.sub(r"\s+", " ", inner)[:160]})
    return hits

# Descripción poética del narrador (sexta corrección del autor, 5-oct): "Cuando describes cosas te vuelves
# muy poético también... hay miles de rellenos poéticos así que no aportan nada". El vault "by day... by night",
# "the racks went off into the dark like the shelves in the Annona's fields", "caught the lamp one at a time as
# you walked past", "All of them.", "which was often". Patrones evidentes; el resto se encuentra leyendo.
DESCRIPTION_PATTERNS = [
    r"\b(?:at night|by night|by day|in daylight)\b[^.]{0,40}\b(?:was|were)\b",
    r"\b(?:caught the (?:light|lamp|sun)|went off into the dark|into the dark on both|pooled|the light (?:fell|lay)|lamp-?light)\b",
    r"\b(?:as you (?:walked|went|came|passed)|you could (?:tell|see|feel|hear) (?:from|that|it|the))\b",
    r"\b(?:which was often|which turned out to matter|which was (?:most of|all of|the point|how)|that was the \w+ all over)\b",
    r"\bthe (?:quiet|silence|stillness|noise|sound|smell) of (?:two thousand|a|people|men|everyone)\b",
    r"\bwas a different (?:room|place|building|yard|field) (?:from|at|by)\b",
]

def description_report(text):
    spans = dialogue_spans(text); hits = []
    for pat in DESCRIPTION_PATTERNS:
        for m in re.finditer(pat, text, re.I):
            if any(a <= m.start() < b for a, b in spans):
                continue
            a = max(0, m.start() - 60); b = min(len(text), m.end() + 60)
            hits.append({"hit": m.group(0)[:60], "text": re.sub(r"\s+", " ", text[a:b]).strip()})
    return hits

# Contar cosas (séptima corrección, 5-oct): "todo el mundo cuenta cosas, 40 pasos, 30 frases... les hace muy robóticos".
_NUM = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|hundred)(?:[- ](?:one|two|three|four|five|six|seven|eight|nine))?"
COUNTING_PATTERNS = [
    r"\b(?:I|he|she|they|Dex|Pále|Sabina|Felix|Tulia|Castor|Brennus|Aurelia) (?:had )?counted\b",
    r"\b(?:'d counted|kept count|was counting|counted (?:them|it|every|out|the (?:steps|lines|names|seconds)))\b",
    r"\b" + _NUM + r" (?:steps|paces|strides|sentences|words|breaths|heartbeats|seconds|names|ticks|rungs|stairs)\b",
    # "lines" solo con cinco o más: "two lines" es una línea de sangre (sistema); "Thirteen lines" es contar la tira
    r"\b(?:\d{2,}|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty)(?:[- ](?:one|two|three|four|five|six|seven|eight|nine))? lines\b",
]

def counting_report(text):
    hits = []
    for pat in COUNTING_PATTERNS:
        for m in re.finditer(pat, text, re.I):
            a = max(0, m.start() - 60); b = min(len(text), m.end() + 50)
            hits.append({"hit": m.group(0)[:50], "text": re.sub(r"\s+", " ", text[a:b]).strip()})
    return hits

# Conversación como HWFWM (octava corrección, 5-oct): "son robots... no eres capaz de coger la forma de escribir del autor".
# Medido sobre HWFWM 1-8: 37 % de las réplicas son preguntas (CORVUS 9-12 %); frases de <=2 palabras 23 % (CORVUS 31-35 %);
# metáfora de deuda/papeleo 1,8 por 1000 palabras de diálogo (CORVUS 5, cap. 7 15). Se miden las tres.
TRANSACTION_PATTERNS = [
    r"\b(?:started a tab|run(?:ning)? a tab|we(?:'re| are) even|call it even|that pays|pay(?:s|ing)? (?:it|the debt|you back|that back)|a debt|my debt|debts|owe you|owing|i cannot stand owing|receipt|ledger|invoice|watch the paperwork|on my slate|on the slate|that's the rent|the rent|the price of|that's the price|costs? (?:you|me|him|her|us) (?:nothing|something|more)|in the book|i'm keeping (?:count|score))\b",
    # Papeleo como muletilla (corrección del 5-oct: "ya basta de records y filing"): expedientes y registros dichos de
    # boquilla. Los documentos de verdad (el expediente del Censorado, el registro Veda, la tira) se nombran sin estas frases.
    r"\b(?:for the record|on the record|off the record|on a record|goes on (?:a|the) record|put (?:it|that) on record|"
    r"where it (?:can be|gets|'s) written down|i'd like it (?:noted|on record|minuted)|for the file|make a note of (?:it|that))\b",
]

# Acción (novena corrección, 5-oct): "llevo varios capítulos sin acción... tienen que enseñarles a pelear".
# Densidad de verbos de contacto, esfuerzo y daño por 1000 palabras. Es una medida tosca: solo avisa cuando el
# capítulo Y el anterior están por debajo del umbral (dos seguidos sin acción física), y nunca en interludios.
ACTION_PATTERN = re.compile(
    r"\b(?:hit|hits|hitting|struck|strikes?|striking|thrust(?:s|ing)?|punch\w*|kick(?:ed|s|ing)?|block(?:ed|ing)|"
    r"parr(?:y|ied|ies|ying)|swung|swing(?:s|ing)?|blows?|knock(?:ed|s|ing)?|shov(?:e|ed|es|ing)|slamm?(?:ed|ing)?|"
    r"thrown|tripp?(?:ed|ing)|swept|sprawl\w*|bled|bleed\w*|blood|ribs?|jaw|tooth|teeth|bruis\w*|in the tanks?|"
    r"yield(?:ed|s)?|sparr\w*|bouts?|fought|fight(?:ing)?|lung(?:e|ed|ing)|grappl\w*|clinch\w*|wrestl\w*|dodg\w*|"
    r"ducked|went down|on the sand|got up|winded|sprint\w*|laps?|climb(?:ed|ing)?|dragg(?:ed|ing)|haul(?:ed|ing)|"
    r"jump(?:ed|ing)|fell|falling|to (?:his|her|their) knees|on (?:his|her) back|threw (?:him|her|me|them)|"
    r"carr(?:ied|ying) (?:the|a|him|her|iron|bars?|shields?))\b", re.I)

def action_density(text):
    return round(1000 * len(ACTION_PATTERN.findall(text)) / max(1, len(text.split())), 1)

def conversation_report(text):
    spans = dialogue_spans(text)
    turns = [text[a + 1:b - 1] for a, b in spans]
    q = sum(1 for t in turns if "?" in t)
    sents = [x for t in turns for x in re.split(r"(?<=[.!?])\s+", t) if x.strip()]
    frag = sum(1 for x in sents if len(x.split()) <= 2)
    trans = []
    for t in turns:
        for pat in TRANSACTION_PATTERNS:
            for m in re.finditer(pat, t, re.I):
                trans.append({"hit": m.group(0), "text": re.sub(r"\s+", " ", t)[:140]})
    return {"turns": len(turns), "question_pct": round(100 * q / max(1, len(turns)), 1),
            "fragment_pct": round(100 * frag / max(1, len(sents)), 1), "transaction_hits": trans}

def dialogue_spans(text):
    """Tramos entre comillas dobles (rectas o tipográficas) en una misma línea."""
    spans = []
    for m in re.finditer(r'"[^"\n]{2,}"|“[^”\n]{2,}”|«[^»\n]{2,}»', text):
        spans.append((m.start(), m.end()))
    return spans

def figurative_report(text):
    """Símiles en boca de personajes vs. en narración, y léxico de poeta-matemático, con extractos."""
    low = text.lower()
    spans = dialogue_spans(text)
    def in_dialogue(i):
        return any(a <= i < b for a, b in spans)
    def excerpt(i, j):
        a = max(0, i - 60); b = min(len(text), j + 60)
        return re.sub(r"\s+", " ", text[a:b]).strip()
    sim_d, sim_n, examples = 0, 0, []
    for pat in SIMILE_PATTERNS:
        for m in re.finditer(pat, low):
            if in_dialogue(m.start()):
                sim_d += 1
                examples.append({"where": "dialogue", "hit": m.group(0).strip(), "text": excerpt(m.start(), m.end())})
            else:
                sim_n += 1
                examples.append({"where": "narration", "hit": m.group(0).strip(), "text": excerpt(m.start(), m.end())})
    poet_hits = Counter()
    for phrase in POET_LEXICON:
        for m in re.finditer(r"\b" + re.escape(phrase) + r"\b", low):
            poet_hits[phrase] += 1
            examples.append({"where": "dialogue" if in_dialogue(m.start()) else "narration",
                             "hit": phrase, "text": excerpt(m.start(), m.end())})
    return sim_d, sim_n, dict(poet_hits), examples

# Palabras en -ly que NO son adverbios de manera (no cuentan para el tic)
LY_STOPLIST = {
    "only", "family", "early", "reply", "supply", "apply", "belly", "bully",
    "rally", "jelly", "holy", "ugly", "assembly", "likely", "unlikely",
    "friendly", "lovely", "lonely", "elderly", "silly", "fly", "ally",
    "tally", "daily", "deadly", "orderly", "costly", "italy", "july",
    "monopoly", "anomaly", "melancholy", "butterfly", "multiply", "imply",
}

OBVIOUS_QUESTION = re.compile(
    r"(?i)\b(?:is|was|isn't|wasn't) (?:that|it|this) (?:good|bad|good or bad|bad or good|a good thing|a bad thing)\b[^.?!\"]{0,25}\?"
    r"|\bwhat does (?:that|it|this) mean\?")

UMBRALES = {
    "std_frase_min": 6.0,        # desviación típica de longitud de frase (palabras)
    "mente_por_1000_max": 16.0,  # adverbios de manera (-mente / -ly) por 1000 palabras (HWFWM ~14)
    "simil_por_1000_max": 3.0,   # "como" comparativo por 1000 palabras (aprox)
    "slop_por_1000_max": 1.0,
    "no_sino_por_1000_max": 0.8,
    "arranque_repetido_max": 0.18,  # fracción de frases que arrancan con la misma palabra
    "fragmento_final_parrafo_max": 0.30,  # párrafos que cierran con frase < 6 palabras
    # Métricas page-turner (calibradas sobre 15k palabras de HWFWM: media 13.6, std 7.2,
    # 1.3% frases >30 palabras, 27 palabras/párrafo, 0 guiones largos, 'said' casi único)
    "media_frase_max": 16.0,          # media de palabras por frase
    "frases_largas_pct_max": 4.0,     # % de frases con más de 30 palabras
    "palabras_parrafo_media_max": 40.0,
    "guion_largo_por_1000_max": 1.0,  # guiones largos (— –) por 1000 palabras
    "said_ratio_min": 0.75,           # proporción de atribuciones que son said/asked
    # Anti-poeta (corrección del autor, v2.2): los personajes hablan NORMAL.
    "simil_dialogo_max": 2,           # símiles en boca de personajes por capítulo (y solo de calle)
    "simil_narracion_por_1000_max": 0.3,  # símiles del narrador por 1000 palabras
    "poeta_lexico_max": 0,            # léxico de poeta-matemático: cero
    "epigrama_dialogo_max": 3,        # frases redondas en boca de personajes por capítulo
    "remate_dialogo_max": 2,
    "descripcion_poetica_max": 1,
    "contar_cosas_max": 2,
    "preguntas_dialogo_min": 20,      # % de réplicas que son preguntas (HWFWM 37 %)
    "fragmentos_dialogo_max": 25,     # % de frases de diálogo de dos palabras o menos (HWFWM 23 %)
    "sorry_max": 5,                   # "sorry" en boca de personajes por capítulo (muletilla de Sabina y Dex)
    "pregunta_obvia_max": 1,          # "Is that good?" y similares: hacen parecer tonto al que pregunta
    "accion_por_1000_min": 4.0,       # verbos de contacto/esfuerzo por 1000 palabras (dos capítulos seguidos por debajo = aviso)
    "metafora_papeleo_max": 0,        # deudas, cuentas, papeleo como metáfora en diálogo            # contar pasos, frases, segundos, "I counted"... por capítulo     # relleno descriptivo evidente en narración por capítulo          # remates para quedar bien ("People always do", "So what") por capítulo
    "ingenio_marcadores_max": 12,     # remates "which was X", párrafos-remate de una línea, etc.
    "personificacion_narracion_max": 2,  # instituciones/objetos con verbos de persona, en narración
}


def split_sentences(text):
    text = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?…])\s+", text)
    return [p.strip() for p in parts if len(p.strip().split()) >= 1]


def analyze_text(text, prev_texts=None):
    words = text.split()
    n_words = max(1, len(words))
    sentences = split_sentences(text)
    n_sent = max(1, len(sentences))
    lengths = [len(s.split()) for s in sentences]
    mean_len = sum(lengths) / n_sent
    std_len = (sum((l - mean_len) ** 2 for l in lengths) / n_sent) ** 0.5

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    dialogue_paras = [p for p in paragraphs if p.lstrip().startswith(("—", "–", "«", '"', "-", "“"))]

    low = text.lower()
    mente = len(re.findall(r"\b\w{4,}mente\b", low))
    mente += sum(1 for w in re.findall(r"\b[a-z]{3,}ly\b", low) if w not in LY_STOPLIST)
    similes = len(re.findall(r"\bcomo (?:si |un |una |el |la )", low))
    similes += len(re.findall(r"\blike (?:a |an |the |some )|\bas (?:if |though )", low))
    no_sino = len(re.findall(r"\bno \b[^,.;]{2,40}, sino\b", low))
    no_sino += len(re.findall(r"\bnot \b[^,.;]{2,40}, but\b", low))
    slop_hits = {p: low.count(p) for p in SLOP_LEXICON if p in low}

    openers = Counter(s.split()[0].lower().strip("—–«\"'¿¡") for s in sentences if s.split())
    top_opener, top_count = (openers.most_common(1)[0] if openers else ("", 0))

    frag_endings = 0
    for p in paragraphs:
        last = split_sentences(p)
        if last and len(last[-1].split()) < 6:
            frag_endings += 1

    # Page-turner: guiones largos, tamaño de párrafo, atribuciones de diálogo
    em_dashes = text.count("—") + text.count("–")
    para_words = [len(p.split()) for p in paragraphs] or [0]
    tag_said = len(re.findall(r"\b(said|asked)\b", low))
    tag_other = len(re.findall(r"\b(replied|muttered|exclaimed|grinned|chuckled|smirked|murmured|snapped|hissed|breathed|drawled|quipped|retorted|deadpanned|intoned|declared|observed|remarked|whispered|growled|sighed|offered|managed|added|noted)\b", low))
    said_ratio = round(tag_said / max(1, tag_said + tag_other), 2)

    # Muletillas: 4-gramas repetidos dentro del texto
    tokens = [w.lower().strip(".,;:!?…—«»\"'()") for w in words]
    grams = Counter(" ".join(tokens[i:i + 4]) for i in range(len(tokens) - 3))
    internal_rep = [(g, c) for g, c in grams.most_common(50) if c >= 3][:8]

    # Muletillas entre capítulos: 5-gramas compartidos con capítulos previos
    cross_rep = []
    if prev_texts:
        prev_grams = Counter()
        for pt in prev_texts:
            ptoks = [w.lower().strip(".,;:!?…—«»\"'()") for w in pt.split()]
            prev_grams.update(set(" ".join(ptoks[i:i + 5]) for i in range(len(ptoks) - 4)))
        this_grams = set(" ".join(tokens[i:i + 5]) for i in range(len(tokens) - 4))
        shared = [(g, prev_grams[g]) for g in this_grams if prev_grams[g] >= 1]
        cross_rep = sorted(shared, key=lambda x: -x[1])[:8]

    sim_d, sim_n, poet_hits, fig_examples = figurative_report(text)
    epi_d, epi_n, epi_examples = epigram_report(text)
    punch_hits = punchline_report(text)
    desc_hits = description_report(text)
    count_hits = counting_report(text)
    conv = conversation_report(text)
    wit_hits = wit_report(text)
    person_hits = personification_report(text)

    return {
        "words": n_words,
        "dialogue_similes": sim_d,
        "narration_similes_per_1000": round(1000 * sim_n / n_words, 2),
        "poet_lexicon_hits": poet_hits,
        "figurative_examples": fig_examples,
        "personification_hits": len(person_hits),
        "personification_narration": sum(1 for h in person_hits if h["where"] == "narration"),
        "personification_examples": person_hits[:60],
        "wit_markers": len(wit_hits),
        "wit_examples": wit_hits[:40],
        "dialogue_punchlines": len(punch_hits),
        "description_filler": len(desc_hits),
        "counting_habit": len(count_hits),
        "dialogue_question_pct": conv["question_pct"],
        "dialogue_fragment_pct": conv["fragment_pct"],
        "transaction_metaphors": len(conv["transaction_hits"]),
        "action_per_1000": action_density(text),
        "dialogue_sorry": sum(len(re.findall(r"(?i)\bsorry\b", text[x:y])) for x, y in dialogue_spans(text)),
        "dialogue_obvious_questions": sum(len(re.findall(OBVIOUS_QUESTION, text[x:y])) for x, y in dialogue_spans(text)),
        "previous_chapter_action_per_1000": (action_density(prev_texts[0]) if prev_texts and len(prev_texts[0].split()) > 2000 else None),
        "transaction_examples": conv["transaction_hits"][:10],
        "counting_examples": count_hits[:12],
        "description_examples": desc_hits[:12],
        "punchline_examples": punch_hits[:12],
        "dialogue_epigrams": epi_d,
        "narration_epigrams": epi_n,
        "epigram_examples": epi_examples,
        "sentences": n_sent,
        "sentence_length_mean": round(mean_len, 1),
        "sentence_length_std": round(std_len, 1),
        "short_sentences_pct": round(100 * sum(1 for l in lengths if l < 8) / n_sent, 1),
        "long_sentences_pct": round(100 * sum(1 for l in lengths if l > 30) / n_sent, 1),
        "dialogue_paragraph_pct": round(100 * len(dialogue_paras) / max(1, len(paragraphs)), 1),
        "mente_per_1000": round(1000 * mente / n_words, 2),
        "simile_per_1000": round(1000 * similes / n_words, 2),
        "no_sino_per_1000": round(1000 * no_sino / n_words, 2),
        "slop_per_1000": round(1000 * sum(slop_hits.values()) / n_words, 2),
        "slop_hits": slop_hits,
        "top_sentence_opener": {"word": top_opener, "fraction": round(top_count / n_sent, 2)},
        "fragment_paragraph_endings_pct": round(100 * frag_endings / max(1, len(paragraphs)), 1),
        "em_dash_per_1000": round(1000 * em_dashes / n_words, 2),
        "paragraph_words_mean": round(sum(para_words) / len(para_words), 1),
        "said_ratio": said_ratio,
        "repeated_4grams": internal_rep,
        "pet_phrases_from_previous_chapters": cross_rep,
    }


def evaluate(metrics, anchor_metrics=None):
    warnings = []
    m = metrics
    if m["sentence_length_std"] < UMBRALES["std_frase_min"] and m["sentences"] > 20:
        warnings.append(f"RITMO UNIFORME (voz robot): desviación de longitud de frase {m['sentence_length_std']} "
                        f"(mínimo sano ~{UMBRALES['std_frase_min']}). Alternar frases cortas y largas.")
    if m["mente_per_1000"] > UMBRALES["mente_por_1000_max"]:
        warnings.append(f"Adverbios en -mente: {m['mente_per_1000']}/1000 palabras (máximo sano ~{UMBRALES['mente_por_1000_max']}).")
    if m["simile_per_1000"] > UMBRALES["simil_por_1000_max"]:
        warnings.append(f"Densidad de símiles: {m['simile_per_1000']}/1000 (máximo sano ~{UMBRALES['simil_por_1000_max']}). La lectura se vuelve pesada.")
    if m["slop_per_1000"] > UMBRALES["slop_por_1000_max"]:
        warnings.append(f"Léxico quemado: {m['slop_per_1000']}/1000. Frases detectadas: {list(m['slop_hits'])[:5]}")
    if m["no_sino_per_1000"] > UMBRALES["no_sino_por_1000_max"]:
        warnings.append(f"Tic 'no X, sino Y': {m['no_sino_per_1000']}/1000. Es una muletilla de IA reconocible.")
    if m["top_sentence_opener"]["fraction"] > UMBRALES["arranque_repetido_max"] and m["sentences"] > 20:
        warnings.append(f"El {int(m['top_sentence_opener']['fraction']*100)}% de las frases arrancan con "
                        f"'{m['top_sentence_opener']['word']}'. Variar los arranques.")
    if m["fragment_paragraph_endings_pct"] > UMBRALES["fragmento_final_parrafo_max"] * 100:
        warnings.append(f"El {m['fragment_paragraph_endings_pct']}% de los párrafos cierran con fragmento efectista. "
                        "Usado en exceso, pierde el efecto.")
    if m["sentence_length_mean"] > UMBRALES["media_frase_max"]:
        warnings.append(f"FRASE LARGA DE MEDIA: {m['sentence_length_mean']} palabras (page-turner ~13-15). Acortar.")
    if m["long_sentences_pct"] > UMBRALES["frases_largas_pct_max"]:
        warnings.append(f"Frases de más de 30 palabras: {m['long_sentences_pct']}% (máximo sano ~{UMBRALES['frases_largas_pct_max']}%).")
    if m["paragraph_words_mean"] > UMBRALES["palabras_parrafo_media_max"]:
        warnings.append(f"PÁRRAFOS LARGOS: media {m['paragraph_words_mean']} palabras (page-turner ~25-30). Partir.")
    if m["em_dash_per_1000"] > UMBRALES["guion_largo_por_1000_max"]:
        warnings.append(f"GUIONES LARGOS: {m['em_dash_per_1000']}/1000 (la prosa de referencia tiene 0). Sustituir por punto o coma.")
    if m["said_ratio"] < UMBRALES["said_ratio_min"] and (m["dialogue_paragraph_pct"] > 10):
        warnings.append(f"Atribuciones de diálogo rebuscadas: solo {int(m['said_ratio']*100)}% son said/asked. Usar 'said'.")
    if m["dialogue_similes"] > UMBRALES["simil_dialogo_max"]:
        warnings.append(f"POETAS EN EL DIÁLOGO: {m['dialogue_similes']} símiles o comparaciones en boca de personajes "
                        f"(máximo {UMBRALES['simil_dialogo_max']}, y solo de calle). La gente habla normal. Ver figurative_examples.")
    if m["narration_similes_per_1000"] > UMBRALES["simil_narracion_por_1000_max"]:
        warnings.append(f"Símiles del narrador: {m['narration_similes_per_1000']}/1000 (máximo {UMBRALES['simil_narracion_por_1000_max']}). "
                        "Cortar los literarios; dejar solo los concretos que diría un chaval de dieciséis.")
    if m["dialogue_epigrams"] > UMBRALES["epigrama_dialogo_max"]:
        warnings.append(f"EPIGRAMAS EN EL DIÁLOGO: {m['dialogue_epigrams']} frases redondas en boca de personajes "
                        f"(máximo {UMBRALES['epigrama_dialogo_max']}). Antítesis, definiciones, 'the only thing that', 'there's a word for it', "
                        "anáforas. La gente dice lo que quiere decir, con sintaxis normal. Ver epigram_examples.")
    if m["dialogue_paragraph_pct"] > 10 and m["dialogue_question_pct"] < UMBRALES["preguntas_dialogo_min"]:
        warnings.append(f"CONVERSACIÓN DE ROBOTS: solo el {m['dialogue_question_pct']}% de las réplicas son preguntas "
                        f"(HWFWM 37 %, mínimo {UMBRALES['preguntas_dialogo_min']} %). La gente se pregunta cosas, reacciona, "
                        "se queja y contesta a lo que le dicen; no se turna para soltar declaraciones.")
    if m["dialogue_paragraph_pct"] > 10 and m["dialogue_fragment_pct"] > UMBRALES["fragmentos_dialogo_max"]:
        warnings.append(f"DIÁLOGO A TROZOS: {m['dialogue_fragment_pct']}% de las frases de diálogo tienen dos palabras o menos "
                        f"(HWFWM 23 %, máximo {UMBRALES['fragmentos_dialogo_max']} %). Frases completas y normales.")
    if m["dialogue_obvious_questions"] > UMBRALES["pregunta_obvia_max"]:
        warnings.append(f"PREGUNTA OBVIA: {m['dialogue_obvious_questions']} preguntas del tipo 'Is that good?' / 'What does that mean?' "
                        f"(máximo {UMBRALES['pregunta_obvia_max']}). Dex es listo: saca la conclusión él solo y pregunta lo que de verdad "
                        "no puede saber, enseñando que ya lo ha pensado.")
    if m["dialogue_sorry"] > UMBRALES["sorry_max"]:
        warnings.append(f"MULETILLA SORRY: {m['dialogue_sorry']} 'sorry' en el diálogo (máximo {UMBRALES['sorry_max']}). "
                        "Sabina se corrige y Dex es educado, pero una disculpa en cada frase les convierte en una muletilla. "
                        "Como mucho uno por escena, y solo donde de verdad se disculparía.")
    if (m["words"] > 2000 and m["action_per_1000"] < UMBRALES["accion_por_1000_min"]
            and m.get("previous_chapter_action_per_1000") is not None
            and m["previous_chapter_action_per_1000"] < UMBRALES["accion_por_1000_min"]):
        warnings.append(f"POCA ACCIÓN: este capítulo ({m['action_per_1000']}/1000) y el anterior "
                        f"({m['previous_chapter_action_per_1000']}/1000) casi no tienen golpes, entrenamiento con contacto ni "
                        f"esfuerzo físico (mínimo {UMBRALES['accion_por_1000_min']}). Medida tosca: revisar. Dos capítulos seguidos "
                        "sin acción física aburren; el entrenamiento se enseña en la página, con contacto y consecuencias.")
    if m["transaction_metaphors"] > UMBRALES["metafora_papeleo_max"]:
        warnings.append(f"METÁFORA DE PAPELEO: {m['transaction_metaphors']} veces se habla de deudas, cuentas, 'we're even', "
                        "'a tab', 'watch the paperwork' para hablar de personas o favores. El dinero y los papeles de verdad, sí; "
                        "como metáfora, no. Ver transaction_examples.")
    if m["counting_habit"] > UMBRALES["contar_cosas_max"]:
        warnings.append(f"CONTAR COSAS: {m['counting_habit']} veces alguien cuenta pasos, frases, líneas, segundos o dice "
                        f"'I counted' (máximo {UMBRALES['contar_cosas_max']}). La gente normal no cuenta; les vuelve robóticos. "
                        "Números solo para el sistema, el dinero y la cuenta de Pále en pelea. Ver counting_examples.")
    if m["description_filler"] > UMBRALES["descripcion_poetica_max"]:
        warnings.append(f"DESCRIPCIÓN POÉTICA: {m['description_filler']} rellenos descriptivos evidentes en narración "
                        f"(máximo {UMBRALES['descripcion_poetica_max']}): contrastes 'by day/by night', luz y sombra, "
                        "'as you walked past', remates del narrador. Se describe solo lo que la escena necesita, en una o dos "
                        "frases normales. Ver description_examples.")
    if m["dialogue_punchlines"] > UMBRALES["remate_dialogo_max"]:
        warnings.append(f"REMATES EN EL DIÁLOGO: {m['dialogue_punchlines']} frases que solo están para quedar bien "
                        f"(máximo {UMBRALES['remate_dialogo_max']}): generalizaciones sabiondas, apartes ingeniosos, 'So what', "
                        "'People always do', un 'Sir.' suelto tras una pulla. Hacen repelentes a los personajes. La gente dice "
                        "lo que tiene que decir y se calla. Ver punchline_examples.")
    if m["personification_narration"] > UMBRALES["personificacion_narracion_max"]:
        warnings.append(f"LAS INSTITUCIONES NO TIENEN OJOS: {m['personification_narration']} sujetos institucionales, colectivos u objetos "
                        f"con verbos de persona en narración (máximo {UMBRALES['personificacion_narracion_max']}). 'The levy didn't look at medical notes': "
                        "las levas no miran, los médicos de la leva sí. Ver personification_examples.")
    if m["wit_markers"] > UMBRALES["ingenio_marcadores_max"]:
        warnings.append(f"INGENIO DE NARRADOR: {m['wit_markers']} marcadores (remates 'which was X', párrafos-remate de una línea, "
                        f"hipérboles; máximo {UMBRALES['ingenio_marcadores_max']}). Una observación ligera por página. Ver wit_examples.")
    if sum(m["poet_lexicon_hits"].values()) > UMBRALES["poeta_lexico_max"]:
        warnings.append(f"LÉXICO DE POETA-MATEMÁTICO ({sum(m['poet_lexicon_hits'].values())} usos): "
                        f"{dict(list(m['poet_lexicon_hits'].items())[:8])}. Prohibido: nadie describe una pelea o un sentimiento con aritmética, gramática o geometría.")
    for gram, count in m["repeated_4grams"][:3]:
        warnings.append(f"Muletilla interna: '{gram}' aparece {count} veces en el capítulo.")
    for gram, _ in m["pet_phrases_from_previous_chapters"][:3]:
        warnings.append(f"Muletilla ENTRE capítulos: '{gram}' ya apareció en capítulos anteriores.")

    drift = []
    if anchor_metrics:
        for key, label in [("sentence_length_mean", "longitud media de frase"),
                           ("sentence_length_std", "variación de ritmo"),
                           ("dialogue_paragraph_pct", "proporción de diálogo"),
                           ("mente_per_1000", "adverbios en -mente"),
                           ("simile_per_1000", "densidad de símiles")]:
            a, c = anchor_metrics.get(key), m.get(key)
            if a and c is not None and a > 0:
                ratio = c / a
                if ratio < 0.6 or ratio > 1.67:
                    drift.append(f"DERIVA del ancla en {label}: ancla {a} → capítulo {c}.")
    return warnings, drift


def main():
    parser = argparse.ArgumentParser(description="Linter de prosa SuperNarrative")
    parser.add_argument("--file", default=None, help="Fichero de texto a analizar")
    parser.add_argument("--chapter", type=int, default=None, help="Capítulo (usa su file_path de la DB)")
    parser.add_argument("--set-anchor", default=None, metavar="FILE",
                        help="Fijar el pasaje de este fichero como ancla de estilo del proyecto")
    parser.add_argument("--project", default=None, help="ID del proyecto")
    parser.add_argument("--db", required=True, help="Ruta a la base de datos SQLite")
    args = parser.parse_args()

    require_db(args.db)
    conn = connect(args.db)
    project_id = get_project_id(conn, args.project)

    if args.set_anchor:
        if not os.path.exists(args.set_anchor):
            fail(f"Fichero no encontrado: {args.set_anchor}")
        with open(args.set_anchor, encoding="utf-8") as f:
            anchor_text = f.read()
        metrics = analyze_text(anchor_text)
        conn.execute("UPDATE projects SET style_anchor = ?, style_anchor_metrics = ?, "
                     "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                     (anchor_text, json.dumps(metrics), project_id))
        conn.commit()
        print(json.dumps({"status": "success", "action": "set_anchor",
                          "anchor_words": metrics["words"], "anchor_metrics": metrics,
                          "message": "Ancla de estilo fijada. Cada capítulo se comparará contra ella."},
                         ensure_ascii=False, indent=2))
        return

    if args.chapter is not None:
        row = conn.execute(
            "SELECT file_path FROM chapters WHERE project_id = ? AND chapter_number = ?",
            (project_id, args.chapter)).fetchone()
        if not row or not row["file_path"] or not os.path.exists(row["file_path"]):
            fail(f"El capítulo {args.chapter} no tiene file_path válido. Usa --file o asigna el fichero al analizar.")
        path = row["file_path"]
    elif args.file:
        if not os.path.exists(args.file):
            fail(f"Fichero no encontrado: {args.file}")
        path = args.file
    else:
        fail("Indica --file, --chapter o --set-anchor")

    with open(path, encoding="utf-8") as f:
        text = f.read()

    # Capítulos previos para detectar muletillas recurrentes
    prev_texts = []
    current_num = args.chapter if args.chapter is not None else 10 ** 9
    for row in conn.execute(
            "SELECT file_path FROM chapters WHERE project_id = ? AND chapter_number < ? "
            "AND file_path IS NOT NULL ORDER BY chapter_number DESC LIMIT 5",
            (project_id, current_num)):
        if row["file_path"] and os.path.exists(row["file_path"]) and row["file_path"] != path:
            with open(row["file_path"], encoding="utf-8") as f:
                prev_texts.append(f.read())

    anchor_row = conn.execute(
        "SELECT style_anchor_metrics FROM projects WHERE id = ?", (project_id,)).fetchone()
    anchor_metrics = json.loads(anchor_row["style_anchor_metrics"]) \
        if anchor_row and anchor_row["style_anchor_metrics"] else None
    conn.close()

    metrics = analyze_text(text, prev_texts)
    warnings, drift = evaluate(metrics, anchor_metrics)

    print(json.dumps({
        "status": "success",
        "file": path,
        "metrics": metrics,
        "warnings": warnings,
        "anchor_drift": drift,
        "clean": not warnings and not drift,
        "note": None if anchor_metrics else
                "Sin ancla de estilo fijada: usa --set-anchor para activar la detección de deriva.",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
