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
- Los personajes NO son poetas ni matemáticos: hablan normal. Cero símiles y comparaciones poéticas en diálogo, cero léxico abstracto de oficio (arithmetic, geometry, grammar, ledger, "a kind of", "the shape of"...). Tampoco frases redondas: ni antítesis-remate ("That's not X. That's Y."), ni definiciones como sabiduría, ni "there's a word for it", ni anáforas. La gente dice la cosa concreta con sintaxis normal. Si el linter avisa de POETAS, LÉXICO DE POETA-MATEMÁTICO o EPIGRAMAS, el capítulo no está terminado. Es mi regresión más típica: revisarla en cada pasada
- Presupuesto de ingenio: UNA réplica ingeniosa por intercambio y UNA observación ligera por página de narración, como máximo, y siempre literal. Nada de chistes con metáfora dentro, ni remates "which was X", ni personificaciones, ni hipérboles, ni resúmenes-sentencia. Los secundarios hablan como su oficio. Ver source/style_spec.md v2.3
