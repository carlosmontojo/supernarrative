"""Los dos agentes del experimento Pacioli v0.

AgenteRed   — línea base: clasificador neuronal entrenado online (SGD),
              consulta transacciones al azar. Representa el paradigma estándar
              en miniatura.
AgenteLibro — la mente Pacioli: asientos con procedencia, saldos como
              creencias, conciliación como aprendizaje, partidas abiertas como
              curiosidad, cierres que consolidan esquemas (abstracción).

Ambos ven exactamente UNA transacción por paso. La única ventaja permitida a
LIBRO es *elegir* cuál mirar cuando sus cuentas no cuadran.
"""
from collections import defaultdict, deque

import numpy as np

from mundo import TIPOS, CUENTAS, N_PROVEEDORES, PROVEEDORES_NUEVOS

N_PROV_TOTAL = N_PROVEEDORES + PROVEEDORES_NUEVOS
IDX_TIPO = {t: i for i, t in enumerate(TIPOS)}
IDX_CUENTA = {c: i for i, c in enumerate(CUENTAS)}


class AgenteRed:
    """Softmax lineal sobre one-hot(tipo) ⊕ one-hot(proveedor), SGD online."""

    # lr=1.0: el mejor de un barrido {0.15, 0.3, 0.6, 1.0} en este mundo —
    # la línea base se compara en su mejor versión, no debilitada.
    def __init__(self, lr=1.0, seed=0):
        self.lr = lr
        n_feats = len(TIPOS) + N_PROV_TOTAL
        rng = np.random.default_rng(seed)
        self.W = rng.normal(0, 0.01, size=(n_feats, len(CUENTAS)))

    def _x(self, clave):
        tipo, prov = clave
        x = np.zeros(self.W.shape[0])
        x[IDX_TIPO[tipo]] = 1.0
        x[len(TIPOS) + prov] = 1.0
        return x

    def predecir(self, clave):
        z = self._x(clave) @ self.W
        p = np.exp(z - z.max())
        p /= p.sum()
        i = int(p.argmax())
        return CUENTAS[i], float(p[i])

    def elegir_consulta(self):
        return None  # siempre al azar

    def observar(self, clave, cuenta, paso):
        x = self._x(clave)
        z = x @ self.W
        p = np.exp(z - z.max())
        p /= p.sum()
        y = np.zeros(len(CUENTAS))
        y[IDX_CUENTA[cuenta]] = 1.0
        self.W += self.lr * np.outer(x, y - p)

    def auditar(self, clave):
        return "(una red no puede enseñar sus asientos: la creencia vive repartida en los pesos)"


class AgenteLibro:
    """La mente con partida doble. Ver TESIS.md para el mapa conceptual."""

    AJUSTE = 0.2          # al descuadrar, la evidencia vieja se deprecia a este factor
    UMBRAL_ESQUEMA = 0.6  # consenso mínimo entre claves para consolidar esquema
    SOSPECHA_CIERRE = 3   # descuadres de un tipo que fuerzan cierre extraordinario

    def __init__(self, curiosidad=True, cierre=True, cierre_cada=100):
        self.curiosidad = curiosidad
        self.con_cierre = cierre
        self.cierre_cada = cierre_cada
        self.libro = defaultdict(lambda: deque(maxlen=10))  # clave -> últimos asientos
        self.saldos = defaultdict(lambda: defaultdict(float))  # clave -> cuenta -> peso
        self.esquemas = {}          # tipo -> (cuenta, consenso)
        self.esquema_paso = {}      # tipo -> paso del último cambio de criterio
        self.diario = defaultdict(lambda: deque(maxlen=10))  # tipo -> asientos recientes
        self.ultima_obs = {}        # clave -> último paso observado
        self.partidas = {}          # clave -> gravedad (curiosidad local)
        self.sospechas = defaultdict(float)   # tipo -> descuadres acumulados (curiosidad global)
        self.pendientes = defaultdict(deque)  # tipo -> proveedores por verificar tras sospecha
        self.n_asientos = 0

    # ---------- creencias ----------

    def predecir(self, clave):
        tipo, _ = clave
        saldo = self.saldos.get(clave)
        esquema = self.esquemas.get(tipo)
        conf_factor = 0.6 if self.sospechas[tipo] >= 1.0 else 1.0  # reforma en curso: prudencia
        if saldo:
            total = sum(saldo.values())
            cuenta = max(saldo, key=saldo.get)
            # Regla de reexpresión: un saldo anterior al último cambio de
            # criterio no puede pisar el criterio nuevo hasta reconciliarse.
            # (Una excepción observada DESPUÉS del cambio conserva su saldo.)
            if (esquema and esquema[0] != cuenta
                    and self.esquema_paso.get(tipo, -1) > self.ultima_obs.get(clave, -1)):
                return esquema[0], 0.7 * esquema[1] * conf_factor
            conf = (saldo[cuenta] / (total + 0.3))
            return cuenta, conf * conf_factor
        if esquema:
            return esquema[0], 0.8 * esquema[1] * conf_factor
        return CUENTAS[0], 1.0 / len(CUENTAS)  # sin saldo ni esquema: no sabe

    # ---------- aprendizaje = conciliación ----------

    def observar(self, clave, cuenta, paso):
        tipo, prov = clave
        pred, _ = self.predecir(clave)
        self.libro[clave].append((paso, cuenta))
        self.diario[tipo].append(cuenta)
        self.ultima_obs[clave] = paso
        self.n_asientos += 1
        if pred != cuenta and (clave in self.saldos or tipo in self.esquemas):
            # Descuadre: asiento de ajuste (la realidad manda, lo viejo se deprecia)
            for c in list(self.saldos[clave]):
                self.saldos[clave][c] *= self.AJUSTE
            self.partidas[clave] = self.partidas.get(clave, 0) + 2
            self.sospechas[tipo] = min(self.sospechas[tipo] + 1.0, 6.0)
            if not self.pendientes[tipo]:
                self.pendientes[tipo] = deque(range(N_PROVEEDORES))
        else:
            self.partidas.pop(clave, None)
            self.sospechas[tipo] *= 0.5
        self.saldos[clave][cuenta] += 1.0
        if self.pendientes[tipo] and prov in self.pendientes[tipo]:
            self.pendientes[tipo].remove(prov)
        # Cierre extraordinario: demasiados descuadres del mismo tipo.
        # La sospecha NO se apaga aquí: solo la apagan las predicciones que
        # vuelven a cuadrar (el descuadre se resuelve, no se archiva).
        if self.con_cierre and self.sospechas[tipo] >= self.SOSPECHA_CIERRE:
            self._consolidar(tipo, paso)
        if self.con_cierre and paso > 0 and paso % self.cierre_cada == 0:
            self.cierre(paso)

    # ---------- curiosidad = partidas abiertas ----------

    def elegir_consulta(self):
        if not self.curiosidad:
            return None
        # Prioridad 1: un tipo bajo sospecha, verificando proveedores aún no revisados
        sospechosos = [t for t, s in self.sospechas.items() if s >= 1.0 and self.pendientes[t]]
        if sospechosos:
            tipo = max(sospechosos, key=lambda t: self.sospechas[t])
            return tipo, self.pendientes[tipo][0]
        # Prioridad 2: la partida abierta más grave
        if self.partidas:
            return max(self.partidas, key=self.partidas.get)
        return None

    # ---------- abstracción = cierre del ejercicio ----------

    def _consolidar(self, tipo, paso=0):
        """El esquema lo deciden los asientos del ejercicio corriente (los
        recientes), no los saldos históricos: la vigencia manda."""
        reciente = list(self.diario[tipo])
        if len(reciente) < 5:
            return
        cuenta = max(set(reciente), key=reciente.count)
        consenso = reciente.count(cuenta) / len(reciente)
        if consenso < self.UMBRAL_ESQUEMA:
            return
        anterior = self.esquemas.get(tipo, (None, 0.0))[0]
        self.esquemas[tipo] = (cuenta, consenso)
        if anterior is not None and anterior != cuenta:
            # Cambio de criterio contable → reexpresión retroactiva: los
            # saldos que seguían el criterio antiguo se deprecian y quedan
            # supeditados al esquema nuevo hasta reconciliarse uno a uno.
            self.esquema_paso[tipo] = paso
            for (t, _p), saldo in self.saldos.items():
                if t == tipo and saldo and max(saldo, key=saldo.get) == anterior:
                    for c in list(saldo):
                        saldo[c] *= self.AJUSTE

    def cierre(self, paso=0):
        for tipo in TIPOS:
            self._consolidar(tipo, paso)
        for clave in list(self.partidas):
            self.partidas[clave] -= 1
            if self.partidas[clave] <= 0:
                del self.partidas[clave]

    # ---------- auditoría ----------

    def auditar(self, clave):
        tipo, _ = clave
        pred, conf = self.predecir(clave)
        lineas = [f"Predicción para {clave}: cuenta {pred} (confianza {conf:.2f})"]
        if clave in self.libro and self.libro[clave]:
            asientos = ", ".join(f"paso {p}→{c}" for p, c in self.libro[clave])
            lineas.append(f"  Asientos propios: {asientos}")
        if tipo in self.esquemas:
            c, r = self.esquemas[tipo]
            lineas.append(f"  Esquema '{tipo}' → {c} (consenso {r:.2f}, del cierre)")
        if self.sospechas[tipo] >= 1.0:
            lineas.append(f"  ⚠ tipo '{tipo}' bajo sospecha ({self.sospechas[tipo]:.1f} descuadres)")
        return "\n".join(lineas)
