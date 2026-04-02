#!/usr/bin/env python3
"""
Narratium — Inicializar proyecto nuevo
Crea un proyecto en la DB y opcionalmente carga reglas narrativas por defecto.
"""

import argparse
import json
import sqlite3
import os
import sys
from datetime import datetime


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


def create_project(db_path: str, name: str, genre: str = None, description: str = None,
                   target_words: int = None, voice: str = "third_person",
                   skip_defaults: bool = False) -> str:
    """Crea un proyecto nuevo y retorna su ID."""
    
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cursor = conn.cursor()
    
    # Crear proyecto
    cursor.execute("""
        INSERT INTO projects (name, description, genre, target_word_count, narrative_voice)
        VALUES (?, ?, ?, ?, ?)
    """, (name, description, genre, target_words, voice))
    
    project_id = cursor.execute("SELECT id FROM projects ORDER BY created_at DESC LIMIT 1").fetchone()[0]
    
    # Cargar reglas por defecto
    if not skip_defaults:
        for category, rule, priority in DEFAULT_RULES:
            cursor.execute("""
                INSERT INTO narrative_rules (project_id, category, rule, priority)
                VALUES (?, ?, ?, ?)
            """, (project_id, category, rule, priority))
    
    conn.commit()
    
    result = {
        "status": "success",
        "project_id": project_id,
        "name": name,
        "genre": genre,
        "rules_loaded": len(DEFAULT_RULES) if not skip_defaults else 0,
        "message": f"Proyecto '{name}' creado con ID {project_id}"
    }
    
    conn.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return project_id


def main():
    parser = argparse.ArgumentParser(description="Crear proyecto Narratium")
    parser.add_argument("--name", required=True, help="Nombre de la novela")
    parser.add_argument("--genre", default=None, help="Género: thriller, fantasy, scifi, literary, horror, mystery, romance")
    parser.add_argument("--description", default=None, help="Descripción general de la novela")
    parser.add_argument("--target-words", type=int, default=None, help="Objetivo de palabras")
    parser.add_argument("--voice", default="third_person", help="Voz narrativa: first_person, third_person, third_omniscient")
    parser.add_argument("--skip-defaults", action="store_true", help="No cargar reglas narrativas por defecto")
    parser.add_argument("--db", required=True, help="Ruta a la base de datos SQLite")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.db):
        print(json.dumps({"status": "error", "message": f"DB no encontrada: {args.db}. Ejecuta primero: sqlite3 {args.db} < db/schema.sql"}))
        sys.exit(1)
    
    create_project(
        db_path=args.db,
        name=args.name,
        genre=args.genre,
        description=args.description,
        target_words=args.target_words,
        voice=args.voice,
        skip_defaults=args.skip_defaults
    )


if __name__ == "__main__":
    main()
