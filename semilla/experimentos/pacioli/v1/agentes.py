"""Agentes v1: perciben documentos (tokens + proveedor), no claves limpias.

AgenteRedV1   — extremo a extremo: multi-hot de tokens ⊕ one-hot de proveedor
                → softmax, SGD online. El lr se barre y se publica entero.
AgenteLibroV1 — el libro por tokens: cada token lleva su saldo de cuentas.
                La informatividad de un token no se programa: emerge de la
                pureza de su saldo (los tokens comunes acumulan de todo,
                su pureza cae y se auto-anulan). El problema del asiento,
                resuelto por contabilidad.

Disciplina del descuadre (respuesta al dilema estabilidad/plasticidad):
solo es descuadre lo que contradice la propia confianza (conf ≥ 0.75).
El ruido esperado se asienta sin depreciar nada; la sorpresa reexpresa
los saldos que la sostuvieron y abre sospecha (curiosidad).
"""
from collections import defaultdict, deque

import numpy as np

from mundo import TIPOS, CUENTAS, TOKENS_COMUNES, N_PROVEEDORES, PROVEEDORES_NUEVOS

VOCAB = [tok for t in TIPOS for tok in (f"{t}#a", f"{t}#b", f"{t}#c")] + TOKENS_COMUNES
IDX_TOKEN = {tok: i for i, tok in enumerate(VOCAB)}
IDX_CUENTA = {c: i for i, c in enumerate(CUENTAS)}
N_PROV_TOTAL = N_PROVEEDORES + PROVEEDORES_NUEVOS


class AgenteRedV1:
    def __init__(self, lr=0.3, seed=0):
        self.lr = lr
        rng = np.random.default_rng(seed)
        self.W = rng.normal(0, 0.01, size=(len(VOCAB) + N_PROV_TOTAL, len(CUENTAS)))

    def _x(self, doc, prov):
        x = np.zeros(self.W.shape[0])
        for tok in doc:
            x[IDX_TOKEN[tok]] = 1.0
        x[len(VOCAB) + prov] = 1.0
        return x

    def predecir(self, doc, prov):
        z = self._x(doc, prov) @ self.W
        p = np.exp(z - z.max())
        p /= p.sum()
        i = int(p.argmax())
        return CUENTAS[i], float(p[i])

    def elegir_consulta(self):
        return None

    def observar(self, doc, prov, cuenta, paso):
        x = self._x(doc, prov)
        z = x @ self.W
        p = np.exp(z - z.max())
        p /= p.sum()
        y = np.zeros(len(CUENTAS))
        y[IDX_CUENTA[cuenta]] = 1.0
        self.W += self.lr * np.outer(x, y - p)

    def auditar(self, doc, prov):
        return "(la creencia vive repartida en los pesos)"


class AgenteLibroV1:
    AJUSTE = 0.2            # depreciación al reexpresar un saldo descuadrado
    UMBRAL_SORPRESA = 0.75  # por debajo, un fallo es ruido esperado, no descuadre
    PUREZA_REEXPRESION = 0.6

    def __init__(self, curiosidad=True):
        self.curiosidad = curiosidad
        self.saldos = defaultdict(lambda: defaultdict(float))  # llave: token o ("prov", p)
        self.sospechas = defaultdict(float)                    # token -> descuadres vivos
        self.libro = defaultdict(lambda: deque(maxlen=8))      # firma doc -> asientos

    # ---------- creencias ----------

    def _voto(self, llave):
        s = self.saldos.get(llave)
        if not s:
            return None
        total = sum(s.values())
        if total <= 0:
            return None
        cuenta = max(s, key=s.get)
        pureza = s[cuenta] / total
        peso = (pureza ** 2) * min(1.0, total / 2.0)
        return s, total, pureza, peso

    def predecir(self, doc, prov, interno=False):
        """interno=True devuelve la convicción de los saldos (dispara la
        reexpresión); interno=False, la confianza declarada (con prudencia
        si hay descuadres vivos). Un contable puede dudar de cara al informe
        y aun así saber perfectamente qué decían sus libros."""
        scores, evidencia = defaultdict(float), 0.0
        for llave in list(doc) + [("prov", prov)]:
            voto = self._voto(llave)
            if voto is None:
                continue
            s, total, pureza, peso = voto
            for c, w in s.items():
                scores[c] += peso * (w / total)
            evidencia += total * (pureza ** 2)
        if not scores:
            return CUENTAS[0], 1.0 / len(CUENTAS)
        total_s = sum(scores.values())
        cuenta = max(scores, key=scores.get)
        conf = (scores[cuenta] / total_s) * (evidencia / (evidencia + 0.5))
        if not interno and any(self.sospechas[t] >= 1.0 for t in doc):
            conf *= 0.6  # hay un descuadre vivo sobre la mesa: prudencia
        return cuenta, conf

    # ---------- aprendizaje = conciliación ----------

    def observar(self, doc, prov, cuenta, paso):
        pred, conf = self.predecir(doc, prov, interno=True)
        if pred != cuenta and conf >= self.UMBRAL_SORPRESA:
            # Descuadre genuino: reexpresar los saldos que sostuvieron el error
            for tok in doc:
                voto = self._voto(tok)
                if voto is None:
                    continue
                s, _total, pureza, _peso = voto
                if max(s, key=s.get) == pred and pureza >= self.PUREZA_REEXPRESION:
                    for c in list(s):
                        s[c] *= self.AJUSTE
                    self.sospechas[tok] = min(self.sospechas[tok] + 1.0, 6.0)
        elif pred == cuenta:
            for tok in doc:
                if self.sospechas[tok] > 0:
                    self.sospechas[tok] *= 0.5
        for llave in list(doc) + [("prov", prov)]:
            self.saldos[llave][cuenta] += 1.0
        self.libro[tuple(sorted(doc))].append((paso, cuenta))

    # ---------- curiosidad = partidas abiertas ----------

    def elegir_consulta(self):
        if not self.curiosidad:
            return None
        vivos = [(s, t) for t, s in self.sospechas.items() if s >= 1.0]
        if vivos:
            return max(vivos)[1]
        return None

    # ---------- auditoría ----------

    def auditar(self, doc, prov):
        pred, conf = self.predecir(doc, prov)
        lineas = [f"Predicción para {doc} (prov {prov}): {pred} (confianza {conf:.2f})"]
        for tok in doc:
            voto = self._voto(tok)
            if voto is None:
                lineas.append(f"  '{tok}': sin saldo (no informa)")
                continue
            s, total, pureza, peso = voto
            reparto = ", ".join(f"{c}:{w:.1f}" for c, w in sorted(s.items(), key=lambda x: -x[1])[:3])
            marca = " ⚠ bajo sospecha" if self.sospechas[tok] >= 1.0 else ""
            lineas.append(f"  '{tok}': saldo [{reparto}] pureza {pureza:.2f} peso {peso:.2f}{marca}")
        return "\n".join(lineas)
