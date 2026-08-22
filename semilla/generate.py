"""Generación de texto desde un checkpoint de Semilla.

Uso:
    python generate.py --prompt "En un lugar de" --tokens 300
    python generate.py --checkpoint checkpoints/best.pt --temperature 0.8 --top-k 40
"""
import argparse
from pathlib import Path

import torch

from config import GPTConfig
from model import GPT
from tokenizer import CharTokenizer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default="checkpoints/best.pt")
    ap.add_argument("--prompt", default="\n")
    ap.add_argument("--tokens", type=int, default=300)
    ap.add_argument("--temperature", type=float, default=0.9)
    ap.add_argument("--top-k", type=int, default=50)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()

    if args.seed is not None:
        torch.manual_seed(args.seed)

    ckpt = torch.load(Path(args.checkpoint), map_location=args.device)
    config = GPTConfig(**ckpt["config"])
    tok = CharTokenizer(ckpt["tokenizer"]["chars"])

    model = GPT(config).to(args.device)
    model.load_state_dict(ckpt["model"])

    prompt = args.prompt if args.prompt else "\n"
    ids = tok.encode(prompt) or tok.encode("\n")
    x = torch.tensor([ids], dtype=torch.long, device=args.device)

    y = model.generate(
        x, max_new_tokens=args.tokens,
        temperature=args.temperature, top_k=args.top_k,
    )
    print(tok.decode(y[0].tolist()))


if __name__ == "__main__":
    main()
