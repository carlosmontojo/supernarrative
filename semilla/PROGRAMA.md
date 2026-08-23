# PROGRAMA — el documento madre

*Escrito el 2026-08-23, al cierre de la sesión fundacional. Este documento
ordena todo lo demás: si solo lees un fichero al volver al proyecto, es este.*

## Qué hay construido (dos días)

1. **Semilla**: pipeline completo de LLM desde cero (tokenizador → GPT →
   entrenamiento → generación), validado dos veces (Quijote y BOE).
   `boe.py` descarga legislación consolidada. `evals/` con los primeros 12
   casos de CFO. `ROADMAP.md` con las fases del producto.
2. **Tres tesis con cicatrices**: Pacioli (TESIS.md), Ágora (TESIS-AGORA.md)
   y Cría (TESIS-CRIA.md) — cada una con experimentos o auditoría, criterios
   prerregistrados, derrotas registradas y búsqueda bibliográfica adversarial
   hecha (2026-08-23).
3. **Un mapa empírico**: tres paradigmas medidos en la misma pista — el
   gradiente reina con ruido, el libro en mundo asentado (y es el único
   auditable), el mercado es el generalista robusto. Ningún mecanismo posee
   todos los regímenes.

## La decisión estratégica: dos vías, en este orden

### Vía 1 — EL MOTOR: el CFO de Quentax (prioridad absoluta)

La búsqueda bibliográfica dio aquí la mejor noticia disfrazada de mala: el
espacio "memoria de agente auditable con procedencia" explota en 2025-2026.
Para un *paper* eso es competencia; para un *producto* es validación — la
arquitectura que la intuición contable de este proyecto propuso es hacia
donde converge el campo. Y un producto no necesita novedad: necesita el
mejor CFO fiscal en español, y eso lo deciden los activos que nadie más
tiene:

- **El volante de correcciones**: diseñar Quentax para capturar cada
  corrección de usuario (conciliaciones, categorizaciones) desde YA.
  Es la acción más importante de todo este documento.
- **Los evals**: crecer `evals/casos.jsonl` con dudas reales de usuarios
  hasta cientos de casos. Es la especificación del producto.
- **El corpus**: legislación con `boe.py` + doctrina + contenido propio.
- **La arquitectura**: el modelo redacta, las fuentes afirman, el código
  calcula, Quentax ejecuta — con memoria estilo Pacioli (auditable, con
  procedencia), propia o adaptada de las herramientas que están emergiendo
  (Zep/Graphiti, etc.: usarlas no es traición, es velocidad).

### Vía 2 — EL LABORATORIO: una sola bandera a la vez

De las tres esquinas defendibles que dejó la búsqueda, se planta **una**:

**La señal del bebé** (TESIS-CRIA.md) — la curva longitudinal de velocidad
de aprendizaje como criterio primario de no-saturación. Por qué esta:

- Es la más barata de operacionalizar y la más citable (un instrumento de
  medida, no un paradigma — los instrumentos sobreviven a las teorías).
- Nuestro laboratorio es su primer caso de uso: demostrar con la curva que
  RED, LIBRO y MERCADO se saturan es a la vez el estreno del instrumento y
  un resultado honesto.
- El trabajo difícil es de diseño, no de cómputo: definir el mundo
  composicional y la normalización de dificultad para que la curva no sea
  un artefacto. Eso se piensa antes de programarse.

**Cola del laboratorio** (después, no en paralelo):
2º) el formalismo de partida doble de Pacioli — responder "¿cuál es el haber
epistémico que equilibra cada debe?" y si el cuadre global aporta algo
medible sobre la partida simple con procedencia; alimenta directamente la
Vía 1. 3º) el híbrido traders-libro, con el criterio anti-epiciclo ("gana
borrando mecanismos o no cuenta").

## Lo que NO hacemos (tan importante como lo anterior)

- **No** competir por la bandera "LLMs como padres" (BabyLM/SIMA 2 llegaron
  antes) ni por la semilla mínima (Zador).
- **No** usar la retórica "inteligencia sin optimizador" (desmontada por los
  teoremas de equivalencia; Ágora queda aparcada como tesis, viva como
  agente en el banco de pruebas).
- **No** entrenar modelos grandes todavía: la apuesta del cómputo sigue
  siendo esperar mientras se acumula lo que no se abarata.
- **No** abrir una cuarta tesis hasta que la señal del bebé esté publicada o
  muerta.

## Próximos pasos concretos, en orden

1. **[Producto]** Hook de captura de correcciones en Quentax + 20 evals
   nuevos de dudas reales. (Sin esto, todo lo demás es hobby.)
2. **[Lab]** Documento de diseño de la señal del bebé: definición formal de
   la curva, el mundo composicional, normalización de dificultad, y qué
   contaría como refutación del propio instrumento.
3. **[Lab]** Instrumentar a los tres agentes existentes con la métrica y
   publicar la primera curva (esperado: tres saturaciones — ese ES el
   resultado).
4. **[Infra]** Mover `semilla/` a su propio repositorio (decisión pendiente
   del autor: repo nuevo `quentax-ia` o dentro de quentax-dashboard).

## Regla de la casa

Todo lo nuevo entra igual: enunciado → premortem sin sesgo → criterios de
muerte prerregistrados → experimento barato → registro del resultado, gane o
pierda → búsqueda bibliográfica antes de reclamar nada. Es lo que ha hecho
que dos días de juguetes produzcan conocimiento en vez de ilusión.
