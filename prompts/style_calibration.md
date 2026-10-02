# Prompt de Calibración de Estilo

Se usa UNA VEZ al arrancar un proyecto (o cuando el autor quiera redefinir la
prosa). Su resultado se asienta y gobierna todos los capítulos: el estilo se
decide aquí, no capítulo a capítulo.

## Proceso

### Paso 1 — Entrevista breve al autor

Preguntar (y aceptar "no sé, enséñame opciones" como respuesta):

1. ¿Dos o tres autores cuya PROSA (no cuyas tramas) admiras para este libro?
2. ¿Frases largas y envolventes, cortas y secas, o mezcla? ¿Presente o pasado?
3. ¿Cuánta imagen poética toleras? (1 = Carver, 10 = García Márquez)
4. ¿Cuánto monólogo interior? (1 = conductista puro, 10 = flujo de conciencia)
5. ¿Hay algo que ODIES encontrarte en un libro?

### Paso 2 — Tres muestras en competencia

Escribir LA MISMA escena (una página, ~350 palabras, con diálogo y acción)
en TRES estilos genuinamente distintos según las respuestas. Etiquetarlas
A/B/C sin explicación. Diferencias reales de sintaxis, temperatura de imagen
y densidad — no tres versiones de lo mismo.

### Paso 3 — Asentar el ancla

El autor elige (o pide mezclar, y se itera). La muestra ganadora se guarda
como **ancla de estilo**:

```bash
python3 supernarrative.py prose --set-anchor muestra_ganadora.md
```

Desde ese momento:
- El ancla viaja en cada context package y se cita ÍNTEGRA en cada prompt de
  generación: "escribe en ESTA prosa" vale más que mil adjetivos de estilo.
- `prose --chapter N` mide la deriva de cada capítulo contra el ancla
  (ritmo, densidad de símiles, proporción de diálogo...). La regresión a la
  voz por defecto deja de ser una sensación: es un número que salta.

### Paso 4 — Fichas de voz de personajes

Para cada personaje principal, rellenar en su ficha (`voice_notes` y
`speech_patterns`):

- **Registro**: culto/coloquial/técnico/arcaico; longitud típica de réplica.
- **Sintaxis**: ¿frases completas o truncadas? ¿subordina o yuxtapone?
- **Muletillas y vocabulario prohibido**: qué dice siempre, qué no diría jamás.
- **speech_patterns: 2-3 RÉPLICAS DE EJEMPLO literales.** Son el ancla de la
  voz: al escribir, imitar esas réplicas, no la descripción.

Regla de oro: las voces se definen POR CONTRASTE. Si dos fichas suenan
parecidas, reescribir una hasta que el test de la línea las distinga.
