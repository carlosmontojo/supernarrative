#!/usr/bin/env python3
"""
Narratium — Análisis Post-Capítulo
Toma el output JSON del análisis del LLM y lo prepara para actualización.
Este script NO ejecuta el LLM — recibe el JSON ya generado.

Flujo:
1. Claude Code lee el capítulo y ejecuta el prompt de análisis
2. Claude Code genera el JSON de análisis
3. Este script valida el JSON y lo almacena como propuesta
4. El autor revisa y confirma
5. update.py aplica los cambios confirmados
"""

import argparse
import json
import sqlite3
import sys
import os
from datetime import datetime


ANALYSIS_SCHEMA = {
    "required_fields": ["summary", "events", "knowledge_changes", "reader_knowledge_changes",
                        "thread_beats", "clues", "character_locations_end",
                        "tension_level", "scene_type", "pacing", "emotional_tone"],
    "event_types": ["movement", "death", "discovery", "destruction", "transformation", "revelation", "encounter"],
    "knowledge_levels": ["knows", "suspects", "partial", "wrong_belief", "unaware"],
    "beat_types": ["plant", "reinforce", "complicate", "twist", "escalate", "near_reveal", "reveal", "resolve", "subvert"],
    "clue_types": ["verbal", "visual", "object", "behavioral", "environmental", "structural", "intertextual"],
    "scene_types": ["action", "dialogue", "reflection", "revelation", "transition", "flashback", "confrontation", "investigation"],
    "pacing_values": ["slow", "medium", "fast", "frantic"]
}


def validate_analysis(analysis: dict) -> dict:
    """Valida el JSON de análisis contra el schema esperado."""
    errors = []
    warnings = []
    
    for field in ANALYSIS_SCHEMA["required_fields"]:
        if field not in analysis:
            errors.append(f"Campo requerido ausente: {field}")
    
    if "events" in analysis:
        for i, event in enumerate(analysis["events"]):
            if event.get("type") not in ANALYSIS_SCHEMA["event_types"]:
                warnings.append(f"Evento {i}: tipo '{event.get('type')}' no reconocido")
    
    if "tension_level" in analysis:
        t = analysis["tension_level"]
        if not isinstance(t, (int, float)) or t < 1 or t > 10:
            warnings.append(f"tension_level debe ser 1-10, recibido: {t}")
    
    if "scene_type" in analysis:
        if analysis["scene_type"] not in ANALYSIS_SCHEMA["scene_types"]:
            warnings.append(f"scene_type '{analysis['scene_type']}' no reconocido")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def store_pending_analysis(db_path: str, project_id: str, chapter_number: int,
                           analysis: dict, chapter_file: str = None) -> dict:
    """Almacena el análisis como propuesta pendiente de confirmación."""
    
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Verificar que el capítulo existe o crearlo
    chapter = conn.execute(
        "SELECT id FROM chapters WHERE project_id = ? AND chapter_number = ?",
        (project_id, chapter_number)
    ).fetchone()
    
    if not chapter:
        conn.execute("""
            INSERT INTO chapters (project_id, chapter_number, chapter_order, status, file_path)
            VALUES (?, ?, ?, 'draft', ?)
        """, (project_id, chapter_number, chapter_number, chapter_file))
        chapter_id = conn.execute(
            "SELECT id FROM chapters WHERE project_id = ? AND chapter_number = ?",
            (project_id, chapter_number)
        ).fetchone()[0]
    else:
        chapter_id = chapter[0]
    
    # Guardar análisis pendiente como nota del autor para revisión
    conn.execute("""
        INSERT INTO author_notes (project_id, chapter_id, note_type, content)
        VALUES (?, ?, 'pending_analysis', ?)
    """, (project_id, chapter_id, json.dumps(analysis, ensure_ascii=False)))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "pending",
        "chapter_id": chapter_id,
        "chapter_number": chapter_number,
        "summary": analysis.get("summary", ""),
        "events_count": len(analysis.get("events", [])),
        "knowledge_changes_count": len(analysis.get("knowledge_changes", [])),
        "thread_beats_count": len(analysis.get("thread_beats", [])),
        "clues_count": len(analysis.get("clues", [])),
        "tension_level": analysis.get("tension_level"),
        "scene_type": analysis.get("scene_type"),
        "pacing": analysis.get("pacing"),
        "emotional_tone": analysis.get("emotional_tone"),
        "message": "Análisis almacenado como pendiente. Usa update.py --confirm para aplicar."
    }


def main():
    parser = argparse.ArgumentParser(description="Procesar análisis post-capítulo")
    parser.add_argument("--chapter", type=int, required=True, help="Número de capítulo")
    parser.add_argument("--project", default=None, help="ID del proyecto")
    parser.add_argument("--analysis-json", required=True, help="Ruta al JSON de análisis generado por el LLM")
    parser.add_argument("--chapter-file", default=None, help="Ruta al archivo .md del capítulo")
    parser.add_argument("--db", required=True, help="Ruta a la base de datos SQLite")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.db):
        print(json.dumps({"status": "error", "message": f"DB no encontrada: {args.db}"}))
        sys.exit(1)
    
    # Cargar análisis
    with open(args.analysis_json, 'r') as f:
        analysis = json.load(f)
    
    # Validar
    validation = validate_analysis(analysis)
    if not validation["valid"]:
        print(json.dumps({"status": "error", "validation": validation}))
        sys.exit(1)
    
    if validation["warnings"]:
        print(json.dumps({"status": "warning", "warnings": validation["warnings"]}), file=sys.stderr)
    
    # Obtener project_id
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
    
    # Almacenar
    result = store_pending_analysis(args.db, project_id, args.chapter, analysis, args.chapter_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
