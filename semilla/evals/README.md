# evals/ — la definición de "sabe ser el CFO de Quentax"

Un caso de eval es una pregunta de CFO con **respuesta correcta cerrada y fuente
verificable**. La colección completa ES la especificación de la IA de Quentax:
el día que un modelo pase estos casos, ese modelo es el producto; mientras
tanto, miden cuánto falta. Sin evals, "el modelo mejora" es una opinión; con
evals, es un porcentaje.

## Formato (`casos.jsonl`, un JSON por línea)

```json
{"id": "iva-001", "area": "iva", "modo": "conocimiento",
 "pregunta": "...", "respuesta": "...", "fuente": "..."}
```

- **area**: `iva`, `contabilidad`, `conciliacion`, `facturacion`, `plazos`, `tesoreria`, ...
  Deben acabar cubriendo TODO lo que hace Quentax.
- **modo**: cómo debe resolverse en la arquitectura final —
  - `conocimiento`: el modelo responde con apoyo del RAG (norma citada).
  - `herramienta`: el modelo NO debe responder de memoria; debe invocar código
    (cálculo, matching de conciliación). El eval comprueba que delega, además
    de que el resultado es correcto. Esto codifica la regla del proyecto:
    *el modelo redacta, las fuentes afirman, el código calcula*.

## Reglas de la colección

1. **Solo respuestas cerradas y verificables hoy.** "Explica bien el IVA" no es
   un eval; "¿tipo general de IVA?" sí.
2. **Cada caso lleva fuente** (norma y artículo, o regla de negocio de Quentax).
3. **La vigencia caduca**: revisar la colección con cada cambio normativo.
   Fecha de revisión en el commit, no en el fichero.
4. **De dónde salen los casos**: dudas reales de usuarios de Quentax, errores
   que un contable junior cometería, y cada bug/corrección del producto.

## Uso

Hoy la colección se ejecuta contra modelos con instrucción-tuning (Fase 3) o
contra modelos ajenos como referencia (¿qué nota saca un modelo abierto sin
nuestro corpus? esa es la línea base a batir). Los checkpoints char-level de
la Fase 0 no pueden pasarlos y no importa: la colección se construye ahora
porque el criterio es más lento de acumular que el cómputo de abaratar.
