"""Experimento Ágora v0: tres paradigmas en la misma pista.

RED (gradiente, barrido de lr) vs LIBRO (Pacioli v1) vs MERCADO (Ágora),
sobre el banco de pruebas de la v1: mundo no estacionario con tipos
estocásticos (70/30) y ruido de percepción opcional. Protocolo y métricas
idénticos a pacioli/v1 (Brier esperado analítico incluido).

Uso:
    python experimento.py                    # percepción limpia
    python experimento.py --ruido-doc 0.3    # ruido de asiento
"""
import argparse
import pathlib
import statistics
import sys

V1 = pathlib.Path(__file__).resolve().parent.parent / "pacioli" / "v1"
sys.path.insert(0, str(V1))
from mundo import MundoV1, TIPOS               # noqa: E402
from agentes import AgenteRedV1, AgenteLibroV1  # noqa: E402
from experimento import sondas, evaluar         # noqa: E402

from agora import AgenteMercado                 # noqa: E402

LRS = [0.05, 0.15, 0.3, 0.6, 1.0]


def correr(seed, pasos, reforma_cada, ruido_doc):
    mundo = MundoV1(seed=seed, p_error_doc=ruido_doc)
    agentes = {f"RED {lr}": AgenteRedV1(lr=lr, seed=seed) for lr in LRS}
    agentes["LIBRO"] = AgenteLibroV1()
    agentes["MERCADO"] = AgenteMercado(seed=seed)
    lista = sondas(mundo)
    res = {n: {"acc": [], "eb": [], "nuevos": [], "recuperaciones": [],
               "colapsos": 0} for n in agentes}
    pendiente = {n: None for n in agentes}

    for paso in range(1, pasos + 1):
        if paso % reforma_cada == 0 and paso < pasos - 200:
            cambiados = mundo.reforma()
            for n in agentes:
                if pendiente[n] is not None:
                    res[n]["recuperaciones"].append(float("inf"))
                pendiente[n] = (paso, cambiados)

        for nombre, ag in agentes.items():
            token = ag.elegir_consulta()
            if token is not None:
                doc, prov, cuenta, _ = mundo.transaccion_por_token(token)
            else:
                doc, prov, cuenta, _ = mundo.transaccion()
            ag.observar(doc, prov, cuenta, paso)

        if paso % 10 == 0:
            for nombre, ag in agentes.items():
                acc, eb, nuevos, acc_tipo = evaluar(ag, mundo, lista)
                res[nombre]["acc"].append(acc)
                res[nombre]["eb"].append(eb)
                res[nombre]["nuevos"].append(nuevos)
                if acc < 0.5 and paso > 300:
                    res[nombre]["colapsos"] += 1
                if pendiente[nombre] is not None:
                    p0, cambiados = pendiente[nombre]
                    if all(acc_tipo[t] >= 0.9 for t in cambiados):
                        res[nombre]["recuperaciones"].append(paso - p0)
                        pendiente[nombre] = None
    return res, agentes, mundo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semillas", type=int, default=5)
    ap.add_argument("--pasos", type=int, default=3000)
    ap.add_argument("--reforma-cada", type=int, default=500)
    ap.add_argument("--ruido-doc", type=float, default=0.0)
    args = ap.parse_args()

    nombres = [f"RED {lr}" for lr in LRS] + ["LIBRO", "MERCADO"]
    agg = {n: {"rec": [], "eb": [], "acc": [], "nuevos": [], "norec": 0,
               "colapsos": 0} for n in nombres}
    for s in range(args.semillas):
        res, agentes, mundo = correr(seed=s, pasos=args.pasos,
                                     reforma_cada=args.reforma_cada,
                                     ruido_doc=args.ruido_doc)
        for n in nombres:
            finitas = [r for r in res[n]["recuperaciones"] if r != float("inf")]
            if finitas:
                agg[n]["rec"].append(statistics.mean(finitas))
            agg[n]["norec"] += len(res[n]["recuperaciones"]) - len(finitas)
            agg[n]["eb"].append(statistics.mean(res[n]["eb"]))
            agg[n]["acc"].append(statistics.mean(res[n]["acc"]))
            agg[n]["nuevos"].append(statistics.mean(res[n]["nuevos"]))
            agg[n]["colapsos"] += res[n]["colapsos"]

    print(f"\n=== Ágora v0 | {args.semillas} semillas × {args.pasos} pasos | "
          f"reforma cada {args.reforma_cada} | ε={args.ruido_doc} ===\n")
    print(f"{'métrica':26}" + "".join(f"{n:>10}" for n in nombres))
    filas = [("P1' recuperación", "rec", "{:.0f}"),
             ("  reformas fallidas", "norec", None),
             ("P2' Brier esp.", "eb", "{:.3f}"),
             ("acierto modal", "acc", "{:.1%}"),
             ("fuentes nuevas", "nuevos", "{:.1%}"),
             ("  evals en colapso", "colapsos", None)]
    for etiqueta, campo, fmt in filas:
        fila = f"{etiqueta:26}"
        for n in nombres:
            if fmt is None:
                fila += f"{agg[n][campo]:>10}"
            else:
                vals = agg[n][campo]
                fila += f"{fmt.format(statistics.mean(vals)) if vals else 'nunca':>10}"
        print(fila)

    print("\n--- auditoría MERCADO (última semilla) ---")
    doc = mundo.documento("suministro", canonico=True)
    print(agentes["MERCADO"].auditar(doc, 0))


if __name__ == "__main__":
    main()
