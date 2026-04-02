#!/usr/bin/env python3
"""
Narratium — Búsqueda narrativa
Consultas sobre el estado de la novela sin escribir SQL.
"""

import argparse
import json
import sqlite3
import sys
import os


def get_project_id(conn, project_id=None):
    if project_id:
        return project_id
    row = conn.execute("SELECT id FROM projects ORDER BY updated_at DESC LIMIT 1").fetchone()
    if not row:
        return None
    return row["id"]


def who_knows(conn, project_id, query):
    """Dado un texto, busca facts que coincidan y muestra quién sabe qué."""
    facts = conn.execute("""
        SELECT id, description, category, is_true
        FROM story_facts
        WHERE project_id = ? AND description LIKE ?
    """, (project_id, f"%{query}%")).fetchall()

    if not facts:
        return {"results": [], "message": f"No se encontraron hechos con '{query}'"}

    results = []
    for fact in facts:
        states = conn.execute("""
            SELECT ks.knower_id, ks.knowledge_level, ks.how_learned,
                   ks.learned_in_chapter, ks.confidence, ks.wrong_belief_detail,
                   COALESCE(c.name, ks.knower_id) as knower_name
            FROM knowledge_states ks
            LEFT JOIN characters c ON ks.knower_id = c.id
            WHERE ks.fact_id = ?
            ORDER BY ks.knowledge_level
        """, (fact["id"],)).fetchall()

        results.append({
            "fact": dict(fact),
            "knowledge": [dict(s) for s in states]
        })

    return {"results": results}


def who_knows_about(conn, project_id, query):
    """Dado un personaje, muestra TODO lo que sabe."""
    char = conn.execute("""
        SELECT id, name FROM characters
        WHERE project_id = ? AND (name LIKE ? OR full_name LIKE ? OR aliases LIKE ?)
    """, (project_id, f"%{query}%", f"%{query}%", f"%{query}%")).fetchone()

    if not char:
        return {"error": f"Personaje '{query}' no encontrado"}

    knowledge = conn.execute("""
        SELECT sf.description, sf.category, sf.is_true,
               ks.knowledge_level, ks.how_learned, ks.learned_in_chapter,
               ks.confidence, ks.wrong_belief_detail
        FROM knowledge_states ks
        JOIN story_facts sf ON ks.fact_id = sf.id
        WHERE ks.knower_id = ?
        ORDER BY ks.knowledge_level, sf.category
    """, (char["id"],)).fetchall()

    grouped = {}
    for k in knowledge:
        level = k["knowledge_level"]
        if level not in grouped:
            grouped[level] = []
        grouped[level].append(dict(k))

    return {
        "character": dict(char),
        "knowledge_by_level": grouped,
        "total_facts": len(knowledge)
    }


def where_is(conn, project_id, query):
    """Ubicación actual de un personaje."""
    chars = conn.execute("""
        SELECT c.name, c.status, c.emotional_state,
               l.name as location, l.description as location_desc
        FROM characters c
        LEFT JOIN locations l ON c.current_location_id = l.id
        WHERE c.project_id = ? AND (c.name LIKE ? OR c.full_name LIKE ?)
    """, (project_id, f"%{query}%", f"%{query}%")).fetchall()

    if not chars:
        return {"error": f"Personaje '{query}' no encontrado"}

    return {"results": [dict(c) for c in chars]}


def character_info(conn, project_id, query):
    """Ficha completa de un personaje."""
    char = conn.execute("""
        SELECT c.*, l.name as location_name
        FROM characters c
        LEFT JOIN locations l ON c.current_location_id = l.id
        WHERE c.project_id = ? AND (c.name LIKE ? OR c.full_name LIKE ? OR c.aliases LIKE ?)
    """, (project_id, f"%{query}%", f"%{query}%", f"%{query}%")).fetchone()

    if not char:
        return {"error": f"Personaje '{query}' no encontrado"}

    char_dict = dict(char)
    char_id = char_dict["id"]

    # Relaciones
    rels = conn.execute("""
        SELECT cr.relationship_type, cr.description, cr.public_perception,
               cr.private_reality, cr.status,
               CASE WHEN cr.character_a_id = ? THEN cb.name ELSE ca.name END as other_character
        FROM character_relationships cr
        JOIN characters ca ON cr.character_a_id = ca.id
        JOIN characters cb ON cr.character_b_id = cb.id
        WHERE cr.character_a_id = ? OR cr.character_b_id = ?
    """, (char_id, char_id, char_id)).fetchall()

    # Conocimiento
    knowledge = conn.execute("""
        SELECT sf.description, ks.knowledge_level, ks.confidence
        FROM knowledge_states ks
        JOIN story_facts sf ON ks.fact_id = sf.id
        WHERE ks.knower_id = ?
    """, (char_id,)).fetchall()

    # Última aparición
    last_chapter = conn.execute("""
        SELECT ch.chapter_number, ch.title
        FROM chapters ch
        WHERE ch.pov_character_id = ? OR EXISTS (
            SELECT 1 FROM scenes s
            WHERE s.chapter_id = ch.id AND s.characters_present LIKE ?
        )
        ORDER BY ch.chapter_number DESC LIMIT 1
    """, (char_id, f"%{char_id}%")).fetchone()

    return {
        "character": char_dict,
        "relationships": [dict(r) for r in rels],
        "knowledge": [dict(k) for k in knowledge],
        "last_appearance": dict(last_chapter) if last_chapter else None
    }


def active_clues(conn, project_id, query=None):
    """Pistas activas con antigüedad y thread asociado."""
    clues = conn.execute("""
        SELECT cl.description, cl.clue_type, cl.subtlety, cl.mechanism,
               cl.intended_resolution, cl.status,
               cl.planted_in_chapter,
               pt.name as thread_name,
               ch.chapter_number as planted_chapter_num
        FROM clues cl
        LEFT JOIN plot_threads pt ON cl.thread_id = pt.id
        LEFT JOIN chapters ch ON cl.planted_in_chapter = ch.id
        WHERE cl.project_id = ? AND cl.status IN ('active', 'reinforced')
        ORDER BY cl.subtlety DESC
    """, (project_id,)).fetchall()

    results = [dict(c) for c in clues]
    if query:
        results = [c for c in results if query.lower() in json.dumps(c, ensure_ascii=False).lower()]

    return {
        "active_clues": results,
        "total": len(results)
    }


def thread_status(conn, project_id, query):
    """Estado de un hilo narrativo con beats."""
    threads = conn.execute("""
        SELECT * FROM plot_threads
        WHERE project_id = ? AND (name LIKE ? OR description LIKE ?)
    """, (project_id, f"%{query}%", f"%{query}%")).fetchall()

    if not threads:
        return {"error": f"Hilo '{query}' no encontrado"}

    results = []
    for thread in threads:
        beats = conn.execute("""
            SELECT tb.beat_type, tb.description, tb.impact_level,
                   ch.chapter_number, ch.title as chapter_title
            FROM thread_beats tb
            LEFT JOIN chapters ch ON tb.chapter_id = ch.id
            WHERE tb.thread_id = ?
            ORDER BY ch.chapter_number
        """, (thread["id"],)).fetchall()

        deps = conn.execute("""
            SELECT pt.name as required_thread, td.required_status, td.description
            FROM thread_dependencies td
            JOIN plot_threads pt ON td.required_thread_id = pt.id
            WHERE td.dependent_thread_id = ?
        """, (thread["id"],)).fetchall()

        results.append({
            "thread": dict(thread),
            "beats": [dict(b) for b in beats],
            "dependencies": [dict(d) for d in deps]
        })

    return {"results": results}


def timeline(conn, project_id, query=None):
    """Eventos por capítulo."""
    if query:
        events = conn.execute("""
            SELECT we.event_type, we.description, we.story_timestamp,
                   ch.chapter_number, ch.title as chapter_title
            FROM world_events we
            JOIN chapters ch ON we.chapter_id = ch.id
            WHERE we.project_id = ? AND (
                ch.id LIKE ? OR CAST(ch.chapter_number AS TEXT) = ?
                OR we.description LIKE ?
            )
            ORDER BY ch.chapter_number, we.story_timestamp
        """, (project_id, f"%{query}%", query, f"%{query}%")).fetchall()
    else:
        events = conn.execute("""
            SELECT we.event_type, we.description, we.story_timestamp,
                   ch.chapter_number, ch.title as chapter_title
            FROM world_events we
            JOIN chapters ch ON we.chapter_id = ch.id
            WHERE we.project_id = ?
            ORDER BY ch.chapter_number, we.story_timestamp
        """, (project_id,)).fetchall()

    return {"events": [dict(e) for e in events], "total": len(events)}


def search_all(conn, project_id, query):
    """Búsqueda de texto libre en múltiples tablas."""
    pattern = f"%{query}%"
    results = {}

    # Characters
    chars = conn.execute("""
        SELECT name, role, status FROM characters
        WHERE project_id = ? AND (name LIKE ? OR full_name LIKE ? OR aliases LIKE ?
              OR backstory LIKE ? OR description_psychological LIKE ?)
    """, (project_id, pattern, pattern, pattern, pattern, pattern)).fetchall()
    if chars:
        results["characters"] = [dict(c) for c in chars]

    # Story facts
    facts = conn.execute("""
        SELECT description, category, is_true FROM story_facts
        WHERE project_id = ? AND description LIKE ?
    """, (project_id, pattern)).fetchall()
    if facts:
        results["story_facts"] = [dict(f) for f in facts]

    # Clues
    clues = conn.execute("""
        SELECT description, clue_type, status, subtlety FROM clues
        WHERE project_id = ? AND (description LIKE ? OR mechanism LIKE ?)
    """, (project_id, pattern, pattern)).fetchall()
    if clues:
        results["clues"] = [dict(c) for c in clues]

    # Plot threads
    threads = conn.execute("""
        SELECT name, thread_type, status, priority FROM plot_threads
        WHERE project_id = ? AND (name LIKE ? OR description LIKE ? OR notes LIKE ?)
    """, (project_id, pattern, pattern, pattern)).fetchall()
    if threads:
        results["plot_threads"] = [dict(t) for t in threads]

    # Objects
    objects = conn.execute("""
        SELECT name, status, significance FROM objects
        WHERE project_id = ? AND (name LIKE ? OR description LIKE ? OR significance LIKE ?)
    """, (project_id, pattern, pattern, pattern)).fetchall()
    if objects:
        results["objects"] = [dict(o) for o in objects]

    # Locations
    locations = conn.execute("""
        SELECT name, description FROM locations
        WHERE project_id = ? AND (name LIKE ? OR description LIKE ?)
    """, (project_id, pattern, pattern)).fetchall()
    if locations:
        results["locations"] = [dict(l) for l in locations]

    total = sum(len(v) for v in results.values())
    return {"query": query, "total_results": total, "results": results}


ACTIONS = {
    "who_knows": who_knows,
    "who_knows_about": who_knows_about,
    "where_is": where_is,
    "character_info": character_info,
    "active_clues": active_clues,
    "thread_status": thread_status,
    "timeline": timeline,
    "search_all": search_all,
}


def main():
    parser = argparse.ArgumentParser(description="Búsqueda narrativa Narratium")
    parser.add_argument("--db", required=True, help="Ruta a la base de datos SQLite")
    parser.add_argument("--action", required=True, choices=list(ACTIONS.keys()),
                        help="Tipo de búsqueda")
    parser.add_argument("--query", default=None, help="Texto de búsqueda")
    parser.add_argument("--project", default=None, help="ID del proyecto")

    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(json.dumps({"status": "error", "message": f"DB no encontrada: {args.db}"}))
        sys.exit(1)

    if args.action not in ("active_clues", "timeline") and not args.query:
        print(json.dumps({"status": "error", "message": f"La acción '{args.action}' requiere --query"}))
        sys.exit(1)

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")

    project_id = get_project_id(conn, args.project)
    if not project_id:
        print(json.dumps({"status": "error", "message": "No hay proyectos"}))
        sys.exit(1)

    action_fn = ACTIONS[args.action]
    if args.action in ("active_clues", "timeline"):
        result = action_fn(conn, project_id, args.query)
    else:
        result = action_fn(conn, project_id, args.query)

    result["status"] = "success"
    result["action"] = args.action
    print(json.dumps(result, ensure_ascii=False, indent=2))
    conn.close()


if __name__ == "__main__":
    main()
