#!/usr/bin/env python3
"""
Narratium — Snapshot/Backup de la base de datos
Crea copias con timestamp, lista y restaura snapshots.
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime


def get_snapshots_dir(db_path):
    return os.path.join(os.path.dirname(db_path), "snapshots")


def create_snapshot(db_path):
    """Crea snapshot de la DB con timestamp."""
    snapshots_dir = get_snapshots_dir(db_path)
    os.makedirs(snapshots_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    db_name = os.path.splitext(os.path.basename(db_path))[0]
    snapshot_name = f"{db_name}_{timestamp}.db"
    snapshot_path = os.path.join(snapshots_dir, snapshot_name)

    shutil.copy2(db_path, snapshot_path)

    size_bytes = os.path.getsize(snapshot_path)
    size_kb = round(size_bytes / 1024, 1)

    return {
        "status": "success",
        "action": "create",
        "snapshot": snapshot_name,
        "path": snapshot_path,
        "size_kb": size_kb,
        "timestamp": timestamp
    }


def list_snapshots(db_path):
    """Lista snapshots existentes."""
    snapshots_dir = get_snapshots_dir(db_path)

    if not os.path.exists(snapshots_dir):
        return {"status": "success", "action": "list", "snapshots": [], "total": 0}

    snapshots = []
    for f in sorted(os.listdir(snapshots_dir)):
        if f.endswith(".db"):
            fpath = os.path.join(snapshots_dir, f)
            size_kb = round(os.path.getsize(fpath) / 1024, 1)
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%d %H:%M:%S")
            snapshots.append({
                "name": f,
                "size_kb": size_kb,
                "created": mtime
            })

    return {
        "status": "success",
        "action": "list",
        "snapshots": snapshots,
        "total": len(snapshots)
    }


def restore_snapshot(db_path, timestamp):
    """Restaura un snapshot. Guarda el actual como .bak primero."""
    snapshots_dir = get_snapshots_dir(db_path)
    db_name = os.path.splitext(os.path.basename(db_path))[0]

    # Buscar snapshot que coincida con timestamp
    matching = None
    for f in os.listdir(snapshots_dir):
        if f.endswith(".db") and timestamp in f:
            matching = f
            break

    if not matching:
        return {"status": "error", "message": f"No se encontró snapshot con timestamp '{timestamp}'"}

    snapshot_path = os.path.join(snapshots_dir, matching)

    # Backup del actual antes de restaurar
    bak_timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    bak_path = f"{db_path}.pre_restore_{bak_timestamp}.bak"
    shutil.copy2(db_path, bak_path)

    # Restaurar
    shutil.copy2(snapshot_path, db_path)

    return {
        "status": "success",
        "action": "restore",
        "restored_from": matching,
        "backup_of_current": os.path.basename(bak_path),
        "message": f"DB restaurada desde {matching}. Backup previo en {os.path.basename(bak_path)}"
    }


def main():
    parser = argparse.ArgumentParser(description="Snapshots de la base de datos Narratium")
    parser.add_argument("--db", required=True, help="Ruta a la base de datos SQLite")
    parser.add_argument("--list", action="store_true", help="Listar snapshots existentes")
    parser.add_argument("--restore", metavar="TIMESTAMP", help="Restaurar snapshot por timestamp")

    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(json.dumps({"status": "error", "message": f"DB no encontrada: {args.db}"}))
        sys.exit(1)

    if args.list:
        result = list_snapshots(args.db)
    elif args.restore:
        result = restore_snapshot(args.db, args.restore)
    else:
        result = create_snapshot(args.db)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
