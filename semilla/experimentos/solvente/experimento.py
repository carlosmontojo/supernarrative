"""Experimento Solvencia v0 — vidas completas de las cuatro variantes.

Cada vida: un organismo, un mundo (ruido ε=0.15, reforma cada 500), 3500
pasos máximo, ruina absorbente. 30 vidas independientes por variante (solo
para estadística: ninguna vida aprende de otra).

Métricas del prerregistro (TESIS-SOLVENCIA.md):
  K1  supervivencia SOLVENTE vs TEMERARIO
  K2  Brier esperado SOLVENTE vs SALARIO (sondas fuera de la economía)
  K3  memoria SOLVENTE vs GRATIS (con su coste en acierto)
  K4  curva de tasa de crecimiento del log-presupuesto (señal del bebé)

Uso:  python experimento.py [--vidas 30] [--pasos 3500]
"""
import argparse
import math
import pathlib
import statistics
import sys

V1 = pathlib.Path(__file__).resolve().parent.parent / "pacioli" / "v1"
sys.path.insert(0, str(V1))
from mundo import MundoV1, TIPOS          # noqa: E402
from experimento import sondas, evaluar    # noqa: E402

from organismo import Organismo            # noqa: E402

VARIANTES = ["SOLVENTE", "TEMERARIO", "GRATIS", "SALARIO"]
VENTANA = 250  # pasos por ventana para la tasa de crecimiento


def una_vida(variante, seed, pasos):
    mundo = MundoV1(seed=seed, p_error_doc=0.15)
    org = Organismo(seed=seed, variante=variante)
    lista = sondas(mundo)
    log_pres = []          # (paso, log presupuesto)
    ebs, accs = [], []
    for paso in range(1, pasos + 1):
        if paso % 500 == 0 and paso < pasos - 200:
            mundo.reforma()
        doc, prov, cuenta, _ = mundo.transaccion()
        org.vivir_paso(doc, prov, cuenta, paso)
        if not org.viva:
            return {"vida": paso, "log_pres": log_pres, "eb": ebs, "acc": accs,
                    "celulas": len(org.celulas), "abst": org.abstenciones,
                    "final": 0.0}
        if paso % 50 == 0:
            log_pres.append((paso, math.log(max(org.presupuesto, 1e-9))))
        if paso % 100 == 0:
            acc, eb, _, _ = evaluar(org, mundo, lista)
            ebs.append(eb)
            accs.append(acc)
    return {"vida": pasos, "log_pres": log_pres, "eb": ebs, "acc": accs,
            "celulas": len(org.celulas), "abst": org.abstenciones,
            "final": org.presupuesto}


def tasa_crecimiento(log_pres, pasos_max):
    """Tasa media de crecimiento del log-presupuesto por ventana (nats/paso)."""
    tasas = {}
    puntos = dict(log_pres)
    ventanas = range(VENTANA, pasos_max + 1, VENTANA)
    for fin in ventanas:
        ini = fin - VENTANA
        if ini in puntos or ini == 0:
            a = puntos.get(ini, math.log(Organismo.DOTE))
            if fin in puntos:
                tasas[fin] = (puntos[fin] - a) / VENTANA
    return tasas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vidas", type=int, default=30)
    ap.add_argument("--pasos", type=int, default=3500)
    args = ap.parse_args()

    res = {}
    for var in VARIANTES:
        vidas = [una_vida(var, s, args.pasos) for s in range(args.vidas)]
        res[var] = vidas

    print(f"\n=== Solvencia v0 | {args.vidas} vidas × {args.pasos} pasos | "
          f"ε=0.15, reforma cada 500, ruina absorbente ===\n")
    print(f"{'métrica':28}" + "".join(f"{v:>11}" for v in VARIANTES))
    filas = []
    for var in VARIANTES:
        vidas = res[var]
        n = len(vidas)
        super = sum(1 for v in vidas if v["vida"] == args.pasos)
        vida_media = statistics.mean(v["vida"] for v in vidas)
        finales = [v["final"] for v in vidas if v["final"] > 0]
        eb = statistics.mean(statistics.mean(v["eb"]) for v in vidas if v["eb"])
        acc = statistics.mean(statistics.mean(v["acc"]) for v in vidas if v["acc"])
        cel = statistics.mean(v["celulas"] for v in vidas)
        filas.append((var, super / n, vida_media,
                      statistics.median(finales) if finales else 0.0,
                      eb, acc, cel))
    for etiqueta, idx, fmt in [
        ("supervivencia (de 30)", 1, "{:.0%}"),
        ("vida media (pasos)", 2, "{:.0f}"),
        ("presupuesto final (mediana)", 3, "{:.1f}"),
        ("Brier esperado (sondas)", 4, "{:.3f}"),
        ("acierto (sondas)", 5, "{:.1%}"),
        ("células al final", 6, "{:.0f}"),
    ]:
        fila = f"{etiqueta:28}"
        for f in filas:
            fila += f"{fmt.format(f[idx]):>11}"
        print(fila)

    # K4: la señal del bebé — tasa de crecimiento por ventanas (supervivientes)
    print("\n--- K4: tasa de crecimiento del log-presupuesto (nats/paso × 1000),"
          " mediana entre vidas ---")
    print(f"{'ventana hasta paso':>20}", end="")
    ventanas = list(range(VENTANA, args.pasos + 1, VENTANA))
    for fin in ventanas[:12]:
        print(f"{fin:>7}", end="")
    print()
    for var in VARIANTES:
        tasas_por_v = [tasa_crecimiento(v["log_pres"], args.pasos)
                       for v in res[var]]
        print(f"{var:>20}", end="")
        for fin in ventanas[:12]:
            vals = [t[fin] * 1000 for t in tasas_por_v if fin in t]
            print(f"{statistics.median(vals):>7.1f}" if vals else f"{'—':>7}",
                  end="")
        print()


if __name__ == "__main__":
    main()
