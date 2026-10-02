#!/usr/bin/env python3
"""
SuperNarrative — Exportar manuscrito
Ensambla la novela completa en un único Markdown: portada, índice y
capítulos (desde sus file_path), en orden.

Uso:
  python3 supernarrative.py export                      # exports/<nombre>.md
  python3 supernarrative.py export --output novela.md
"""

import argparse
import json
import os
import re
import sys

from _common import connect, get_project_id, require_db


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "novela"


def export_manuscript(db_path, project_id=None, output=None):
    conn = connect(db_path)
    project_id = get_project_id(conn, project_id)
    project = dict(conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone())

    chapters = conn.execute("""
        SELECT chapter_number, title, status, file_path, word_count, summary
        FROM chapters WHERE project_id = ? AND status != 'planned'
        ORDER BY chapter_order, chapter_number
    """, (project_id,)).fetchall()
    conn.close()

    if not chapters:
        return {"status": "error", "message": "No hay capítulos escritos que exportar."}

    if not output:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(db_path)), "..", "exports")
        os.makedirs(out_dir, exist_ok=True)
        output = os.path.normpath(os.path.join(out_dir, f"{slugify(project['name'])}.md"))

    lines = [f"# {project['name']}", ""]
    if project.get("description"):
        lines += [f"*{project['description']}*", ""]
    lines += ["---", "", "## Índice", ""]
    for ch in chapters:
        title = ch["title"] or f"Capítulo {ch['chapter_number']}"
        lines.append(f"{ch['chapter_number']}. {title}")
    lines += ["", "---", ""]

    missing, total_words = [], 0
    for ch in chapters:
        title = ch["title"] or f"Capítulo {ch['chapter_number']}"
        lines += [f"\n\n## Capítulo {ch['chapter_number']}: {title}" if ch["title"]
                  else f"\n\n## Capítulo {ch['chapter_number']}", ""]
        if ch["file_path"] and os.path.exists(ch["file_path"]):
            with open(ch["file_path"], encoding="utf-8", errors="replace") as f:
                content = f.read().strip()
            lines += [content, ""]
            total_words += len(content.split())
        else:
            missing.append(ch["chapter_number"])
            lines += [f"*[Texto no disponible — file_path: {ch['file_path'] or 'sin asignar'}]*", ""]

    with open(output, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    result = {
        "status": "success",
        "output": output,
        "chapters_exported": len(chapters),
        "words": total_words,
    }
    if missing:
        result["status"] = "success_with_warnings"
        result["chapters_without_file"] = missing
        result["warning"] = ("Algunos capítulos no tienen fichero asociado. Asigna file_path "
                             "al analizarlos (--chapter-file) o con db_ops.")
    return result


def main():
    parser = argparse.ArgumentParser(description="Exportar manuscrito SuperNarrative")
    parser.add_argument("--project", default=None, help="ID del proyecto")
    parser.add_argument("--output", default=None, help="Ruta del Markdown de salida")
    parser.add_argument("--db", required=True, help="Ruta a la base de datos SQLite")
    args = parser.parse_args()

    require_db(args.db)
    result = export_manuscript(args.db, args.project, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
