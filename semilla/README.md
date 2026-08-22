# SEMILLA — La IA propia de Quentax, plantada hoy

> *"El mejor momento para plantar un árbol fue hace veinte años. El segundo mejor momento es ahora."*

Semilla es un modelo de lenguaje (LLM) entrenado **desde cero** — no un wrapper sobre la API de nadie, no un fine-tuning de pesos ajenos. Tuyo desde la primera neurona. Su destino: ser el cerebro del **CFO autónomo de Quentax** — una IA que domina todo lo que hace Quentax: gestión financiera de empresa, contabilidad, conciliación bancaria, facturación y tipos, tesorería e impuestos.

## Anatomía de un CFO artificial

Un CFO "que lo hace todo" no es un modelo: es un **agente** con cuatro órganos, y solo uno de ellos es la red neuronal.

| Órgano | Qué es | De dónde sale |
|---|---|---|
| **Cerebro** | El modelo de lenguaje: entiende, razona, redacta | Este repo (Semilla) |
| **Manos y ojos** | Las herramientas: conciliar, emitir facturas, leer el banco, presentar modelos | **Quentax ya las tiene** — esa es tu ventaja estructural |
| **Memoria** | Los datos del cliente: su contabilidad, sus facturas, su histórico | La base de datos de Quentax |
| **Calculadora** | Cuotas, retenciones, plazos, asientos: código determinista | Código, nunca la red neuronal |

La mayoría de la gente que quiere "crear una IA" solo puede aspirar al cerebro. Tú ya tienes las otras tres cuartas partes construidas: Semilla es la pieza que falta, no el proyecto entero. Ese es el plan.

## La apuesta

La premisa del proyecto: **el coste de cómputo para entrenar modelos cae de forma sostenida**. Lo que hoy cuesta millones costará miles, y lo que cuesta miles costará céntimos. Cuando ese momento llegue, la diferencia entre tener tu IA y no tenerla no será el dinero: será haber preparado durante años lo que el dinero no compra.

Porque hay dos tipos de activos en este proyecto:

| Se abarata con el tiempo | NO se abarata con el tiempo |
|---|---|
| Entrenar N parámetros | El corpus curado: legislación, contabilidad, doctrina y, sobre todo, el contenido y los datos operativos de Quentax |
| El hardware | El criterio de dominio: saber qué respuesta financiera es correcta y cuál es un desastre |
| El software de entrenamiento (esto se reescribe en un fin de semana) | Los evals (`evals/`): casos de CFO con respuesta verificable que definen qué es "la IA de Quentax" |

Semilla existe para acumular la columna derecha mientras la izquierda se abarata sola.

## Honestidad por delante (doble, porque esto es fiscal)

1. Un modelo entrenado hoy en un ordenador personal **no compite con ChatGPT**. Con corpus pequeño y pocos millones de parámetros se obtiene un modelo que aprende la textura del lenguaje financiero, no un asesor. El objetivo de la Fase 0 no es inteligencia: es el **pipeline completo funcionando** (corpus → tokenizador → entrenamiento → generación → evaluación), para que escalar sea cambiar números en un config.

2. En finanzas y fiscal, **un modelo que se inventa cosas es un pasivo, no un producto**. El CFO de Quentax nunca será "un modelo que se sabe la ley de memoria": será un modelo que entiende y redacta + recuperación de la norma vigente (RAG) + las herramientas de Quentax ejecutando las acciones + cálculo hecho por código. La regla en una frase: **el modelo redacta, las fuentes afirman, el código calcula, Quentax ejecuta**. Y para las acciones irreversibles (pagar, presentar un modelo), confirmación humana. Ese principio guía todo el roadmap.

## Inicio rápido

```bash
cd semilla
pip install -r requirements.txt

# 1. Corpus de arranque: normativa consolidada del BOE (dominio público)
python boe.py BOE-A-2006-20764 BOE-A-1992-28740 BOE-A-2007-19884   # IRPF, IVA, PGC
# (lista completa de normas fiscales+contables en corpus/README.md)

# 2. Prepara los datos (construye tokenizador y dataset)
python prepare.py

# 3. Entrena (preset "nano" funciona en CPU; sube de preset con GPU)
python train.py --preset nano --steps 2000

# 4. Habla con tu criatura
python generate.py --prompt "El contribuyente" --tokens 300
```

## Estructura

```
semilla/
├── config.py      # Arquitectura y presets de tamaño (nano → base)
├── tokenizer.py   # Tokenizador a nivel de carácter (v0; BPE en Fase 1)
├── boe.py         # Descarga legislación consolidada del BOE → corpus/boe/
├── prepare.py     # corpus/ → dataset binario + tokenizador
├── model.py       # El transformer GPT, desde cero, comentado
├── train.py       # Bucle de entrenamiento con checkpoints y validación
├── generate.py    # Muestreo desde un checkpoint
├── evals/         # Casos de CFO con respuesta verificable: la especificación del producto
├── corpus/        # Los textos de entrenamiento (no se versionan en git)
├── data/          # Dataset procesado (generado, no se versiona)
└── checkpoints/   # Modelos entrenados (generados, no se versionan)
```

## Presets de tamaño

| Preset | Parámetros aprox. | Hardware | Cuándo |
|---|---|---|---|
| `nano`  | ~1M   | CPU de portátil | Hoy: validar el pipeline |
| `micro` | ~10M  | CPU paciente o cualquier GPU | Hoy: primer modelo "de verdad" |
| `mini`  | ~30M  | GPU de consumo | Cuando el corpus fiscal tenga volumen |
| `base`  | ~110M (escala GPT-2) | GPU de consumo buena | Fase 2 |

Escalar más allá es cambiar tres números en `config.py`. El código no cambia: esa es la gracia.

## Filosofía

1. **Cero magia**: cada línea del modelo está en este repo y se puede leer en una tarde. Si no lo entiendes, no es tuyo.
2. **El corpus es el proyecto**: el código es commodity; el corpus fiscal curado y el contenido propio de Quentax no. La identidad del modelo la decide el corpus — el mismo código que balbuceaba Quijote balbucea IRPF al cambiar los textos.
3. **Siempre entrenable hoy**: cada fase del roadmap debe poder ejecutarse con el hardware de su momento. Nada de "cuando tenga un cluster".
4. **En fiscal, la verdad se consulta, no se recuerda**: el modelo pone el lenguaje; la norma vigente y los cálculos vienen de fuentes verificables.
