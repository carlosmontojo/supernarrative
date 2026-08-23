# Tesis Solvencia — el aprendiz con algo en juego

*Estado: hipótesis viva, auditada bibliográficamente el mismo día de su
formulación (2026-08-23). Candidata a tesis central del laboratorio.*

## El diagnóstico (dónde se equivoca el consenso, bajo nuestro criterio)

Ningún aprendiz artificial tiene nada en juego. LLMs, RL, y nuestras propias
tesis optimizan señales de corrección — loss, recompensa, descuadre — que no
le cuestan nada al sistema: puede estar equivocado para siempre sin
consecuencia. Y la versión matemática de la grieta: **el campo optimiza
promedios de conjunto (valor esperado) para sistemas que viven UNA sola
trayectoria irreversible**. Para procesos no ergódicos con ruina absorbente,
maximizar la esperanza es incorrecto; lo correcto es la tasa de crecimiento
temporal (Kelly). La IA moderna es el apostador que maximiza esperanza porque
nunca puede arruinarse.

Evidencia interna de esta sesión: cada emergencia buena de nuestro laboratorio
salió de que algo tuviera consecuencias (las conjunciones robustas de Ágora
nacieron porque errar costaba capital; la reexpresión de Pacioli se dispara
por descuadre; la debilidad transversal de RED es que yerra con confianza y
solo "se ajusta").

## Enunciado

> Un aprendiz es un sistema de viabilidad: un único presupuesto del que TODO
> cobra — computar, recordar, percibir, actuar — con ingresos solo por ser
> útil o acertar en el mundo, ruina genuinamente absorbente, y como objetivo
> la tasa de crecimiento temporal de su propia solvencia. El conocimiento es
> lo que se paga a sí mismo; lo que no se amortiza, se liquida.

**Cuatro emergencias predichas desde el único principio** (los tests):
1. **Calibración natural**: la sobreconfianza es apalancamiento y el
   apalancamiento arruina — no hace falta diseñar prudencia.
2. **Exploración presupuestada**: la curiosidad es inversión con retorno
   esperado, no un bonus artificial.
3. **Olvido natural**: la memoria paga renta; lo que no rinde, se recicla.
4. **Crecimiento compuesto**: el conocimiento se reinvierte en capacidad de
   ganar conocimiento — la señal del bebé (TESIS-CRIA.md) ES la curva de
   interés compuesto; la saturación es reinversión cero. Esta tesis contiene
   a la tercera.

Corolario teórico inesperado: un recién nacido con capital diminuto no
sobrevive a la varianza ni siendo óptimo → la infancia subvencionada (los
padres/tutores de la Tesis Cría) deja de ser una metáfora y pasa a ser una
**necesidad matemática** del aprendiz solvente.

## Búsqueda bibliográfica adversarial (2026-08-23)

**Veredicto: parcialmente novedosa (confianza media, ~65%).** Cada
ingrediente por separado es reinvención, a menudo por los autores canónicos:

- **Ergodicidad + RL, ya fusionados por el propio Ole Peters**: Baumann,
  Peters et al. (TMLR 2025, arXiv:2310.11335) — RL con objetivo de
  crecimiento temporal; también arXiv:2601.08726 (2026, deep RL alineado
  con Kelly).
- **Ruina absorbente estudiada**: survival bandits (arXiv:2206.03019),
  risk-of-ruin (COLT 2019), mortalidad en agentes universales
  (Martin/Everitt/Hutter 2016).
- **Supervivencia/homeostasis como señal**: Keramati & Gutkin (eLife 2014),
  Yoshida 2016, Polyworld/Avida (30 años de ALife), "Survival Instinct in
  Offline RL" (NeurIPS 2023).
- **Manifiestos "la mortalidad es el ingrediente que falta"**: Hinton (2022),
  Ororbia & Friston "Mortal Computation" (arXiv:2311.09589), CACM, Bach.
- **Presupuesto + muerte + ingresos reales, operacional**: **OpenLife**
  (Ikegami et al., arXiv:2606.31046, 2026) — cada llamada al LLM debita
  energía, agotamiento = muerte, primer ingreso auto-ganado. El vecino más
  cercano; sin objetivo de crecimiento temporal ni aprendizaje por gradiente.
- **Calibración emergente de la riqueza, con teorema**: Logical Induction
  (Garrabrant 2016). **Exploración presupuestada**: Bandits with Knapsacks.
  **Pagar por pensar**: Ortega & Braun, Russell & Wefald, resource-rationality.
  **Quiebra interna**: bucket brigade (Holland), Hayek (Baum 1999).
  **Agentes que pagan su inferencia**: Vending-Bench/Project Vend, x402 (2025).

**El hueco que la búsqueda NO encontró ocupado**: la síntesis exacta —
(a) presupuesto unificado que cobra también computación, memoria y percepción,
(b) como ÚNICA señal de aprendizaje con actualización de parámetros,
(c) objetivo explícito de crecimiento temporal del propio presupuesto,
(d) ruina genuinamente absorbente en trayectoria única (sin resets ni
promediado durante el aprendizaje), y (e) **éxito medido por la forma
compuesta de la curva de solvencia** — con las cuatro emergencias derivadas
de un solo principio. En particular, (e) no apareció en ningún sitio.

**Advertencia de scoop**: el vecindario se está colonizando rápido (Energentic
Intelligence 2025, OpenLife 2026, revival de arquitecturas de mercado). Si
esta bandera se planta, se planta pronto.

## Premortem (cinco muertes, tres vidas)

| # | Modo de muerte | Gravedad |
|---|---|---|
| 1 | **Scoop cuasi-simultáneo**: el hueco es estrecho y el barrio arde. | Alta |
| 2 | **Reducción**: un revisor mostrará que "presupuesto + crecimiento log" se reduce a RL sensible al riesgo con recompensa log-riqueza y costes — contabilidad bonita sobre matemática conocida. La defensa solo puede ser empírica: que las cuatro emergencias aparezcan SIN diseñarlas, cosa que el RL-con-recompensa-log no exhibe por sí solo. | Alta |
| 3 | **El problema del ingreso**: si el pago lo define el diseñador, la "viabilidad" es una recompensa disfrazada y volvemos al RL. Se necesita un mundo que pague de verdad (odds externas, o una economía real). | Alta — es el agujero conceptual profundo |
| 4 | **Trampa metodológica de la trayectoria única**: sin resets, la propia investigación se vuelve lenta; muchas vidas independientes dan estadística, pero cada vida no puede usar información de ensamble sin traicionar la tesis. | Media |
| 5 | **Muerte infantil estocástica**: la varianza mata a buenos aprendices pobres antes de que aprendan; la infancia subvencionada lo mitiga pero hay que justificarla como mecanismo y no como parche. | Media |

| # | Escenario de vida |
|---|---|
| 1 | Cuatro emergencias medibles desde un principio único — barato de testear y muy citable si sale. |
| 2 | Explica retroactivamente los resultados de todo nuestro laboratorio (las consecuencias hicieron el trabajo en cada tesis). |
| 3 | **La convergencia con Quentax es total**: la solvencia es el dominio del producto, y Quentax puede ser el primer "mundo que paga de verdad" — un agente cuyos ingresos dependan de conciliaciones correctas resuelve el modo de muerte nº 3 con economía real, no simulada. |

## v0 (esbozo, pendiente de diseño detallado)

El "organismo-mercado": un agente (reutilizando la maquinaria de Ágora como
órganos internos) con presupuesto único; costes de metabolismo por paso, de
computación por consulta y renta de memoria por estructura; ingresos por
predicción correcta a odds fijadas por el mundo (no por el diseñador de la
recompensa); una vida por corrida, sin resets. Líneas base: el mismo agente
con apuestas de valor esperado (no-Kelly) y con cognición gratuita (sin
costes). Métricas: forma de la curva de solvencia (¿fase compuesta?),
supervivencia, calibración del tamaño de apuesta, olvido observado.

**Criterios de muerte de la v0** (se prerregistrarán en detalle antes de
ejecutar): si las cuatro emergencias no aparecen sin diseñarlas, o si el
agente solvente no supera a sus líneas base en ningún régimen, o si la única
forma de que sobreviva es amañar los ingresos, la tesis muere y se archiva.

## Relación con las demás tesis

Solvencia es candidata a tesis central porque las contiene: la señal del bebé
(Cría) es su métrica (e); la demografía de Ágora es su mecanismo poblacional;
la disciplina del descuadre de Pacioli es su contabilidad; y la infancia
subvencionada reintroduce a los tutores de Cría como necesidad matemática.
Si muere, las otras siguen en pie por separado.
