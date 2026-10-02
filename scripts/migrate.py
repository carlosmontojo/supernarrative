#!/usr/bin/env python3
"""
SuperNarrative — Migración de bases de datos v1 → v2

Qué corrige:
  - En v0.1, update.py guardaba IDs hex de capítulo en las columnas
    *_in_chapter (planted_in_chapter, learned_in_chapter, etc.), rompiendo
    el envejecimiento de pistas y los ordenamientos. v2 estandariza: esas
    columnas guardan el NÚMERO de capítulo.
  - Añade el PRAGMA user_version = 2.

Es idempotente y hace backup antes de tocar nada.

Uso:
  python3 supernarrative.py migrate            # migra la DB detectada
  python3 scripts/migrate.py --db db/mi.db     # o explícita
"""

import argparse
import json
import sqlite3
import sys
import os

# Columnas que en v2 guardan números de capítulo: (tabla, columna)
CHAPTER_NUMBER_COLUMNS = [
    ("story_facts", "established_in_chapter"),
    ("story_facts", "revealed_to_reader_in"),
    ("knowledge_states", "learned_in_chapter"),
    ("plot_threads", "planted_in_chapter"),
    ("plot_threads", "target_resolution_chapter"),
    ("plot_threads", "resolved_in_chapter"),
    ("clues", "planted_in_chapter"),
    ("clues", "resolved_in_chapter"),
    ("characters", "introduced_in_chapter"),
    ("character_relationships", "established_in_chapter"),
    ("objects", "introduced_in_chapter"),
]


def migrate(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    version = conn.execute("PRAGMA user_version").fetchone()[0]
    report = {"status": "success", "from_version": version, "fixes": []}

    # Backup de seguridad con la API de SQLite
    bak_path = db_path + ".pre_migrate.bak"
    bak = sqlite3.connect(bak_path)
    with bak:
        conn.backup(bak)
    bak.close()
    report["backup"] = bak_path

    # Mapa chapters.id -> chapter_number
    id_to_num = {r["id"]: r["chapter_number"]
                 for r in conn.execute("SELECT id, chapter_number FROM chapters")}

    total_fixed = 0
    for table, column in CHAPTER_NUMBER_COLUMNS:
        try:
            rows = conn.execute(
                f"SELECT rowid, {column} AS val FROM {table} WHERE {column} IS NOT NULL"
            ).fetchall()
        except sqlite3.OperationalError:
            continue  # tabla/columna ausente en schemas muy antiguos
        fixed = 0
        for row in rows:
            val = row["val"]
            if isinstance(val, int) or (isinstance(val, str) and val.isdigit()):
                continue  # ya es un número
            if val in id_to_num:
                conn.execute(f"UPDATE {table} SET {column} = ? WHERE rowid = ?",
                             (id_to_num[val], row["rowid"]))
                fixed += 1
        if fixed:
            report["fixes"].append(f"{table}.{column}: {fixed} IDs convertidos a números")
            total_fixed += fixed

    # reinforced_in_chapters: arrays JSON de ids -> números
    try:
        rows = conn.execute(
            "SELECT rowid, reinforced_in_chapters AS val FROM clues "
            "WHERE reinforced_in_chapters IS NOT NULL"
        ).fetchall()
        fixed = 0
        for row in rows:
            try:
                arr = json.loads(row["val"])
            except (json.JSONDecodeError, TypeError):
                continue
            new_arr, changed = [], False
            for item in arr:
                if item in id_to_num:
                    new_arr.append(id_to_num[item])
                    changed = True
                else:
                    new_arr.append(item)
            if changed:
                conn.execute("UPDATE clues SET reinforced_in_chapters = ? WHERE rowid = ?",
                             (json.dumps(new_arr), row["rowid"]))
                fixed += 1
        if fixed:
            report["fixes"].append(f"clues.reinforced_in_chapters: {fixed} arrays convertidos")
            total_fixed += fixed
    except sqlite3.OperationalError:
        pass

    # Columnas nuevas de v0.3 (sistema de estilo)
    existing = {r[1] for r in conn.execute("PRAGMA table_info(projects)")}
    for col in ("style_anchor", "style_anchor_metrics"):
        if col not in existing:
            conn.execute(f"ALTER TABLE projects ADD COLUMN {col} TEXT")
            report["fixes"].append(f"projects.{col}: columna añadida")

    conn.execute("PRAGMA user_version = 2")
    conn.commit()
    conn.close()

    report["to_version"] = 2
    report["total_values_fixed"] = total_fixed
    if not report["fixes"]:
        report["message"] = "Nada que migrar: la DB ya estaba en formato v2."
    return report


def main():
    parser = argparse.ArgumentParser(description="Migrar DB SuperNarrative v1 → v2")
    parser.add_argument("--db", required=True, help="Ruta a la base de datos SQLite")
    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(json.dumps({"status": "error", "message": f"DB no encontrada: {args.db}"}))
        sys.exit(1)

    print(json.dumps(migrate(args.db), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
