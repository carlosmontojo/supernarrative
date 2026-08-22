# Experimento Pacioli v1

Segunda ronda de la [Tesis Pacioli](../../../TESIS.md): mundo **estocástico**
(tipos 70/30 — la calibración se mide con Brier esperado analítico contra la
distribución verdadera) y **percepción ruidosa** (documentos de tokens con
error de asiento con probabilidad ε).

```bash
python experimento.py                    # percepción limpia
python experimento.py --ruido-doc 0.3    # problema del asiento
python experimento.py --sin-curiosidad   # ablación
```

RED se compara en barrido completo de lr {0.05 … 1.0}, publicado entero.

**Resultado (2026-08-22)**: con percepción limpia, LIBRO domina en Pareto a
todas las configuraciones de RED (recuperación 34 vs 70, Brier 0.075 vs 0.093,
acierto 98.6% vs 92.8%) — escapa al dilema estabilidad/plasticidad gracias a
la disciplina del descuadre. Con ε=0.3, RED gana con claridad: el veneno de
los asientos erróneos persiste en los saldos. La frontera de lo asentable,
dibujada empíricamente. Detalle completo en TESIS.md, "Registro de resultados".
