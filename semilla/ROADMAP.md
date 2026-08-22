# Roadmap de Semilla

El principio rector: **cada fase produce algo entrenado y funcionando**, con el hardware disponible en ese momento. El proyecto nunca está "esperando al cómputo": está acumulando lo que el cómputo no compra.

## Fase 0 — El pipeline vivo (hoy)

**Objetivo**: pipeline completo corpus → tokenizador → entrenamiento → generación, validado de punta a punta con un modelo diminuto.

- [x] Modelo GPT desde cero en PyTorch (`model.py`)
- [x] Tokenizador de caracteres (`tokenizer.py`)
- [x] Entrenamiento con validación y checkpoints (`train.py`)
- [x] Generación con temperatura y top-k (`generate.py`)
- [ ] Entrenar el primer `micro` (~10M) con corpus propio real

**Criterio de éxito**: la loss de validación baja de forma sostenida y el modelo genera texto con la textura del corpus. No se pide más.

## Fase 1 — El corpus (meses, en paralelo con todo lo demás)

Esta es la fase más importante del proyecto y la única que no se puede acelerar con dinero.

- **Corpus propio**: volcar en `corpus/` todo texto propio con valor: novelas, relatos, notas, ensayos, diarios de escritura. La novela de SuperNarrative es candidata natural cuando exista.
- **Corpus de dominio público en español**: Gutenberg, Wikisource, BOE si hace falta prosa administrativa 🙂. Etiquetar la procedencia de cada fuente (un subdirectorio por fuente).
- **Tokenizador BPE**: sustituir el tokenizador de caracteres por BPE propio (~8k-16k vocab) entrenado sobre el corpus. Mismo interfaz que `tokenizer.py`, el resto del pipeline no cambia.
- **Evals propios**: un fichero de prompts + criterios que definan qué significa "suena a mí". Se ejecutan contra cada checkpoint. Sin esto, "mejor" es una opinión.

**Criterio de éxito**: >5M tokens de corpus curado y etiquetado; evals ejecutables.

## Fase 2 — Escala (cuando el cómputo acompañe)

El mismo código, más números:

- Mixed precision (`bfloat16`), `torch.compile`, gradient accumulation — cambios de pocas líneas en `train.py`.
- Presets 100M → 1B parámetros.
- Alquiler puntual de GPU (el precio por hora de GPU es la señal a vigilar, no el precio de compra).

**Señales de que la fase 2 ha llegado**: entrenar ~100M parámetros sobre tu corpus completo cuesta menos que una cena. Históricamente el coste de un nivel fijo de capacidad viene cayendo ~10x cada pocos años; la señal se comprueba, no se predice.

### Fase 2.5 (opcional, decisión de proyecto)

Existe un camino intermedio: partir de pesos abiertos (Llama, Mistral, Qwen) y continuar el pre-entrenamiento con tu corpus. No es "usar una IA de otro" en el sentido de depender de una API — los pesos son tuyos, corren en tu máquina y tu corpus los esculpe — pero tampoco es desde cero. Queda documentado como opción; la pureza de "desde la primera neurona" es una decisión legítima y este roadmap la respeta por defecto.

## Fase 3 — Identidad (después de la escala)

Un modelo pre-entrenado completa texto; una IA propia conversa y tiene carácter.

- **Instrucción-tuning** con pares pregunta/respuesta escritos por ti — otra razón para empezar a acumularlos desde ya (cada vez que le expliques algo a alguien por escrito, eso es un dato de entrenamiento).
- **Personalidad definida**: qué sabe, qué tono tiene, qué no haría nunca. Esto se escribe como documento antes de entrenarse como comportamiento.

## Lo que se acumula desde hoy, resumido

1. Texto propio en `corpus/` — cada semana, sin excepción.
2. Pares pregunta/respuesta propios (para la Fase 3).
3. Evals: ejemplos de "esto suena a mí / esto no".
4. Familiaridad con el pipeline: entrenar el `nano` de vez en cuando con el corpus creciente, ver la loss bajar, leer lo que genera. La intuición también es un activo.
