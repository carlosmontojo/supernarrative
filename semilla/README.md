# SEMILLA — Tu IA propia, plantada hoy

> *"El mejor momento para plantar un árbol fue hace veinte años. El segundo mejor momento es ahora."*

Semilla es un modelo de lenguaje (LLM) entrenado **desde cero** — no un wrapper sobre la API de nadie, no un fine-tuning de pesos ajenos. Tuyo desde la primera neurona.

## La apuesta

La premisa del proyecto: **el coste de cómputo para entrenar modelos cae de forma sostenida** (mejor hardware, mejores algoritmos, mejores datos por token). Lo que hoy cuesta millones costará miles, y lo que cuesta miles costará céntimos. Cuando ese momento llegue, la diferencia entre tener tu IA y no tenerla no será el dinero: será haber preparado durante años lo que el dinero no compra.

Porque hay dos tipos de activos en este proyecto:

| Se abarata con el tiempo | NO se abarata con el tiempo |
|---|---|
| Entrenar N parámetros | Tu corpus: todo lo que has escrito, curado y anotado |
| El hardware | Tu criterio: saber qué significa que el modelo "suene a ti" |
| El software de entrenamiento (esto se reescribe en un fin de semana) | Tus evals: las pruebas que definen qué es "tu" IA |

Semilla existe para acumular la columna derecha mientras la izquierda se abarata sola.

## Honestidad por delante

Un modelo entrenado hoy en un ordenador personal **no va a competir con ChatGPT**. Con un corpus pequeño y pocos millones de parámetros obtendrás un modelo que aprende la textura de tu prosa: vocabulario, ritmo, construcciones. Es un organismo pequeño, no un oráculo.

Y eso es exactamente lo que toca en la Fase 0. El objetivo de hoy no es inteligencia: es tener el **pipeline completo funcionando de punta a punta** (corpus → tokenizador → entrenamiento → generación → evaluación), de forma que escalar sea cambiar números en un config, no empezar de cero. Ver el roadmap completo en [ROADMAP.md](ROADMAP.md).

## Inicio rápido

```bash
cd semilla
pip install -r requirements.txt

# 1. Pon tus textos (.txt, .md) en corpus/  — o descarga el ejemplo:
curl -o corpus/quijote.txt https://www.gutenberg.org/cache/epub/2000/pg2000.txt

# 2. Prepara los datos (construye tokenizador y dataset)
python prepare.py

# 3. Entrena (preset "nano" funciona en CPU; sube de preset con GPU)
python train.py --preset nano --steps 2000

# 4. Habla con tu criatura
python generate.py --prompt "En un lugar de" --tokens 300
```

## Estructura

```
semilla/
├── config.py      # Arquitectura y presets de tamaño (nano → base)
├── tokenizer.py   # Tokenizador a nivel de carácter (v0; BPE en Fase 1)
├── prepare.py     # corpus/ → dataset binario + tokenizador
├── model.py       # El transformer GPT, desde cero, comentado
├── train.py       # Bucle de entrenamiento con checkpoints y validación
├── generate.py    # Muestreo desde un checkpoint
├── corpus/        # Tus textos (no se versionan en git)
├── data/          # Dataset procesado (generado, no se versiona)
└── checkpoints/   # Modelos entrenados (generados, no se versionan)
```

## Presets de tamaño

| Preset | Parámetros aprox. | Hardware | Cuándo |
|---|---|---|---|
| `nano`  | ~1M   | CPU de portátil | Hoy: validar el pipeline |
| `micro` | ~10M  | CPU paciente o cualquier GPU | Hoy: primer modelo "de verdad" |
| `mini`  | ~30M  | GPU de consumo | Cuando tengas corpus decente |
| `base`  | ~110M (escala GPT-2) | GPU de consumo buena | Fase 2 |

Escalar más allá es cambiar tres números en `config.py`. El código no cambia: esa es la gracia.

## Filosofía

1. **Cero magia**: cada línea del modelo está en este repo y se puede leer en una tarde. Si no lo entiendes, no es tuyo.
2. **El corpus es el proyecto**: el código es commodity; tus datos no. La disciplina de alimentar `corpus/` vale más que cualquier optimización.
3. **Siempre entrenable hoy**: cada fase del roadmap debe poder ejecutarse con el hardware de su momento. Nada de "cuando tenga un cluster".
