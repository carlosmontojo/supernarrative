# Roadmap de Semilla (la IA de Quentax)

El principio rector: **cada fase produce algo entrenado y funcionando**, con el hardware disponible en ese momento. El proyecto nunca está "esperando al cómputo": está acumulando lo que el cómputo no compra.

## Fase 0 — El pipeline vivo (hoy)

**Objetivo**: pipeline completo corpus → tokenizador → entrenamiento → generación, validado de punta a punta con un modelo diminuto sobre texto fiscal real.

- [x] Modelo GPT desde cero en PyTorch (`model.py`)
- [x] Tokenizador de caracteres (`tokenizer.py`)
- [x] Entrenamiento con validación y checkpoints (`train.py`)
- [x] Generación con temperatura y top-k (`generate.py`)
- [x] Descargador de legislación consolidada del BOE (`boe.py`)
- [ ] Entrenar el primer `micro` (~10M) con el corpus fiscal ampliado

**Criterio de éxito**: la loss de validación baja de forma sostenida y el modelo genera texto con la textura del corpus. No se pide más.

## Fase 1 — El corpus fiscal (meses, en paralelo con todo lo demás)

La fase más importante del proyecto y la única que no se puede acelerar con dinero. Tres capas, de más pública a más valiosa:

1. **Legislación y normativa (dominio público, art. 13 LPI)** — con `boe.py`:
   IRPF (BOE-A-2006-20764), IVA (BOE-A-1992-28740), Sociedades (BOE-A-2014-12328),
   LGT (BOE-A-2003-23186), reglamentos, Plan General Contable. Volumen gratis y limpio.
2. **Doctrina y práctica**: consultas vinculantes de la DGT, resoluciones del TEAC,
   manuales de la AEAT. Público, pero exige limpieza y etiquetado de procedencia y vigencia.
3. **El contenido propio de Quentax** — el activo insustituible: documentación del
   producto, FAQs, respuestas de soporte, explicaciones a clientes, casos resueltos.
   Cada respuesta buena que Quentax da a un usuario es un dato de entrenamiento.
   Empezar a guardarlas con formato desde YA.

Además:

- **Tokenizador BPE** propio (~8k-16k vocab) entrenado sobre el corpus fiscal. Mismo interfaz que `tokenizer.py`; el resto del pipeline no cambia.
- **Evals fiscales**: la ventaja de este dominio es que hay respuestas verificables. Un fichero de casos: "¿plazo del modelo 303 del 2T?", "¿tipo de IVA de X?", "¿casilla del modelo 100 para Y?" — con la respuesta correcta y la norma que la sustenta. Se ejecutan contra cada checkpoint. Sin esto, "mejor" es una opinión; con esto, es un porcentaje.

**Criterio de éxito**: >10M tokens de corpus fiscal curado y etiquetado por fuente y fecha de vigencia; evals ejecutables con respuesta cerrada.

## Fase 2 — Escala (cuando el cómputo acompañe)

El mismo código, más números:

- Mixed precision (`bfloat16`), `torch.compile`, gradient accumulation — cambios de pocas líneas en `train.py`.
- Presets 100M → 1B parámetros.
- Alquiler puntual de GPU (el precio por hora de GPU es la señal a vigilar, no el precio de compra).

**Señales de que la fase 2 ha llegado**: entrenar ~100M parámetros sobre el corpus completo cuesta menos que una cena. Históricamente el coste de un nivel fijo de capacidad viene cayendo ~10x cada pocos años; la señal se comprueba, no se predice.

### Fase 2.5 (opcional, decisión de proyecto)

Camino intermedio: partir de pesos abiertos (Llama, Mistral, Qwen) y continuar el pre-entrenamiento con el corpus fiscal. No es depender de una API — los pesos corren en tu máquina y tu corpus los esculpe — pero tampoco es desde cero. Para un producto fiscal en producción esta vía llegará antes a "útil"; la vía desde cero sigue siendo la principal del proyecto por decisión de fundador. Ambas comparten todo: corpus, evals, tokenizador. Nada de lo acumulado se tira.

## Fase 3 — Identidad y arquitectura de producto

Un modelo pre-entrenado completa texto; la IA de Quentax conversa, cita y no se inventa nada. Esta fase tiene dos mitades:

- **Instrucción-tuning** con pares pregunta/respuesta fiscales escritos/curados por ti (por eso se acumulan desde la Fase 1). Personalidad definida por escrito antes de entrenarse: qué tono, qué no responde, cuándo deriva a un asesor humano.
- **Arquitectura de verdad verificable** — el modelo NUNCA es la fuente:
  - la norma vigente llega por recuperación (RAG sobre el corpus legislativo, con fechas de vigencia);
  - los cálculos (cuotas, retenciones, plazos) los hace código determinista, no la red;
  - cada afirmación normativa sale con su cita (norma, artículo, fecha).

En fiscal, la regla es: **el modelo redacta, las fuentes afirman, el código calcula**.

## Lo que se acumula desde hoy, resumido

1. Corpus fiscal en `corpus/` — legislación con `boe.py`, doctrina, y contenido propio de Quentax, cada semana.
2. Pares pregunta/respuesta fiscales (para la Fase 3).
3. Evals: casos fiscales con respuesta verificable y su norma.
4. Familiaridad con el pipeline: entrenar el `nano` de vez en cuando con el corpus creciente, ver la loss bajar, leer lo que genera. La intuición también es un activo.
