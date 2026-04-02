# NARRATIUM — Skill de Memoria Narrativa Profunda para Claude Code

## Qué es Narratium

Narratium es un sistema de memoria narrativa persistente para escritura de ficción compleja. Trata una novela como un programa de software: con estado, dependencias, verificación y consistencia. La memoria vive en una base de datos SQLite que persiste entre conversaciones.

**Analogía fundamental**: Así como un proyecto de software grande necesita Git, tests, CI/CD y gestión de dependencias para no colapsar, una novela compleja necesita un sistema equivalente. Narratium es esa infraestructura.

---

## Setup inicial

Si la DB no existe, crearla:

```bash
cd /path/to/narratium
sqlite3 db/narratium.db < db/schema.sql
```

Si es un proyecto nuevo, inicializar:

```bash
python scripts/init_project.py --name "Nombre de la novela" --genre "thriller" --db db/narratium.db
```

Si el usuario ya tiene una novela en progreso (biblia, continuidad, capítulos escritos), importar:

```bash
python scripts/import_existing.py --bible archivo_biblia.docx --continuity archivo_continuidad.md --db db/narratium.db
```

---

## Protocolo de escritura — SEGUIR SIEMPRE

### Antes de escribir un capítulo

1. **Ejecutar context.py** para obtener el context package:
```bash
python scripts/context.py --chapter N --db db/narratium.db
```
Esto genera un informe con:
- Estado del mundo (ubicaciones de personajes, objetos, fecha/hora en la historia)
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
python scripts/analyze.py --chapter N --db db/narratium.db --file exports/chapters/capitulo_XX.md
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
python scripts/update.py --chapter N --db db/narratium.db --confirm
```

8. **Ejecutar verify.py** para verificación de consistencia:
```bash
python scripts/verify.py --chapter N --db db/narratium.db
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
python scripts/dashboard.py --db db/narratium.db
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
- **Backups** — Antes de cada sesión larga, copiar `narratium.db` con timestamp.
