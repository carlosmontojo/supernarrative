#!/usr/bin/env python3
"""
SuperNarrative — Operaciones CRUD de la DB
Helper para que Claude Code (o el autor) ejecute operaciones comunes.

Uso:
  python db_ops.py --db supernarrative.db --action add_character --data '{"name": "Lucrezia", ...}'
  python db_ops.py --db supernarrative.db --action add_dependency --data '{"dependent": "...", "required": "...", "required_status": "resolved"}'
  python db_ops.py --db supernarrative.db --action list_characters
  python db_ops.py --db supernarrative.db --action query --sql "SELECT ..."   (solo lectura)
"""

import argparse
import json
import sqlite3
import sys
import os

from _common import (connect, gen_id, get_or_create_location, get_project_id,
                     require_db, resolve_character, resolve_thread)


def add_character(conn, project_id, data):
    char_id = gen_id()
    conn.execute("""
        INSERT INTO characters (id, project_id, name, full_name, aliases, role,
            description_physical, description_psychological, backstory, motivation,
            secret, flaw, arc_summary, voice_notes, speech_patterns, status,
            emotional_state, introduced_in_chapter)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        char_id, project_id, data["name"], data.get("full_name"),
        json.dumps(data.get("aliases", [])), data.get("role", "secondary"),
        data.get("description_physical"), data.get("description_psychological"),
        data.get("backstory"), data.get("motivation"), data.get("secret"),
        data.get("flaw"), data.get("arc_summary"), data.get("voice_notes"),
        data.get("speech_patterns"), data.get("status", "alive"),
        data.get("emotional_state"), data.get("introduced_in_chapter"),
    ))
    conn.commit()
    return {"status": "success", "id": char_id, "name": data["name"]}


def list_characters(conn, project_id):
    rows = conn.execute("""
        SELECT c.id, c.name, c.role, c.status, c.emotional_state,
               l.name as location
        FROM characters c LEFT JOIN locations l ON c.current_location_id = l.id
        WHERE c.project_id = ?
        ORDER BY CASE c.role WHEN 'protagonist' THEN 1 WHEN 'antagonist' THEN 2 WHEN 'secondary' THEN 3 ELSE 4 END
    """, (project_id,)).fetchall()
    return {"characters": [dict(r) for r in rows]}


def list_threads(conn, project_id):
    rows = conn.execute("""
        SELECT pt.id, pt.name, pt.thread_type, pt.status, pt.priority,
               pt.planted_in_chapter, pt.target_resolution_chapter,
               COUNT(tb.id) as beats
        FROM plot_threads pt
        LEFT JOIN thread_beats tb ON tb.thread_id = pt.id
        WHERE pt.project_id = ?
        GROUP BY pt.id ORDER BY pt.priority DESC
    """, (project_id,)).fetchall()
    return {"threads": [dict(r) for r in rows]}


def add_location(conn, project_id, data):
    parent_id = None
    if data.get("parent"):
        parent = conn.execute(
            "SELECT id FROM locations WHERE project_id = ? AND name = ? COLLATE NOCASE",
            (project_id, data["parent"])).fetchone()
        parent_id = parent["id"] if parent else None

    loc_id = gen_id()
    conn.execute("""
        INSERT INTO locations (id, project_id, name, description, parent_location_id, attributes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (loc_id, project_id, data["name"], data.get("description"), parent_id,
          json.dumps(data.get("attributes", {}))))
    conn.commit()
    return {"status": "success", "id": loc_id, "name": data["name"]}


def add_fact(conn, project_id, data):
    fact_id = gen_id()
    conn.execute("""
        INSERT INTO story_facts (id, project_id, category, description, is_true,
            significance, established_in_chapter)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (fact_id, project_id, data.get("category", "event"), data["description"],
          data.get("is_true", True), data.get("significance", 5),
          data.get("established_in_chapter")))
    conn.commit()
    return {"status": "success", "id": fact_id}


def set_knowledge(conn, project_id, data):
    name = data["character"]
    if name.lower() in ("reader", "lector", "__reader__"):
        knower_id = "__reader__"
    else:
        char = resolve_character(conn, project_id, name)
        if not char:
            return {"status": "error", "message": f"Personaje '{name}' no encontrado"}
        knower_id = char["id"]

    fact_row = conn.execute(
        "SELECT id FROM story_facts WHERE project_id = ? AND description = ?",
        (project_id, data["fact"])).fetchone()
    if not fact_row:
        return {"status": "error",
                "message": f"Hecho no encontrado: '{data['fact']}'. Créalo primero con add_fact."}

    conn.execute("""
        INSERT INTO knowledge_states (id, project_id, knower_id, fact_id,
            knowledge_level, how_learned, wrong_belief_detail, learned_in_chapter)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(knower_id, fact_id) DO UPDATE SET
            knowledge_level = excluded.knowledge_level,
            how_learned = excluded.how_learned,
            wrong_belief_detail = excluded.wrong_belief_detail,
            learned_in_chapter = COALESCE(excluded.learned_in_chapter, learned_in_chapter),
            updated_at = CURRENT_TIMESTAMP
    """, (gen_id(), project_id, knower_id, fact_row["id"],
          data.get("knowledge_level", "knows"), data.get("how_learned"),
          data.get("wrong_belief_detail"), data.get("learned_in_chapter")))
    conn.commit()
    return {"status": "success", "character": name,
            "level": data.get("knowledge_level", "knows")}


def add_thread(conn, project_id, data):
    thread_id = gen_id()
    conn.execute("""
        INSERT INTO plot_threads (id, project_id, name, description, thread_type,
            status, priority, notes, target_resolution_chapter)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (thread_id, project_id, data["name"], data.get("description"),
          data.get("thread_type", "subplot"), data.get("status", "planned"),
          data.get("priority", 5), data.get("notes"),
          data.get("target_resolution_chapter")))
    conn.commit()
    return {"status": "success", "id": thread_id, "name": data["name"]}


def add_dependency(conn, project_id, data):
    """Declara que un hilo no puede avanzar hasta que otro alcance un estado.
    (En v0.1 la única forma de crear dependencias era SQL a mano.)"""
    dependent = resolve_thread(conn, project_id, data["dependent"])
    required = resolve_thread(conn, project_id, data["required"])
    if not dependent or not required:
        return {"status": "error", "message": "Uno o ambos hilos no encontrados",
                "dependent_found": bool(dependent), "required_found": bool(required)}
    conn.execute("""
        INSERT INTO thread_dependencies (id, dependent_thread_id, required_thread_id,
            required_status, description)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(dependent_thread_id, required_thread_id) DO UPDATE SET
            required_status = excluded.required_status,
            description = excluded.description
    """, (gen_id(), dependent["id"], required["id"],
          data.get("required_status", "resolved"), data.get("description")))
    conn.commit()
    return {"status": "success",
            "dependency": f"'{dependent['name']}' requiere '{required['name']}' en "
                          f"'{data.get('required_status', 'resolved')}'"}


def add_clue(conn, project_id, data):
    thread = resolve_thread(conn, project_id, data.get("thread")) if data.get("thread") else None
    clue_id = gen_id()
    conn.execute("""
        INSERT INTO clues (id, project_id, thread_id, description, planted_in_chapter,
            clue_type, subtlety, mechanism, intended_resolution)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (clue_id, project_id, thread["id"] if thread else None,
          data["description"], data["planted_in_chapter"],
          data.get("clue_type", "verbal"), data.get("subtlety", 5),
          data.get("mechanism"), data.get("intended_resolution")))
    conn.commit()
    return {"status": "success", "id": clue_id}


def add_beat(conn, project_id, data):
    thread = resolve_thread(conn, project_id, data["thread"])
    if not thread:
        return {"status": "error", "message": f"Hilo '{data['thread']}' no encontrado"}
    ch = conn.execute(
        "SELECT id FROM chapters WHERE project_id = ? AND chapter_number = ?",
        (project_id, data["chapter"])).fetchone()
    if not ch:
        return {"status": "error", "message": f"Capítulo {data['chapter']} no existe en la DB"}
    conn.execute("""
        INSERT INTO thread_beats (id, thread_id, chapter_id, beat_type, description, impact_level)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (gen_id(), thread["id"], ch["id"], data.get("beat_type", "reinforce"),
          data.get("description", ""), data.get("impact_level", 5)))
    conn.commit()
    return {"status": "success", "thread": thread["name"]}


def add_relationship(conn, project_id, data):
    char_a = resolve_character(conn, project_id, data["character_a"])
    char_b = resolve_character(conn, project_id, data["character_b"])
    if not char_a or not char_b:
        return {"status": "error", "message": "Uno o ambos personajes no encontrados"}

    conn.execute("""
        INSERT INTO character_relationships (id, project_id, character_a_id, character_b_id,
            relationship_type, description, public_perception, private_reality, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(character_a_id, character_b_id, relationship_type) DO UPDATE SET
            description = excluded.description,
            public_perception = excluded.public_perception,
            private_reality = excluded.private_reality,
            status = excluded.status,
            updated_at = CURRENT_TIMESTAMP
    """, (gen_id(), project_id, char_a["id"], char_b["id"],
          data.get("relationship_type", "unknown"), data.get("description"),
          data.get("public_perception"), data.get("private_reality"),
          data.get("status", "active")))
    conn.commit()
    return {"status": "success", "characters": [char_a["name"], char_b["name"]]}


def add_style_reference(conn, project_id, data):
    conn.execute("""
        INSERT INTO style_references (id, project_id, author, work, technique, example_description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (gen_id(), project_id, data["author"], data.get("work"),
          data["technique"], data.get("example_description")))
    conn.commit()
    return {"status": "success", "author": data["author"]}


def add_object(conn, project_id, data):
    holder_id = None
    if data.get("holder"):
        holder = resolve_character(conn, project_id, data["holder"])
        holder_id = holder["id"] if holder else None
    location_id = get_or_create_location(conn, project_id, data["location"]) \
        if data.get("location") else None

    obj_id = gen_id()
    conn.execute("""
        INSERT INTO objects (id, project_id, name, description, current_location_id,
            current_holder_id, status, significance, introduced_in_chapter)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (obj_id, project_id, data["name"], data.get("description"), location_id,
          holder_id, data.get("status", "active"), data.get("significance"),
          data.get("introduced_in_chapter")))
    conn.commit()
    return {"status": "success", "id": obj_id, "name": data["name"]}


def resolve_issue(conn, project_id, data):
    """Marca un issue de consistencia como resuelto (por fragmento de su descripción)."""
    rows = conn.execute("""
        SELECT id, description FROM consistency_issues
        WHERE project_id = ? AND resolved = 0 AND description LIKE ?
    """, (project_id, f"%{data['description']}%")).fetchall()
    if not rows:
        return {"status": "error", "message": "Ningún issue sin resolver coincide"}
    if len(rows) > 1 and not data.get("all"):
        return {"status": "error", "message": f"{len(rows)} issues coinciden; afina la descripción o pasa \"all\": true",
                "matches": [r["description"] for r in rows]}
    for r in rows:
        conn.execute("""
            UPDATE consistency_issues SET resolved = 1, resolved_note = ?,
                resolved_at = CURRENT_TIMESTAMP WHERE id = ?
        """, (data.get("note"), r["id"]))
    conn.commit()
    return {"status": "success", "resolved": len(rows)}


def run_query(db_path, sql):
    """Consulta de solo lectura (la conexión se abre en modo ro)."""
    try:
        conn = sqlite3.connect(f"file:{os.path.abspath(db_path)}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql).fetchall()
        conn.close()
        return {"status": "success", "rows": [dict(r) for r in rows], "count": len(rows)}
    except Exception as e:
        return {"status": "error", "message": str(e),
                "note": "La acción 'query' es de solo lectura. Para escribir, usa las acciones add_*/set_*."}


ACTIONS = {
    "add_character": add_character,
    "list_characters": lambda conn, pid, data=None: list_characters(conn, pid),
    "list_threads": lambda conn, pid, data=None: list_threads(conn, pid),
    "add_location": add_location,
    "add_fact": add_fact,
    "set_knowledge": set_knowledge,
    "add_thread": add_thread,
    "add_dependency": add_dependency,
    "add_clue": add_clue,
    "add_beat": add_beat,
    "add_relationship": add_relationship,
    "add_style_reference": add_style_reference,
    "add_object": add_object,
    "resolve_issue": resolve_issue,
}


def main():
    parser = argparse.ArgumentParser(description="Operaciones CRUD SuperNarrative")
    parser.add_argument("--db", required=True, help="Ruta a la DB")
    parser.add_argument("--action", required=True, help="Acción a ejecutar")
    parser.add_argument("--data", default=None, help="JSON con los datos")
    parser.add_argument("--sql", default=None, help="SQL para acción 'query' (solo lectura)")
    parser.add_argument("--project", default=None, help="ID del proyecto")
    args = parser.parse_args()

    require_db(args.db)

    if args.action == "query":
        print(json.dumps(run_query(args.db, args.sql), ensure_ascii=False, indent=2))
        return

    conn = connect(args.db)
    project_id = get_project_id(conn, args.project)

    if args.action in ACTIONS:
        data = json.loads(args.data) if args.data else {}
        try:
            result = ACTIONS[args.action](conn, project_id, data)
        except KeyError as e:
            result = {"status": "error", "message": f"Falta el campo requerido {e} en --data"}
    else:
        result = {"status": "error", "message": f"Acción desconocida: {args.action}",
                  "available": sorted(ACTIONS.keys()) + ["query"]}

    conn.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("status") == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
