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
- Remates: leer la última frase de cada réplica. Si solo está para quedar
  bien (generalización sabionda, aparte ingenioso, "So what.", "Obviously.",
  "Sir." suelto, tríptico con giro, detalle raro para hacer gracia), quitarla
  o decir la cosa normal. Si quitándola la réplica dice lo mismo, sobra.
  El linter cuenta los evidentes (dialogue_punchlines); los demás se buscan leyendo.
- Cada réplica informativa ("Como sabes, el testamento..."): eliminarla.
  La información se gana en escena o no se da.

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
