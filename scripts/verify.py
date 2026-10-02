#!/usr/bin/env python3
"""
SuperNarrative — Motor de Verificación de Consistencia
El "linter" para narrativa. Cruza el estado de la DB contra sí mismo
buscando inconsistencias, plot holes, y problemas.

v0.2:
  - El chequeo de dependencias entre hilos FUNCIONA (en v0.1 una colisión
    de alias SQL lo dejaba muerto: nunca había saltado).
  - Cada ejecución reemplaza los issues automáticos sin resolver, en vez de
    duplicarlos sin fin.
  - El chequeo de personajes muertos usa escenas Y eventos del mundo.
"""

import argparse
import json
import sys

from _common import connect, get_project_id, require_db

STATUS_ORDER = ["planned", "planted", "developing", "climax", "resolved"]


def status_index(status):
    return STATUS_ORDER.index(status) if status in STATUS_ORDER else -1


class ConsistencyChecker:
    def __init__(self, db_path, project_id=None):
        self.conn = connect(db_path)
        self.project_id = get_project_id(self.conn, project_id)
        self.issues = []

    def add_issue(self, issue_type, severity, description,
                  chapter_id=None, suggestion=None):
        self.issues.append({
            "type": issue_type, "severity": severity,
            "description": description, "chapter_id": chapter_id,
            "suggestion": suggestion,
        })

    def check_epistemic_flags(self):
        """Personajes principales que desconocen hechos muy significativos.
        Heurístico: marca para revisión, no certeza."""
        rows = self.conn.execute("""
            SELECT c.name, sf.description, sf.significance
            FROM knowledge_states ks
            JOIN characters c ON ks.knower_id = c.id
            JOIN story_facts sf ON ks.fact_id = sf.id
            WHERE ks.project_id = ? AND ks.knowledge_level = 'unaware'
              AND sf.significance >= 7
              AND c.role IN ('protagonist', 'antagonist', 'secondary')
        """, (self.project_id,)).fetchall()
        for row in rows:
            self.add_issue(
                "epistemic", "suggestion",
                f"{row['name']} desconoce '{row['description']}' "
                f"(significancia: {row['significance']}). Verificar si es intencional.",
                suggestion="Si el personaje debería saberlo, actualizar la matriz epistémica.")

    def check_dead_characters_appearing(self):
        """Personajes muertos que aparecen después de su muerte (en escenas
        o como afectados por eventos posteriores)."""
        dead = self.conn.execute("""
            SELECT c.id, c.name, MIN(ch.chapter_number) as died_in
            FROM characters c
            JOIN world_events we ON we.event_type = 'death'
                AND we.affected_entities LIKE '%"' || c.id || '"%'
            JOIN chapters ch ON we.chapter_id = ch.id
            WHERE c.project_id = ? AND c.status = 'dead'
            GROUP BY c.id
        """, (self.project_id,)).fetchall()

        for char in dead:
            appearances = self.conn.execute("""
                SELECT DISTINCT ch.chapter_number FROM scenes s
                JOIN chapters ch ON s.chapter_id = ch.id
                WHERE s.characters_present LIKE ? AND ch.chapter_number > ?
                UNION
                SELECT DISTINCT ch.chapter_number FROM world_events we
                JOIN chapters ch ON we.chapter_id = ch.id
                WHERE we.event_type != 'death'
                  AND we.affected_entities LIKE ? AND ch.chapter_number > ?
            """, (f'%"{char["id"]}"%', char["died_in"],
                  f'%"{char["id"]}"%', char["died_in"])).fetchall()
            for app in appearances:
                self.add_issue(
                    "continuity", "critical",
                    f"{char['name']} murió en capítulo {char['died_in']} "
                    f"pero aparece en capítulo {app['chapter_number']}.",
                    suggestion="Eliminar la aparición o cambiarla a flashback/recuerdo.")

    def check_thread_dependencies(self):
        """Un hilo dependiente no debe avanzar más allá de lo que permite el
        estado del hilo del que depende."""
        rows = self.conn.execute("""
            SELECT td.description as dep_description,
                   dep.name as dependent_name, dep.status as dependent_status,
                   req.name as required_name, req.status as actual_status,
                   td.required_status as needed_status
            FROM thread_dependencies td
            JOIN plot_threads dep ON td.dependent_thread_id = dep.id
            JOIN plot_threads req ON td.required_thread_id = req.id
            WHERE dep.project_id = ?
        """, (self.project_id,)).fetchall()

        for row in rows:
            dep_idx = status_index(row["dependent_status"])
            actual_idx = status_index(row["actual_status"])
            needed_idx = status_index(row["needed_status"])
            # Violación: el dependiente ya está en marcha (developing+) pero
            # el requerido aún no alcanzó el estado exigido.
            if dep_idx >= status_index("developing") and actual_idx < needed_idx:
                severity = "critical" if dep_idx >= status_index("climax") else "warning"
                self.add_issue(
                    "dependency", severity,
                    f"'{row['dependent_name']}' está en '{row['dependent_status']}' pero requiere "
                    f"que '{row['required_name']}' alcance '{row['needed_status']}' "
                    f"(actualmente: '{row['actual_status']}').",
                    suggestion=row["dep_description"] or
                    "Avanzar el hilo requerido antes, o revisar la dependencia.")

    def check_abandoned_clues(self, stale_threshold=10):
        max_chapter = self.conn.execute(
            "SELECT MAX(chapter_number) FROM chapters WHERE project_id = ? AND status != 'planned'",
            (self.project_id,)).fetchone()[0] or 0

        rows = self.conn.execute("""
            SELECT c.description, c.planted_in_chapter, c.reinforced_in_chapters,
                   pt.name as thread_name
            FROM clues c
            LEFT JOIN plot_threads pt ON c.thread_id = pt.id
            WHERE c.project_id = ? AND c.status IN ('active', 'reinforced')
        """, (self.project_id,)).fetchall()

        for row in rows:
            try:
                planted = int(row["planted_in_chapter"])
            except (TypeError, ValueError):
                continue
            # El último refuerzo también cuenta como actividad
            last_activity = planted
            try:
                reinforced = json.loads(row["reinforced_in_chapters"] or "[]")
                nums = [int(x) for x in reinforced if str(x).isdigit()]
                if nums:
                    last_activity = max(last_activity, max(nums))
            except (ValueError, json.JSONDecodeError):
                pass
            if max_chapter - last_activity >= stale_threshold:
                thread_info = f" (hilo: {row['thread_name']})" if row["thread_name"] else ""
                self.add_issue(
                    "clue", "warning",
                    f"Pista abandonada{thread_info}: '{row['description']}' sin actividad "
                    f"desde el capítulo {last_activity} ({max_chapter - last_activity} capítulos).",
                    suggestion="Reforzar la pista, resolverla, o marcarla como red herring.")

    def check_pacing_monotony(self, threshold=3):
        rows = self.conn.execute("""
            SELECT chapter_number, scene_type, tension_level
            FROM chapters
            WHERE project_id = ? AND status != 'planned' AND scene_type IS NOT NULL
            ORDER BY chapter_number
        """, (self.project_id,)).fetchall()

        if len(rows) >= threshold:
            for i in range(len(rows) - threshold + 1):
                window = rows[i:i + threshold]
                types = [r["scene_type"] for r in window]
                if len(set(types)) == 1:
                    self.add_issue(
                        "pacing", "warning",
                        f"Capítulos {window[0]['chapter_number']}-{window[-1]['chapter_number']}: "
                        f"todos son '{types[0]}'. Monotonía de ritmo.",
                        suggestion="Introducir variación de tipo de escena.")

        tensions = [r["tension_level"] for r in rows if r["tension_level"]]
        if len(tensions) >= 5:
            last_5 = tensions[-5:]
            avg = sum(last_5) / len(last_5)
            variance = sum((t - avg) ** 2 for t in last_5) / len(last_5)
            if variance < 1.5:
                self.add_issue(
                    "pacing", "suggestion",
                    f"La tensión de los últimos 5 capítulos es muy uniforme "
                    f"(promedio: {avg:.1f}, varianza: {variance:.1f}).",
                    suggestion="Introducir un pico o un valle deliberado para crear contraste.")

    def check_dormant_characters(self, threshold=7):
        max_chapter = self.conn.execute(
            "SELECT MAX(chapter_number) FROM chapters WHERE project_id = ? AND status != 'planned'",
            (self.project_id,)).fetchone()[0] or 0

        rows = self.conn.execute("""
            SELECT c.name, c.role, MAX(ch.chapter_number) as last_appearance
            FROM characters c
            LEFT JOIN scenes s ON s.characters_present LIKE '%"' || c.id || '"%'
            LEFT JOIN chapters ch ON s.chapter_id = ch.id
            WHERE c.project_id = ? AND c.status = 'alive'
              AND c.role IN ('protagonist', 'secondary', 'antagonist')
            GROUP BY c.id
        """, (self.project_id,)).fetchall()

        for row in rows:
            last = row["last_appearance"] or 0
            if max_chapter - last >= threshold:
                self.add_issue(
                    "continuity", "suggestion",
                    f"{row['name']} ({row['role']}) no aparece desde el capítulo {last}. "
                    f"Lleva {max_chapter - last} capítulos ausente.",
                    suggestion="Reintroducir al personaje o justificar su ausencia.")

    def check_wrong_beliefs_unresolved(self):
        rows = self.conn.execute("""
            SELECT c.name, sf.description as fact, ks.wrong_belief_detail
            FROM knowledge_states ks
            JOIN characters c ON ks.knower_id = c.id
            JOIN story_facts sf ON ks.fact_id = sf.id
            WHERE ks.project_id = ? AND ks.knowledge_level = 'wrong_belief'
              AND c.role IN ('protagonist', 'secondary')
        """, (self.project_id,)).fetchall()
        for row in rows:
            self.add_issue(
                "epistemic", "suggestion",
                f"{row['name']} cree erróneamente que '{row['wrong_belief_detail']}' "
                f"(la verdad: '{row['fact']}'). Asegurar que se resuelve.",
                suggestion="Planear una escena de revelación o confrontación con la verdad.")

    def check_overdue_threads(self):
        """Hilos que pasaron su capítulo objetivo de resolución."""
        max_chapter = self.conn.execute(
            "SELECT MAX(chapter_number) FROM chapters WHERE project_id = ? AND status != 'planned'",
            (self.project_id,)).fetchone()[0] or 0
        rows = self.conn.execute("""
            SELECT name, status, target_resolution_chapter
            FROM plot_threads
            WHERE project_id = ? AND status NOT IN ('resolved', 'abandoned')
              AND target_resolution_chapter IS NOT NULL
        """, (self.project_id,)).fetchall()
        for row in rows:
            try:
                target = int(row["target_resolution_chapter"])
            except (TypeError, ValueError):
                continue
            if max_chapter > target:
                self.add_issue(
                    "plot_hole", "warning",
                    f"El hilo '{row['name']}' debía resolverse hacia el capítulo {target} "
                    f"y sigue '{row['status']}' en el capítulo {max_chapter}.",
                    suggestion="Resolverlo, reprogramar su objetivo, o abandonarlo explícitamente.")

    def run_all_checks(self):
        self.issues = []
        self.check_epistemic_flags()
        self.check_dead_characters_appearing()
        self.check_thread_dependencies()
        self.check_abandoned_clues()
        self.check_pacing_monotony()
        self.check_dormant_characters()
        self.check_wrong_beliefs_unresolved()
        self.check_overdue_threads()

        # Reemplazar los issues automáticos sin resolver (evita duplicados
        # acumulados ejecución tras ejecución; los resueltos se conservan)
        self.conn.execute(
            "DELETE FROM consistency_issues WHERE project_id = ? AND resolved = 0",
            (self.project_id,))
        for issue in self.issues:
            self.conn.execute("""
                INSERT INTO consistency_issues (project_id, chapter_id, issue_type,
                    severity, description, suggestion)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.project_id, issue.get("chapter_id"), issue["type"],
                  issue["severity"], issue["description"], issue.get("suggestion")))
        self.conn.commit()

        critical = len([i for i in self.issues if i["severity"] == "critical"])
        warnings = len([i for i in self.issues if i["severity"] == "warning"])
        suggestions = len([i for i in self.issues if i["severity"] == "suggestion"])
        return {
            "status": "success",
            "total_issues": len(self.issues),
            "critical": critical,
            "warnings": warnings,
            "suggestions": suggestions,
            "is_consistent": critical == 0,
            "issues": self.issues,
        }


def main():
    parser = argparse.ArgumentParser(description="Verificar consistencia narrativa")
    parser.add_argument("--chapter", type=int, default=None,
                        help="Contexto informativo; los checks estructurales son globales. "
                             "La verificación por capítulo del texto la hace el LLM con prompts/verification.md")
    parser.add_argument("--project", default=None, help="ID del proyecto")
    parser.add_argument("--db", required=True, help="Ruta a la base de datos SQLite")
    args = parser.parse_args()

    require_db(args.db)
    checker = ConsistencyChecker(args.db, args.project)
    result = checker.run_all_checks()
    if args.chapter is not None:
        result["note"] = (f"Checks estructurales globales tras el capítulo {args.chapter}. "
                          "Para verificar el TEXTO del capítulo, usar prompts/verification.md con el LLM.")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
