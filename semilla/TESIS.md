# Tesis Pacioli — una mente con partida doble

*Estado: hipótesis viva. Este documento existe para ser falsado, no defendido.*

## Enunciado

> Una inteligencia cuya memoria es un libro contable — experiencias como asientos
> con procedencia, creencias como saldos que no existen sin asientos que los
> respalden, aprendizaje como conciliación de predicciones contra resultados,
> curiosidad como lista de partidas abiertas, y olvido/abstracción como cierre de
> ejercicio — aprende con órdenes de magnitud menos datos en dominios donde la
> verdad es asentable, sabe lo que no sabe, y puede auditar cada una de sus
> creencias.

La percepción sigue siendo neuronal (una red propone asientos); la memoria, la
verdad y la señal de aprendizaje son el libro. La señal no es "predice el
siguiente token": es **el error de conciliación**.

## Las dos preguntas que la tesis debe responder

### ¿Reduce el cómputo en órdenes de magnitud?

Análisis honesto, en dos mitades:

- **Donde SÍ hay un argumento fuerte**: un LLM quema una fracción enorme de sus
  parámetros y de su cómputo en *memorizar hechos* a base de miles de pasadas de
  gradiente. En Pacioli un hecho cuesta un asiento: una escritura, no un
  entrenamiento. Y mantenerse al día (nueva ley, nuevo proveedor) es apuntar, no
  reentrenar: el cómputo *marginal* del aprendizaje continuo tiende a cero.
  Además, la curiosidad dirigida sustituye "tragar billones de tokens aleatorios"
  por "perseguir exactamente el dato que cierra un descuadre" — y cómputo ≈ 6 ×
  parámetros × datos, así que cada orden de magnitud de eficiencia de datos es un
  orden de magnitud de cómputo.
- **Donde NO**: la *competencia perceptiva* (leer, ver, entender lenguaje) es
  justo lo que costó los billones de tokens, y el libro no percibe: necesita un
  frontal neuronal que proponga los asientos. O se destila de modelos existentes
  (heredando su cómputo hundido) o hay que ganarla con experiencia. **La tesis
  reduce el cómputo de mantener y ampliar una mente; no está demostrado que
  reduzca el de arrancarla.**

### ¿Puede llegar a ser inteligente?

Lo que el libro aporta: calibración estructural (no puede afirmar sin saldo),
aprendizaje factual de un solo ejemplo, curiosidad con dirección, sin olvido
catastrófico, auditabilidad total. Lo que no aporta por sí solo: la intuición
compilada — reconocer una cara, el tono de un email, la jugada elegante. Esa
parte sigue siendo neuronal. Techo plausible: **Pacioli no sustituye al sustrato
neuronal; lo completa como capa de memoria y verdad.** Si la tesis gana, el
resultado no es "AGI sin redes": es una mente híbrida cuyo conocimiento es
barato, continuo y auditable.

## Premortem (sin sesgo: cinco muertes, tres vidas)

### Cómo muere

| # | Modo de muerte | Gravedad |
|---|---|---|
| 1 | **El problema del asiento**: el mundo no llega detallado en apuntes. Decidir *qué* asentar (el esquema) es el problema duro de percepción, y el libro lo presupone resuelto. Esto mató a los sistemas expertos y a los truth maintenance systems de los 80. | Alta — es la objeción principal |
| 2 | **Explosión de partidas abiertas**: en un mundo rico todo descuadra un poco; la lista de curiosidad crece sin límite y el sistema se dispersa. Priorizar bien es otro problema de aprendizaje. | Media |
| 3 | **Rigidez**: los libros son discretos; la inteligencia necesita similitud graduada ("este caso se *parece* a aquel"). Sin mezcla entre asientos, no hay generalización: queda una base de datos con curiosidad. | Alta |
| 4 | **El precedente empírico en contra**: las arquitecturas con memoria externa (Neural Turing Machines, memorias diferenciables) llevan una década perdiendo contra "haz el transformer más grande". | Alta |
| 5 | **Lección Amarga**: la estructura modular acaba siendo el cuello de botella frente al gradiente de extremo a extremo cuando llega la escala. | Media |

### Cómo vive

| # | Escenario de vida | Por qué es plausible |
|---|---|---|
| 1 | **El dominio pre-asentado**: la objeción nº 1 es fatal en general… y está *ya resuelta* en finanzas. Una factura ES un asiento; un extracto ES un libro; el mundo financiero nace detallado. Pacioli puede fallar para la visión y funcionar para la contabilidad — el único dominio donde la realidad llega itemizada de fábrica. | Fuerte, y es nuestra cuña |
| 2 | **Victoria parcial valiosa**: aunque no sea camino a la AGI, un agente que aprende en continuo sin reentrenar, sabe lo que no sabe y enseña sus asientos al auditor es exactamente lo que la regulación financiera exigirá a la IA. El fracaso grande deja un éxito pequeño en pie. | Fuerte |
| 3 | **Llegar pronto no es llegar mal**: las memorias externas quizá no estaban equivocadas sino adelantadas — el aprendizaje continuo se está volviendo EL cuello de botella de la industria, y cuando una limitación se vuelve el cuello de botella, sus soluciones renacen (le pasó al RL). | Especulativo pero real |

### Veredicto numérico (apuesta honesta, no certeza)

- Como paradigma completo que sustituye a los LLMs: **~2-5%**.
- Como capa de memoria/verdad injertada al sustrato neuronal, con ahorro grande
  de cómputo en aprendizaje continuo: **~15-30%**.
- Como arquitectura correcta para el CFO de Quentax (dominio pre-asentado):
  **~60%+**.
- Coste de averiguarlo a escala nano: **~0 €**.

Con esa matriz, no probarla sería lo irracional.

## La estrategia: la frontera de lo asentable

No atacar la generalidad de frente. Empezar donde el problema del asiento no
existe (finanzas), demostrar las propiedades (eficiencia, calibración,
auditoría), y después **empujar hacia fuera la frontera de lo asentable**: cada
dominio nuevo exige aprender a asentarlo. Si la frontera se expande, la tesis
escala; si se atasca en cuanto sale de finanzas, la tesis queda en arquitectura
de producto. Ambos resultados son información.

## Experimento v0 (`experimentos/pacioli/`)

Mundo simulado pre-asentado (declarado: v0 esquiva a propósito el problema del
asiento — prueba el bucle de aprendizaje, no la percepción): una empresa genera
transacciones; reglas ocultas asignan cuenta contable según tipo y proveedor,
con excepciones; cada cierto tiempo una "reforma" cambia reglas sin avisar.

Agentes con el mismo flujo de observaciones:

- **RED**: clasificador neuronal entrenado online (SGD), consultas aleatorias.
- **LIBRO**: mente Pacioli — asientos, saldos, conciliación, partidas abiertas
  que dirigen qué consultar, cierres periódicos que consolidan esquemas.
  Ablaciones: `--sin-curiosidad`, `--sin-cierre`.

### Predicciones falsables

- **P1 (adaptación)**: tras cada reforma, LIBRO recupera >90% de acierto en las
  reglas cambiadas con bastantes menos observaciones que RED.
- **P2 (calibración)**: la confianza de LIBRO cae cuando sus cuentas no cuadran
  (mejor Brier score); RED sigue confiado mientras se equivoca.
- **P3 (transferencia)**: ante un proveedor nunca visto, LIBRO acierta desde el
  esquema consolidado.
- **P4 (auditoría)**: cualquier predicción de LIBRO se explica listando los
  asientos que la respaldan. (RED no puede por construcción.)

### Criterios de muerte de la v0

Si LIBRO no gana con claridad en P1 **y** P2 en un mundo diseñado para sus
puntos fuertes, la tesis muere aquí y se archiva este documento con el
resultado. Si gana: siguiente peldaño (mundo con ruido en la percepción — el
frontal neuronal propone asientos imperfectos — que es donde empieza la verdad).

**Advertencia contra el autoengaño**: ganar en la v0 NO valida la tesis — valida
los mecanismos en un mundo hecho a su medida. Lo único que la v0 puede hacer es
matarla barato o ganarse el derecho al siguiente experimento.

## Registro de resultados (se escribe, no se borra)

### 2026-08-22 — v0, rondas 1 y 2

**Ronda 1**: primera implementación de LIBRO, derrotada por RED en todo menos
auditoría (recuperación 218 vs 144; Brier 0.158 vs 0.049). Diagnóstico: faltaba
el mecanismo contable central — al cambiar el criterio (reforma), los saldos
viejos pisaban al esquema nuevo. El arreglo salió del propio marco de la tesis:
**reexpresión retroactiva** (un saldo anterior al cambio de criterio no puede
pisar el criterio nuevo hasta reconciliarse). Que el vocabulario contable
generara el movimiento de depuración es evidencia débil pero real de que el
marco tiene poder generativo.

**Ronda 2** (RED en su mejor lr=1.0 tras barrido — línea base sin debilitar;
5 semillas × 3000 pasos):

| Métrica | RED | LIBRO | LIBRO sin curiosidad | LIBRO sin cierre |
|---|---|---|---|---|
| P1 recuperación tras reforma (pasos) | 67 | **38** | 85 (1 reforma nunca superada) | **nunca** |
| P2 Brier (menor = mejor) | **0.019** | 0.053 | 0.070 | 0.070 |
| P3 acierto proveedores nuevos | **98.1%** | 96.3% | 95.2% | 8.7% |
| Acierto global | **98.0%** | 96.4% | 94.2% | 38.7% |
| P4 auditoría | no puede | **sí** | sí | sí |

**Lectura sin maquillaje**:

- **P1 ganada** (1.8× más rápido que la línea base en su mejor versión), pero
  no en órdenes de magnitud como enuncia la tesis. Las ablaciones asignan el
  mérito: el cierre con reexpresión es el mecanismo de carga (sin él, colapso
  total) y la curiosidad aporta el resto (38→85 sin ella).
- **P2 perdida**. Nota metodológica declarada *a posteriori* (y por tanto
  sospechosa por definición — moverle la portería a un experimento es como
  empieza la mala ciencia, así que queda marcado): el mundo v0 es determinista,
  y en un mundo sin ruido la calibración óptima ES la confianza máxima — el
  test premiaba estructuralmente a la red segura de sí misma. Un test justo de
  calibración exige un mundo con incertidumbre real (v1). P2 queda **no
  resuelta**, no aprobada.
- **P3 empate práctico** (96 vs 98): el descubrimiento incómodo de la ronda 1
  se mantiene — el SGD con features compartidas ya ES un consolidador continuo
  de esquemas; la Lección Amarga apareció en miniatura exactamente como
  predijo el premortem (#4).
- **P4 ganada por construcción**, que era el punto: es la propiedad que ningún
  ajuste de la red puede darle.

**Veredicto v0 según criterios prerregistrados** ("ganar con claridad P1 y
P2"): estrictamente, **no superado** — P1 sí, P2 no. Decisión pendiente del
autor: (a) archivar, o (b) v1 con mundo estocástico (test de calibración
justo) y percepción ruidosa (primer contacto con el problema del asiento),
aceptando que esto es una revisión post-hoc del protocolo y dejándolo escrito.

## Precedentes declarados

Truth maintenance systems (Doyle, años 80) — registro de justificaciones de
creencias; *predictive processing* — el cerebro como minimizador de errores de
predicción (conciliar es eso, con disciplina contable); memorias externas
diferenciables (NTM, memorias episódicas) y su historial de derrotas frente a la
escala; BabyLM — la comunidad que investiga aprender idioma con presupuesto de
niño; sistemas de RAG con procedencia. La síntesis específica (partida doble
como estructura de memoria + conciliación como bucle + partidas abiertas como
curiosidad + cierre como abstracción + auditabilidad estructural) no la
conocemos desarrollada; establecer su novedad exige búsqueda bibliográfica
seria, que está pendiente y se hará antes de reclamar nada.
