# Prompt de Revisión de Prosa (segunda pasada)

El borrador ya existe y la trama es correcta. Esta pasada NO toca la
historia: afila la prosa. Es obligatoria — la buena prosa de IA se consigue
en revisión dirigida, no en el primer intento.

## ANCLA DE ESTILO DEL PROYECTO
{{style_anchor}}

## INFORME DEL LINTER (prose --chapter N)
{{prose_report}}

## FICHAS DE VOZ DE LOS PERSONAJES PRESENTES
{{voice_cards}}

## CAPÍTULO A REVISAR
{{chapter_content}}

---

## OPERACIONES, EN ESTE ORDEN

### 0. Leer la voz del protagonista
- Si el proyecto tiene `prompts/voz_*.md` (en CORVUS, `prompts/voz_dex.md`), leerlo ENTERO antes de
  empezar. Manda sobre todo lo de abajo en lo que toca a cómo habla y piensa el protagonista: si una
  operación de esta pasada le quitaría la gracia, le haría contestar corto o le callaría, esa operación
  no se le aplica.
- Pasar su lista de comprobación (§9) a cada escena en la que sale.

### 1. Matar los tics de IA (usa el informe del linter como lista de objetivos)
- Cada frase señalada por el léxico quemado: reescribirla desde la escena,
  no sustituirla por otro cliché.
- Cada "no X, sino Y": elegir X o Y, y afirmar.
- Reducir símiles hasta el presupuesto (1 por página). Conservar SOLO los que
  el personaje POV podría pensar — la imagen pertenece al personaje, no al autor.
- Adverbios en -mente: sustituir por verbo preciso o borrar.
- **Los personajes no son poetas ni matemáticos**: cada símil o comparación en
  boca de un personaje se sustituye por el hecho concreto que quería decir
  (ver `figurative_examples` del linter). Cero léxico de poeta-matemático
  (arithmetic, geometry, grammar, ledger, "a kind of", "the shape of"...).
  Cero frases redondas (`epigram_examples`): antítesis-remate, definiciones
  como sabiduría, "there's a word for it", anáforas, fragmentos-sentencia.
  El ingenio permitido es literal y se entiende a la primera.
- Emoción explicada ("sintió que...", "una oleada de..."): borrar la
  explicación; dejar el gesto, el objeto, el silencio.

### 2. Romper el ritmo uniforme
- Leer cada párrafo en voz alta (mentalmente). Donde todas las frases pesen
  lo mismo: fundir dos, partir una. La frase corta se GANA con las largas
  de alrededor.
- Arranques de frase: si el linter marca repetición, variar los tres primeros
  arranques del párrafo señalado.
- Finales de párrafo: máximo uno de cada tres puede cerrar en fragmento
  efectista. Los demás, que terminen donde termina el pensamiento.

### 3. Test de la línea (diálogos)
- Quitar mentalmente las atribuciones de un diálogo de 6+ réplicas.
  ¿Se distingue quién habla por sintaxis, registro y muletillas?
- Si no: reescribir usando las réplicas de ejemplo de cada ficha como
  diapasón. NO añadir atribuciones para compensar — cambiar las voces.
- Remates de superioridad: leer la última frase de cada réplica. Si está para
  poner a alguien por encima de otro (generalización sabionda, aparte de listillo,
  "So what.", "Obviously.", "Sir." suelto tras una pulla, tríptico con giro),
  quitarla o decir la cosa normal. La gracia del protagonista (contestar con el
  chiste dentro, comentar, picar, reírse de sí mismo) NO es un remate y se queda:
  ver la voz del protagonista. El linter cuenta los evidentes (dialogue_punchlines);
  los demás se buscan leyendo.
- Cada réplica informativa ("Como sabes, el testamento..."): eliminarla.
  La información se gana en escena o no se da.

### 3a. Hablan como personas (mecánica de conversación de HWFWM)
- ¿Alguien pregunta algo? ¿Alguien reacciona a lo que acaba de oír? Si nadie
  pregunta ni reacciona, reescribir como pregunta → respuesta directa y completa →
  reacción → siguiente pregunta. (dialogue_question_pct es solo información: cómo
  suena se juzga leyendo la escena al lado de una de HWFWM, no con números.)
- Frases enteras y contracciones para todos, adultos incluidos. Las respuestas
  cortas no van en ristra ("Hm. Again. Better. One."), y el protagonista contesta
  entero (ver su voz).
- Cero metáforas de deudas, cuentas, papeleo, pestañas, precios o "estar en paz"
  para hablar de personas o favores (transaction_metaphors = 0). Se dice la cosa.
- Modelo: capítulo 7 (Livia, Gracchus, Cassius, Aurelia en el desayuno).

### 3b. Narración normal (descripción)
- Cada párrafo de descripción: ¿lo necesita la escena para entenderse? Si no, fuera.
  Si sí, una o dos frases normales: qué hay y dónde. Sin ambiente, sin luz y sombra,
  sin contrastes de efecto, sin símiles, sin "you" genérico, sin remate final.
- El linter cuenta los evidentes (description_filler); el resto se encuentra leyendo.

### 4. Pasada de fluidez
- Transiciones entre escenas: cortar la primera y la última frase de cada
  escena si no pierden nada (suelen ser andamiaje).
- Verbos: cazar "había", "estaba", "parecía" en exceso; activar.

## SALIDA
El capítulo completo revisado, seguido de un bloque final:

```
CAMBIOS: [número] tics eliminados, [número] símiles cortados, [número]
réplicas reescritas por voz, [frase ejemplo del peor tic corregido → cómo quedó]
```
