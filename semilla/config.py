"""Configuración de arquitectura de Semilla.

Escalar el modelo es elegir otro preset (o escribir el tuyo). El código de
model.py y train.py no cambia entre un modelo de 1M y uno de 1B de parámetros:
solo cambian estos números y el hardware que los soporta.
"""
from dataclasses import dataclass, asdict


@dataclass
class GPTConfig:
    block_size: int = 256   # longitud máxima de contexto (en tokens)
    vocab_size: int = 256   # lo fija el tokenizador al preparar los datos
    n_layer: int = 4        # número de bloques transformer
    n_head: int = 4         # cabezas de atención por bloque
    n_embd: int = 128       # dimensión de los embeddings
    dropout: float = 0.1    # con corpus pequeño, el dropout es tu amigo
    bias: bool = False      # sin bias en Linear/LayerNorm: más simple e igual de bueno

    def to_dict(self):
        return asdict(self)


# Presets: parámetros aproximados con vocabulario de caracteres (~100-200 símbolos).
# Con tokenizador BPE (Fase 1) el conteo sube por la tabla de embeddings.
PRESETS = {
    # ~1M params — entrena en CPU de portátil en minutos. Para validar el pipeline.
    "nano": GPTConfig(n_layer=4, n_head=4, n_embd=128, block_size=256, dropout=0.1),

    # ~10M params — CPU paciente (horas) o cualquier GPU (minutos).
    "micro": GPTConfig(n_layer=6, n_head=6, n_embd=384, block_size=256, dropout=0.2),

    # ~30M params — GPU de consumo. Primer modelo con corpus serio.
    "mini": GPTConfig(n_layer=8, n_head=8, n_embd=512, block_size=512, dropout=0.1),

    # ~110M params — escala GPT-2 small. Fase 2.
    "base": GPTConfig(n_layer=12, n_head=12, n_embd=768, block_size=1024, dropout=0.1),
}
