# SUPERNARRATIVE — Skill de Memoria Narrativa Profunda para Claude Code

## Qué es SuperNarrative

SuperNarrative es un sistema de memoria narrativa persistente para escritura de ficción compleja. Trata una novela como un programa de software: con estado, dependencias, verificación y consistencia. La memoria vive en una base de datos SQLite que persiste entre conversaciones.

**Analogía fundamental**: Así como un proyecto de software grande necesita Git, tests, CI/CD y gestión de dependencias para no colapsar, una novela compleja necesita un sistema equivalente. SuperNarrative es esa infraestructura.

---

## Setup inicial

Crear el proyecto (la base de datos se crea sola si no existe):

```bash
python3 supernarrative.py init --name "Nombre de la novela" --genre "thriller"
```

Si el usuario ya tiene una novela en progreso (biblia, continuidad, capítulos escritos), importar:

```bash
python3 supernarrative.py import --bible archivo_biblia.docx --continuity archivo_continuidad.md --chapters-dir capitulos/
```

Si la base de datos viene de una versión anterior (v0.1), migrarla una vez:

```bash
python3 supernarrative.py migrate
```


---

## Protocolo de estilo — SE ASIENTA UNA VEZ, GOBIERNA SIEMPRE

El estilo NO se decide capítulo a capítulo: se calibra al arrancar el
proyecto y se mantiene. Es la contramedida a la regresión a la "voz por
defecto" de los LLMs.

1. **Calibrar** (una vez): seguir `prompts/style_calibration.md` —
   entrevista breve al autor, tres muestras de prosa en competencia sobre la
   misma escena, el autor elige.
2. **Asentar el ancla**: `python3 supernarrative.py prose --set-anchor muestra.md`.
   El ancla viaja en cada context package y se cita íntegra en cada prompt
   de generación: la prosa de cada capítulo debe poder intercalarse en ella
   sin costura.
3. **Fichas de voz por contraste**: cada personaje principal con registro,
   sintaxis, muletillas y 2-3 RÉPLICAS DE EJEMPLO literales en
   `speech_patterns` (se imitan los ejemplos, no las descripciones). Si dos
   fichas suenan parecidas, una está mal.
4. **Medir cada capítulo**: `python3 supernarrative.py prose --chapter N` —
   el linter detecta ritmo uniforme (voz robot), exceso de símiles y
   adverbios, léxico quemado de IA, muletillas internas y ENTRE capítulos,
   y la deriva respecto al ancla. Sus avisos alimentan la pasada de revisión.
5. **Revisar siempre** (`prompts/revision.md`): la buena prosa de IA se
   consigue en segunda pasada dirigida — matar tics, romper ritmo uniforme,
   test de la línea en los diálogos. El borrador nunca es la entrega.
6. **Los personajes no son poetas ni matemáticos** (regla fija, corrección del
   autor): la gente habla NORMAL. Cero símiles literarios en diálogo, cero
   léxico de poeta-matemático (arithmetic, geometry, grammar, ledger, "a kind
   of", "the shape of"...) en diálogo y en narración, y cero frases redondas
   (antítesis-remate, definiciones como sabiduría, "there's a word for it",
   anáforas, fragmentos-sentencia). El ingenio es literal y se entiende a la
   primera. El linter lo mide por separado (`dialogue_similes`,
   `poet_lexicon_hits`, `dialogue_epigrams`, con extractos) y un capítulo con
   ese aviso no está terminado. Es la regresión más típica del modelo: vigilar
   en CADA pasada.
7. **Presupuesto de ingenio**: una réplica ingeniosa por intercambio y una
   observación ligera por página de narración, como máximo, siempre literal.
   Nada de chistes con metáfora dentro, remates "which was X",
   personificaciones, hipérboles ni resúmenes-sentencia. Los secundarios hablan
   como su oficio. La densidad se juzga leyendo: más de una frase ingeniosa por
   página es demasiado.

---

## Protocolo de escritura — SEGUIR SIEMPRE

### Antes de escribir un capítulo

1. **Ejecutar context** para obtener el context package:
```bash
python3 supernarrative.py context --chapter N
```
Esto genera un informe con:
- Estado del mundo (ubicaciones de personajes, objetos, fecha/hora en la historia)
- Fichas de los personajes principales (motivación, secreto, defecto, voz)
- Eventos recientes de los últimos capítulos
- Matriz epistémica de los personajes que participarán (qué sabe cada uno)
- Hilos activos que deben considerarse
- Pistas que deben reforzarse o plantarse
- Análisis de ritmo (últimos capítulos) y sugerencia
- Reglas narrativas del proyecto

2. **Mostrar al autor** el context package y confirmar el plan del capítulo.

3. **Escribir el capítulo** usando el prompt de generación (`prompts/generation.md`) con el contexto inyectado. SIEMPRE respetar:
   - El personaje POV SOLO actúa basándose en lo que sabe (consultar matriz epistémica)
   - Nunca forzar exposición a través de diálogo inverosímil
   - Las pistas deben ser extremadamente sutiles
   - La información se gana con investigación, no se regala
   - Preguntarse: "¿esta persona realmente diría esto a alguien que acaba de conocer?"

### Después de escribir un capítulo

4. **Guardar el capítulo** en `exports/chapters/capitulo_XX.md`

5. **Ejecutar analyze.py** para análisis automático:
```bash
python3 supernarrative.py analyze --chapter N --analysis-json analisis.json --chapter-file exports/chapters/capitulo_XX.md
```
Esto extrae automáticamente:
- Eventos ocurridos (movimientos, descubrimientos, revelaciones)
- Cambios epistémicos (quién aprendió qué)
- Beats de hilos narrativos
- Pistas plantadas o reforzadas
- Nivel de tensión y tipo de escena

6. **Mostrar al autor** las actualizaciones propuestas y pedir confirmación.

7. **Ejecutar update.py** para confirmar los cambios:
```bash
python3 supernarrative.py update --chapter N --confirm
# Si devuelve "unmatched", corregir los nombres y reaplicar con --replace
```

8. **Pasar el linter de prosa** y aplicar la revisión dirigida:
```bash
python3 supernarrative.py prose --chapter N
```
Con sus avisos, ejecutar la pasada de `prompts/revision.md` (tics de IA, ritmo, test de la línea) y actualizar el fichero del capítulo.

9. **Ejecutar verify.py** para verificación de consistencia:
```bash
python3 supernarrative.py verify --chapter N
```
Reporta:
- Errores de continuidad física
- Violaciones epistémicas (personaje actúa con info que no tiene)
- Problemas de timeline
- Inconsistencias de voz
- Dependencias de trama violadas
- Pistas abandonadas

### Cada 5 capítulos

9. **Ejecutar dashboard.py** para estado general:
```bash
python3 supernarrative.py dashboard --format terminal
```
Muestra:
- Progreso general
- Hilos activos y su estado
- Pistas sin resolver (con antigüedad)
- Personajes por última aparición
- Curva de tensión
- Issues de consistencia pendientes

---

## Comandos disponibles

El autor puede pedir cualquiera de estas acciones:

| Comando | Acción |
|---------|--------|
| "escribe capítulo N" | Ejecutar protocolo completo de escritura |
| "estado del mundo" | Mostrar ubicaciones, objetos, timeline |
| "qué sabe X" | Mostrar todo lo que sabe un personaje |
| "quién sabe sobre Y" | Mostrar todos los que saben un hecho |
| "hilos activos" | Listar hilos con estado y último beat |
| "pistas activas" | Listar pistas sin resolver |
| "verificar capítulo N" | Re-ejecutar verificación de consistencia |
| "dashboard" | Estado general del proyecto |
| "añadir personaje" | Crear nuevo personaje con ficha completa |
| "añadir localización" | Crear nueva localización |
| "añadir hilo" | Crear nuevo hilo narrativo |
| "añadir regla" | Añadir regla narrativa al proyecto |
| "relación entre X e Y" | Ver/crear/editar relación entre personajes |
| "timeline" | Mostrar cronología de eventos |
| "importar capítulo" | Importar capítulo existente y analizarlo |
| "exportar novela" | Generar documento completo de la novela |
| "buscar inconsistencias" | Verificar toda la novela de golpe |

---

## Reglas narrativas por defecto

Estas reglas se inyectan en cada prompt de generación. El autor puede añadir, quitar o modificar:

1. **Nunca forzar exposición** — Ningún personaje revela información clave a un desconocido sin motivación fuerte.
2. **La información se gana** — Las pistas y revelaciones llegan a través de investigación, observación o deducción, nunca regaladas.
3. **Pistas sutiles** — El lector no debe poder adivinar lo que viene. La pista debe ser invisible en primera lectura y obvia en segunda.
4. **Verosimilitud** — Antes de cada interacción, preguntarse: "¿esta persona realmente diría esto?"
5. **Respetar la matriz epistémica** — Un personaje NUNCA actúa basándose en información que no tiene.
6. **Cada capítulo cierra con hook** — Pregunta sin responder, revelación parcial, decisión pendiente, o peligro inminente.
7. **Variar el ritmo** — No más de 2-3 capítulos consecutivos del mismo tipo de escena.
8. **No resolver sin abrir** — Cada pregunta respondida debe abrir al menos una nueva.

---

## Formato de respuestas de scripts

Todos los scripts devuelven JSON para que Claude Code pueda procesarlos e integrarlos en la conversación de forma natural. Claude Code debe leer el JSON y presentar la información al autor de forma legible y útil, no volcar el JSON crudo.

---

## Notas importantes

- **La DB es la fuente de verdad** — Todo lo que importa está en SQLite. No confiar en la memoria de la conversación para datos narrativos.
- **El autor siempre confirma** — Nunca actualizar la DB sin que el autor revise los cambios propuestos.
- **Offline first** — El sistema de memoria funciona sin LLM. El LLM es un asistente, la memoria es obligatoria.
- **Backups** — Antes de cada sesión larga: `python3 supernarrative.py snapshot` (usa la API de backup de SQLite, segura con WAL).
