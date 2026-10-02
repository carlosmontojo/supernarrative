#!/usr/bin/env python3
"""
SuperNarrative — Helpers compartidos entre scripts.

Convención de referencias a capítulos (v0.2):
  - Columnas llamadas `chapter_id` almacenan chapters.id (clave hex).
  - Columnas llamadas `*_in_chapter` / `*_chapter` almacenan el NÚMERO de
    capítulo (entero), que es estable y legible para el autor.
Los scripts anteriores a v0.2 mezclaban ambas; scripts/migrate.py corrige
bases de datos antiguas.
"""

import json
import os
import secrets
import sqlite3
import sys


def gen_id() -> str:
    """ID hex de 16 caracteres, generado en Python para evitar el patrón
    frágil de SELECT-después-de-INSERT por nombre."""
    return secrets.token_hex(8)


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def fail(message: str, **extra):
    out = {"status": "error", "message": message}
    out.update(extra)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(1)


def require_db(db_path: str):
    if not os.path.exists(db_path):
        fail(f"DB no encontrada: {db_path}. Ejecuta primero: "
             f"python3 supernarrative.py init --name \"Mi Novela\"")


def get_project_id(conn, project_id: str = None) -> str:
    if project_id:
        row = conn.execute("SELECT id FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not row:
            fail(f"Proyecto no encontrado: {project_id}")
        return project_id
    row = conn.execute(
        "SELECT id FROM projects ORDER BY updated_at DESC, created_at DESC LIMIT 1"
    ).fetchone()
    if not row:
        fail("No hay proyectos en la DB. Crea uno con: supernarrative init --name \"Mi Novela\"")
    return row["id"]


def resolve_character(conn, project_id: str, name: str):
    """Resuelve un personaje por nombre, full_name o alias (insensible a
    mayúsculas). Devuelve la fila o None — el llamador decide qué hacer y
    DEBE reportar los no resueltos, nunca descartarlos en silencio."""
    if not name:
        return None
    row = conn.execute(
        """SELECT * FROM characters WHERE project_id = ?
           AND (name = ? COLLATE NOCASE OR full_name = ? COLLATE NOCASE)""",
        (project_id, name, name),
    ).fetchone()
    if row:
        return row
    # Alias (JSON array) o coincidencia parcial inequívoca
    rows = conn.execute(
        """SELECT * FROM characters WHERE project_id = ?
           AND (aliases LIKE ? OR name LIKE ? COLLATE NOCASE
                OR full_name LIKE ? COLLATE NOCASE)""",
        (project_id, f'%"{name}"%', f"%{name}%", f"%{name}%"),
    ).fetchall()
    return rows[0] if len(rows) == 1 else None


def resolve_thread(conn, project_id: str, name: str):
    if not name:
        return None
    row = conn.execute(
        "SELECT * FROM plot_threads WHERE project_id = ? AND name = ? COLLATE NOCASE",
        (project_id, name),
    ).fetchone()
    if row:
        return row
    rows = conn.execute(
        "SELECT * FROM plot_threads WHERE project_id = ? AND name LIKE ? COLLATE NOCASE",
        (project_id, f"%{name}%"),
    ).fetchall()
    return rows[0] if len(rows) == 1 else None


def get_or_create_location(conn, project_id: str, name: str) -> str:
    row = conn.execute(
        "SELECT id FROM locations WHERE project_id = ? AND name = ? COLLATE NOCASE",
        (project_id, name),
    ).fetchone()
    if row:
        return row["id"]
    loc_id = gen_id()
    conn.execute(
        "INSERT INTO locations (id, project_id, name) VALUES (?, ?, ?)",
        (loc_id, project_id, name),
    )
    return loc_id


def get_or_create_fact(conn, project_id: str, description: str,
                       category: str = "event", chapter_number: int = None) -> str:
    row = conn.execute(
        "SELECT id FROM story_facts WHERE project_id = ? AND description = ?",
        (project_id, description),
    ).fetchone()
    if row:
        return row["id"]
    fact_id = gen_id()
    conn.execute(
        """INSERT INTO story_facts (id, project_id, category, description, established_in_chapter)
           VALUES (?, ?, ?, ?, ?)""",
        (fact_id, project_id, category, description, chapter_number),
    )
    return fact_id


def get_or_create_chapter(conn, project_id: str, chapter_number: int,
                          file_path: str = None) -> str:
    row = conn.execute(
        "SELECT id FROM chapters WHERE project_id = ? AND chapter_number = ?",
        (project_id, chapter_number),
    ).fetchone()
    if row:
        return row["id"]
    ch_id = gen_id()
    conn.execute(
        """INSERT INTO chapters (id, project_id, chapter_number, chapter_order, status, file_path)
           VALUES (?, ?, ?, ?, 'draft', ?)""",
        (ch_id, project_id, chapter_number, chapter_number, file_path),
    )
    return ch_id


def count_words_in_file(path: str):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return len(f.read().split())
    except OSError:
        return None
