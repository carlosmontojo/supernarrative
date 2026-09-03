#!/usr/bin/env python3
"""Seed the SuperNarrative DB from the five canon files (outline, power system,
world bible, characters, romance). Idempotent enough for a fresh DB."""
import json, sqlite3, sys
db = sys.argv[1] if len(sys.argv) > 1 else "db/narratium.db"
c = sqlite3.connect(db); c.execute("PRAGMA foreign_keys=ON")
P = c.execute("SELECT id FROM projects ORDER BY updated_at DESC LIMIT 1").fetchone()[0]

def q(sql, *a): c.execute(sql, a)

# ---------- narrative rules (voice bible) ----------
rules = [
 ("voice","Third person limited, past tense, on Jonah. Two short interludes from other eyes (Marchand ch.4, Priscus ch.34), never more than 2,000 words each.",10),
 ("style","Short and medium sentences. One idea per sentence. Minimal subordinate clauses. Plain contemporary English, HWFWM register.",10),
 ("forbidden","Zero poetic similes, zero lyrical metaphors. Comparisons only functional or comic, and only from Jonah's head.",10),
 ("forbidden","No em dashes in narration. No triple adjectives. Never explain the joke. Never 'like a shadow', 'the silence was', 'time seemed to stop'.",10),
 ("style","Fights in short declaratives: what moved, what cut, what it cost. No slow motion. Seams, footwork, fangs. The number says how hard, the gift says where, the Form says when.",9),
 ("voice","Jonah jokes upward, never downward, and shuts up when someone is about to die. Every chapter: one laugh he should not have, one he should have and does not.",9),
 ("structure","Progression is the spine: from ch.1 no chapter leaves Jonah's grade where it found it, except ch.17 and ch.30 where holding still is the drama. Show the step.",10),
 ("structure","System information is earned through experience and crystallized in block READINGS (indented, no ornament) at investiture, intake, inspections, black market.",8),
 ("voice","Register is caste. Collars plain and short. Thinstripes like officers. Blanks like clerks. Broadstripes in subordinate clauses and never 'I think'. The reader hears Jonah learn to switch.",8),
 ("structure","Lore enters only when a character needs it, argues about it, or gets it wrong. Jonah gets it wrong on purpose.",8),
 ("structure","Livia: no declarations before Book 6. They talk about Forms, the Matter, her brother, the law. Never about themselves. Physical contact budget: a grip correction, a hand on a shoulder in a fight.",9),
 ("structure","Tacitus is wordless until ch.31 ('Name.'). Before that: pressure, hunger, pull, heartbeat. It learns the world through names.",10),
 ("structure","The Law of Spoils runs everywhere: rations by challenge in the Pit, sharpening on Anvil, spolia among Stripes. The strong eat the weak by statute and the text never editorializes it. Jonah does.",8),
 ("structure","Integrity mechanic: when Jonah lies to himself the plate misfires. Never as punishment, always as symptom. He keeps whole by not lying and by saying names.",9),
]
for cat, r, pr in rules: q("INSERT INTO narrative_rules (project_id,category,rule,priority) VALUES (?,?,?,?)", P, cat, r, pr)

# ---------- style references ----------
refs = [
 ("Shirtaloon","He Who Fights With Monsters","Protagonist voice: anti-authority sarcasm that punches up, drops when stakes are real; system exposition through lived experience; close third that lets the reader sit in the joke.","Jason answering a god with a quip and then getting quiet when a friend is dying."),
 ("Pierce Brown","Red Rising","Blade culture: razors, Roman castes, duels decided by footwork and seams, the arena as social ladder, the annexed underclass with its own songs.","Darrow learning the razor from Lorn au Arcos; the Institute as a ladder made of bodies."),
 ("Bryce O'Connor","Iron Prince","Suit progression with readouts, ranks, specs; a unique defective/unique device that evolves with the user; tournament ladder; clean numbers on the page.","Rei's CAD readouts after every fight; the rank letters everyone tracks."),
 ("Alexandre Dumas","The Count of Monte Cristo","Revenge as engine; the sage in the prison; the returned man with a new name; the innocent (Edouard) killed by the machine; the moral cost of vengeance; Valentine and Renee as the women inside the enemy house.","Faria teaching Dantes everything; the Count hesitating after the child dies."),
]
for a,w,t,e in refs: q("INSERT INTO style_references (project_id,author,work,technique,example_description) VALUES (?,?,?,?,?)", P,a,w,t,e)

# ---------- locations ----------
locs = [
 ("Quirinus system", None, "Gas giant Quirinus and its moons and rings, on the Limes."),
 ("Rings of Quirinus", "Quirinus system", "Four centuries of wreckage. Where the derelict is."),
 ("The derelict", "Rings of Quirinus", "Founding-era Flamen hull. Reliquary with the seed."),
 ("The Kestrel", "Quirinus system", "Morrow's salvage barge, two hundred metres. Jonah flies it."),
 ("The Vigilant", "Quirinus system", "Imperial patrol cutter. Decurion Varro's ship."),
 ("Anvil", "Quirinus system", "Quirinus IV. Shipbreaking moon. Yards in vacuum on the surface, Collar tenements cut into the rock."),
 ("Anvil yards", "Anvil", "Morrow yard and three Imperial contractors. Hulls broken with steel in vacuum."),
 ("Anvil tenements", "Anvil", "Collar housing under the rock. The Vale rooms are here."),
 ("Founding Square", "Anvil", "Where the Lesser Ludi and sharpening bouts are held on Founding Day."),
 ("Quaestor's house, Anvil", "Anvil", "Priscus's residence and offices while posted. Holding cells beneath."),
 ("Holding cells, Anvil", "Quaestor's house, Anvil", "Where Jonah is held after the arrest. The bars."),
 ("The transport", None, "Prison transport from Anvil to Metalla VII."),
 ("Metalla VII", None, "The Pit. Planetoid with the Vein in it."),
 ("Pit surface garrison", "Metalla VII", "Tullus's garrison and the Flamens' college outpost."),
 ("The Throat", "Metalla VII", "Intake shaft, ten kilometres. Unstripping done here."),
 ("The Shallows", "Metalla VII", "Upper galleries. Thin dead Vein. Auger's ground."),
 ("The Deep", "Metalla VII", "Thick living Vein. Deep-diggers. Two years of life."),
 ("The Chamber", "The Deep", "Sealed cell off the Deep where the Censor lives. Officially does not exist."),
 ("The Mouth", "The Deep", "Deepest point reached. A wall that breathes."),
 ("The Heron", None, "Yara's contractor freighter. Matter skimmer."),
 ("The City", None, "Capital, on Latium. Seven hills, the Forum, the Senate, the Great College, the Ludi Maximi."),
 ("The Belt", None, "Halyard country. Smugglers."),
]
for n,p,d in locs:
    pid = c.execute("SELECT id FROM locations WHERE project_id=? AND name=?", (P,p)).fetchone() if p else None
    q("INSERT INTO locations (project_id,name,description,parent_location_id) VALUES (?,?,?,?)", P,n,d, pid[0] if pid else None)
def L(n): return c.execute("SELECT id FROM locations WHERE project_id=? AND name=?", (P,n)).fetchone()[0]

# ---------- characters ----------
chars = [
 dict(name="Jonah Vale", full_name="Jonah Vale", aliases=["Vale","Peregrine","4471","Gaius Sertorius"], role="protagonist",
  description_physical="Nineteen at start. Lean, yard-strong, all ten fingers because he flies instead of cuts. Black collar ring at the throat. Later a thin black line on the forearm (ch.5), later a self-made white scar (ch.8).",
  description_psychological="Anti-authority to the bone. Sarcastic, dry, funny at power's expense, never at the weak's. Shuts up when someone is about to die. Keeps his word past sense. Too honest: believes the system has rules.",
  backstory="Collar from Anvil, Ferrum blood. Mother's collar melted at the pyre when he was nine; foreman said her name wrong; he corrected him and was beaten. Barge pilot for Morrow six years under Captain Ochoa.",
  motivation="To get out. Then to be counted. Then four names and an Empire.",
  secret="He liked the moment after killing Varro: fang back in, still standing, the stripe not.",
  flaw="Believes the system has rules. Priscus cures him.",
  arc_summary="Book 1: from a good man with rules to a good man without them, who keeps one: he does not lie to himself. Grade 4 (ch.1) to Centurion 42 (ch.40).",
  voice_notes="Short, plain, dry. Asks questions he knows the answer to so the other man has to say it. Curses rarely, precisely. Jokes upward.",
  speech_patterns="'Vale. Like the goodbye, not like the valley.' 'Guess.' 'If the Empire wanted to flog him for it, it could get in line.'",
  emotional_state="Tired, competent, mouthy."),
 dict(name="Tacitus", full_name="Tacitus (the seed)", aliases=["the seed","it"], role="secondary",
  description_physical="A whole genius of the Matter. Dark glass plate with no template. Lives under Jonah's skin.",
  description_psychological="Ancient, curious, literal, hungry. Wordless until ch.31. Learns the world through names. Learns sarcasm from Jonah before it learns anything else.",
  backstory="Uncut piece of the Matter, hidden by the Censor in the derelict in 366. Remembers the first cut.",
  motivation="To stay. Things with names stay.", secret="It can leave. It chooses not to, daily. Jonah learns this in Book 6.",
  flaw="Hunger.", arc_summary="Book 1: bond, hunger born, first word 'Name.' Series: warms as Jonah cools.",
  voice_notes="None until ch.31. Pressure, pull, hunger, heartbeat.", speech_patterns="'Name.'", emotional_state="Curious. Hungry."),
 dict(name="Aulus Terentius Pharus", full_name="Aulus Terentius Pharus", aliases=["the Censor","the old man","the tapper"], role="secondary",
  description_physical="Seventy. Unstripped: white scar where the broad stripe was. Thin, straight-backed, hands that still move like a duellist's.",
  description_psychological="Precise, amused, guilty. Teaches with a stick. Cannot say please.",
  backstory="Senator, Master of the Flamens, best fang of his generation. Designed the Pit at 31. Discovered the Vein's truth, hid the last seed (366), brought it to the Senate, condemned, erased, unstripped. Twenty years in the Chamber, kept alive because Tullus needs his numbers.",
  motivation="To be forgiven by the dead. To make one man who can do what he could not.",
  secret="He hid the seed out of fear of what a whole genius would do in a man, not to save it. He designed the Pit.",
  flaw="Pride wearing guilt's clothes.", arc_summary="Ch.10 taps Jonah through the bond; ch.12 met; ch.13-21 teaches two ladders; ch.20 secret out; ch.22 dies.",
  voice_notes="Precise, eight registers, Latin when tired. 'Boy' until ch.21. 'Sertorius' once, dying.",
  speech_patterns="'Nobody here dies of the Vein. They die of not understanding it.' 'You fight like a man with a fang. Fight like a man with a hand.'",
  emotional_state="Waiting."),
 dict(name="Marcus Vibius Priscus", full_name="Marcus Vibius Priscus", aliases=["Priscus","the quaestor"], role="antagonist",
  description_physical="Thirty-two. Broad purple stripe. Tribune 62. Still, economical, never hurries. Vibian Form.",
  description_psychological="Believes in the law with a convert's fury. Subordinate clauses. Never 'I think'. Holds Pulse and never needs to ask twice.",
  backstory="Inherited Aequitas at twenty and killed his cousin for it the same week. Father is a Gracchan; he has known since sixteen. Quaestor posted to Anvil to build a career. Wife Aemilia, son Marcus (one year old), sister Livia thirteen years younger whom he half raised.",
  motivation="Praetor, consul, remembered as the magistrate who never bent the law.",
  secret="His father is a Gracchan treasurer. He burned the seal and buried Jonah without trial (ch.6). He told Livia the boy went home and recorded him dead in the Throat.",
  flaw="He arranges the world so the court never hears the question.",
  arc_summary="Ch.3 stops a flogging because the boy won. Ch.6 buries the same boy. Ch.34 lies to his sister. Book 4: praetor, falls, his son with him.",
  voice_notes="Courtroom syntax. Asks a question once, then waits.", speech_patterns="'The boy won. Flog the instructor.' 'Collars see monsters in every barge.'",
  emotional_state="Bored, then not."),
 dict(name="Livia Vibia", full_name="Livia Vibia", aliases=["Livia","the quaestor's sister"], role="secondary",
  description_physical="Nineteen at start, Jonah's age. Broad stripe on a cadet's cutting, Centurion 40. Twenty-five in ch.25 as a Flamen scholar-novice.",
  description_psychological="Asks questions she does not know the answer to. Precise like her brother, then a joke. Will not spoil. Wins and stops.",
  backstory="Second child of Vibius the elder, so a cutting, not the house lorica. Half raised by Priscus. Best fang in the house. Flamen-scholar track after refusing marriages.",
  motivation="To know what the Matter is. To be right or wrong about her brother and survive it.",
  secret="Her own note: 'Throat, 4471, reading unstable.' Not reported. She read her brother with her own Pulse at fifteen and he lied.",
  flaw="Trusts the reading less and the man more.", arc_summary="Book 1 five touches: ch.3 yard edge, ch.5 wrong colour, ch.6 the bars, ch.25 the Throat, ch.34 the register. Series slow burn, resolves Book 6.",
  voice_notes="Precise, then a joke. Never lies to Jonah.", speech_patterns="'He won.' 'How did you do that?'", emotional_state="Bored at the games."),
 dict(name="Tom Vale", full_name="Tom Vale", aliases=["Tom"], role="secondary",
  description_physical="Fifty-five, yard-broken, nine fingers.", description_psychological="Believes in the ladder. Formal with Stripes in a way that makes Jonah want to hit something.",
  backstory="Sold the coordinates of a founding-era hull to a Gracchan agent twenty years ago for a winter's food. Never knew what was in it.",
  motivation="A stripe for his son.", secret="The coordinates.", flaw="Faith in a promise never paid.",
  arc_summary="Weeps at the investiture (ch.5). Fangs at his throat at the arrest. Dies in 389, unrecorded.", voice_notes="Slow, kind, formal.", speech_patterns="'Sir.'", emotional_state="Proud, afraid."),
 dict(name="Mara Ansel", full_name="Mara Ansel", aliases=["Mara"], role="secondary",
  description_physical="Twenty. Hull welder. Burn scars on the forearms. Collar.", description_psychological="Direct, unsentimental, funny in a way that used to match Jonah's. She taught him to joke upward.",
  backstory="Ferrum family; father lost a hand in the yards and was docked scrip for the glove.", motivation="To keep the people she has.",
  secret="Knew Jonah was alive for two years (Morrow told her). Married Corin in the third.", flaw="Love does not pay rent.",
  arc_summary="Ch.3 the hull ring. Ch.36 the ring on a chain under Corin's roof. Book 3: 'And what are you now?'", voice_notes="Direct.", speech_patterns="", emotional_state="Happy, for once."),
 dict(name="Corin Aldane", full_name="Corin Aldane", aliases=["Corin"], role="antagonist",
  description_physical="Twenty-one. Big, yard-strong, quick. Collar. Later a thin purple stripe.", description_psychological="Brave in every fight, coward in every room. Says 'sir' to people who do not deserve it.",
  backstory="Called to sharpen at fourteen, lost, lived because the Stripe was bored. Wins the Lesser Ludi ch.3. Auxiliaries. Earns his stripe at Tessera (390) by opening the yard doors.",
  motivation="To be a Stripe. To stop being afraid.", secret="Signed the letter because Jonah won a bout Corin could not have won, not for Mara. Believes it was for Mara.",
  flaw="Fear dressed as ambition.", arc_summary="Ch.3 wins, watches Mara. Ch.4 signs. Ch.36 a Thinstripe with auxiliaries, sees the Sertorian Form. Book 3 falls.",
  voice_notes="Careful. 'Sir.' 'Friend.'", speech_patterns="", emotional_state="Jealous, ashamed of it."),
 dict(name="Silas Marchand", full_name="Silas Marchand", aliases=["Marchand","the purser"], role="antagonist",
  description_physical="Thirty-one. Blank, Tiro 3. Neat, soft-handed, ledger under one arm.", description_psychological="Precise, envious, afraid. Never says a number he has not checked. Has never lost a negotiation.",
  backstory="Purser of the Kestrel. Passed over for the captaincy for a Collar.", motivation="To be paid what he is worth, computed to the shard.",
  secret="Saw the plate through the hatch (ch.2). Wrote the letter out of fear before envy.", flaw="Small.",
  arc_summary="Ch.2 'I didn't see anything, Captain.' Ch.4 writes the letter. Becomes a publican. Book 2 falls.", voice_notes="'Let's be precise.'", speech_patterns="", emotional_state="Calculating."),
 dict(name="Gaspar Roake", full_name="Gaspar Roake", aliases=["Gaspar"], role="antagonist",
  description_physical="Forty. Welder. Drunk. Collar.", description_psychological="Born tired. Honest when drunk, which is always.",
  backstory="Tom Vale's neighbour and friend.", motivation="The next drink.", secret="Loved Tom. Let his son go. Not sober since.",
  flaw="Silence.", arc_summary="Ch.4 drinks while the letter is written. Ch.35 sells the story to a hooded stranger for a shard.", voice_notes="Slurred, honest.", speech_patterns="", emotional_state="Drunk."),
 dict(name="Ezra Morrow", full_name="Ezra Morrow", aliases=["Morrow"], role="secondary",
  description_physical="Fifty. Blank. Big, tired, kind.", description_psychological="Pays Collars like citizens and is therefore poor and therefore the only rich man on Anvil.",
  backstory="Son of a publican. Built the yard as an apology.", motivation="A yard where nobody loses a hand for a glove.",
  secret="Told Mara Jonah was alive. Asked the Gracchans for help; they asked what the boy was carrying.", flaw="Decency in an indecent market.",
  arc_summary="Ch.1 stops the flogging. Ch.2 announces the petition. Ch.37 saved anonymously.", voice_notes="Warm, blunt.", speech_patterns="", emotional_state="Grieving Ochoa."),
 dict(name="Julia Morrow", full_name="Julia Morrow", aliases=["Julia"], role="tertiary", description_physical="Nine at start, sixteen in ch.37.", description_psychological="The Morrow habit of noticing.", backstory="", motivation="", secret="", flaw="", arc_summary="Ch.37 sees a hooded man. Book 3.", voice_notes="", speech_patterns="", emotional_state=""),
 dict(name="Captain Ochoa", full_name="Ochoa", aliases=["the captain"], role="secondary",
  description_physical="Sixty. Ferrum sailor. Careful in everything.", description_psychological="Careful.",
  backstory="Gracchan courier for money, then for the cause. Bought the hull coordinates from Tom Vale's Gracchan. Went looking before the Flamens could.",
  motivation="Get the seed out of the rings before the war.", secret="He never told Jonah what the derelict was. Was going to, that night.", flaw="Waited a night too long.",
  arc_summary="Dies ch.1 mid-sentence on Varro's fang. Last words: 'The seal. Vibius. Promise.'", voice_notes="Few words.", speech_patterns="", emotional_state="", status="alive"),
 dict(name="Decurion Varro", full_name="Titus Varro", aliases=["Varro","the officer"], role="antagonist",
  description_physical="Thirty-five. Narrow stripe, sleeve rolled. Principal 24. Fulvian Form from a manual.", description_psychological="Contempt for Collars as a reflex. Kills to save paperwork.",
  backstory="Thinstripe from Etruria, posted to the Vigilant as punishment for a duel won too publicly.", motivation="The claim.", secret="", flaw="Laughs at the wrong arm.",
  arc_summary="Kills Ochoa ch.1. Killed by Jonah ch.1. Devoured ch.2. Lives on as an echo in Jonah's hands.", voice_notes="Officer.", speech_patterns="'Peregrine. What's in the box?'", emotional_state=""),
 dict(name="Marcius Tullus", full_name="Marcius Tullus", aliases=["Tullus","the prefect"], role="antagonist",
  description_physical="Fifty. Principal 38, fused at 39. Trimmed once at twenty-six.", description_psychological="Decent administrator of an atrocity. Numbers.",
  backstory="Never got the licence. Remembers what 52 felt like.", motivation="The licence. The quota.", secret="Uses the Censor's numbers monthly.", flaw="Believes the Pit is necessary and needs to.",
  arc_summary="Ch.14 raises quota. Ch.19 decimates. Ch.29 harvest.", voice_notes="Quotas, casks, shards, men.", speech_patterns="", emotional_state=""),
 dict(name="Gnaeus Sabinus", full_name="Gnaeus Sabinus", aliases=["Sabinus","the Trimmer"], role="antagonist",
  description_physical="Forty. Centurion 45 on licence. Trimmed twice. Claudian-trained without the Wall. Fast.", description_psychological="Wants a fight that is not a harvest. Knows what a trim feels like.",
  backstory="Client of the Princeps' house, washed out because he could not bear to grind.", motivation="Never be trimmed again.", secret="Read about the Sertorian Form once. Recognizes it in ch.30 and says 'Oh'.", flaw="Likes it fast.",
  arc_summary="Ch.19 harvests convicts in the riot. Ch.29-30 the duel. Devoured.", voice_notes="Few words, amused.", speech_patterns="", emotional_state=""),
 dict(name="Decimus", full_name="Decimus", aliases=[], role="secondary",
  description_physical="Forty-five. Blank guard, Tiro 7. Licensed to 9, never took it.", description_psychological="Fair, tired, funny in a small way. The only guard who says please.",
  backstory="Daughter Sula, nine, in the Interior. Stays for the pay.", motivation="Finish the posting, go home.", secret="", flaw="Orders.",
  arc_summary="Ch.9 met. Ch.17 the good guard. Ch.19 saved by Jonah. Ch.30 killed by Jonah. In the book.", voice_notes="'Please.'", speech_patterns="", emotional_state=""),
 dict(name="Auger", full_name="Auger", aliases=["the king of the Shallows"], role="secondary",
  description_physical="Fifty. Unstripped Blank, was 6. Scar. Chisel.", description_psychological="Cruelest man in the Pit and runs a fair challenge.",
  backstory="Won a legal sharpening against a Thinstripe and was unstripped for winning. Daughter on Marl thinks he is dead.", motivation="Hold the Shallows until he dies.", secret="The daughter.", flaw="", arc_summary="Ch.9 law. Ch.19 the play. Ch.28 demands in. Ch.29 does not betray.", voice_notes="", speech_patterns="", emotional_state=""),
 dict(name="Ulli", full_name="Ulli", aliases=[], role="secondary", description_physical="Marl-born deep-digger. Thirty.", description_psychological="Sings field songs to the Vein. It sings back.", backstory="", motivation="", secret="", flaw="", arc_summary="Ch.18 the Vein sings names. Ch.27 stays to cover. 'Two l's.'", voice_notes="", speech_patterns="", emotional_state=""),
 dict(name="Yara", full_name="Yara", aliases=["the captain of the Heron"], role="secondary",
  description_physical="Thirty-five. Halyard blood on a Blank's stripe. Tiro 9. Hush turned inward.", description_psychological="Never cheated a partner, cheated every authority. Has a wife on the Belt.",
  backstory="Got citizenship by informing on her family's yard.", motivation="A ship that is hers and a Belt with no Empire in it.", secret="How she got the stripe.", flaw="", arc_summary="Ch.32-33 the hold, the price. First ally.", voice_notes="Flat, quick.", speech_patterns="'So who are you now?'", emotional_state=""),
 dict(name="Vibius the elder", full_name="Lucius Vibius", aliases=["Vibius","the senator"], role="tertiary", description_physical="Seventy. Tribune 66.", description_psychological="Wants the Senate to hold the Wall. Would not free a Collar.", backstory="Gracchan treasurer. The seal was addressed to him.", motivation="", secret="Gracchan.", flaw="", arc_summary="Book 4 learns his son burned the seal, from Livia.", voice_notes="", speech_patterns="", emotional_state=""),
 dict(name="Cassius Rufus", full_name="Cassius Rufus", aliases=["the cadet"], role="tertiary", description_physical="Nineteen. Thinstripe cadet, Miles 12.", description_psychological="Bored, cruel, then humiliated.", backstory="", motivation="", secret="", flaw="", arc_summary="Ch.3 calls Jonah to sharpen and loses in nine seconds. Book 2.", voice_notes="", speech_patterns="", emotional_state=""),
 dict(name="Pollio", full_name="Pollio", aliases=["the young Flamen"], role="tertiary", description_physical="Blank, college, grade 8. Lorica Sight, Scent.", description_psychological="Careful. Writes things down.", backstory="", motivation="", secret="", flaw="", arc_summary="Ch.25 frowns and writes it down. Book 2.", voice_notes="", speech_patterns="", emotional_state=""),
 dict(name="Nasso", full_name="Nasso", aliases=["the black-market Flamen"], role="tertiary", description_physical="Defrocked Flamen on Anvil's lower docks.", description_psychological="Afraid and greedy.", backstory="", motivation="", secret="", flaw="", arc_summary="Ch.38 reads Jonah, is bought, sells the reading to a Frumentarius ch.40.", voice_notes="", speech_patterns="", emotional_state=""),
 dict(name="Tiberius Claudius Septimus", full_name="Tiberius Claudius Septimus", aliases=["the Princeps"], role="mentioned", description_physical="Seventy-one. Imperator 131. Holds the Wall.", description_psychological="Tired in the way that makes men dangerous.", backstory="", motivation="", secret="Has done the Censor's arithmetic.", flaw="", arc_summary="Book 2.", voice_notes="", speech_patterns="", emotional_state=""),
]
for d in chars:
    q("""INSERT INTO characters (project_id,name,full_name,aliases,role,description_physical,description_psychological,backstory,motivation,secret,flaw,arc_summary,voice_notes,speech_patterns,status,emotional_state)
         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", P,d["name"],d.get("full_name"),json.dumps(d.get("aliases",[])),d["role"],d.get("description_physical"),d.get("description_psychological"),d.get("backstory"),d.get("motivation"),d.get("secret"),d.get("flaw"),d.get("arc_summary"),d.get("voice_notes"),d.get("speech_patterns"),d.get("status","alive"),d.get("emotional_state"))
def C(n): return c.execute("SELECT id FROM characters WHERE project_id=? AND name=?", (P,n)).fetchone()[0]

# starting locations
start = {"Jonah Vale":"The Kestrel","Tacitus":"The derelict","Captain Ochoa":"The Kestrel","Silas Marchand":"The Kestrel","Decurion Varro":"The Vigilant",
 "Tom Vale":"Anvil tenements","Mara Ansel":"Anvil yards","Corin Aldane":"Anvil yards","Gaspar Roake":"Anvil tenements","Ezra Morrow":"Anvil yards","Julia Morrow":"Anvil",
 "Marcus Vibius Priscus":"Quaestor's house, Anvil","Livia Vibia":"Quaestor's house, Anvil","Cassius Rufus":"Anvil","Aulus Terentius Pharus":"The Chamber",
 "Marcius Tullus":"Pit surface garrison","Gnaeus Sabinus":"Pit surface garrison","Decimus":"The Shallows","Auger":"The Shallows","Ulli":"The Deep","Yara":"The Belt",
 "Vibius the elder":"The City","Pollio":"Pit surface garrison","Nasso":"Anvil","Tiberius Claudius Septimus":"The City"}
for n,l in start.items(): q("UPDATE characters SET current_location_id=? WHERE id=?", L(l), C(n))

# ---------- objects ----------
objs = [
 ("The seed","Uncut whole piece of the Matter in a sealed reliquary box. Becomes Tacitus.","The derelict",None,"active","Jonah's edge. Hidden by the Censor in 366."),
 ("The seal","Ochoa's sealed Gracchan packet addressed to Vibius the elder. Proof of the seed.","The Kestrel","Captain Ochoa","active","Why Jonah is buried. Priscus burns it ch.6."),
 ("The hull ring","Ring cut from the first ship Jonah broke. Given to Mara ch.3.","Anvil",None,"active","Ch.36 on a chain under Corin's roof."),
 ("Varro's lorica","Principal 24 cutting. Devoured ch.2.","The Kestrel","Decurion Varro","active","First spolia. First echo."),
 ("The book of names","The Censor's ledger of every condemned man's name.","The Chamber","Aulus Terentius Pharus","active","The most religious object in the series."),
 ("The Kestrel","Morrow's barge.","The Kestrel",None,"active","Jonah's ship."),
 ("Jonah's collar","Standard-issue peregrine collar. Devoured hollow by Tacitus ch.2.","The Kestrel","Jonah Vale","active","Lock stops working on him."),
 ("Pit register","Tullus's intake register. Later in Priscus's study: 'Vale, Jonah. Died in the Throat, 389.'","Pit surface garrison",None,"active","Ch.34 Livia finds it."),
 ("Livia's notebook","Her own notebook, not the College's. 'Throat, 4471, reading unstable.'","The City","Livia Vibia","active","Ch.25, ch.34."),
]
for n,d,l,h,s,sig in objs:
    q("INSERT INTO objects (project_id,name,description,current_location_id,current_holder_id,status,significance) VALUES (?,?,?,?,?,?,?)", P,n,d,L(l), C(h) if h else None, s, sig)

# ---------- facts + knowledge ----------
facts = [
 ("secret","The derelict holds a whole uncut seed of the Matter, hidden by the Censor in 366.",True,10),
 ("secret","Ochoa was a Gracchan courier carrying a seal addressed to Senator Vibius the elder, with the proof of the seed.",True,9),
 ("secret","Jonah carries a whole, unregistered genius (Tacitus) that does not obey imperium and has no fuse.",True,10),
 ("event","Jonah killed Decurion Varro on the derelict and devoured his lorica.",True,9),
 ("event","Tom Vale sold the derelict's coordinates to a Gracchan agent twenty years ago.",True,6),
 ("secret","The Vein is one organism; every lorica is a cutting lobotomized at the Wit line; fuses were introduced in 152 to cap the orders.",True,10),
 ("secret","The Censor designed the Pit.",True,8),
 ("secret","The Censor is alive in the Chamber and Tullus uses his numbers to keep the deep galleries stable.",True,7),
 ("identity","Livia Vibia is Priscus's younger sister and the daughter of Vibius the elder, the seal's addressee.",True,7),
 ("event","Marchand wrote the denunciation (unregistered genius, Gracchan seal); Corin signed it; Gaspar watched and said nothing.",True,9),
 ("event","Priscus burned the seal and buried Jonah without trial to protect his father.",True,10),
 ("event","Priscus told Livia the boy from Anvil was released and went home.",False,7),
 ("event","Priscus recorded Jonah as 'died in the Throat, 389' in the Pit register.",True,7),
 ("event","Tom Vale died in 389; nobody recorded his name.",True,7),
 ("event","Mara married Corin in 391 after her family went under.",True,7),
 ("event","Corin earned his thin stripe by opening the yard doors during the Tessera rising of 390.",True,8),
 ("secret","Marchand saw Jonah's plate through the Kestrel's hatch.",True,8),
 ("secret","Livia noted convict 4471's unstable reading in her own notebook and did not report it.",True,8),
 ("identity","The man in the Pit calling himself 4471 is Jonah Vale.",True,9),
 ("secret","Sabinus once read about the Sertorian Form.",True,5),
]
for cat,d,t,s in facts: q("INSERT INTO story_facts (project_id,category,description,is_true,significance) VALUES (?,?,?,?,?)", P,cat,d,t,s)
def F(prefix): return c.execute("SELECT id FROM story_facts WHERE project_id=? AND description LIKE ?", (P,prefix+"%")).fetchone()[0]
fix12 = F("Priscus told Livia"); q("UPDATE story_facts SET contradiction_of=? WHERE id=?", F("Priscus burned"), fix12)

K = [  # (knower, fact prefix, level, how, detail)
 ("Aulus Terentius Pharus","The derelict holds","knows","witnessed",None),
 ("Captain Ochoa","The derelict holds","partial","told_by:Gracchans","Knows it is a Flamen relic worth a war; not what a seed is."),
 ("Jonah Vale","The derelict holds","unaware",None,None),
 ("Captain Ochoa","Ochoa was a Gracchan","knows","witnessed",None),
 ("Jonah Vale","Ochoa was a Gracchan","unaware",None,None),
 ("Vibius the elder","Ochoa was a Gracchan","knows","witnessed",None),
 ("Aulus Terentius Pharus","The Censor designed","knows","witnessed",None),
 ("Marcius Tullus","The Censor is alive","knows","witnessed",None),
 ("Aulus Terentius Pharus","The Vein is one organism","knows","deduced",None),
 ("Tiberius Claudius Septimus","The Vein is one organism","knows","read",None),
 ("Jonah Vale","The Vein is one organism","unaware",None,None),
 ("Tom Vale","Tom Vale sold","knows","witnessed",None),
 ("Jonah Vale","Tom Vale sold","unaware",None,None),
 ("Captain Ochoa","Tom Vale sold","knows","told_by:Gracchans",None),
 ("Marcus Vibius Priscus","Livia Vibia is","knows","witnessed",None),
 ("Livia Vibia","Livia Vibia is","knows","witnessed",None),
 ("Jonah Vale","Livia Vibia is","unaware",None,None),
 ("Gnaeus Sabinus","Sabinus once read","knows","read",None),
]
for kn,fp,lv,how,det in K:
    q("INSERT INTO knowledge_states (project_id,knower_id,fact_id,knowledge_level,how_learned,wrong_belief_detail) VALUES (?,?,?,?,?,?)", P, C(kn), F(fp), lv, how, det)
for fp in ["The derelict holds","Ochoa was a Gracchan","Jonah carries a whole","The Vein is one organism","The Censor designed","Livia Vibia is"]:
    q("INSERT INTO knowledge_states (project_id,knower_id,fact_id,knowledge_level,how_learned) VALUES (?,?,?,?,?)", P, "__reader__", F(fp), "unaware", "reader_inference")

# ---------- threads ----------
threads = [
 ("Revenge: the four names","Marchand, Corin, Gaspar, Priscus. Jonah learns the names ch.35 and commits ch.39.","main_plot","planned",10,"Series spine. Book 1 plants; resolves across books 2-4."),
 ("The seed and the seal","What the derelict was, why Ochoa went, what the seal proved, who buried whom for it.","mystery","planned",10,"Ch.1 seal; ch.6 burned; ch.12 the Censor explains; ch.35 Tom's coordinates."),
 ("Tacitus","The genius: bond, hunger, echoes, integrity, first word.","character_arc","planned",10,"Wordless until ch.31."),
 ("The Forms","The Censor's blade training: Varro's echo out, four Forms in, the Sertorian Form.","subplot","planned",9,"Ch.13-21. Pays off ch.30."),
 ("Escape from the Pit","Casks, manifest, Ulli, Auger, harvest day, the Trimmer, Decimus.","main_plot","planned",10,"Ch.26-31."),
 ("Livia","The slow burn. Five touches in Book 1.","romance","planned",9,"Ch.3, 5, 6, 25, 34, 39. No declarations before Book 6."),
 ("The book of names","Collars die twice. The Censor's ledger. Jonah inherits it.","thematic","planned",9,"Ch.16 first seen; ch.22 inherited; ch.30 Decimus added; ch.40 recited."),
 ("Mara and Corin","The ring, the letter, the marriage, the stripe.","subplot","planned",7,"Ch.3, 4, 36."),
 ("Marchand's letter","Who denounced Jonah and why. Jonah does not know until ch.35.","mystery","planned",8,"Reader knows from ch.4."),
 ("The Frumentarii","An unregistered genius. The file opens ch.40.","subplot","planned",7,"Hook for Book 2."),
 ("Hunger and Integrity","The costs of Tacitus as mechanics.","thematic","planned",8,"Ch.10 hunger born; ch.18 integrity shown; ch.30 integrity holds."),
 ("Decimus","The good guard. Saved ch.19, killed ch.30, in the book.","character_arc","planned",8,""),
 ("Auger's law","Rations by challenge. The king of the Shallows. Demands in ch.28.","subplot","planned",6,""),
 ("The Vein's truth","What the Matter is. Cuttings, fuses, seeds. The Mouth.","mystery","planned",9,"Ch.16, 23."),
 ("The Censor's guilt","He designed the Pit. Ch.20 rupture.","subplot","planned",8,""),
 ("Morrow's ruin","Marchand's bank. Saved anonymously ch.37.","subplot","planned",6,""),
 ("Priscus's law","A just man who bent the law once. Stops a flogging ch.3, buries Jonah ch.6, lies to Livia ch.34.","character_arc","planned",8,""),
]
for n,d,t,s,pr,notes in threads: q("INSERT INTO plot_threads (project_id,name,description,thread_type,status,priority,notes) VALUES (?,?,?,?,?,?,?)", P,n,d,t,s,pr,notes)
def T(n): return c.execute("SELECT id FROM plot_threads WHERE project_id=? AND name=?", (P,n)).fetchone()[0]
deps = [("Escape from the Pit","The Forms","developing","Jonah cannot beat Sabinus without the Sertorian Form."),
        ("Revenge: the four names","Marchand's letter","resolved","Jonah must learn the names before he can act."),
        ("The Frumentarii","Escape from the Pit","resolved","The file opens once he is out and read."),
        ("Escape from the Pit","The book of names","developing","He must have inherited the book before Decimus dies.")]
for a,b,st,d in deps: q("INSERT INTO thread_dependencies (dependent_thread_id,required_thread_id,required_status,description) VALUES (?,?,?,?)", T(a),T(b),st,d)

# ---------- relationships ----------
rels = [
 ("Jonah Vale","Mara Ansel","lover","Engaged ch.3.","Yard sweethearts.","She survives; marries Corin in 391.","active"),
 ("Jonah Vale","Tom Vale","family","Father and son.","","He believes in the ladder; Jonah does not.","active"),
 ("Jonah Vale","Corin Aldane","rival","Yard friends, rivals for Mara and for the bout.","Friends.","Corin signs the letter.","active"),
 ("Jonah Vale","Captain Ochoa","mentor","Six years on the Kestrel.","Captain and pilot.","Ochoa never told him about the seed.","active"),
 ("Jonah Vale","Ezra Morrow","ally","Owner and pilot.","","Morrow petitions his manumission.","active"),
 ("Jonah Vale","Silas Marchand","enemy","Purser and pilot.","Colleagues.","Marchand fears him after ch.2 and denounces him.","secret"),
 ("Jonah Vale","Marcus Vibius Priscus","enemy","Quaestor and Collar.","Magistrate and accused.","Priscus buries him for a seal.","active"),
 ("Jonah Vale","Livia Vibia","unknown","The slow burn.","A Broadstripe and a Collar who spoke twice.","Every book an almost.","evolving"),
 ("Jonah Vale","Aulus Terentius Pharus","mentor","The Censor and the boy.","","Two ladders. He designed the Pit.","active"),
 ("Jonah Vale","Decimus","ally","Guard and convict.","","Saved ch.19, killed ch.30.","active"),
 ("Marcus Vibius Priscus","Livia Vibia","family","Brother and sister, thirteen years apart. He half raised her.","","He lied to her about the boy.","active"),
 ("Marcus Vibius Priscus","Vibius the elder","family","Father and son.","","The father is a Gracchan; the son burned his seal.","active"),
 ("Corin Aldane","Mara Ansel","lover","Corin wants Mara; marries her in 391.","","She does not love him and is a good wife.","evolving"),
 ("Silas Marchand","Corin Aldane","colleague","Wrote and signed the letter together.","","","secret"),
 ("Marcius Tullus","Aulus Terentius Pharus","colleague","Prefect and the prisoner he needs.","Does not exist.","Monthly numbers.","secret"),
]
for a,b,t,d,pub,priv,s in rels:
    q("INSERT INTO character_relationships (project_id,character_a_id,character_b_id,relationship_type,description,public_perception,private_reality,status) VALUES (?,?,?,?,?,?,?,?)", P,C(a),C(b),t,d,pub,priv,s)

# ---------- chapters (planned) ----------
chs = [
 (1,"Derelict",6000,"action",9,"fast","dread","388, three weeks before Founding Day"),
 (2,"The Rings",4200,"action",8,"frantic","chaotic","388, same night"),
 (3,"Sharpening",5000,"confrontation",7,"medium","hopeful","388, Founding Day"),
 (4,"Interlude: Three Men and a Letter",2000,"dialogue",5,"slow","paranoid","388, Founding Night"),
 (5,"Investiture",4600,"revelation",8,"medium","dread","388, Founding Week"),
 (6,"Imperium",4200,"confrontation",8,"slow","dread","388, Founding Week, next day"),
 (7,"Ad Metalla",4000,"action",7,"medium","dread","388"),
 (8,"The Pit",4800,"revelation",9,"medium","dread","388"),
 (9,"Decury",3800,"action",6,"medium","neutral","388-389"),
 (10,"Mother",4400,"transformation",9,"slow","chaotic","389"),
 (11,"A Voice in the Rock",3600,"dialogue",5,"slow","hopeful","389"),
 (12,"The Censor",4400,"revelation",7,"medium","intimate","389"),
 (13,"Chisel",4200,"action",6,"medium","melancholy","389"),
 (14,"Quota",4400,"confrontation",8,"fast","dread","390"),
 (15,"Grade",3800,"dialogue",5,"medium","neutral","390"),
 (16,"What the Vein Wants",4000,"revelation",7,"slow","paranoid","390"),
 (17,"Decimus",3400,"dialogue",4,"slow","intimate","391"),
 (18,"Deep",4400,"action",8,"fast","chaotic","391"),
 (19,"The Riot",5800,"action",10,"frantic","chaotic","391"),
 (20,"What the Censor Did",3800,"reflection",6,"slow","melancholy","391-392"),
 (21,"The Sertorian Form",5000,"action",6,"medium","triumphant","392-393"),
 (22,"Names",4200,"dialogue",7,"slow","melancholy","394"),
 (23,"The Mouth",5000,"revelation",9,"slow","dread","394"),
 (24,"Tacitus",4000,"reflection",6,"medium","intimate","394"),
 (25,"Inspection",4400,"confrontation",9,"slow","paranoid","394"),
 (26,"Plan",3800,"investigation",6,"medium","neutral","394"),
 (27,"What You Ask of a Friend",3400,"dialogue",6,"slow","melancholy","394"),
 (28,"Auger",3800,"confrontation",7,"medium","paranoid","394"),
 (29,"Harvest",6000,"action",10,"frantic","chaotic","395"),
 (30,"The Trimmer",5500,"action",10,"fast","dread","395"),
 (31,"The Coffin",3200,"reflection",5,"slow","intimate","395"),
 (32,"Hold",4600,"action",8,"fast","chaotic","395"),
 (33,"Smugglers",4000,"dialogue",6,"medium","neutral","395"),
 (34,"Interlude: Priscus",2000,"dialogue",5,"slow","paranoid","395, the City"),
 (35,"Anvil Again",4000,"investigation",6,"medium","melancholy","395"),
 (36,"Mara",3800,"action",7,"medium","melancholy","395"),
 (37,"Morrow",3600,"transition",4,"slow","hopeful","395"),
 (38,"What a Stripe Is Worth",4000,"revelation",7,"medium","paranoid","395"),
 (39,"Sertorius",3400,"dialogue",6,"slow","triumphant","395"),
 (40,"Counted by Head",3200,"reflection",7,"slow","dread","395"),
]
for n,t,wc,st,tl,pc,tone,date in chs:
    q("INSERT INTO chapters (project_id,chapter_number,title,status,scene_type,tension_level,pacing,emotional_tone,story_date,chapter_order,pov_character_id) VALUES (?,?,?,'planned',?,?,?,?,?,?,?)",
      P,n,t,st,tl,pc,tone,date,n, C("Silas Marchand") if n==4 else (C("Marcus Vibius Priscus") if n==34 else C("Jonah Vale")))
c.commit()
print(json.dumps({"characters":c.execute("select count(*) from characters").fetchone()[0],"locations":c.execute("select count(*) from locations").fetchone()[0],
 "facts":c.execute("select count(*) from story_facts").fetchone()[0],"knowledge":c.execute("select count(*) from knowledge_states").fetchone()[0],
 "threads":c.execute("select count(*) from plot_threads").fetchone()[0],"chapters":c.execute("select count(*) from chapters").fetchone()[0],
 "rules":c.execute("select count(*) from narrative_rules").fetchone()[0],"objects":c.execute("select count(*) from objects").fetchone()[0],
 "relationships":c.execute("select count(*) from character_relationships").fetchone()[0]}))
