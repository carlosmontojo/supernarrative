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

### 2026-08-22 — v1: protocolo prerregistrado (escrito ANTES de ejecutar)

Decisión del autor: continuar. Cambios respecto a v0, atacando sus dos huecos:

1. **Mundo estocástico**: algunos tipos tienen incertidumbre real (la cuenta
   correcta se sortea, p. ej. 70/30). La calibración se mide con Brier
   *esperado* analítico contra la distribución verdadera — un agente
   perfectamente calibrado debe decir "70%", no "100%". Esto corrige el test
   que en v0 premiaba estructuralmente la sobreconfianza.
2. **Percepción ruidosa (primer contacto con el problema del asiento)**: la
   transacción ya no llega como clave limpia sino como documento (bolsa de
   tokens, algunos comunes a todo, alguno erróneo con probabilidad ε). El
   agente debe aprender qué tokens son asentables. LIBRO lleva saldos por
   token cuya informatividad se aprende (los tokens comunes se auto-anulan
   por entropía); RED recibe los mismos tokens como features de extremo a
   extremo.
3. **La disciplina del descuadre**: LIBRO solo asienta ajuste (depreciación +
   sospecha) cuando el fallo contradice su propia confianza (conf ≥ 0.75). El
   ruido esperado se asienta sin drama; solo la sorpresa es descuadre. Esta es
   la respuesta de la tesis al dilema estabilidad/plasticidad.
4. **RED sin debilitar**: barrido completo de lr {0.05, 0.15, 0.3, 0.6, 1.0}
   publicado entero.

**Criterios de vida o muerte de la v1** (fijados antes de ver un solo número):

- **VIVE** si ningún lr único de RED iguala o supera a LIBRO simultáneamente
  en P1' (recuperación) y P2' (Brier esperado) — es decir, si LIBRO escapa al
  dilema estabilidad/plasticidad que obliga a RED a elegir; Y ADEMÁS con
  ε = 0.3 de ruido de percepción LIBRO conserva ≥ 85% de su acierto limpio.
- **MUERE** si algún lr de RED gana o empata ambas a la vez, o si el ruido de
  percepción lo derrumba (el problema del asiento pudo con él a la primera).

### 2026-08-22 — v1: resultados (5 semillas × 3000 pasos, barrido RED completo)

Durante la puesta a punto (sanity, 2 semillas) se corrigió una interacción:
la prudencia declarada suprimía la señal de sorpresa y detenía la reexpresión
a medias. Arreglo conceptual, no paramétrico: separar **convicción interna**
(dispara el descuadre; solo evidencia) de **confianza declarada** (con
prudencia; la que se evalúa). Aplicado antes de las corridas finales.

**ε = 0 (percepción limpia, mundo estocástico):**

| Métrica | mejor RED del barrido | LIBRO |
|---|---|---|
| P1' recuperación | 70 pasos (lr 1.0) | **34** |
| P2' Brier esperado | 0.093 (lr 0.6) | **0.075** |
| Acierto modal | 92.8% (lr 0.15) | **98.6%** |
| Proveedores nuevos | 92.9% | **98.7%** |

**LIBRO domina en Pareto a las cinco configuraciones de RED a la vez**: ningún
lr escapa al dilema estabilidad/plasticidad; la disciplina del descuadre sí
(los fallos esperados no deprecian nada; solo la sorpresa reexpresa). La
derrota de calibración de la v0 era, en efecto, el artefacto del mundo
determinista.

**ε = 0.3 (problema del asiento):**

| Métrica | mejor RED | LIBRO |
|---|---|---|
| P1' recuperación | 80 pasos (lr 0.6) | 288, con **7/25 reformas nunca superadas** |
| P2' Brier esperado | 0.095 | 0.157 |
| Acierto modal | 92.7% | 87.1% |
| Retención vs. su acierto limpio | — | 88.3% (criterio ≥85%: pasa) |

Con percepción ruidosa, **RED gana con claridad**: la escritura nítida de
LIBRO acredita cuentas equivocadas a tokens equivocados y el veneno persiste;
la ponderación blanda del gradiente digiere el ruido mejor. El premortem #1
acertó en diana.

**Veredicto v1 según criterios prerregistrados**: el criterio se redactó sin
fijar a qué ε aplicaba el test de Pareto — ambigüedad nuestra y queda anotada.
Lectura estricta: **VIVE en régimen pre-asentado, MUERE (por ahora) bajo ruido
de percepción**. El experimento ha hecho algo mejor que aprobar o suspender:
ha **dibujado empíricamente la frontera de lo asentable** que la estrategia de
esta tesis ya postulaba. Donde los documentos llegan limpios (finanzas), el
libro domina en todo; donde la percepción es turbia, manda el gradiente.

**Dirección v2** (de nuevo dictada por la contabilidad): LIBRO v1 asienta toda
observación en firme. Un contable no hace eso: lo dudoso va a una **cuenta
puente — 555, "partidas pendientes de aplicación", existe literalmente en el
PGC** — y solo pasa al mayor cuando se concilia. v2 = asientos provisionales
para documentos de baja confianza perceptiva, aplicados o revertidos al
aclararse. Si eso no cierra el hueco con ruido, la tesis queda confinada al
dominio pre-asentado y se archiva como arquitectura (valiosa) de producto.

## Precedentes declarados

Truth maintenance systems (Doyle, años 80) — registro de justificaciones de
creencias; *predictive processing* — el cerebro como minimizador de errores de
predicción (conciliar es eso, con disciplina contable); memorias externas
diferenciables (NTM, memorias episódicas) y su historial de derrotas frente a la
escala; BabyLM — la comunidad que investiga aprender idioma con presupuesto de
niño; sistemas de RAG con procedencia.

## Búsqueda bibliográfica adversarial (2026-08-23)

Hecha con la instrucción de ENCONTRAR el prior art, no de halagarnos.
**Veredicto: parcialmente novedosa (confianza media-alta).**

El espacio "memoria de agente auditable con procedencia" está ardiendo en
2025-2026 — cada mecanismo individual tiene dueño:

- Creencias que exigen evidencia previa: TMS/ATMS (Doyle 1979, de Kleer 1986);
  **Eywa** (arXiv:2605.30771, invariante "evidence precedes belief");
  **Kumiho** (arXiv:2603.17244, revisión AGM sobre grafo con procedencia).
- Diario append-only → estado derivado: **"The Log is the Agent"**
  (arXiv:2605.21997) y la familia event-sourcing; **Zep/Graphiti** (grafo
  bi-temporal con invalidación retroactiva ≈ nuestra reexpresión).
- Aserción sin respaldo = fallo estructural: **CANONIC** (arXiv:2607.05410),
  EviBound, Proof-or-Stop.
- Ledger "pendiente" ≈ cuenta puente: **TARL** (arXiv:2608.03699).
- Curiosidad por brecha: Loewenstein, Schmidhuber, ICM, INFOGATHERER.
- Consolidación periódica → esquemas: Generative Agents (Park 2023) y sucesores.

**Lo que NO se encontró en ningún sitio**: la partida doble propiamente dicha —
la restricción bilateral debe/haber, un invariante global de cuadre (balance de
comprobación) cuya violación sea la señal de error, y el sistema completo
(diario + saldos + conciliación + cierre + reexpresión + cuentas puente +
partidas abiertas como curiosidad) unificado bajo UN formalismo contable. Ni
una mención a Pacioli en arXiv.

**Reclamación revisada de la tesis** (más estrecha y más fuerte): la novedad
defendible no son los mecanismos — es el **formalismo unificador de partida
doble**, y su carga de la prueba es demostrar que la dualidad debe/haber y el
invariante de cuadre global aportan algo medible que la "partida simple con
procedencia" (que ya existe publicada) no aporta. Pregunta abierta que la v2
debe responder antes que ninguna otra: ¿cuál es el "haber" epistémico que
equilibra cada "debe"?

**Lectura estratégica**: que una docena de papers de 2025-2026 converjan hacia
este territorio valida la dirección (el campo está llegando adonde la intuición
contable ya estaba) y mete prisa: el espacio se está reclamando ahora.
