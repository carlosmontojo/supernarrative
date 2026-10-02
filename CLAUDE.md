# SuperNarrative Skill

## Instrucciones automáticas

- Siempre lee SKILL.md al iniciar
- Siempre consulta la base de datos db/supernarrative.db para conocer el estado actual de la novela antes de hacer cualquier cosa (si no existe, créala con `python3 supernarrative.py init`)
- Antes de escribir cualquier capítulo, ejecuta `python3 supernarrative.py context --chapter N` para obtener el context package
- Si el proyecto no tiene ancla de estilo, calibra primero con prompts/style_calibration.md y fíjala con `prose --set-anchor` — el estilo se asienta una vez y se mantiene
- Después de escribir cualquier capítulo: `prose --chapter N` (linter), pasada de revisión con prompts/revision.md, y luego analyze, update (tras confirmación del autor) y verify
- Nunca actualices la base de datos sin mostrarme los cambios primero
- Si update devuelve "unmatched", muéstramelo y corrige los nombres antes de reaplicar con --replace
- Los archivos de la novela están en source/
- Antes de sesiones largas, crea un snapshot: `python3 supernarrative.py snapshot`
