"""Prepara el dataset: corpus/ -> tokenizador + tensores de entrenamiento.

Lee todos los .txt y .md de corpus/ (recursivamente), construye el vocabulario,
codifica el texto completo y lo parte en train (90%) / val (10%). El resultado
queda en data/ listo para train.py.

Uso:
    python prepare.py [--corpus corpus] [--out data]
"""
import argparse
from pathlib import Path

import torch

from tokenizer import CharTokenizer


def load_corpus(corpus_dir: Path) -> str:
    files = sorted(
        p for p in corpus_dir.rglob("*")
        if p.suffix.lower() in (".txt", ".md") and p.name != "README.md"
    )
    if not files:
        raise SystemExit(
            f"No hay ficheros .txt/.md en {corpus_dir}/ — pon ahí tus textos "
            "(o descarga el ejemplo, ver corpus/README.md)."
        )
    parts = []
    for p in files:
        text = p.read_text(encoding="utf-8", errors="replace")
        parts.append(text)
        print(f"  {p.relative_to(corpus_dir)}: {len(text):,} caracteres")
    # Separador entre documentos: doble salto de línea
    return "\n\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="corpus", help="directorio con .txt/.md")
    ap.add_argument("--out", default="data", help="directorio de salida")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Leyendo corpus de {args.corpus}/ ...")
    text = load_corpus(Path(args.corpus))
    print(f"Corpus total: {len(text):,} caracteres")

    tok = CharTokenizer.from_text(text)
    print(f"Vocabulario: {tok.vocab_size} símbolos")

    ids = torch.tensor(tok.encode(text), dtype=torch.int32)
    n = int(len(ids) * 0.9)
    train_ids, val_ids = ids[:n], ids[n:]
    print(f"Train: {len(train_ids):,} tokens | Val: {len(val_ids):,} tokens")

    torch.save(train_ids, out_dir / "train.pt")
    torch.save(val_ids, out_dir / "val.pt")
    tok.save(out_dir / "tokenizer.json")
    print(f"Listo: {out_dir}/train.pt, {out_dir}/val.pt, {out_dir}/tokenizer.json")


if __name__ == "__main__":
    main()
