#!/usr/bin/env python3
"""
SuperNarrative — Aplicar actualizaciones confirmadas
Toma el análisis pendiente y actualiza todas las capas de memoria.

Garantías v0.2:
  - Nada se descarta en silencio: los nombres de personajes/hilos que no se
    resuelven se devuelven en "unmatched" para que el autor los corrija.
  - Las columnas *_in_chapter guardan NÚMEROS de capítulo (no IDs internos).
  - Aplica TODO lo que produce el prompt de análisis: eventos, conocimiento,
    beats, pistas (nuevas, refuerzos y resoluciones), ubicaciones, estados
    emocionales, hooks, word_count y escenas.
  - --replace borra los datos previos del capítulo antes de aplicar (para
    re-análisis tras reescritura, sin duplicados).
"""

import argparse
import json
import sys

from _common import (connect, fail, gen_id, get_or_create_fact,
                     get_or_create_location, get_project_id, require_db,
                     resolve_character, resolve_thread, count_words_in_file)


def get_pending_analysis(conn, project_id, chapter_number):
    row = conn.execute("""
        SELECT an.content, ch.id as chapter_id, ch.file_path
        FROM author_notes an
        JOIN chapters ch ON an.chapter_id = ch.id
        WHERE an.project_id = ? AND ch.chapter_number = ?
          AND an.note_type = 'pending_analysis' AND an.resolved = 0
        ORDER BY an.created_at DESC LIMIT 1
    """, (project_id, chapter_number)).fetchone()
    if not row:
        return None
    return {"analysis": json.loads(row["content"]),
            "chapter_id": row["chapter_id"], "file_path": row["file_path"]}


def clear_chapter_data(conn, project_id, chapter_id, chapter_number):
    """Borra los datos derivados de un capítulo (para re-análisis limpio)."""
    conn.execute("DELETE FROM world_events WHERE chapter_id = ?", (chapter_id,))
    conn.execute("DELETE FROM thread_beats WHERE chapter_id = ?", (chapter_id,))
    conn.execute("DELETE FROM scenes WHERE chapter_id = ?", (chapter_id,))
    conn.execute(
        "DELETE FROM clues WHERE project_id = ? AND planted_in_chapter = ?",
        (project_id, chapter_number))


def apply_analysis(db_path, project_id, chapter_number, replace=False):
    conn = connect(db_path)

    pending = get_pending_analysis(conn, project_id, chapter_number)
    if not pending:
        return {"status": "error",
                "message": f"No hay análisis pendiente para capítulo {chapter_number}. "
                           "Ejecuta antes: supernarrative analyze --chapter N --analysis-json ..."}

    analysis = pending["analysis"]
    chapter_id = pending["chapter_id"]
    changes = []
    unmatched = {"characters": set(), "threads": set(), "clues": set()}

    if replace:
        clear_chapter_data(conn, project_id, chapter_id, chapter_number)
        changes.append("replace: datos previos del capítulo borrados")

    # 1. Metadata del capítulo (incluye hooks y word_count, antes ignorados)
    word_count = analysis.get("word_count")
    if not word_count and pending["file_path"]:
        word_count = count_words_in_file(pending["file_path"])
    conn.execute("""
        UPDATE chapters SET
            summary = COALESCE(?, summary),
            scene_type = COALESCE(?, scene_type),
            tension_level = COALESCE(?, tension_level),
            pacing = COALESCE(?, pacing),
            emotional_tone = COALESCE(?, emotional_tone),
            opening_hook = COALESCE(?, opening_hook),
            closing_hook = COALESCE(?, closing_hook),
            word_count = COALESCE(?, word_count),
            story_date = COALESCE(?, story_date),
            status = CASE WHEN status = 'planned' THEN 'draft' ELSE status END,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (analysis.get("summary"), analysis.get("scene_type"),
          analysis.get("tension_level"), analysis.get("pacing"),
          analysis.get("emotional_tone"), analysis.get("opening_hook"),
          analysis.get("closing_hook"), word_count,
          analysis.get("story_date"), chapter_id))
    changes.append("chapter_metadata")

    # 2. Eventos del mundo (resolviendo nombres a IDs para que los checks
    #    de verify.py puedan cruzarlos)
    for event in analysis.get("events", []):
        entities = []
        for name in event.get("affected_characters", []):
            char = resolve_character(conn, project_id, name)
            if char:
                entities.append(char["id"])
                # Una muerte explícita actualiza el estado del personaje
                if event.get("type") == "death":
                    conn.execute(
                        "UPDATE characters SET status = 'dead', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (char["id"],))
            else:
                entities.append(name)
                unmatched["characters"].add(name)
        entities.extend(event.get("affected_objects", []))
        conn.execute("""
            INSERT INTO world_events (id, project_id, chapter_id, event_type,
                description, story_timestamp, affected_entities)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (gen_id(), project_id, chapter_id,
              event.get("type", "discovery"), event.get("description", ""),
              event.get("story_timestamp"), json.dumps(entities)))
    if analysis.get("events"):
        changes.append(f"world_events ({len(analysis['events'])})")

    # 3. Ubicaciones de personajes al final del capítulo
    applied = 0
    for loc in analysis.get("character_locations_end", []):
        char = resolve_character(conn, project_id, loc.get("character_name"))
        if not char:
            unmatched["characters"].add(loc.get("character_name"))
            continue
        loc_id = get_or_create_location(conn, project_id, loc.get("location"))
        conn.execute(
            "UPDATE characters SET current_location_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (loc_id, char["id"]))
        applied += 1
    if applied:
        changes.append(f"character_locations ({applied})")

    # 4. Estados emocionales (el prompt los produce; antes se perdían)
    applied = 0
    for es in analysis.get("character_emotional_states", []):
        char = resolve_character(conn, project_id, es.get("character_name"))
        if not char:
            unmatched["characters"].add(es.get("character_name"))
            continue
        conn.execute(
            "UPDATE characters SET emotional_state = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (es.get("emotional_state"), char["id"]))
        applied += 1
    if applied:
        changes.append(f"emotional_states ({applied})")

    # 5. Conocimiento de personajes
    applied = 0
    for kc in analysis.get("knowledge_changes", []):
        char = resolve_character(conn, project_id, kc.get("character_name"))
        if not char:
            unmatched["characters"].add(kc.get("character_name"))
            continue
        fact_id = get_or_create_fact(conn, project_id, kc.get("fact", ""),
                                     chapter_number=chapter_number)
        conn.execute("""
            INSERT INTO knowledge_states (id, project_id, knower_id, fact_id,
                knowledge_level, wrong_belief_detail, how_learned, learned_in_chapter)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(knower_id, fact_id) DO UPDATE SET
                knowledge_level = excluded.knowledge_level,
                wrong_belief_detail = excluded.wrong_belief_detail,
                how_learned = excluded.how_learned,
                learned_in_chapter = excluded.learned_in_chapter,
                updated_at = CURRENT_TIMESTAMP
        """, (gen_id(), project_id, char["id"], fact_id,
              kc.get("new_knowledge_level", "knows"),
              kc.get("wrong_belief_detail"),
              kc.get("how_learned", "witnessed"), chapter_number))
        applied += 1
    if applied:
        changes.append(f"knowledge_states ({applied})")

    # 6. Conocimiento del lector
    for rkc in analysis.get("reader_knowledge_changes", []):
        fact_id = get_or_create_fact(conn, project_id, rkc.get("fact", ""),
                                     chapter_number=chapter_number)
        conn.execute(
            "UPDATE story_facts SET revealed_to_reader_in = ? WHERE id = ? AND revealed_to_reader_in IS NULL",
            (chapter_number, fact_id))
        conn.execute("""
            INSERT INTO knowledge_states (id, project_id, knower_id, fact_id,
                knowledge_level, how_learned, learned_in_chapter)
            VALUES (?, ?, '__reader__', ?, ?, 'reader_inference', ?)
            ON CONFLICT(knower_id, fact_id) DO UPDATE SET
                knowledge_level = excluded.knowledge_level,
                learned_in_chapter = excluded.learned_in_chapter,
                updated_at = CURRENT_TIMESTAMP
        """, (gen_id(), project_id, fact_id,
              rkc.get("new_knowledge_level", "knows"), chapter_number))
    if analysis.get("reader_knowledge_changes"):
        changes.append(f"reader_knowledge ({len(analysis['reader_knowledge_changes'])})")

    # 7. Beats de hilos, con progresión de estado coherente
    applied = 0
    for tb in analysis.get("thread_beats", []):
        thread = resolve_thread(conn, project_id, tb.get("thread_name"))
        if not thread:
            unmatched["threads"].add(tb.get("thread_name"))
            continue
        conn.execute("""
            INSERT INTO thread_beats (id, thread_id, chapter_id, beat_type, description, impact_level)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (gen_id(), thread["id"], chapter_id,
              tb.get("beat_type", "reinforce"), tb.get("description", ""),
              tb.get("impact_level", 5)))
        beat_type = tb.get("beat_type")
        if beat_type == "resolve":
            conn.execute(
                "UPDATE plot_threads SET status = 'resolved', resolved_in_chapter = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (chapter_number, thread["id"]))
        elif beat_type == "plant":
            conn.execute("""
                UPDATE plot_threads SET status = CASE WHEN status = 'planned' THEN 'planted' ELSE status END,
                    planted_in_chapter = COALESCE(planted_in_chapter, ?),
                    updated_at = CURRENT_TIMESTAMP WHERE id = ?
            """, (chapter_number, thread["id"]))
        else:
            # Cualquier otro beat sobre un hilo planned/planted lo pone en marcha
            conn.execute("""
                UPDATE plot_threads SET status = CASE WHEN status IN ('planned', 'planted')
                    THEN 'developing' ELSE status END,
                    updated_at = CURRENT_TIMESTAMP WHERE id = ?
            """, (thread["id"],))
        applied += 1
    if applied:
        changes.append(f"thread_beats ({applied})")

    # 8. Pistas nuevas
    for clue in analysis.get("clues", []):
        thread = resolve_thread(conn, project_id, clue.get("related_thread"))
        if clue.get("related_thread") and not thread:
            unmatched["threads"].add(clue.get("related_thread"))
        conn.execute("""
            INSERT INTO clues (id, project_id, thread_id, description,
                planted_in_chapter, clue_type, subtlety, mechanism, intended_resolution)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (gen_id(), project_id, thread["id"] if thread else None,
              clue.get("description", ""), chapter_number,
              clue.get("type", "verbal"), clue.get("subtlety", 5),
              clue.get("mechanism"), clue.get("intended_resolution")))
    if analysis.get("clues"):
        changes.append(f"clues ({len(analysis['clues'])})")

    # 9. Refuerzos y resoluciones de pistas existentes (antes imposibles)
    def find_clue(text):
        rows = conn.execute(
            "SELECT id, reinforced_in_chapters FROM clues WHERE project_id = ? AND description LIKE ?",
            (project_id, f"%{text}%")).fetchall()
        return rows[0] if len(rows) == 1 else None

    applied = 0
    for ref in analysis.get("clue_reinforcements", []):
        clue = find_clue(ref.get("clue_description", ""))
        if not clue:
            unmatched["clues"].add(ref.get("clue_description"))
            continue
        reinforced = json.loads(clue["reinforced_in_chapters"] or "[]")
        if chapter_number not in reinforced:
            reinforced.append(chapter_number)
        conn.execute(
            "UPDATE clues SET reinforced_in_chapters = ?, status = 'reinforced', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (json.dumps(reinforced), clue["id"]))
        applied += 1
    for res in analysis.get("clue_resolutions", []):
        clue = find_clue(res.get("clue_description", ""))
        if not clue:
            unmatched["clues"].add(res.get("clue_description"))
            continue
        conn.execute(
            "UPDATE clues SET status = 'resolved', resolved_in_chapter = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (chapter_number, clue["id"]))
        applied += 1
    if applied:
        changes.append(f"clue_updates ({applied})")

    # 10. Escenas (alimentan los checks de personajes dormidos/muertos)
    for i, scene in enumerate(analysis.get("scenes", []), start=1):
        present = []
        for name in scene.get("characters_present", []):
            char = resolve_character(conn, project_id, name)
            if char:
                present.append(char["id"])
            else:
                unmatched["characters"].add(name)
        loc_id = get_or_create_location(conn, project_id, scene["location"]) \
            if scene.get("location") else None
        conn.execute("""
            INSERT INTO scenes (id, chapter_id, scene_number, location_id,
                characters_present, summary, purpose, scene_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (gen_id(), chapter_id, scene.get("scene_number", i), loc_id,
              json.dumps(present), scene.get("summary"),
              scene.get("purpose"), scene.get("scene_number", i)))
    if analysis.get("scenes"):
        changes.append(f"scenes ({len(analysis['scenes'])})")

    # 11. Cerrar el análisis pendiente y refrescar el word count del proyecto
    conn.execute("""
        UPDATE author_notes SET resolved = 1
        WHERE project_id = ? AND chapter_id = ? AND note_type = 'pending_analysis'
    """, (project_id, chapter_id))
    conn.execute("""
        UPDATE projects SET
            current_word_count = (SELECT COALESCE(SUM(word_count), 0) FROM chapters WHERE project_id = ?),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (project_id, project_id))

    conn.commit()
    conn.close()

    result = {
        "status": "success",
        "chapter_number": chapter_number,
        "changes_applied": changes,
        "message": f"Capítulo {chapter_number} actualizado. Cambios: {', '.join(changes)}",
    }
    unmatched = {k: sorted(v) for k, v in unmatched.items() if v}
    if unmatched:
        result["status"] = "success_with_warnings"
        result["unmatched"] = unmatched
        result["warning"] = ("Algunos nombres no se pudieron resolver y sus cambios NO se aplicaron. "
                             "Revisa 'unmatched', corrige los nombres en el JSON de análisis "
                             "(o crea los personajes/hilos que falten) y vuelve a ejecutar con --replace.")
    return result


def main():
    parser = argparse.ArgumentParser(description="Aplicar análisis confirmado")
    parser.add_argument("--chapter", type=int, required=True, help="Número de capítulo")
    parser.add_argument("--project", default=None, help="ID del proyecto")
    parser.add_argument("--confirm", action="store_true", help="Confirmar aplicación")
    parser.add_argument("--replace", action="store_true",
                        help="Borrar datos previos del capítulo antes de aplicar (re-análisis)")
    parser.add_argument("--db", required=True, help="Ruta a la base de datos SQLite")
    args = parser.parse_args()

    require_db(args.db)

    if not args.confirm:
        print(json.dumps({"status": "info",
                          "message": "Usa --confirm para aplicar los cambios "
                                     "(el autor debe revisarlos primero)"}))
        return

    conn = connect(args.db)
    project_id = get_project_id(conn, args.project)
    conn.close()

    result = apply_analysis(args.db, project_id, args.chapter, replace=args.replace)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
