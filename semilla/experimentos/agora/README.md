# Experimento Ágora v0

Primera prueba de la [Tesis Ágora](../../TESIS-AGORA.md): una mente-economía
(población de traders que apuestan capital de credibilidad, mercado
pari-mutuel, quiebras, reproducción con mutación e inmigración empirista —
sin gradiente ni optimizador central), medida contra RED (gradiente, barrido
de lr) y LIBRO (Pacioli v1) en el mismo banco de pruebas no estacionario.

```bash
python experimento.py                    # percepción limpia
python experimento.py --ruido-doc 0.3    # ruido de asiento
```

**Resultado (2026-08-22)**: veredicto partido, registrado en TESIS-AGORA.md.
En limpio, RED 1.0 domina a MERCADO (criterio (a) fallado) y LIBRO domina a
todos. Bajo ruido de percepción, MERCADO gana justo donde LIBRO murió (92.5%
vs 86.0%, 0 reformas falladas vs 9) — criterio (b) superado. Hallazgo
emergente: bajo ruido, la selección descubrió sola condiciones conjuntivas
robustas al veneno. Tres paradigmas, tres regímenes: el mapa completo está en
la tesis.
