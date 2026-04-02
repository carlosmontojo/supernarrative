#!/usr/bin/env python3
"""
Narratium — Motor de Verificación de Consistencia
El "linter" para narrativa. Cruza el estado de la DB contra sí mismo
buscando inconsistencias, plot holes, y problemas.
"""

import argparse
import json
import sqlite3
import sys
import os


class ConsistencyChecker:
    def __init__(self, db_path: str, project_id: str = None):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        
        if project_id:
            self.project_id = project_id
        else:
            row = self.conn.execute("SELECT id FROM projects ORDER BY updated_at DESC LIMIT 1").fetchone()
            if not row:
                raise ValueError("No hay proyectos en la DB")
            self.project_id = row["id"]
        
        self.issues = []
    
    def add_issue(self, issue_type: str, severity: str, description: str,
                  chapter_id: str = None, suggestion: str = None):
        self.issues.append({
            "type": issue_type,
            "severity": severity,
            "description": description,
            "chapter_id": chapter_id,
            "suggestion": suggestion
        })
    
    def check_epistemic_violations(self):
        """Buscar personajes que podrían estar actuando con info que no tienen."""
        # Hechos que nadie le ha dicho a ciertos personajes pero que deberían saber
        # Esto es heurístico — marca sospecha, no certeza
        
        # Personajes con knowledge_level = "unaware" de hechos con significance >= 7
        rows = self.conn.execute("""
            SELECT c.name, sf.description, sf.significance, ks.knowledge_level
            FROM knowledge_states ks
            JOIN characters c ON ks.knower_id = c.id
            JOIN story_facts sf ON ks.fact_id = sf.id
            WHERE ks.project_id = ? AND ks.knowledge_level = 'unaware' AND sf.significance >= 7
              AND c.role IN ('protagonist', 'antagonist', 'secondary')
        """, (self.project_id,)).fetchall()
        
        for row in rows:
            self.add_issue(
                "epistemic", "suggestion",
                f"{row['name']} desconoce '{row['description']}' (significancia: {row['significance']}). Verificar si esto es intencional.",
                suggestion="Si el personaje debería saberlo, actualizar la matriz epistémica."
            )
    
    def check_dead_characters_appearing(self):
        """Personajes muertos que aparecen en escenas posteriores a su muerte."""
        dead = self.conn.execute("""
            SELECT c.id, c.name, ch.chapter_number as died_in
            FROM characters c
            JOIN world_events we ON we.affected_entities LIKE '%' || c.id || '%'
            JOIN chapters ch ON we.chapter_id = ch.id
            WHERE c.project_id = ? AND c.status = 'dead' AND we.event_type = 'death'
        """, (self.project_id,)).fetchall()
        
        for char in dead:
            # Buscar apariciones posteriores
            appearances = self.conn.execute("""
                SELECT ch.chapter_number
                FROM scenes s
                JOIN chapters ch ON s.chapter_id = ch.id
                WHERE s.characters_present LIKE ? AND ch.chapter_number > ?
            """, (f'%{char["id"]}%', char["died_in"])).fetchall()
            
            for app in appearances:
                if app["chapter_number"] > char["died_in"]:
                    self.add_issue(
                        "continuity", "critical",
                        f"{char['name']} murió en capítulo {char['died_in']} pero aparece en capítulo {app['chapter_number']}.",
                        suggestion="Eliminar la aparición o cambiarla a flashback/recuerdo."
                    )
    
    def check_thread_dependencies(self):
        """Verificar que no se violan dependencias entre hilos."""
        rows = self.conn.execute("""
            SELECT td.description,
                   dep.name as dependent_thread, dep.status as dependent_status,
                   req.name as required_thread, req.status as required_status,
                   td.required_status
            FROM thread_dependencies td
            JOIN plot_threads dep ON td.dependent_thread_id = dep.id
            JOIN plot_threads req ON td.required_thread_id = req.id
            WHERE dep.project_id = ?
        """, (self.project_id,)).fetchall()
        
        for row in rows:
            dep_status_order = ["planned", "planted", "developing", "climax", "resolved"]
            req_status_order = dep_status_order
            
            dep_idx = dep_status_order.index(row["dependent_status"]) if row["dependent_status"] in dep_status_order else -1
            req_idx = req_status_order.index(row["required_status"]) if row["required_status"] in req_status_order else -1
            actual_req_idx = req_status_order.index(row["required_status"]) if row["required_status"] in req_status_order else -1
            
            # Si el hilo dependiente está más avanzado que lo que el requerido permite
            if dep_idx > 1 and row["required_status"] != row["required_status"]:  # simplified check
                current_req = req_status_order.index(row["required_status"]) if row["required_status"] in req_status_order else -1
                if row["required_status"] != row["required_status"]:
                    self.add_issue(
                        "dependency", "warning",
                        f"'{row['dependent_thread']}' requiere que '{row['required_thread']}' esté en estado '{row['required_status']}' (actualmente: '{row['required_status']}').",
                        suggestion=row["description"]
                    )
    
    def check_abandoned_clues(self, stale_threshold: int = 10):
        """Pistas que llevan demasiados capítulos sin refuerzo ni resolución."""
        max_chapter = self.conn.execute(
            "SELECT MAX(chapter_number) FROM chapters WHERE project_id = ? AND status != 'planned'",
            (self.project_id,)
        ).fetchone()[0] or 0
        
        rows = self.conn.execute("""
            SELECT c.description, c.planted_in_chapter, c.clue_type, c.subtlety,
                   pt.name as thread_name, c.reinforced_in_chapters
            FROM clues c
            LEFT JOIN plot_threads pt ON c.thread_id = pt.id
            WHERE c.project_id = ? AND c.status = 'active'
        """, (self.project_id,)).fetchall()
        
        for row in rows:
            planted_ch = row["planted_in_chapter"]
            if planted_ch:
                # Intentar obtener el chapter_number
                ch_row = self.conn.execute(
                    "SELECT chapter_number FROM chapters WHERE id = ?", (planted_ch,)
                ).fetchone()
                planted_num = ch_row["chapter_number"] if ch_row else 0
                
                if max_chapter - planted_num >= stale_threshold:
                    thread_info = f" (hilo: {row['thread_name']})" if row["thread_name"] else ""
                    self.add_issue(
                        "clue", "warning",
                        f"Pista abandonada{thread_info}: '{row['description']}' plantada hace {max_chapter - planted_num} capítulos sin resolver ni reforzar.",
                        suggestion="Reforzar la pista, resolverla, o marcarla como red herring."
                    )
    
    def check_pacing_monotony(self, threshold: int = 3):
        """Detectar monotonía en el ritmo."""
        rows = self.conn.execute("""
            SELECT chapter_number, scene_type, tension_level, pacing
            FROM chapters
            WHERE project_id = ? AND status != 'planned' AND scene_type IS NOT NULL
            ORDER BY chapter_number
        """, (self.project_id,)).fetchall()
        
        if len(rows) < threshold:
            return
        
        # Verificar tipos de escena repetidos
        for i in range(len(rows) - threshold + 1):
            window = rows[i:i + threshold]
            types = [r["scene_type"] for r in window]
            if len(set(types)) == 1:
                self.add_issue(
                    "pacing", "warning",
                    f"Capítulos {window[0]['chapter_number']}-{window[-1]['chapter_number']}: todos son '{types[0]}'. Monotonía de ritmo.",
                    suggestion=f"Introducir variación. Después de '{types[0]}' prueba con un tipo diferente."
                )
        
        # Verificar tensión plana
        tensions = [r["tension_level"] for r in rows if r["tension_level"]]
        if len(tensions) >= 5:
            last_5 = tensions[-5:]
            avg = sum(last_5) / len(last_5)
            variance = sum((t - avg) ** 2 for t in last_5) / len(last_5)
            if variance < 1.5:
                self.add_issue(
                    "pacing", "suggestion",
                    f"La tensión de los últimos 5 capítulos es muy uniforme (promedio: {avg:.1f}, varianza: {variance:.1f}). La narrativa puede sentirse plana.",
                    suggestion="Introducir un pico de tensión o un valle deliberado para crear contraste."
                )
    
    def check_dormant_characters(self, threshold: int = 7):
        """Personajes importantes que no aparecen hace mucho."""
        max_chapter = self.conn.execute(
            "SELECT MAX(chapter_number) FROM chapters WHERE project_id = ? AND status != 'planned'",
            (self.project_id,)
        ).fetchone()[0] or 0
        
        rows = self.conn.execute("""
            SELECT c.name, c.role,
                   MAX(ch.chapter_number) as last_appearance
            FROM characters c
            LEFT JOIN scenes s ON s.characters_present LIKE '%' || c.id || '%'
            LEFT JOIN chapters ch ON s.chapter_id = ch.id
            WHERE c.project_id = ? AND c.status = 'alive' AND c.role IN ('protagonist', 'secondary', 'antagonist')
            GROUP BY c.id
        """, (self.project_id,)).fetchall()
        
        for row in rows:
            last = row["last_appearance"] or 0
            if max_chapter - last >= threshold:
                self.add_issue(
                    "continuity", "suggestion",
                    f"{row['name']} ({row['role']}) no aparece desde el capítulo {last}. Llevan {max_chapter - last} capítulos ausente.",
                    suggestion="Reintroducir al personaje o justificar su ausencia narrativamente."
                )
    
    def check_wrong_beliefs_unresolved(self):
        """Personajes con creencias erróneas que nunca se corrigen."""
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
                f"{row['name']} cree erróneamente que '{row['wrong_belief_detail']}' (la verdad: '{row['fact']}'). Asegurar que esto se resuelve eventualmente.",
                suggestion="Planear una escena de revelación o confrontación con la verdad."
            )
    
    def run_all_checks(self) -> dict:
        """Ejecutar todas las verificaciones."""
        self.issues = []
        
        self.check_epistemic_violations()
        self.check_dead_characters_appearing()
        self.check_thread_dependencies()
        self.check_abandoned_clues()
        self.check_pacing_monotony()
        self.check_dormant_characters()
        self.check_wrong_beliefs_unresolved()
        
        # Guardar issues en la DB
        for issue in self.issues:
            self.conn.execute("""
                INSERT INTO consistency_issues (project_id, chapter_id, issue_type, severity, description, suggestion)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.project_id, issue.get("chapter_id"),
                issue["type"], issue["severity"],
                issue["description"], issue.get("suggestion")
            ))
        
        self.conn.commit()
        
        # Resumen
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
            "issues": self.issues
        }


def main():
    parser = argparse.ArgumentParser(description="Verificar consistencia narrativa")
    parser.add_argument("--chapter", type=int, default=None, help="Verificar capítulo específico (default: toda la novela)")
    parser.add_argument("--project", default=None, help="ID del proyecto")
    parser.add_argument("--db", required=True, help="Ruta a la base de datos SQLite")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.db):
        print(json.dumps({"status": "error", "message": f"DB no encontrada: {args.db}"}))
        sys.exit(1)
    
    checker = ConsistencyChecker(args.db, args.project)
    result = checker.run_all_checks()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
