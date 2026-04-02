#!/usr/bin/env python3
"""
Narratium — Aplicar actualizaciones confirmadas
Toma el análisis pendiente y actualiza todas las capas de memoria.
"""

import argparse
import json
import sqlite3
import sys
import os
from datetime import datetime


def get_pending_analysis(conn, project_id: str, chapter_number: int) -> dict:
    """Recupera el análisis pendiente de un capítulo."""
    row = conn.execute("""
        SELECT an.content, ch.id as chapter_id
        FROM author_notes an
        JOIN chapters ch ON an.chapter_id = ch.id
        WHERE an.project_id = ? AND ch.chapter_number = ? AND an.note_type = 'pending_analysis' AND an.resolved = 0
        ORDER BY an.created_at DESC LIMIT 1
    """, (project_id, chapter_number)).fetchone()
    
    if not row:
        return None
    
    return {"analysis": json.loads(row[0]), "chapter_id": row[1]}


def apply_analysis(db_path: str, project_id: str, chapter_number: int) -> dict:
    """Aplica el análisis confirmado a todas las capas de la DB."""
    
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    
    pending = get_pending_analysis(conn, project_id, chapter_number)
    if not pending:
        return {"status": "error", "message": f"No hay análisis pendiente para capítulo {chapter_number}"}
    
    analysis = pending["analysis"]
    chapter_id = pending["chapter_id"]
    changes_applied = []
    
    # 1. Actualizar metadata del capítulo
    conn.execute("""
        UPDATE chapters SET
            summary = ?,
            scene_type = ?,
            tension_level = ?,
            pacing = ?,
            emotional_tone = ?,
            status = CASE WHEN status = 'planned' THEN 'draft' ELSE status END,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        analysis.get("summary"),
        analysis.get("scene_type"),
        analysis.get("tension_level"),
        analysis.get("pacing"),
        analysis.get("emotional_tone"),
        chapter_id
    ))
    changes_applied.append("chapter_metadata")
    
    # 2. Registrar eventos del mundo
    for event in analysis.get("events", []):
        conn.execute("""
            INSERT INTO world_events (project_id, chapter_id, event_type, description, story_timestamp, affected_entities)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            project_id, chapter_id,
            event.get("type", "discovery"),
            event.get("description", ""),
            event.get("story_timestamp"),
            json.dumps(event.get("affected_characters", []) + event.get("affected_objects", []))
        ))
    if analysis.get("events"):
        changes_applied.append(f"world_events ({len(analysis['events'])})")
    
    # 3. Actualizar ubicaciones de personajes
    for loc in analysis.get("character_locations_end", []):
        char_name = loc.get("character_name")
        location_name = loc.get("location")
        
        # Buscar personaje por nombre
        char_row = conn.execute(
            "SELECT id FROM characters WHERE project_id = ? AND name = ?",
            (project_id, char_name)
        ).fetchone()
        
        if char_row:
            # Buscar o crear ubicación
            loc_row = conn.execute(
                "SELECT id FROM locations WHERE project_id = ? AND name = ?",
                (project_id, location_name)
            ).fetchone()
            
            if not loc_row:
                conn.execute(
                    "INSERT INTO locations (project_id, name) VALUES (?, ?)",
                    (project_id, location_name)
                )
                loc_row = conn.execute(
                    "SELECT id FROM locations WHERE project_id = ? AND name = ?",
                    (project_id, location_name)
                ).fetchone()
            
            conn.execute(
                "UPDATE characters SET current_location_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (loc_row["id"], char_row["id"])
            )
    if analysis.get("character_locations_end"):
        changes_applied.append(f"character_locations ({len(analysis['character_locations_end'])})")
    
    # 4. Actualizar conocimiento de personajes
    for kc in analysis.get("knowledge_changes", []):
        char_name = kc.get("character_name")
        char_row = conn.execute(
            "SELECT id FROM characters WHERE project_id = ? AND name = ?",
            (project_id, char_name)
        ).fetchone()
        
        if char_row:
            # Buscar o crear el hecho
            fact_desc = kc.get("fact", "")
            fact_row = conn.execute(
                "SELECT id FROM story_facts WHERE project_id = ? AND description = ?",
                (project_id, fact_desc)
            ).fetchone()
            
            if not fact_row:
                conn.execute(
                    "INSERT INTO story_facts (project_id, category, description, established_in_chapter) VALUES (?, 'event', ?, ?)",
                    (project_id, fact_desc, chapter_id)
                )
                fact_row = conn.execute(
                    "SELECT id FROM story_facts WHERE project_id = ? AND description = ?",
                    (project_id, fact_desc)
                ).fetchone()
            
            # Insertar o actualizar knowledge_state
            conn.execute("""
                INSERT INTO knowledge_states (project_id, knower_id, fact_id, knowledge_level, how_learned, learned_in_chapter)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(knower_id, fact_id) DO UPDATE SET
                    knowledge_level = excluded.knowledge_level,
                    how_learned = excluded.how_learned,
                    learned_in_chapter = excluded.learned_in_chapter,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                project_id, char_row["id"], fact_row["id"],
                kc.get("new_knowledge_level", "knows"),
                kc.get("how_learned", "witnessed"),
                chapter_id
            ))
    if analysis.get("knowledge_changes"):
        changes_applied.append(f"knowledge_states ({len(analysis['knowledge_changes'])})")
    
    # 5. Actualizar conocimiento del lector
    for rkc in analysis.get("reader_knowledge_changes", []):
        fact_desc = rkc.get("fact", "")
        fact_row = conn.execute(
            "SELECT id FROM story_facts WHERE project_id = ? AND description = ?",
            (project_id, fact_desc)
        ).fetchone()
        
        if not fact_row:
            conn.execute(
                "INSERT INTO story_facts (project_id, category, description, established_in_chapter, revealed_to_reader_in) VALUES (?, 'event', ?, ?, ?)",
                (project_id, fact_desc, chapter_id, chapter_id)
            )
            fact_row = conn.execute(
                "SELECT id FROM story_facts WHERE project_id = ? AND description = ?",
                (project_id, fact_desc)
            ).fetchone()
        else:
            conn.execute(
                "UPDATE story_facts SET revealed_to_reader_in = ? WHERE id = ? AND revealed_to_reader_in IS NULL",
                (chapter_id, fact_row["id"])
            )
        
        conn.execute("""
            INSERT INTO knowledge_states (project_id, knower_id, fact_id, knowledge_level, how_learned, learned_in_chapter)
            VALUES (?, '__reader__', ?, ?, 'reader_inference', ?)
            ON CONFLICT(knower_id, fact_id) DO UPDATE SET
                knowledge_level = excluded.knowledge_level,
                learned_in_chapter = excluded.learned_in_chapter,
                updated_at = CURRENT_TIMESTAMP
        """, (project_id, fact_row["id"], rkc.get("new_knowledge_level", "knows"), chapter_id))
    if analysis.get("reader_knowledge_changes"):
        changes_applied.append(f"reader_knowledge ({len(analysis['reader_knowledge_changes'])})")
    
    # 6. Registrar beats de hilos
    for tb in analysis.get("thread_beats", []):
        thread_name = tb.get("thread_name")
        thread_row = conn.execute(
            "SELECT id FROM plot_threads WHERE project_id = ? AND name = ?",
            (project_id, thread_name)
        ).fetchone()
        
        if thread_row:
            conn.execute("""
                INSERT INTO thread_beats (thread_id, chapter_id, beat_type, description)
                VALUES (?, ?, ?, ?)
            """, (thread_row["id"], chapter_id, tb.get("beat_type", "reinforce"), tb.get("description", "")))
            
            # Actualizar status del hilo si el beat lo justifica
            beat_type = tb.get("beat_type")
            if beat_type == "resolve":
                conn.execute(
                    "UPDATE plot_threads SET status = 'resolved', resolved_in_chapter = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (chapter_id, thread_row["id"])
                )
            elif beat_type == "climax":
                conn.execute(
                    "UPDATE plot_threads SET status = 'climax', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (thread_row["id"],)
                )
            elif beat_type in ("plant",):
                conn.execute(
                    "UPDATE plot_threads SET status = 'planted', planted_in_chapter = COALESCE(planted_in_chapter, ?), updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (chapter_id, thread_row["id"])
                )
    if analysis.get("thread_beats"):
        changes_applied.append(f"thread_beats ({len(analysis['thread_beats'])})")
    
    # 7. Registrar pistas
    for clue in analysis.get("clues", []):
        thread_name = clue.get("related_thread")
        thread_id = None
        if thread_name:
            thread_row = conn.execute(
                "SELECT id FROM plot_threads WHERE project_id = ? AND name = ?",
                (project_id, thread_name)
            ).fetchone()
            if thread_row:
                thread_id = thread_row["id"]
        
        conn.execute("""
            INSERT INTO clues (project_id, thread_id, description, planted_in_chapter, clue_type, subtlety, mechanism)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id, thread_id,
            clue.get("description", ""),
            chapter_id,
            clue.get("type", "verbal"),
            clue.get("subtlety", 5),
            clue.get("mechanism")
        ))
    if analysis.get("clues"):
        changes_applied.append(f"clues ({len(analysis['clues'])})")
    
    # 8. Marcar análisis como aplicado
    conn.execute("""
        UPDATE author_notes SET resolved = 1
        WHERE project_id = ? AND chapter_id = ? AND note_type = 'pending_analysis'
    """, (project_id, chapter_id))
    
    # 9. Actualizar word count del proyecto
    conn.execute("""
        UPDATE projects SET
            current_word_count = (SELECT COALESCE(SUM(word_count), 0) FROM chapters WHERE project_id = ?),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (project_id, project_id))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "chapter_number": chapter_number,
        "changes_applied": changes_applied,
        "message": f"Capítulo {chapter_number} actualizado. Cambios: {', '.join(changes_applied)}"
    }


def main():
    parser = argparse.ArgumentParser(description="Aplicar análisis confirmado")
    parser.add_argument("--chapter", type=int, required=True, help="Número de capítulo")
    parser.add_argument("--project", default=None, help="ID del proyecto")
    parser.add_argument("--confirm", action="store_true", help="Confirmar aplicación")
    parser.add_argument("--db", required=True, help="Ruta a la base de datos SQLite")
    
    args = parser.parse_args()
    
    if not args.confirm:
        print(json.dumps({"status": "info", "message": "Usa --confirm para aplicar los cambios"}))
        return
    
    conn = sqlite3.connect(args.db)
    if args.project:
        project_id = args.project
    else:
        row = conn.execute("SELECT id FROM projects ORDER BY updated_at DESC LIMIT 1").fetchone()
        project_id = row[0] if row else None
    conn.close()
    
    if not project_id:
        print(json.dumps({"status": "error", "message": "No hay proyectos en la DB"}))
        sys.exit(1)
    
    result = apply_analysis(args.db, project_id, args.chapter)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
