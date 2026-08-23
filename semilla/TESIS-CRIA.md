# Tesis Cría — la vía del bebé

*Estado: idea auditada bibliográficamente ANTES de formalizarse — el orden
correcto, aprendido de las dos tesis anteriores.*

## Enunciado propuesto (previo a la búsqueda)

> La AGI no saldrá de un modelo ultra-entrenado sino de un cerebro incipiente:
> un aprendiz pequeño de hardware fijo que crece en conocimiento, no en
> cómputo — con la inteligencia de un bebé al principio y más inteligente cada
> día. Tres componentes: (a) criado por LLMs que actúan de padres/tutores (el
> conocimiento entra a precio de conversación, no de entrenamiento); (b) medido
> por la "señal del bebé": que aprender la tarea N+1 cueste cada vez menos
> conforme acumula conocimiento — la curva que separa a un aprendiz abierto de
> uno que se satura; (c) partiendo de una semilla mínima de priors (analogía
> del genoma: ~750 MB de *cómo aprender*, no de qué saber).

Linaje declarado: Turing 1950 ("¿por qué no simular la mente del niño?").

## Búsqueda bibliográfica adversarial (2026-08-23)

**Veredicto por componente:**

- **(a) Criado por LLMs-padres — REINVENCIÓN (confianza alta).** Existe por
  varias vías independientes: el **BabyLM Challenge 2025** tiene una pista de
  interacción literal (profesor Llama tutelando a un modelo-niño, con retórica
  de "child-caregiver dialog"); **Rosie/ITL** (Laird, desde 2012) aprende
  tareas nuevas a precio de conversación con arquitectura fija; **LMA3/ELLM**
  (Oudeyer, Andreas): el LLM propone metas al agente pequeño; **SIMA 2**
  (DeepMind 2025): un Gemini genera tareas y recompensas para criar al agente;
  **TinyStories/phi**: currículos sintéticos escritos por el modelo grande
  para el pequeño; **INTERACT** (2024): el estudiante interroga activamente al
  profesor.
- **(c) Semilla mínima — REINVENCIÓN (confianza alta).** Es la pregunta
  explícita de **Zador** ("A Critique of Pure Learning" 2019; "genomic
  bottleneck" PNAS 2024: comprimir la red órdenes de magnitud mejora la
  transferencia posterior) y de **Chollet** ("On the Measure of Intelligence":
  inteligencia = eficiencia de adquisición controlando priors; Core Knowledge).
- **(b) La señal del bebé — PARCIALMENTE NOVEDOSA (confianza media).** El
  deseo está enunciado casi verbatim (**NELL**, Mitchell 2015: "become better
  learners over time", evitar mesetas) y las piezas métricas existen (forward
  transfer en continual learning — usado como métrica secundaria; learning
  progress de Oudeyer — usado como recompensa, no como evaluación; velocidad
  de adaptación en **AdA** — medida en un punto fijo, no longitudinalmente;
  open-endedness formal de Hughes et al. 2024 — sin operacionalizar como
  curva). **Lo que no se encontró con dueño: la curva longitudinal
  d(velocidad de aprendizaje)/dt como criterio PRIMARIO de éxito de un
  sistema, medida a lo largo de su vida en un mundo composicional.**

## Lo que sobrevive — la reclamación estrecha

1. **La métrica**: la señal del bebé como criterio primario y prerregistrable
   — operacionalizar "no saturarse" como curva medible, y evaluar con ella
   cualquier aprendiz (los nuestros incluidos: LIBRO y MERCADO se saturan, y
   ahora tenemos el instrumento para demostrarlo).
2. **El programa integrado**: los tres tercios existen por separado; nadie los
   declara juntos como programa (BabyLM Interaction es un pre-entrenamiento
   acotado con benchmarks estáticos, no una crianza abierta; SIMA 2 cría a un
   modelo grande y mide tasa de éxito, no velocidad de aprendizaje).

La bandera, si se planta, se planta ahí — citando y diferenciándose de:
BabyLM Interaction 2025, Rosie/ITL, LMA3, SIMA 2, NELL, Alberta Plan/OaK,
AdA, Zador, Chollet, Hughes et al. 2024.

## Estado

Sin experimento aún. El siguiente paso natural NO es correr nada: es diseñar
el mundo composicional abierto y la medición exacta de la curva (¿qué cuenta
como "tarea nueva"? ¿cómo se normaliza su dificultad para que la curva no sea
un artefacto?). Ese diseño es la parte difícil y la parte defendible.
