#!/usr/bin/env python3
"""
Narratium — Operaciones CRUD de la DB
Helper para que Claude Code ejecute operaciones comunes.

Uso:
  python db_ops.py --db narratium.db --action add_character --data '{"name": "Lucrezia", ...}'
  python db_ops.py --db narratium.db --action list_characters
  python db_ops.py --db narratium.db --action add_fact --data '{"description": "...", ...}'
  python db_ops.py --db narratium.db --action add_thread --data '{"name": "...", ...}'
  python db_ops.py --db narratium.db --action add_location --data '{"name": "...", ...}'
  python db_ops.py --db narratium.db --action add_relationship --data '{"character_a": "...", ...}'
  python db_ops.py --db narratium.db --action set_knowledge --data '{"character": "...", "fact": "...", ...}'
  python db_ops.py --db narratium.db --action add_style_reference --data '{"author": "...", ...}'
  python db_ops.py --db narratium.db --action query --sql "SELECT ..."
"""

import argparse
import json
import sqlite3
import sys
import os


def get_project_id(conn):
    row = conn.execute("SELECT id FROM projects ORDER BY updated_at DESC LIMIT 1").fetchone()
    return row[0] if row else None


def add_character(conn, project_id, data):
    conn.execute("""
        INSERT INTO characters (project_id, name, full_name, aliases, role, description_physical,
            description_psychological, backstory, motivation, secret, flaw, arc_summary,
            voice_notes, speech_patterns, status, emotional_state)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        project_id, data["name"], data.get("full_name"), json.dumps(data.get("aliases", [])),
        data.get("role", "secondary"), data.get("description_physical"),
        data.get("description_psychological"), data.get("backstory"),
        data.get("motivation"), data.get("secret"), data.get("flaw"),
        data.get("arc_summary"), data.get("voice_notes"), data.get("speech_patterns"),
        data.get("status", "alive"), data.get("emotional_state")
    ))
    conn.commit()
    char_id = conn.execute("SELECT id FROM characters WHERE project_id = ? AND name = ?",
                           (project_id, data["name"])).fetchone()[0]
    return {"status": "success", "id": char_id, "name": data["name"]}


def list_characters(conn, project_id):
    rows = conn.execute("""
        SELECT id, name, role, status, emotional_state, l.name as location
        FROM characters c LEFT JOIN locations l ON c.current_location_id = l.id
        WHERE c.project_id = ?
        ORDER BY CASE c.role WHEN 'protagonist' THEN 1 WHEN 'antagonist' THEN 2 WHEN 'secondary' THEN 3 ELSE 4 END
    """, (project_id,)).fetchall()
    return {"characters": [dict(r) for r in rows]}


def add_location(conn, project_id, data):
    parent_id = None
    if data.get("parent"):
        parent = conn.execute("SELECT id FROM locations WHERE project_id = ? AND name = ?",
                              (project_id, data["parent"])).fetchone()
        parent_id = parent[0] if parent else None
    
    conn.execute("""
        INSERT INTO locations (project_id, name, description, parent_location_id, attributes)
        VALUES (?, ?, ?, ?, ?)
    """, (project_id, data["name"], data.get("description"), parent_id,
          json.dumps(data.get("attributes", {}))))
    conn.commit()
    return {"status": "success", "name": data["name"]}


def add_fact(conn, project_id, data):
    conn.execute("""
        INSERT INTO story_facts (project_id, category, description, is_true, significance)
        VALUES (?, ?, ?, ?, ?)
    """, (project_id, data.get("category", "event"), data["description"],
          data.get("is_true", True), data.get("significance", 5)))
    conn.commit()
    fact_id = conn.execute("SELECT id FROM story_facts WHERE project_id = ? AND description = ?",
                           (project_id, data["description"])).fetchone()[0]
    return {"status": "success", "id": fact_id}


def set_knowledge(conn, project_id, data):
    # Buscar personaje
    char_row = conn.execute("SELECT id FROM characters WHERE project_id = ? AND name = ?",
                            (project_id, data["character"])).fetchone()
    if not char_row:
        knower_id = "__reader__" if data["character"].lower() in ("reader", "lector", "__reader__") else None
        if not knower_id:
            return {"status": "error", "message": f"Personaje '{data['character']}' no encontrado"}
    else:
        knower_id = char_row[0]
    
    # Buscar hecho
    fact_row = conn.execute("SELECT id FROM story_facts WHERE project_id = ? AND description = ?",
                            (project_id, data["fact"])).fetchone()
    if not fact_row:
        return {"status": "error", "message": f"Hecho no encontrado: '{data['fact']}'. Créalo primero con add_fact."}
    
    conn.execute("""
        INSERT INTO knowledge_states (project_id, knower_id, fact_id, knowledge_level, how_learned, wrong_belief_detail)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(knower_id, fact_id) DO UPDATE SET
            knowledge_level = excluded.knowledge_level,
            how_learned = excluded.how_learned,
            wrong_belief_detail = excluded.wrong_belief_detail,
            updated_at = CURRENT_TIMESTAMP
    """, (project_id, knower_id, fact_row[0],
          data.get("knowledge_level", "knows"),
          data.get("how_learned"),
          data.get("wrong_belief_detail")))
    conn.commit()
    return {"status": "success", "character": data["character"], "level": data.get("knowledge_level", "knows")}


def add_thread(conn, project_id, data):
    conn.execute("""
        INSERT INTO plot_threads (project_id, name, description, thread_type, status, priority, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (project_id, data["name"], data.get("description"),
          data.get("thread_type", "subplot"), data.get("status", "planned"),
          data.get("priority", 5), data.get("notes")))
    conn.commit()
    return {"status": "success", "name": data["name"]}


def add_relationship(conn, project_id, data):
    char_a = conn.execute("SELECT id FROM characters WHERE project_id = ? AND name = ?",
                          (project_id, data["character_a"])).fetchone()
    char_b = conn.execute("SELECT id FROM characters WHERE project_id = ? AND name = ?",
                          (project_id, data["character_b"])).fetchone()
    
    if not char_a or not char_b:
        return {"status": "error", "message": "Uno o ambos personajes no encontrados"}
    
    conn.execute("""
        INSERT INTO character_relationships (project_id, character_a_id, character_b_id,
            relationship_type, description, public_perception, private_reality, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(character_a_id, character_b_id, relationship_type) DO UPDATE SET
            description = excluded.description,
            public_perception = excluded.public_perception,
            private_reality = excluded.private_reality,
            status = excluded.status,
            updated_at = CURRENT_TIMESTAMP
    """, (project_id, char_a[0], char_b[0],
          data.get("relationship_type", "unknown"),
          data.get("description"), data.get("public_perception"),
          data.get("private_reality"), data.get("status", "active")))
    conn.commit()
    return {"status": "success", "characters": [data["character_a"], data["character_b"]]}


def add_style_reference(conn, project_id, data):
    conn.execute("""
        INSERT INTO style_references (project_id, author, work, technique, example_description)
        VALUES (?, ?, ?, ?, ?)
    """, (project_id, data["author"], data.get("work"), data["technique"],
          data.get("example_description")))
    conn.commit()
    return {"status": "success", "author": data["author"]}


def add_object(conn, project_id, data):
    holder_id = None
    if data.get("holder"):
        holder = conn.execute("SELECT id FROM characters WHERE project_id = ? AND name = ?",
                              (project_id, data["holder"])).fetchone()
        holder_id = holder[0] if holder else None
    
    location_id = None
    if data.get("location"):
        loc = conn.execute("SELECT id FROM locations WHERE project_id = ? AND name = ?",
                           (project_id, data["location"])).fetchone()
        location_id = loc[0] if loc else None
    
    conn.execute("""
        INSERT INTO objects (project_id, name, description, current_location_id, current_holder_id,
            status, significance)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (project_id, data["name"], data.get("description"), location_id, holder_id,
          data.get("status", "active"), data.get("significance")))
    conn.commit()
    return {"status": "success", "name": data["name"]}


def run_query(conn, sql):
    try:
        rows = conn.execute(sql).fetchall()
        return {"status": "success", "rows": [dict(r) for r in rows], "count": len(rows)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


ACTIONS = {
    "add_character": add_character,
    "list_characters": lambda conn, pid, data=None: list_characters(conn, pid),
    "add_location": add_location,
    "add_fact": add_fact,
    "set_knowledge": set_knowledge,
    "add_thread": add_thread,
    "add_relationship": add_relationship,
    "add_style_reference": add_style_reference,
    "add_object": add_object,
}


def main():
    parser = argparse.ArgumentParser(description="Operaciones CRUD Narratium")
    parser.add_argument("--db", required=True, help="Ruta a la DB")
    parser.add_argument("--action", required=True, help="Acción a ejecutar")
    parser.add_argument("--data", default=None, help="JSON con los datos")
    parser.add_argument("--sql", default=None, help="SQL para acción 'query'")
    parser.add_argument("--project", default=None, help="ID del proyecto")
    
    args = parser.parse_args()
    
    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    
    project_id = args.project or get_project_id(conn)
    
    if args.action == "query":
        result = run_query(conn, args.sql)
    elif args.action in ACTIONS:
        data = json.loads(args.data) if args.data else {}
        if args.action == "list_characters":
            result = ACTIONS[args.action](conn, project_id)
        else:
            result = ACTIONS[args.action](conn, project_id, data)
    else:
        result = {"status": "error", "message": f"Acción desconocida: {args.action}",
                  "available": list(ACTIONS.keys()) + ["query"]}
    
    conn.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
