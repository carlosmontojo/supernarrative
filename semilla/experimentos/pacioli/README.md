# Experimento Pacioli v0

Primera prueba de la [Tesis Pacioli](../../TESIS.md): ¿una mente cuya memoria
es un libro contable (asientos → saldos → conciliación → partidas abiertas →
cierre) se adapta con menos datos y mejor calibración que una red entrenada
online?

```bash
python experimento.py                      # RED vs LIBRO, 5 semillas
python experimento.py --sin-curiosidad     # ablación: ¿cuánto aporta elegir qué mirar?
python experimento.py --sin-cierre         # ablación: ¿cuánto aporta consolidar esquemas?
```

Mundo: transacciones de una empresa; reglas ocultas tipo→cuenta con excepciones
por proveedor; cada 500 pasos una "reforma" cambia reglas sin avisar. Ambos
agentes ven una transacción por paso; LIBRO puede *elegir* cuál cuando sus
cuentas no cuadran.

**Advertencias de honestidad** (de TESIS.md): el mundo llega pre-asentado — la
v0 prueba el bucle de aprendizaje, no la percepción (el "problema del asiento"
queda para la v1). Ganar aquí no valida la tesis: solo la mantiene viva y
barata de seguir probando. Perder aquí, en un mundo diseñado para sus puntos
fuertes, la mata.

**Resultado (2026-08-22)**: mixto — ver "Registro de resultados" en TESIS.md.
LIBRO se adapta 1.8× más rápido que la RED en su mejor configuración y es el
único auditable; la RED gana calibración (en un mundo determinista que la
favorece estructuralmente) y empata transferencia. Las ablaciones muestran que
el cierre con reexpresión retroactiva es el mecanismo de carga y la curiosidad
el segundo. El criterio prerregistrado (P1 y P2 claras) no se superó.
