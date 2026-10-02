#!/usr/bin/env python3
"""
SuperNarrative — Inicializar proyecto nuevo
Crea la base de datos si no existe (aplicando db/schema.sql automáticamente),
crea el proyecto y carga reglas narrativas por defecto.
"""

import argparse
import json
import os
import sqlite3
import sys

from _common import connect, fail, gen_id

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "..", "db", "schema.sql")

DEFAULT_RULES = [
    ("forbidden", "Nunca forzar exposición a través de diálogo inverosímil. Ningún personaje revela información clave a un desconocido sin motivación fuerte.", 10),
    ("structure", "La información se gana con investigación, observación o deducción. Nunca se regala.", 10),
    ("style", "Las pistas deben ser extremadamente sutiles — invisibles en primera lectura, obvias en segunda.", 9),
    ("voice", "Antes de cada interacción preguntarse: ¿esta persona realmente diría esto a alguien que acaba de conocer? Si no, reescribir.", 10),
    ("structure", "Respetar SIEMPRE la matriz epistémica. Un personaje NUNCA actúa basándose en información que no tiene.", 10),
    ("structure", "Cada capítulo cierra con hook: pregunta sin responder, revelación parcial, decisión pendiente, o peligro inminente.", 8),
    ("rhythm", "No más de 2-3 capítulos consecutivos del mismo tipo de escena. Variar el ritmo.", 7),
    ("structure", "Cada pregunta respondida debe abrir al menos una nueva. No resolver sin abrir.", 8),
    ("style", "Monólogo interno profundo del protagonista. El lector debe sentir lo que siente el personaje.", 7),
    ("forbidden", "No usar coincidencias convenientes para avanzar la trama. Si algo parece demasiado conveniente, lo es.", 9),
]


def ensure_database(db_path: str):
    """Crea la DB desde el schema si no existe (en v0.1 había que ejecutar
    sqlite3 a mano antes de poder hacer nada)."""
    if os.path.exists(db_path):
        return False
    schema_file = os.path.normpath(SCHEMA_PATH)
    if not os.path.exists(schema_file):
        fail(f"No se encontró el schema: {schema_file}")
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    with open(schema_file, encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    return True


def create_project(db_path, name, genre=None, description=None,
                   target_words=None, voice="third_person", skip_defaults=False):
    db_created = ensure_database(db_path)

    conn = connect(db_path)
    project_id = gen_id()
    conn.execute("""
        INSERT INTO projects (id, name, description, genre, target_word_count, narrative_voice)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (project_id, name, description, genre, target_words, voice))

    if not skip_defaults:
        for category, rule, priority in DEFAULT_RULES:
            conn.execute("""
                INSERT INTO narrative_rules (id, project_id, category, rule, priority)
                VALUES (?, ?, ?, ?, ?)
            """, (gen_id(), project_id, category, rule, priority))

    conn.commit()
    conn.close()

    result = {
        "status": "success",
        "project_id": project_id,
        "name": name,
        "genre": genre,
        "database": db_path,
        "database_created": db_created,
        "rules_loaded": 0 if skip_defaults else len(DEFAULT_RULES),
        "message": f"Proyecto '{name}' creado con ID {project_id}",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return project_id


def main():
    parser = argparse.ArgumentParser(description="Crear proyecto SuperNarrative")
    parser.add_argument("--name", required=True, help="Nombre de la novela")
    parser.add_argument("--genre", default=None, help="Género: thriller, fantasy, scifi, literary, horror, mystery, romance")
    parser.add_argument("--description", default=None, help="Descripción general de la novela")
    parser.add_argument("--target-words", type=int, default=None, help="Objetivo de palabras")
    parser.add_argument("--voice", default="third_person", help="Voz narrativa: first_person, third_person, third_omniscient")
    parser.add_argument("--skip-defaults", action="store_true", help="No cargar reglas narrativas por defecto")
    parser.add_argument("--db", required=True, help="Ruta a la base de datos SQLite")
    args = parser.parse_args()

    create_project(db_path=args.db, name=args.name, genre=args.genre,
                   description=args.description, target_words=args.target_words,
                   voice=args.voice, skip_defaults=args.skip_defaults)


if __name__ == "__main__":
    main()
