"""Mundo v1 de la Tesis Pacioli: estocástico y con percepción ruidosa.

Diferencias con v0 (que queda congelado como registro):
1. Tipos ruidosos: en algunos tipos la cuenta correcta se sortea (p. ej. 70/30).
   La calibración perfecta ya no es la confianza máxima.
2. El agente no ve la clave limpia: ve un DOCUMENTO — bolsa de tokens (dos del
   tipo, uno común a todo) — y el proveedor. Con probabilidad p_error_doc un
   token propio se sustituye por uno de otro tipo (ambigüedad de percepción).
   Aprender qué tokens son asentables ES el problema del asiento en miniatura.
"""
import random

TIPOS = ["venta", "compra", "nomina", "suministro", "alquiler",
         "servicio_prof", "publicidad", "seguro"]
CUENTAS = ["700", "600", "640", "628", "621", "623", "627", "625"]
TOKENS_COMUNES = ["fra", "pago", "ref", "sl"]

N_PROVEEDORES = 30
PROVEEDORES_NUEVOS = 5


class MundoV1:
    def __init__(self, seed=0, p_excepcion=0.15, n_tipos_ruidosos=2,
                 p_alt=0.3, p_error_doc=0.0):
        self.rng = random.Random(seed)
        self.regla_tipo = dict(zip(TIPOS, CUENTAS))
        self.p_alt = p_alt
        self.p_error_doc = p_error_doc
        self.proveedores = list(range(N_PROVEEDORES))
        self.proveedores_nuevos = list(range(N_PROVEEDORES,
                                             N_PROVEEDORES + PROVEEDORES_NUEVOS))
        self.excepciones = {}
        for p in self.proveedores:
            if self.rng.random() < p_excepcion:
                t = self.rng.choice(TIPOS)
                otras = [c for c in CUENTAS if c != self.regla_tipo[t]]
                self.excepciones[(t, p)] = self.rng.choice(otras)
        # Tipos con incertidumbre aleatoria real
        self.ruido = {}
        for t in self.rng.sample(TIPOS, n_tipos_ruidosos):
            otras = [c for c in CUENTAS if c != self.regla_tipo[t]]
            self.ruido[t] = self.rng.choice(otras)
        self.tokens_tipo = {t: [f"{t}#a", f"{t}#b", f"{t}#c"] for t in TIPOS}

    # ---------- verdad (solo para evaluación) ----------

    def dist_de(self, clave):
        t, _ = clave
        if clave in self.excepciones:
            return {self.excepciones[clave]: 1.0}
        base = self.regla_tipo[t]
        if t in self.ruido:
            return {base: 1.0 - self.p_alt, self.ruido[t]: self.p_alt}
        return {base: 1.0}

    def modal_de(self, clave):
        d = self.dist_de(clave)
        return max(d, key=d.get)

    # ---------- generación ----------

    def documento(self, tipo, canonico=False):
        if canonico:  # para sondas de evaluación: doc fijo y sin error
            return self.tokens_tipo[tipo][:2] + [TOKENS_COMUNES[0]]
        toks = self.rng.sample(self.tokens_tipo[tipo], 2) + [self.rng.choice(TOKENS_COMUNES)]
        if self.rng.random() < self.p_error_doc:
            otro = self.rng.choice([t for t in TIPOS if t != tipo])
            toks[0] = self.rng.choice(self.tokens_tipo[otro])
        self.rng.shuffle(toks)
        return toks

    def transaccion(self, tipo=None, proveedor=None):
        """Devuelve (documento, proveedor, cuenta_observada, clave_real).
        La clave_real es solo para métricas: el agente no debe usarla."""
        t = tipo if tipo is not None else self.rng.choice(TIPOS)
        p = proveedor if proveedor is not None else self.rng.choice(self.proveedores)
        clave = (t, p)
        dist = self.dist_de(clave)
        r, acum, cuenta = self.rng.random(), 0.0, None
        for c, prob in dist.items():
            acum += prob
            if r <= acum:
                cuenta = c
                break
        return self.documento(t), p, cuenta or c, clave

    def transaccion_por_token(self, token):
        """Consulta dirigida: 'búscame otro documento como este'."""
        for t, toks in self.tokens_tipo.items():
            if token in toks:
                return self.transaccion(tipo=t)
        return self.transaccion()

    def reforma(self, n_tipos=2):
        limpios = [t for t in TIPOS if t not in self.ruido]
        cambiados = self.rng.sample(limpios, n_tipos)
        for t in cambiados:
            otras = [c for c in CUENTAS if c != self.regla_tipo[t]]
            self.regla_tipo[t] = self.rng.choice(otras)
        return cambiados
