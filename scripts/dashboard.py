#!/usr/bin/env python3
"""
Narratium — Dashboard del Proyecto
Estado general de la novela: progreso, hilos, pistas, ritmo, issues.
"""

import argparse
import json
import sqlite3
import sys
import os


def generate_dashboard(db_path: str, project_id: str = None) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    if not project_id:
        row = conn.execute("SELECT id FROM projects ORDER BY updated_at DESC LIMIT 1").fetchone()
        if not row:
            return {"status": "error", "message": "No hay proyectos"}
        project_id = row["id"]
    
    project = dict(conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone())
    
    # Progreso de capítulos
    chapters = conn.execute("""
        SELECT chapter_number, title, status, word_count, scene_type, tension_level, pacing, emotional_tone
        FROM chapters WHERE project_id = ? ORDER BY chapter_number
    """, (project_id,)).fetchall()
    
    total_words = sum(c["word_count"] or 0 for c in chapters)
    chapters_written = len([c for c in chapters if c["status"] not in ("planned", "outlined")])
    chapters_final = len([c for c in chapters if c["status"] == "final"])
    
    # Hilos narrativos
    threads = conn.execute("""
        SELECT pt.name, pt.thread_type, pt.status, pt.priority,
               COUNT(tb.id) as beat_count,
               MAX(ch.chapter_number) as last_beat_chapter
        FROM plot_threads pt
        LEFT JOIN thread_beats tb ON pt.id = tb.thread_id
        LEFT JOIN chapters ch ON tb.chapter_id = ch.id
        WHERE pt.project_id = ?
        GROUP BY pt.id
        ORDER BY pt.priority DESC
    """, (project_id,)).fetchall()
    
    active_threads = [dict(t) for t in threads if t["status"] not in ("resolved", "abandoned")]
    resolved_threads = [dict(t) for t in threads if t["status"] == "resolved"]
    
    # Pistas
    clues = conn.execute("""
        SELECT status, COUNT(*) as count
        FROM clues WHERE project_id = ?
        GROUP BY status
    """, (project_id,)).fetchall()
    clue_summary = {c["status"]: c["count"] for c in clues}
    
    # Personajes
    characters = conn.execute("""
        SELECT c.name, c.role, c.status, c.emotional_state,
               l.name as location
        FROM characters c
        LEFT JOIN locations l ON c.current_location_id = l.id
        WHERE c.project_id = ?
        ORDER BY
            CASE c.role WHEN 'protagonist' THEN 1 WHEN 'antagonist' THEN 2 WHEN 'secondary' THEN 3 ELSE 4 END
    """, (project_id,)).fetchall()
    
    # Issues pendientes
    issues = conn.execute("""
        SELECT severity, COUNT(*) as count
        FROM consistency_issues
        WHERE project_id = ? AND resolved = 0
        GROUP BY severity
    """, (project_id,)).fetchall()
    issue_summary = {i["severity"]: i["count"] for i in issues}
    
    # Curva de tensión
    tension_curve = [
        {"chapter": c["chapter_number"], "tension": c["tension_level"], "type": c["scene_type"], "pacing": c["pacing"]}
        for c in chapters if c["tension_level"] is not None
    ]
    
    # Hechos conocidos por el lector vs total
    total_facts = conn.execute(
        "SELECT COUNT(*) FROM story_facts WHERE project_id = ?", (project_id,)
    ).fetchone()[0]
    reader_known = conn.execute(
        "SELECT COUNT(*) FROM story_facts WHERE project_id = ? AND revealed_to_reader_in IS NOT NULL", (project_id,)
    ).fetchone()[0]
    
    dashboard = {
        "project": {
            "name": project["name"],
            "genre": project["genre"],
            "target_words": project["target_word_count"],
            "current_words": total_words,
            "progress_pct": round(total_words / project["target_word_count"] * 100, 1) if project["target_word_count"] else None
        },
        "chapters": {
            "total": len(chapters),
            "written": chapters_written,
            "final": chapters_final,
            "planned": len(chapters) - chapters_written
        },
        "threads": {
            "active": len(active_threads),
            "resolved": len(resolved_threads),
            "details": active_threads
        },
        "clues": clue_summary,
        "characters": [dict(c) for c in characters],
        "tension_curve": tension_curve,
        "story_facts": {
            "total": total_facts,
            "revealed_to_reader": reader_known,
            "hidden_from_reader": total_facts - reader_known
        },
        "consistency_issues": issue_summary,
        "status": "success"
    }
    
    conn.close()
    return dashboard


def format_terminal(data):
    """Formatea el dashboard para terminal con colores ANSI."""
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    RESET = "\033[0m"
    BAR_FULL = "█"
    BAR_EMPTY = "░"

    lines = []

    # Header
    p = data["project"]
    lines.append("")
    lines.append(f"  {BOLD}{CYAN}╔══════════════════════════════════════════════════╗{RESET}")
    lines.append(f"  {BOLD}{CYAN}║{RESET}  {BOLD}{p['name']}{RESET}")
    lines.append(f"  {BOLD}{CYAN}║{RESET}  {DIM}{p['genre'] or 'Sin género'}{RESET}")
    lines.append(f"  {BOLD}{CYAN}╚══════════════════════════════════════════════════╝{RESET}")

    # Progress bar
    ch = data["chapters"]
    words = p["current_words"] or 0
    target = p["target_words"]
    if target:
        pct = min(100, round(words / target * 100))
        bar_len = 30
        filled = int(bar_len * pct / 100)
        bar = BAR_FULL * filled + BAR_EMPTY * (bar_len - filled)
        lines.append(f"\n  {BOLD}Progreso:{RESET} {bar} {pct}%  ({words:,} / {target:,} palabras)")
    else:
        lines.append(f"\n  {BOLD}Palabras:{RESET} {words:,}")
    lines.append(f"  {BOLD}Capítulos:{RESET} {ch['written']} escritos, {ch['final']} finales, {ch['planned']} planeados")

    # Tension curve (sparkline)
    tc = data.get("tension_curve", [])
    if tc:
        spark_chars = " ▁▂▃▄▅▆▇█"
        max_t = max(t["tension"] for t in tc) or 1
        sparkline = ""
        for t in tc:
            idx = int((t["tension"] or 0) / max_t * 8)
            sparkline += spark_chars[idx]
        lines.append(f"\n  {BOLD}Tensión:{RESET}  {sparkline}  {DIM}(cap {tc[0]['chapter']}→{tc[-1]['chapter']}){RESET}")

    # Active threads
    threads = data["threads"]["details"]
    if threads:
        lines.append(f"\n  {BOLD}{MAGENTA}Hilos activos ({len(threads)}):{RESET}")
        for t in threads:
            status_color = GREEN if t["status"] == "developing" else YELLOW if t["status"] == "planted" else RESET
            prio = "!" * min(3, max(1, t["priority"] // 3))
            lines.append(f"    {status_color}●{RESET} {t['name']} {DIM}[{t['status']}] {t['thread_type']} P{t['priority']} beats:{t['beat_count']}{RESET}")

    # Clues
    clues = data.get("clues", {})
    if clues:
        lines.append(f"\n  {BOLD}{YELLOW}Pistas:{RESET}")
        for status, count in clues.items():
            icon = "◆" if status == "active" else "◇" if status == "reinforced" else "✓"
            lines.append(f"    {icon} {status}: {count}")

    # Characters
    chars = data.get("characters", [])
    if chars:
        lines.append(f"\n  {BOLD}{CYAN}Personajes:{RESET}")
        for c in chars:
            status_icon = "●" if c["status"] == "alive" else "✝" if c["status"] == "dead" else "?"
            loc = c.get("location") or "?"
            emo = c.get("emotional_state") or ""
            role_color = GREEN if c["role"] == "protagonist" else RED if c["role"] == "antagonist" else RESET
            lines.append(f"    {status_icon} {role_color}{c['name']}{RESET} {DIM}[{c['role']}] {loc}{RESET}")
            if emo:
                lines.append(f"      {DIM}{emo}{RESET}")

    # Story facts
    sf = data.get("story_facts", {})
    if sf:
        lines.append(f"\n  {BOLD}Hechos narrativos:{RESET} {sf['total']} total, {sf['revealed_to_reader']} revelados al lector, {sf['hidden_from_reader']} ocultos")

    # Issues
    issues = data.get("consistency_issues", {})
    if issues:
        lines.append(f"\n  {BOLD}{RED}Issues de consistencia:{RESET}")
        for sev, count in issues.items():
            sev_color = RED if sev == "critical" else YELLOW if sev == "warning" else DIM
            lines.append(f"    {sev_color}■ {sev}: {count}{RESET}")
    else:
        lines.append(f"\n  {GREEN}✓ Sin issues de consistencia{RESET}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Dashboard del proyecto Narratium")
    parser.add_argument("--project", default=None, help="ID del proyecto")
    parser.add_argument("--db", required=True, help="Ruta a la base de datos SQLite")
    parser.add_argument("--format", choices=["json", "terminal"], default="json",
                        help="Formato de salida (default: json)")

    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(json.dumps({"status": "error", "message": f"DB no encontrada: {args.db}"}))
        sys.exit(1)

    result = generate_dashboard(args.db, args.project)

    if args.format == "terminal":
        print(format_terminal(result))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
