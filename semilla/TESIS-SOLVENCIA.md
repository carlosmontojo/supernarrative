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

## v0 — PRERREGISTRO (2026-08-23, escrito antes de ejecutar)

### El organismo

Vive en el banco de pruebas v1 (documentos con ruido ε=0.15, reformas cada
500 pasos). Su cuerpo interno son **células de conocimiento** — el híbrido
que aplazamos llega aquí como órgano, no como tesis: cada célula = condición
(1-2 rasgos) + saldo de clases (mini-libro) + **cuenta propia** de
pérdidas/ganancias atribuidas.

**La economía (todo de un único presupuesto):**
- Metabolismo fijo por paso; renta por célula almacenada; coste por célula
  consultada; coste por crear célula nueva (nacen de la observación, como en
  Ágora). Dote inicial: la infancia subvencionada, explícita.
- Ingresos SOLO por apuestas: si decide participar, apuesta una fracción del
  presupuesto por su clase; acierto paga a odds K=6 fijadas por la
  estructura del mundo (con 8 clases, el azar pierde: sin conocimiento no
  hay renta). Puede abstenerse — no saber y no apostar es legítimo.
- **Tamaño de apuesta: Kelly fraccional (½)** sobre su propia creencia — la
  sobreconfianza es apalancamiento real.
- **Las creencias las moldean las consecuencias**: el voto de cada célula
  pesa por su pureza Y por su cuenta de resultados — las células que cuestan
  dinero pierden voz; las rentables mandan.
- **Olvido económico**: la regla es contable (se liquidan células de cuenta
  negativa persistente); el PATRÓN de qué se olvida debe emerger.
- **Ruina absorbente**: presupuesto ≤ 0 = muerte; una vida por corrida, sin
  resets; muchas vidas independientes solo para estadística (sin compartir
  aprendizaje entre vidas).

### Las cuatro comparaciones (mismas tripas, distinta economía)

| Variante | Qué aísla |
|---|---|
| **SOLVENTE** | La tesis completa (Kelly + costes + cuentas) |
| **TEMERARIO** | Apuesta fracción fija agresiva si EV>0 — el maximizador de esperanza. Aísla la afirmación ergódica (c) |
| **GRATIS** | Sin costes de computación/memoria/creación. Aísla el olvido económico |
| **SALARIO** | Sin apuestas: cobra fijo por acierto. Aísla "stakes vs recompensa" — ¿la calibración necesita tener algo en juego? |

30 vidas × 3500 pasos por variante. Métricas: supervivencia, trayectoria de
log-presupuesto y su tasa de crecimiento por ventanas (el instrumento de la
señal del bebé: fase de aceleración → meseta), Brier esperado sobre sondas
(fuera de la economía), tamaño de memoria, tasa de abstención.

### Criterios de vida o muerte (firmados antes de ver un número)

- **K1 (ergodicidad)**: SOLVENTE debe sobrevivir sustancialmente más que
  TEMERARIO (menos ruinas y/o vidas más largas). Si el apostador de
  esperanza vive igual de bien, el núcleo temporal de la tesis cae.
- **K2 (calibración por stakes)**: el Brier esperado de SOLVENTE debe ser
  mejor que el de SALARIO (misma maquinaria, sin nada en juego). Si
  apostarse el pellejo no calibra mejor que cobrar un sueldo, la emergencia
  1 cae.
- **K3 (olvido, informativo)**: SOLVENTE debe mantener bastante menos
  memoria que GRATIS con pérdida de acierto pequeña.
- **K4 (instrumento, informativo)**: la curva de tasa de crecimiento debe
  mostrar fase de aceleración y meseta detectables — el estreno de la señal
  del bebé como instrumento (en un mundo finito, la meseta es lo esperado y
  lo honesto).

**VIVE** si K1 y K2 pasan sin amañar ingresos ni parámetros por variante
(una sola configuración compartida, congelada tras la puesta a punto
documentada). **MUERE** en caso contrario, y se archiva con el resultado.

## Registro de resultados — v0 (2026-08-23, 30 vidas × 3500 pasos por variante)

| Métrica | SOLVENTE | TEMERARIO | GRATIS | SALARIO |
|---|---|---|---|---|
| Supervivencia | **80%** | 40% | 97% | 0% (muerte económica del control) |
| Vida media (pasos) | 2830 | 1932 | 3392 | 2474 |
| Presupuesto final (mediana) | ~3×10¹⁵ | ~8×10¹⁰ | ~5×10¹⁷ | 0 |
| Brier esperado (sondas) | 0.176 | 0.168 | 0.174 | **0.153** |
| Acierto (sondas) | 71.8% | 69.3% | 78.2% | **82.7%** |
| Células | 453 | 295 | 555 | 358 |

**K1 (ergodicidad): SUPERADO, con contundencia.** Con las mismas creencias y
el mismo mundo, el organismo Kelly sobrevive el doble (80% vs 40%) y acumula
cinco órdenes de magnitud más que el maximizador de esperanza. La fila K4 de
TEMERARIO enseña el mecanismo: desplomes de −9/−14/−25/−24 milinats tras cada
reforma — sobre-apostar confianza caducada mata, exactamente como predice la
no-ergodicidad. Este resultado queda establecido y es publicable por sí solo.

**K2 (calibración por stakes): FALLADO, con claridad.** SALARIO — la misma
maquinaria SIN nada en juego — calibra mejor (0.153 vs 0.176) y acierta más
(82.7% vs 71.8%). El voto ponderado por consecuencias EMPEORÓ la epistemia:
células con buena estadística perdían voz por mala suerte en apuestas
colectivas, contaminando el mapa con el ruido del territorio. **La
emergencia central de la tesis salió al revés.**

**K3 (informativo): débil.** 18% menos memoria que GRATIS a cambio de 6.4
puntos de acierto — no es "pérdida pequeña".

**K4 (instrumento): FUNCIONA.** La curva de tasa de crecimiento lee la vida
entera: aceleración infantil (14→33 milinats), heridas de cada reforma,
y decaimiento hacia meseta al final (9.7 y bajando: el mundo aprendido, sin
frontera nueva donde invertir). La señal del bebé queda estrenada y validada
como instrumento — en su primer despliegue detectó la saturación que predijo.

### Veredicto según prerregistro: **MUERE**

VIVE exigía K1 y K2. K2 falló. La tesis, tal como fue enunciada — el
presupuesto de viabilidad como única señal que moldea también las
*creencias* — queda archivada con este resultado.

### Autopsia (lo que la muerte enseñó)

La disección separa limpio de podrido: **la solvencia gobierna cómo ACTUAR
sobre las creencias, no qué CREER.** Kelly sobre creencias honestas = doble
de supervivencia (K1). Consecuencias dentro del voto epistémico = creencias
corrompidas (K2). Es un eco del principio clásico de separar estimación y
decisión — y sugiere una sucesora más estrecha, no prerregistrada aún:
*epistemia de libro honesto (Pacioli) + capa de decisión solvente (Kelly,
costes, ruina)*. Esa hipótesis exigiría su propio prerregistro; no se abre
aquí. Dos pepitas quedan en pie: el resultado K1 (ergodicidad en organismos
que aprenden) y el instrumento K4 (la señal del bebé), que sobrevive a la
muerte de su anfitriona.

## Relación con las demás tesis

Solvencia es candidata a tesis central porque las contiene: la señal del bebé
(Cría) es su métrica (e); la demografía de Ágora es su mecanismo poblacional;
la disciplina del descuadre de Pacioli es su contabilidad; y la infancia
subvencionada reintroduce a los tutores de Cría como necesidad matemática.
Si muere, las otras siguen en pie por separado.
