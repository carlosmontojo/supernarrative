"""AgenteMercado — la mente-economía de la Tesis Ágora.

Una población de traders diminutos. Cada trader: condición (rasgos que exige
en el estímulo) + predicción (una clase) + capital. Predicción del sistema =
mercado pari-mutuel entre los traders activos; aprendizaje = liquidación de
apuestas; adaptación = demografía (quiebras, reproducción con mutación,
inmigración empirista). Sin gradiente, sin objetivo global, sin fase de
entrenamiento.
"""
import random
import sys
import pathlib
from collections import defaultdict, deque

V1 = pathlib.Path(__file__).resolve().parent.parent / "pacioli" / "v1"
sys.path.insert(0, str(V1))
from mundo import CUENTAS  # el banco de pruebas compartido define las clases


class Trader:
    __slots__ = ("cond", "pred", "capital")

    def __init__(self, cond, pred, capital):
        self.cond = cond          # frozenset de rasgos exigidos
        self.pred = pred          # clase que predice
        self.capital = capital    # credibilidad compuesta


class AgenteMercado:
    STAKE = 0.25          # fracción del capital apostada en cada mercado
    UMBRAL_QUIEBRA = 0.05
    CAPITAL_INMIGRANTE = 0.3
    MAX_POBLACION = 400

    def __init__(self, seed=0, curiosidad=False):
        self.rng = random.Random(seed + 7)
        self.poblacion = []
        self.recientes = deque(maxlen=20)  # últimas observaciones (rasgos, clase)

    # ---------- el mercado = la creencia ----------

    def _rasgos(self, doc, prov):
        return set(doc) | {("prov", prov)}

    def _activos(self, rasgos):
        return [t for t in self.poblacion if t.cond <= rasgos]

    def predecir(self, doc, prov):
        activos = self._activos(self._rasgos(doc, prov))
        if not activos:
            return CUENTAS[0], 1.0 / len(CUENTAS)
        apuestas = defaultdict(float)
        for t in activos:
            apuestas[t.pred] += t.capital * self.STAKE
        total = sum(apuestas.values())
        clase = max(apuestas, key=apuestas.get)
        precio = apuestas[clase] / total
        # la liquidez amortigua: poca apuesta total = mercado que duda
        return clase, precio * (total / (total + 0.25))

    # ---------- la liquidación = el aprendizaje ----------

    def observar(self, doc, prov, clase, paso):
        rasgos = self._rasgos(doc, prov)
        activos = self._activos(rasgos)
        bote, ganadores = 0.0, []
        for t in activos:
            apuesta = t.capital * self.STAKE
            t.capital -= apuesta
            bote += apuesta
            if t.pred == clase:
                ganadores.append((t, apuesta))
        if ganadores:
            total_g = sum(a for _, a in ganadores)
            for t, a in ganadores:
                t.capital += bote * (a / total_g)
        # si nadie acertó, el bote se pierde: deflación de los equivocados
        self.recientes.append((tuple(rasgos), clase))
        self._demografia(rasgos, clase)

    # ---------- la demografía = lo que sustituye al gradiente ----------

    def _demografia(self, rasgos, clase):
        # Quiebras
        self.poblacion = [t for t in self.poblacion
                          if t.capital >= self.UMBRAL_QUIEBRA]
        # Reproducción con mutación: torneo entre una muestra; el rico paga dote
        if self.poblacion and self.rng.random() < 0.3:
            muestra = self.rng.sample(self.poblacion,
                                      min(8, len(self.poblacion)))
            padre = max(muestra, key=lambda t: t.capital)
            if padre.capital > 0.6:
                hijo = self._mutar(padre)
                dote = padre.capital * 0.25
                padre.capital -= dote
                hijo.capital = dote
                self.poblacion.append(hijo)
        # Inmigración empirista: nacidos de lo que acaba de pasar. Si el censo
        # está lleno, los nuevos DESPLAZAN a los más pobres: la plasticidad no
        # espera a que haya hueco — el recambio es constante.
        for _ in range(2):
            k = self.rng.choice([1, 1, 2])
            cond = frozenset(self.rng.sample(sorted(rasgos, key=str), k))
            self.poblacion.append(Trader(cond, clase, self.CAPITAL_INMIGRANTE))
        if len(self.poblacion) > self.MAX_POBLACION:
            self.poblacion.sort(key=lambda t: t.capital, reverse=True)
            del self.poblacion[self.MAX_POBLACION:]

    def _mutar(self, padre):
        cond, pred = set(padre.cond), padre.pred
        r = self.rng.random()
        rasgos_recientes, clases_recientes = zip(*self.recientes)
        if r < 0.4 and len(cond) < 3:  # especializarse: exigir un rasgo más
            cond.add(self.rng.choice(sorted(self.rng.choice(rasgos_recientes), key=str)))
        elif r < 0.7 and len(cond) > 1:  # generalizarse: exigir uno menos
            cond.discard(self.rng.choice(sorted(cond, key=str)))
        if self.rng.random() < 0.3:  # cambiar de opinión hacia lo visto
            pred = self.rng.choice(clases_recientes)
        return Trader(frozenset(cond), pred, 0.0)

    # ---------- interfaz común del banco de pruebas ----------

    def elegir_consulta(self):
        return None  # el mercado no dirige consultas: su exploración es demográfica

    def auditar(self, doc, prov):
        activos = sorted(self._activos(self._rasgos(doc, prov)),
                         key=lambda t: -t.capital)[:5]
        lineas = [f"Mercado para {doc} (fuente {prov}): "
                  f"{len(self.poblacion)} traders vivos"]
        for t in activos:
            lineas.append(f"  {set(t.cond)} → {t.pred}  capital {t.capital:.2f}")
        return "\n".join(lineas)
