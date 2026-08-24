"""El organismo solvente — Tesis Solvencia v0.

Un aprendiz con algo en juego: un único presupuesto del que cobra TODO
(metabolismo, memoria, computación, creación de conocimiento) y que solo
ingresa apostando por sus predicciones a odds fijadas por la estructura del
mundo. Ruina absorbente: presupuesto <= 0 es muerte, sin resets.

Cuerpo interno: células de conocimiento (condición -> saldo de clases) con
cuenta propia de resultados atribuidos. Las creencias las moldean las
consecuencias: el voto de cada célula pesa por su pureza Y por su cuenta.

Variantes (misma maquinaria, distinta economía) según el prerregistro:
  SOLVENTE  — Kelly fraccional + todos los costes + cuentas
  TEMERARIO — fracción fija agresiva si EV>0 (el maximizador de esperanza)
  GRATIS    — sin costes de computación/memoria/creación
  SALARIO   — sin apuestas: cobra fijo por acierto
"""
import random
import sys
import pathlib
from collections import defaultdict

V1 = pathlib.Path(__file__).resolve().parent.parent / "pacioli" / "v1"
sys.path.insert(0, str(V1))
from mundo import CUENTAS  # las clases del banco de pruebas


class Celula:
    __slots__ = ("cond", "saldo", "cuenta", "nacida")

    def __init__(self, cond, nacida):
        self.cond = cond                    # frozenset de rasgos exigidos
        self.saldo = defaultdict(float)     # clase -> evidencia
        self.cuenta = 0.0                   # P&G atribuido (moldea su voz)
        self.nacida = nacida


class Organismo:
    # --- economía (una sola configuración, congelada tras la puesta a punto) ---
    DOTE = 15.0            # presupuesto inicial: la infancia subvencionada
    ODDS = 1.3             # pago por unidad apostada; break-even en p≈0.77:
    #                        el azar pierde siempre y solo el conocimiento renta
    METABOLISMO = 0.02     # coste fijo por paso
    RENTA = 0.0008         # coste por célula almacenada, por paso
    COMPUTO = 0.0004       # coste por célula consultada
    CREAR = 0.05           # coste de crear una célula nueva
    KELLY_FRAC = 0.5       # Kelly fraccional (media apuesta de Kelly)
    F_TEMERARIO = 0.4      # fracción fija del maximizador de esperanza
    SALARIO_POR_ACIERTO = 0.25  # cubre costes medios: el control debe vivir
    #                             para poder medir su calibración
    MAX_CELULAS = 600
    UMBRAL_LIQUIDACION = -0.05  # cuenta por debajo -> célula liquidada (si madura)

    def __init__(self, seed=0, variante="SOLVENTE"):
        self.rng = random.Random(seed * 31 + 11)
        self.variante = variante
        self.presupuesto = self.DOTE
        self.celulas = []
        self.viva = True
        self.abstenciones = 0
        self.apuestas = 0
        con_costes = variante != "GRATIS"
        self.c_renta = self.RENTA if con_costes else 0.0
        self.c_computo = self.COMPUTO if con_costes else 0.0
        self.c_crear = self.CREAR if con_costes else 0.0

    # ---------- percepción y creencia ----------

    def _rasgos(self, doc, prov):
        return set(doc) | {("prov", prov)}

    def _voz(self, cel):
        total = sum(cel.saldo.values())
        if total <= 0:
            return 0.0, None
        clase = max(cel.saldo, key=cel.saldo.get)
        pureza = cel.saldo[clase] / total
        # La voz combina competencia (pureza, evidencia) con consecuencias
        # (su cuenta): una célula que cuesta dinero pierde influencia.
        solvencia_cel = max(0.2, 1.0 + 8.0 * cel.cuenta)
        return (pureza ** 2) * min(1.0, total / 2.0) * solvencia_cel, clase

    def creer(self, doc, prov):
        """Devuelve (clase, p, células_consultadas). Consultar cuesta."""
        rasgos = self._rasgos(doc, prov)
        activas = [c for c in self.celulas if c.cond <= rasgos]
        self.presupuesto -= self.c_computo * len(activas)
        if not activas:
            return None, 1.0 / len(CUENTAS), []
        votos = defaultdict(float)
        for cel in activas:
            voz, clase = self._voz(cel)
            if clase is not None and voz > 0:
                total = sum(cel.saldo.values())
                for cl, w in cel.saldo.items():
                    votos[cl] += voz * (w / total)
        if not votos:
            return None, 1.0 / len(CUENTAS), activas
        total_v = sum(votos.values())
        clase = max(votos, key=votos.get)
        evidencia = sum(sum(c.saldo.values()) for c in activas)
        p = (votos[clase] / total_v) * (evidencia / (evidencia + 0.5))
        return clase, p, activas

    # ---------- la decisión con algo en juego ----------

    def _fraccion_apuesta(self, p):
        if self.variante == "SALARIO":
            return 0.0
        ev = p * self.ODDS - 1.0
        if ev <= 0:
            return 0.0
        if self.variante == "TEMERARIO":
            return self.F_TEMERARIO
        kelly = ev / (self.ODDS - 1.0)
        return self.KELLY_FRAC * kelly

    # ---------- un paso de vida ----------

    def vivir_paso(self, doc, prov, clase_real, paso):
        if not self.viva:
            return
        self.presupuesto -= self.METABOLISMO + self.c_renta * len(self.celulas)

        clase, p, activas = self.creer(doc, prov)
        f = self._fraccion_apuesta(p) if clase is not None else 0.0
        apuesta = f * self.presupuesto
        if apuesta > 0:
            self.apuestas += 1
            acierto = clase == clase_real
            antes = self.presupuesto
            ganancia = apuesta * (self.ODDS - 1.0)
            if acierto:
                self.presupuesto += ganancia
            else:
                self.presupuesto -= apuesta
            # Atribución: las células que votaron la clase apostada cobran o
            # pagan en proporción a su voz. En términos RELATIVOS (fracción
            # de la vida ganada/perdida), para que la escala absoluta del
            # presupuesto no infle las cuentas.
            votantes = [(c,) + self._voz(c) for c in activas]
            votantes = [(c, voz) for c, voz, cl in votantes if cl == clase and voz > 0]
            total_voz = sum(v for _, v in votantes)
            if total_voz > 0 and antes > 0:
                delta = ((ganancia if acierto else -apuesta) / antes) * 0.5
                for cel, voz in votantes:
                    cel.cuenta += delta * (voz / total_voz)
        else:
            self.abstenciones += 1

        if self.variante == "SALARIO" and clase == clase_real and clase is not None:
            self.presupuesto += self.SALARIO_POR_ACIERTO

        # Aprender (la observación del resultado es pública y gratuita)
        rasgos = self._rasgos(doc, prov)
        for cel in activas:
            cel.saldo[clase_real] += 1.0
        if not activas and self.presupuesto > self.c_crear * 2:
            # Nacimiento empirista: invertir en conocimiento nuevo
            self.presupuesto -= self.c_crear
            k = self.rng.choice([1, 1, 2])
            cond = frozenset(self.rng.sample(sorted(rasgos, key=str), k))
            cel = Celula(cond, paso)
            cel.saldo[clase_real] += 1.0
            self.celulas.append(cel)
        elif (activas and clase is not None and clase != clase_real
                and self.presupuesto > self.c_crear * 4
                and self.rng.random() < 0.5):
            # Inversión en especialización: el error financia una célula más
            # específica sobre el contexto que acaba de costar dinero
            self.presupuesto -= self.c_crear
            pool = sorted(rasgos, key=str)
            cond = frozenset(self.rng.sample(pool, min(2, len(pool))))
            cel = Celula(cond, paso)
            cel.saldo[clase_real] += 1.0
            self.celulas.append(cel)

        # Olvido económico: liquidar células de cuenta negativa persistente
        if self.c_renta > 0:
            self.celulas = [
                c for c in self.celulas
                if not (c.cuenta < self.UMBRAL_LIQUIDACION and paso - c.nacida > 50)
            ]
        if len(self.celulas) > self.MAX_CELULAS:
            self.celulas.sort(key=lambda c: c.cuenta, reverse=True)
            del self.celulas[self.MAX_CELULAS:]

        if self.presupuesto <= 0:
            self.viva = False  # ruina absorbente: no hay reset

    # ---------- interfaz de evaluación (fuera de la economía) ----------

    def predecir(self, doc, prov):
        """Solo para sondas del instrumento: no cobra ni aprende."""
        rasgos = self._rasgos(doc, prov)
        activas = [c for c in self.celulas if c.cond <= rasgos]
        if not activas:
            return CUENTAS[0], 1.0 / len(CUENTAS)
        votos = defaultdict(float)
        for cel in activas:
            voz, clase = self._voz(cel)
            if clase is not None and voz > 0:
                total = sum(cel.saldo.values())
                for cl, w in cel.saldo.items():
                    votos[cl] += voz * (w / total)
        if not votos:
            return CUENTAS[0], 1.0 / len(CUENTAS)
        total_v = sum(votos.values())
        clase = max(votos, key=votos.get)
        evidencia = sum(sum(c.saldo.values()) for c in activas)
        p = (votos[clase] / total_v) * (evidencia / (evidencia + 0.5))
        return clase, p
