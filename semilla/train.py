"""Entrenamiento de Semilla.

Bucle clásico: batch aleatorio -> forward -> backward -> clip -> step, con
warmup + decaimiento coseno del learning rate, evaluación periódica en el set
de validación y checkpoints (best.pt = mejor val loss, last.pt = último paso).

El checkpoint guarda también la config y el vocabulario, así que generate.py
solo necesita el .pt para funcionar.

Uso:
    python train.py --preset nano --steps 2000
    python train.py --preset micro --steps 20000 --device cuda
"""
import argparse
import json
import math
import time
from pathlib import Path

import torch

from config import PRESETS
from model import GPT
from tokenizer import CharTokenizer


def pick_device(arg):
    if arg != "auto":
        return arg
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def get_batch(data, block_size, batch_size, device):
    ix = torch.randint(len(data) - block_size - 1, (batch_size,))
    x = torch.stack([data[i:i + block_size] for i in ix]).long()
    y = torch.stack([data[i + 1:i + 1 + block_size] for i in ix]).long()
    return x.to(device), y.to(device)


@torch.no_grad()
def estimate_loss(model, splits, block_size, batch_size, device, iters=20):
    model.eval()
    out = {}
    for name, data in splits.items():
        losses = torch.zeros(iters)
        for i in range(iters):
            x, y = get_batch(data, block_size, batch_size, device)
            _, loss = model(x, y)
            losses[i] = loss.item()
        out[name] = losses.mean().item()
    model.train()
    return out


def lr_at(step, max_lr, min_lr, warmup, total):
    if step < warmup:
        return max_lr * (step + 1) / warmup
    if step >= total:
        return min_lr
    ratio = (step - warmup) / max(1, total - warmup)
    return min_lr + 0.5 * (max_lr - min_lr) * (1 + math.cos(math.pi * ratio))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset", default="nano", choices=sorted(PRESETS))
    ap.add_argument("--data", default="data")
    ap.add_argument("--out", default="checkpoints")
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--min-lr", type=float, default=3e-5)
    ap.add_argument("--warmup", type=int, default=100)
    ap.add_argument("--eval-every", type=int, default=250)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--resume", action="store_true",
                    help="continuar desde checkpoints/last.pt")
    args = ap.parse_args()

    device = pick_device(args.device)
    data_dir, out_dir = Path(args.data), Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    train_data = torch.load(data_dir / "train.pt")
    val_data = torch.load(data_dir / "val.pt")
    tok = CharTokenizer.load(data_dir / "tokenizer.json")

    config = PRESETS[args.preset]
    config.vocab_size = tok.vocab_size

    model = GPT(config).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=args.lr, betas=(0.9, 0.95), weight_decay=0.1
    )

    start_step, best_val = 0, float("inf")
    if args.resume:
        ckpt = torch.load(out_dir / "last.pt", map_location=device)
        model.load_state_dict(ckpt["model"])
        optimizer.load_state_dict(ckpt["optimizer"])
        start_step = ckpt["step"] + 1
        best_val = ckpt.get("best_val", best_val)
        print(f"Reanudando desde el paso {start_step}")

    print(f"Modelo '{args.preset}': {model.num_params()/1e6:.2f}M parámetros | "
          f"device={device} | vocab={tok.vocab_size}")

    def save(path, step):
        torch.save({
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "config": config.to_dict(),
            "tokenizer": {"type": "char", "chars": tok.chars},
            "step": step,
            "best_val": best_val,
            "preset": args.preset,
        }, path)

    model.train()
    t0 = time.time()
    for step in range(start_step, args.steps):
        lr = lr_at(step, args.lr, args.min_lr, args.warmup, args.steps)
        for group in optimizer.param_groups:
            group["lr"] = lr

        x, y = get_batch(train_data, config.block_size, args.batch_size, device)
        _, loss = model(x, y)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        last_step = step == args.steps - 1
        if step % args.eval_every == 0 or last_step:
            losses = estimate_loss(
                model, {"train": train_data, "val": val_data},
                config.block_size, args.batch_size, device,
            )
            dt = time.time() - t0
            print(f"paso {step:6d} | loss train {losses['train']:.4f} | "
                  f"loss val {losses['val']:.4f} | lr {lr:.2e} | {dt:.0f}s")
            if losses["val"] < best_val:
                best_val = losses["val"]
                save(out_dir / "best.pt", step)
            save(out_dir / "last.pt", step)

    print(f"Entrenamiento terminado. Mejor loss de validación: {best_val:.4f}")
    print(f"Checkpoints en {out_dir}/ — pruébalo: python generate.py")


if __name__ == "__main__":
    main()
