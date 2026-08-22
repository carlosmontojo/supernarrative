"""Experimento Pacioli v1: mundo estocástico + percepción ruidosa.

Protocolo prerregistrado en TESIS.md ANTES de ejecutar. Métricas:
- P1' recuperación: pasos hasta >90% de acierto modal en tipos reformados.
- P2' Brier esperado ANALÍTICO contra la distribución verdadera:
  EB = conf² − 2·conf·p + p, con p = P(la cuenta predicha sea la observada).
  Un agente perfectamente calibrado en un tipo 70/30 dice conf=0.7 y obtiene
  EB = 0.21; la sobreconfianza se penaliza de verdad.
- Acierto modal y transferencia a proveedores nunca vistos.

RED se barre en lr {0.05, 0.15, 0.3, 0.6, 1.0} y se publica entero.

Uso:
    python experimento.py                    # percepción limpia (ε=0)
    python experimento.py --ruido-doc 0.3    # problema del asiento (ε=0.3)
"""
import argparse
import statistics

from mundo import MundoV1, TIPOS
from agentes import AgenteRedV1, AgenteLibroV1

LRS = [0.05, 0.15, 0.3, 0.6, 1.0]


def sondas(mundo):
    lista = []
    for t in TIPOS:
        vistos = [p for p in mundo.proveedores if (t, p) not in mundo.excepciones][:3]
        for p in vistos:
            lista.append(((t, p), False))
        for p in mundo.proveedores_nuevos:
            lista.append(((t, p), True))
    return lista


def evaluar(agente, mundo, lista):
    acc, eb, nuevos, n_nuevos = 0.0, 0.0, 0.0, 0
    por_tipo_ok, por_tipo_n = {t: 0 for t in TIPOS}, {t: 0 for t in TIPOS}
    for clave, es_nuevo in lista:
        tipo, prov = clave
        doc = mundo.documento(tipo, canonico=True)
        pred, conf = agente.predecir(doc, prov)
        dist = mundo.dist_de(clave)
        ok = pred == mundo.modal_de(clave)
        p_corr = dist.get(pred, 0.0)
        acc += ok
        eb += conf * conf - 2.0 * conf * p_corr + p_corr
        por_tipo_ok[tipo] += ok
        por_tipo_n[tipo] += 1
        if es_nuevo:
            nuevos += ok
            n_nuevos += 1
    n = len(lista)
    acc_tipo = {t: por_tipo_ok[t] / por_tipo_n[t] for t in TIPOS}
    return acc / n, eb / n, nuevos / n_nuevos, acc_tipo


def correr(seed, pasos, reforma_cada, ruido_doc, curiosidad):
    mundo = MundoV1(seed=seed, p_error_doc=ruido_doc)
    agentes = {f"RED {lr}": AgenteRedV1(lr=lr, seed=seed) for lr in LRS}
    agentes["LIBRO"] = AgenteLibroV1(curiosidad=curiosidad)
    lista = sondas(mundo)
    res = {n: {"acc": [], "eb": [], "nuevos": [], "recuperaciones": []} for n in agentes}
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
    ap.add_argument("--sin-curiosidad", action="store_true")
    args = ap.parse_args()

    nombres = [f"RED {lr}" for lr in LRS] + ["LIBRO"]
    agg = {n: {"rec": [], "eb": [], "acc": [], "nuevos": [], "norec": 0} for n in nombres}
    for s in range(args.semillas):
        res, agentes, mundo = correr(seed=s, pasos=args.pasos,
                                     reforma_cada=args.reforma_cada,
                                     ruido_doc=args.ruido_doc,
                                     curiosidad=not args.sin_curiosidad)
        for n in nombres:
            finitas = [r for r in res[n]["recuperaciones"] if r != float("inf")]
            if finitas:
                agg[n]["rec"].append(statistics.mean(finitas))
            agg[n]["norec"] += len(res[n]["recuperaciones"]) - len(finitas)
            agg[n]["eb"].append(statistics.mean(res[n]["eb"]))
            agg[n]["acc"].append(statistics.mean(res[n]["acc"]))
            agg[n]["nuevos"].append(statistics.mean(res[n]["nuevos"]))

    print(f"\n=== Pacioli v1 | {args.semillas} semillas × {args.pasos} pasos | "
          f"reforma cada {args.reforma_cada} | ruido percepción ε={args.ruido_doc}"
          f"{' | LIBRO sin curiosidad' if args.sin_curiosidad else ''} ===\n")
    cab = f"{'métrica':26}" + "".join(f"{n:>10}" for n in nombres)
    print(cab)
    filas = [("P1' recuperación", "rec", "{:.0f}"),
             ("  reformas fallidas", "norec", None),
             ("P2' Brier esp. (menor=mejor)", "eb", "{:.3f}"),
             ("acierto modal", "acc", "{:.1%}"),
             ("prov. nuevos", "nuevos", "{:.1%}")]
    for etiqueta, campo, fmt in filas:
        fila = f"{etiqueta:26}"
        for n in nombres:
            if fmt is None:
                fila += f"{agg[n]['norec']:>10}"
            else:
                vals = agg[n][campo]
                fila += f"{fmt.format(statistics.mean(vals)) if vals else 'nunca':>10}"
        print(fila)

    print("\n--- auditoría LIBRO (última semilla, doc canónico de 'suministro') ---")
    doc = mundo.documento("suministro", canonico=True)
    print(agentes["LIBRO"].auditar(doc, 0))


if __name__ == "__main__":
    main()
