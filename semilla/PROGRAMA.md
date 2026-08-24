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

*(Revisado 2026-08-23, por decisión del autor de buscar "dónde se equivocan
todos": la bandera central cambia.)*

**SOLVENCIA: ejecutada y MUERTA el 2026-08-23** según sus criterios
prerregistrados (K2 falló: las consecuencias dentro del voto epistémico
empeoraron las creencias; el control sin stakes calibró mejor). Registro
completo y autopsia en TESIS-SOLVENCIA.md. Dos supervivientes de la
autopsia:

1. **El resultado K1, establecido**: con creencias idénticas, el organismo
   que apuesta Kelly (media temporal) sobrevive el doble que el maximizador
   de esperanza y acumula 5 órdenes más. La ergodicidad importa en
   organismos que aprenden. Publicable por sí solo.
2. **El instrumento K4, validado**: la señal del bebé leyó la vida entera
   del organismo (aceleración infantil → heridas de reforma → meseta de
   saturación) en su primer despliegue.

**Bandera actual del laboratorio: LA SEÑAL DEL BEBÉ como instrumento**
(TESIS-CRIA.md) — sobrevivió a la muerte de su anfitriona ya validada.
Siguiente paso: el documento de diseño formal (mundo composicional,
normalización de dificultad) y aplicarla sistemáticamente a los agentes
existentes, empaquetando K1+K4 como el primer resultado publicable del
laboratorio.

**Cola del laboratorio** (después, no en paralelo):
2º) el formalismo de partida doble de Pacioli — "¿cuál es el haber epistémico
que equilibra cada debe?"; alimenta directamente la Vía 1. 3º) la sucesora
de Solvencia sugerida por la autopsia (epistemia de libro honesto + capa de
decisión solvente), que exigiría prerregistro propio. 4º) el híbrido
traders-libro, con el criterio anti-epiciclo.

## Lo que NO hacemos (tan importante como lo anterior)

- **No** competir por la bandera "LLMs como padres" (BabyLM/SIMA 2 llegaron
  antes) ni por la semilla mínima (Zador).
- **No** usar la retórica "inteligencia sin optimizador" (desmontada por los
  teoremas de equivalencia; Ágora queda aparcada como tesis, viva como
  agente en el banco de pruebas).
- **No** entrenar modelos grandes todavía: la apuesta del cómputo sigue
  siendo esperar mientras se acumula lo que no se abarata.
- **No** abrir una quinta tesis hasta que Solvencia esté publicada o muerta.
  (La regla original decía "cuarta"; el autor la amendó conscientemente el
  2026-08-23 al pedir el diagnóstico de campo que produjo Solvencia. Las
  reglas se cambian a la vista, no se erosionan.)

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
