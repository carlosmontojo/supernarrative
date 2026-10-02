# SuperNarrative Skill

## Instrucciones automáticas

- Siempre lee SKILL.md al iniciar
- Siempre consulta la base de datos db/supernarrative.db para conocer el estado actual de la novela antes de hacer cualquier cosa (si no existe, créala con `python3 supernarrative.py init`)
- Antes de escribir cualquier capítulo, ejecuta `python3 supernarrative.py context --chapter N` para obtener el context package
- Después de escribir cualquier capítulo, ejecuta analyze, update (tras confirmación del autor) y verify
- Nunca actualices la base de datos sin mostrarme los cambios primero
- Si update devuelve "unmatched", muéstramelo y corrige los nombres antes de reaplicar con --replace
- Los archivos de la novela están en source/
- Antes de sesiones largas, crea un snapshot: `python3 supernarrative.py snapshot`
