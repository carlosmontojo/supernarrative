"""Tokenizador a nivel de carácter.

v0 deliberadamente simple: cada carácter del corpus es un token. Cero
dependencias, cero magia, perfecto para validar el pipeline y sorprendentemente
digno para español (acentos y ñ incluidos, porque el vocabulario sale del
propio corpus).

Fase 1 del roadmap: sustituir por BPE propio manteniendo esta misma interfaz
(encode/decode/save/load y vocab_size); nada más del pipeline tiene que cambiar.
"""
import json


class CharTokenizer:
    def __init__(self, chars):
        self.chars = list(chars)
        self.stoi = {c: i for i, c in enumerate(self.chars)}
        self.itos = {i: c for i, c in enumerate(self.chars)}

    @property
    def vocab_size(self):
        return len(self.chars)

    @classmethod
    def from_text(cls, text):
        return cls(sorted(set(text)))

    def encode(self, text):
        # Los caracteres fuera del vocabulario se ignoran (p. ej. un emoji en el
        # prompt que no existía en el corpus). Con BPE esto desaparece.
        return [self.stoi[c] for c in text if c in self.stoi]

    def decode(self, ids):
        return "".join(self.itos[i] for i in ids)

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"type": "char", "chars": self.chars}, f, ensure_ascii=False)

    @classmethod
    def load(cls, path):
        with open(path, encoding="utf-8") as f:
            meta = json.load(f)
        assert meta["type"] == "char", f"tokenizador desconocido: {meta['type']}"
        return cls(meta["chars"])
