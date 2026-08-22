"""Experimento Pacioli v0: RED (SGD online) vs LIBRO (mente con partida doble).

Protocolo:
- Ambos agentes viven 'pasos' pasos y ven UNA transacción por paso.
- RED siempre observa transacciones al azar; LIBRO puede elegir cuál mirar
  cuando tiene partidas abiertas (misma cantidad de datos, distinta elección).
- Cada 'reforma_cada' pasos, el mundo cambia la regla de 2 tipos sin avisar.
- Cada 10 pasos se evalúa sobre un conjunto fijo de sondas (sin aprender de
  ellas), incluyendo proveedores nunca vistos en entrenamiento.

Métricas (predicciones P1-P4 de TESIS.md):
- P1 recuperación: pasos hasta volver a >90% de acierto en los tipos cambiados.
- P2 calibración: Brier score (confianza vs. acierto). Menor es mejor.
- P3 transferencia: acierto en proveedores nunca vistos.
- P4 auditoría: demo al final (LIBRO enseña sus asientos).

Uso:
    python experimento.py
    python experimento.py --sin-curiosidad          # ablación
    python experimento.py --sin-cierre              # ablación
    python experimento.py --semillas 10 --pasos 4000
"""
import argparse
import statistics

from mundo import Mundo, TIPOS
from agentes import AgenteRed, AgenteLibro


def sondas(mundo):
    """Conjunto fijo de evaluación: por tipo, 3 proveedores vistos sin
    excepción + todos los nuevos (nunca en entrenamiento)."""
    lista = []
    for t in TIPOS:
        vistos = [p for p in mundo.proveedores if (t, p) not in mundo.excepciones][:3]
        for p in vistos:
            lista.append(((t, p), False))
        for p in mundo.proveedores_nuevos:
            lista.append(((t, p), True))
    return lista


def evaluar(agente, mundo, lista):
    acc_total, brier, acc_nuevos, n_nuevos = 0.0, 0.0, 0.0, 0
    por_tipo_ok, por_tipo_n = {t: 0 for t in TIPOS}, {t: 0 for t in TIPOS}
    for clave, es_nuevo in lista:
        pred, conf = agente.predecir(clave)
        ok = pred == mundo.cuenta_de(clave)
        acc_total += ok
        brier += (conf - (1.0 if ok else 0.0)) ** 2
        por_tipo_ok[clave[0]] += ok
        por_tipo_n[clave[0]] += 1
        if es_nuevo:
            acc_nuevos += ok
            n_nuevos += 1
    n = len(lista)
    acc_tipo = {t: por_tipo_ok[t] / por_tipo_n[t] for t in TIPOS}
    return acc_total / n, brier / n, acc_nuevos / n_nuevos, acc_tipo


def correr(seed, pasos, reforma_cada, curiosidad, cierre):
    mundo = Mundo(seed=seed)
    agentes = {
        "RED": AgenteRed(seed=seed),
        "LIBRO": AgenteLibro(curiosidad=curiosidad, cierre=cierre),
    }
    lista = sondas(mundo)
    res = {n: {"brier": [], "acc": [], "nuevos": [], "recuperaciones": []}
           for n in agentes}
    pendiente = {n: None for n in agentes}  # (paso_reforma, tipos_cambiados)

    for paso in range(1, pasos + 1):
        if paso % reforma_cada == 0 and paso < pasos - 200:
            cambiados = mundo.reforma()
            for n in agentes:
                if pendiente[n] is not None:  # nunca se recuperó de la anterior
                    res[n]["recuperaciones"].append(float("inf"))
                pendiente[n] = (paso, cambiados)

        for nombre, ag in agentes.items():
            objetivo = ag.elegir_consulta()
            if objetivo is not None:
                clave, cuenta = mundo.transaccion(*objetivo)
            else:
                clave, cuenta = mundo.transaccion()
            ag.observar(clave, cuenta, paso)

        if paso % 10 == 0:
            for nombre, ag in agentes.items():
                acc, brier, nuevos, acc_tipo = evaluar(ag, mundo, lista)
                res[nombre]["acc"].append(acc)
                res[nombre]["brier"].append(brier)
                res[nombre]["nuevos"].append(nuevos)
                if pendiente[nombre] is not None:
                    p0, cambiados = pendiente[nombre]
                    if all(acc_tipo[t] >= 0.9 for t in cambiados):
                        res[nombre]["recuperaciones"].append(paso - p0)
                        pendiente[nombre] = None
    return res, agentes, mundo


def media(xs):
    finitos = [x for x in xs if x != float("inf")]
    if not finitos:
        return float("inf"), 0
    return statistics.mean(finitos), len(xs) - len(finitos)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semillas", type=int, default=5)
    ap.add_argument("--pasos", type=int, default=3000)
    ap.add_argument("--reforma-cada", type=int, default=500)
    ap.add_argument("--sin-curiosidad", action="store_true")
    ap.add_argument("--sin-cierre", action="store_true")
    args = ap.parse_args()

    agregado = {"RED": {"rec": [], "brier": [], "acc": [], "nuevos": [], "norec": 0},
                "LIBRO": {"rec": [], "brier": [], "acc": [], "nuevos": [], "norec": 0}}
    for s in range(args.semillas):
        res, agentes, mundo = correr(
            seed=s, pasos=args.pasos, reforma_cada=args.reforma_cada,
            curiosidad=not args.sin_curiosidad, cierre=not args.sin_cierre)
        for n in res:
            m, norec = media(res[n]["recuperaciones"])
            if m != float("inf"):
                agregado[n]["rec"].append(m)
            agregado[n]["norec"] += norec
            agregado[n]["brier"].append(statistics.mean(res[n]["brier"]))
            agregado[n]["acc"].append(statistics.mean(res[n]["acc"]))
            agregado[n]["nuevos"].append(statistics.mean(res[n]["nuevos"]))

    modo = []
    if args.sin_curiosidad:
        modo.append("sin curiosidad")
    if args.sin_cierre:
        modo.append("sin cierre")
    print(f"\n=== Pacioli v0 | {args.semillas} semillas × {args.pasos} pasos"
          f" | reforma cada {args.reforma_cada}"
          f"{' | LIBRO ' + ', '.join(modo) if modo else ''} ===\n")
    print(f"{'':22}{'RED':>12}{'LIBRO':>12}")
    for etiqueta, campo, fmt in [
        ("P1 recuperación (pasos)", "rec", "{:.0f}"),
        ("P1 reformas no superadas", None, None),
        ("P2 Brier (menor=mejor)", "brier", "{:.3f}"),
        ("P3 acierto prov. nuevos", "nuevos", "{:.1%}"),
        ("Acierto global", "acc", "{:.1%}"),
    ]:
        if campo is None:
            print(f"{etiqueta:22}{agregado['RED']['norec']:>12}{agregado['LIBRO']['norec']:>12}")
            continue
        fila = f"{etiqueta:22}"
        for n in ("RED", "LIBRO"):
            vals = agregado[n][campo]
            fila += f"{fmt.format(statistics.mean(vals)) if vals else 'nunca':>12}"
        print(fila)

    # P4: demo de auditoría con la última semilla
    print("\n--- P4: auditoría (última semilla) ---")
    clave = (TIPOS[0], 0)
    print(f"[LIBRO] {agentes['LIBRO'].auditar(clave)}")
    print(f"[RED]   {agentes['RED'].auditar(clave)}")


if __name__ == "__main__":
    main()
