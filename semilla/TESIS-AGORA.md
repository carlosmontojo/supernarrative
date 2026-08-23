# Tesis Ágora — inteligencia sin optimizador central

*Estado: hipótesis viva. Hermana de TESIS.md (Pacioli); comparten método y
banco de pruebas, no mecanismo. Este documento existe para ser falsado.*

## Enunciado

> La operación fundamental de la inteligencia no es la optimización sino la
> **selección**. Una mente puede ser una economía: una población de
> predictores diminutos que apuestan su capital de credibilidad en cada
> predicción, cobran o pierden según el resultado, se reproducen con mutación
> cuando prosperan y quiebran cuando fallan. No hay descenso de gradiente, no
> hay objetivo global, no hay fase de entrenamiento: el aprendizaje es
> demografía y el precio del mercado ES la confianza del sistema.

Mecanismo v0, concreto:

- **Trader**: una regla mínima — condición (qué rasgos del estímulo exige) +
  predicción (una clase) + capital.
- **Mercado (predicción)**: los traders cuya condición casa con el estímulo
  apuestan una fracción fija de su capital por su clase. La distribución de
  apuestas es la creencia del sistema; el precio de la clase ganadora, su
  confianza (amortiguada por liquidez: poca apuesta total = "no sé").
- **Liquidación (aprendizaje)**: reparto pari-mutuel — los aciertos se llevan
  el bote en proporción a lo apostado; los fallos lo pierden. El capital es
  credibilidad compuesta.
- **Demografía (lo que sustituye al gradiente)**: quiebra por debajo del
  umbral = muerte; los ricos engendran mutantes pagando dote; e inmigración
  empirista constante — traders recién nacidos de la última observación
  (condición: rasgos del estímulo; predicción: lo que acaba de pasar). Tras
  un cambio de régimen, los inmigrantes que aciertan cobran botes enormes
  contra la vieja guardia equivocada y se capitalizan en pocas rondas.

Propiedades que promete: continuo por construcción (no existe "entrenar y
congelar"); sin dilema estabilidad/plasticidad (la estabilidad vive en los
veteranos ricos, la plasticidad en los mutantes pobres, a la vez);
paralelismo extremo; calibración emergente (en equilibrio, el precio tiende a
la frecuencia verdadera: un contexto 70/30 debe cotizar a ~0.70).

## Precedentes declarados (esta vez hay uno grande)

- **Learning Classifier Systems** (Holland, años 70-90; XCS de Wilson): el
  ancestro más cercano — poblaciones de reglas condición→acción con reparto
  de crédito ("bucket brigade") y evolución. Funcionaron en juguetes y se
  desvanecieron ante el gradiente. **La Tesis Ágora es, en parte, su
  reedición**; lo nuevo es el mecanismo de mercado pari-mutuel puro, la
  inmigración empirista, la lectura de calibración como precio, y probarlo
  con protocolo moderno contra líneas base afinadas. Si esto funciona, los
  LCS estaban adelantados; si no, estamos repitiendo su historia sin saberlo.
- Economía de agentes de Baum ("Hayek machine", ~1999); darwinismo neuronal
  (Edelman); sociedad de la mente (Minsky); AutoML-Zero (2020) — la evolución
  sin gradiente redescubrió el backprop desde operaciones sueltas: la
  selección encuentra lo que el gradiente no puede pisar.

## Premortem (cinco muertes, tres vidas)

| # | Modo de muerte | Gravedad |
|---|---|---|
| 1 | **La sombra de Holland**: los LCS ya recorrieron este camino y no escalaron. Riesgo de estar reviviendo un fracaso con vocabulario nuevo. | Alta |
| 2 | **Ineficiencia muestral**: treinta años de derrotas de los métodos sin gradiente en eficiencia por muestra. La selección malgasta lo que el gradiente aprovecha. | Alta |
| 3 | **Crédito plano**: el pari-mutuel premia o castiga la regla ENTERA; el gradiente reparte crédito dentro de la función — esa es su magia y el mercado no la tiene. Sin crédito estructurado, no hay composición. | Alta |
| 4 | **Inestabilidad de mercado**: burbujas, extinciones en masa, oscilaciones. Ninguna garantía de convergencia. Un crash sostenido = mente que colapsa. | Media |
| 5 | **Reglas planas no abstraen**: sin jerarquía (traders de traders), el sistema memoriza nichos, no construye conceptos. | Media (v2) |

| # | Escenario de vida |
|---|---|
| 1 | La demografía disuelve el dilema estabilidad/plasticidad que atrapó a RED en la v1 — y lo hace sin el mecanismo de sorpresa artesanal de LIBRO. |
| 2 | La selección de condiciones debería digerir el ruido de percepción mejor que el libro: los traders con condiciones sobre tokens venenosos quiebran solos. Justo donde Pacioli murió. |
| 3 | Encaja con el hardware del futuro barato: millones de módulos triviales en paralelo, sin sincronía global. |

## Criterios de vida o muerte de la v0 (fijados antes de ejecutar)

Banco de pruebas: el mundo v1 (estímulo→categoría, no estacionario, tipos
70/30, ruido de percepción ε) — mismos protocolos, misma métrica de Brier
esperado analítico. Tres paradigmas en la misma tabla: RED (barrido de lr),
LIBRO (Pacioli v1) y MERCADO.

- **VIVE** si (a) con ε=0 ningún lr de RED domina a MERCADO en Pareto
  (P1' recuperación y P2' Brier esperado), y (b) con ε=0.3 MERCADO supera a
  LIBRO en acierto y en recuperación — la promesa diferencial: la selección
  debe sobrevivir al ruido de asiento que mató al libro. Y en ningún régimen
  sufre colapsos sostenidos (acierto <50% mantenido = crash = muerte).
- **MUERE** si RED lo domina en limpio, o si bajo ruido no mejora a LIBRO,
  o si el mercado crashea.

Nota de equidad: MERCADO no tiene curiosidad dirigida (no elige qué mirar);
su exploración es demográfica. LIBRO conserva la suya. Cada paradigma compite
con sus propios órganos.

## Registro de resultados

### 2026-08-22 — v0 (5 semillas × 3000 pasos, tres paradigmas en la misma pista)

Puesta a punto documentada (2 ajustes, luego se congeló): la inmigración
pasó a ser por sustitución (con el censo lleno, los nuevos desplazan a los
más pobres — sin recambio no hay plasticidad; recuperación 140→45 en sanity)
y el umbral de reproducción se ajustó al capital diluido. Un barrido de
población/apuesta mostró el dial estabilidad-plasticidad propio del mercado
(más liquidez = mejor calibración, peor adaptación); se congeló la
configuración original (400 traders, apuesta 25%).

**ε = 0 (percepción limpia):**

| | RED 1.0 (mejor) | LIBRO | MERCADO |
|---|---|---|---|
| P1' recuperación | 54 (1 reforma fallida) | **41** (1 fallida) | 61 (**0 fallidas**) |
| P2' Brier esperado | 0.097 | **0.082** | 0.111 |
| Acierto modal | 92.1% | **98.0%** | 90.7% |

**ε = 0.3 (ruido de asiento):**

| | mejor RED | LIBRO | MERCADO |
|---|---|---|---|
| P1' recuperación | 71 (lr 1.0) | 290, **9 fallidas** | **80, 0 fallidas** |
| P2' Brier esperado | 0.098 | 0.152 | 0.118 |
| Acierto modal | 92.9% (lr 0.3) | 86.0% | 92.5% |

**Veredicto según criterios prerregistrados**: (a) **fallado** — en limpio,
RED 1.0 domina a MERCADO en P1' y P2' (nota al pie: excluyendo que RED 1.0
dejó 1 reforma sin superar y MERCADO recuperó 25/25; el criterio, tal como se
redactó, no contemplaba la robustez). (b) **superado con claridad** — donde
el libro murió, el mercado vive: 92.5% vs 86.0% de acierto y 80 vs 290 pasos
de recuperación con 9 fracasos de LIBRO por 0 de MERCADO. Como enunciado
fuerte ("la selección sustituye al optimizador"), la tesis **no vive**; como
enunciado diferencial ("la selección es singularmente robusta al ruido de
percepción"), **confirmada**.

**Hallazgo emergente** (no buscado): bajo ruido, los traders dominantes
evolucionaron condiciones conjuntivas de dos rasgos ({token_a, token_b}) —
casi nunca están ambos envenenados a la vez. Nadie programó esa robustez: la
selección la encontró. Es exactamente el tipo de descubrimiento estructural
que el premortem no predijo.

**El mapa del día, con tres tesis medidas en la misma pista**: cada paradigma
posee un régimen. El gradiente reina cuando hay que digerir ruido con un solo
dial; el libro domina todo cuando el mundo llega asentado (y es el único
auditable); el mercado es el generalista robusto — nunca colapsó, nunca dejó
una reforma sin superar, con UNA configuración en todos los regímenes,
mientras RED necesita elegir su lr por régimen. Ninguno es la revolución
completa; los tres juntos dibujan dónde habría que buscarla.

**Dirección v1 obvia** (anotada, no prometida): hibridar — traders que sean
pequeños libros (condición + saldo con pureza, en vez de condición + clase
fija), o mercado para la percepción y libro para los hechos. La conjetura:
los regímenes se suman. El riesgo: también se suman las complejidades.
