"""Mundo simulado para la v0 de la Tesis Pacioli.

Una empresa genera transacciones. Reglas ocultas asignan la cuenta contable
según el tipo de transacción, con excepciones por proveedor. Cada cierto tiempo
ocurre una "reforma": la regla de algunos tipos cambia sin avisar.

Mundo deliberadamente pre-asentado (cada transacción llega ya itemizada como
clave (tipo, proveedor)): la v0 prueba el bucle de aprendizaje, no la
percepción. Ver TESIS.md, "problema del asiento".
"""
import random

TIPOS = ["venta", "compra", "nomina", "suministro", "alquiler",
         "servicio_prof", "publicidad", "seguro"]
CUENTAS = ["700", "600", "640", "628", "621", "623", "627", "625"]

N_PROVEEDORES = 30        # proveedores del flujo de entrenamiento
PROVEEDORES_NUEVOS = 5    # solo aparecen en evaluación (miden transferencia)


class Mundo:
    def __init__(self, seed=0, p_excepcion=0.15):
        self.rng = random.Random(seed)
        self.regla_tipo = dict(zip(TIPOS, CUENTAS))
        self.proveedores = list(range(N_PROVEEDORES))
        self.proveedores_nuevos = list(range(N_PROVEEDORES,
                                             N_PROVEEDORES + PROVEEDORES_NUEVOS))
        # Excepciones: algunos (tipo, proveedor) no siguen la regla general.
        # Los proveedores de evaluación no tienen excepciones (miden regla pura).
        self.excepciones = {}
        for p in self.proveedores:
            if self.rng.random() < p_excepcion:
                t = self.rng.choice(TIPOS)
                otras = [c for c in CUENTAS if c != self.regla_tipo[t]]
                self.excepciones[(t, p)] = self.rng.choice(otras)

    def cuenta_de(self, clave):
        tipo, prov = clave
        return self.excepciones.get(clave, self.regla_tipo[tipo])

    def transaccion(self, tipo=None, proveedor=None):
        """Devuelve (clave, cuenta_correcta). Sin argumentos: aleatoria."""
        t = tipo if tipo is not None else self.rng.choice(TIPOS)
        p = proveedor if proveedor is not None else self.rng.choice(self.proveedores)
        clave = (t, p)
        return clave, self.cuenta_de(clave)

    def reforma(self, n_tipos=2):
        """Cambia la regla de n_tipos tipos. Devuelve los tipos cambiados."""
        cambiados = self.rng.sample(TIPOS, n_tipos)
        for t in cambiados:
            otras = [c for c in CUENTAS if c != self.regla_tipo[t]]
            self.regla_tipo[t] = self.rng.choice(otras)
        return cambiados
