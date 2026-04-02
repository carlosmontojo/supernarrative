#!/usr/bin/env python3
"""
Narratium — Generador de Context Package
Antes de escribir un capítulo, compila todo el contexto narrativo relevante.
"""

import argparse
import json
import sqlite3
import sys
import os


class ContextGenerator:
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
    
    def get_project(self) -> dict:
        row = self.conn.execute("SELECT * FROM projects WHERE id = ?", (self.project_id,)).fetchone()
        return dict(row) if row else {}
    
    def get_narrative_rules(self) -> list:
        rows = self.conn.execute("""
            SELECT category, rule, priority FROM narrative_rules
            WHERE project_id = ? AND active = 1
            ORDER BY priority DESC
        """, (self.project_id,)).fetchall()
        return [dict(r) for r in rows]
    
    def get_style_references(self) -> list:
        rows = self.conn.execute("""
            SELECT author, work, technique, example_description FROM style_references
            WHERE project_id = ?
        """, (self.project_id,)).fetchall()
        return [dict(r) for r in rows]
    
    def get_world_state(self, up_to_chapter: int) -> dict:
        """Estado del mundo hasta el capítulo N (no inclusive)."""
        
        # Personajes y sus ubicaciones
        characters = self.conn.execute("""
            SELECT c.id, c.name, c.role, c.status, c.emotional_state,
                   l.name as location_name, c.current_location_id
            FROM characters c
            LEFT JOIN locations l ON c.current_location_id = l.id
            WHERE c.project_id = ?
            ORDER BY 
                CASE c.role 
                    WHEN 'protagonist' THEN 1 
                    WHEN 'antagonist' THEN 2 
                    WHEN 'secondary' THEN 3 
                    ELSE 4 
                END
        """, (self.project_id,)).fetchall()
        
        # Objetos relevantes
        objects = self.conn.execute("""
            SELECT o.name, o.status, o.significance,
                   l.name as location_name,
                   c.name as holder_name
            FROM objects o
            LEFT JOIN locations l ON o.current_location_id = l.id
            LEFT JOIN characters c ON o.current_holder_id = c.id
            WHERE o.project_id = ? AND o.status != 'destroyed'
        """, (self.project_id,)).fetchall()
        
        # Último timestamp en la historia
        last_chapter = self.conn.execute("""
            SELECT story_date, story_time_end FROM chapters
            WHERE project_id = ? AND chapter_number < ? AND status != 'planned'
            ORDER BY chapter_number DESC LIMIT 1
        """, (self.project_id, up_to_chapter)).fetchone()
        
        return {
            "characters": [dict(c) for c in characters],
            "objects": [dict(o) for o in objects],
            "last_story_datetime": {
                "date": last_chapter["story_date"] if last_chapter else None,
                "time": last_chapter["story_time_end"] if last_chapter else None
            }
        }
    
    def get_epistemic_state(self, character_ids: list = None) -> dict:
        """Matriz epistémica: qué sabe cada personaje (y el lector)."""
        
        query = """
            SELECT ks.knower_id, c.name as knower_name,
                   sf.description as fact_description, sf.category as fact_category,
                   sf.is_true, ks.knowledge_level, ks.wrong_belief_detail,
                   ks.how_learned, ks.confidence
            FROM knowledge_states ks
            JOIN story_facts sf ON ks.fact_id = sf.id
            LEFT JOIN characters c ON ks.knower_id = c.id
            WHERE ks.project_id = ?
            ORDER BY ks.knower_id, sf.significance DESC
        """
        rows = self.conn.execute(query, (self.project_id,)).fetchall()
        
        # Agrupar por personaje
        by_knower = {}
        for row in rows:
            row = dict(row)
            knower = row["knower_name"] if row["knower_name"] else "LECTOR"
            if knower not in by_knower:
                by_knower[knower] = {"knows": [], "suspects": [], "wrong_beliefs": [], "unaware": []}
            
            level = row["knowledge_level"]
            entry = {
                "fact": row["fact_description"],
                "category": row["fact_category"],
                "is_actually_true": bool(row["is_true"]),
                "how_learned": row["how_learned"],
                "confidence": row["confidence"]
            }
            
            if level == "knows":
                by_knower[knower]["knows"].append(entry)
            elif level == "suspects":
                by_knower[knower]["suspects"].append(entry)
            elif level == "wrong_belief":
                entry["believes_instead"] = row["wrong_belief_detail"]
                by_knower[knower]["wrong_beliefs"].append(entry)
            elif level == "unaware":
                by_knower[knower]["unaware"].append(entry)
        
        return by_knower
    
    def get_active_threads(self) -> list:
        """Hilos narrativos activos con su último beat."""
        rows = self.conn.execute("""
            SELECT pt.id, pt.name, pt.thread_type, pt.status, pt.priority,
                   pt.planted_in_chapter, pt.target_resolution_chapter,
                   pt.notes,
                   tb.beat_type as last_beat_type,
                   tb.description as last_beat_description,
                   tb.chapter_id as last_beat_chapter
            FROM plot_threads pt
            LEFT JOIN (
                SELECT thread_id, beat_type, description, chapter_id,
                       ROW_NUMBER() OVER (PARTITION BY thread_id ORDER BY created_at DESC) as rn
                FROM thread_beats
            ) tb ON pt.id = tb.thread_id AND tb.rn = 1
            WHERE pt.project_id = ? AND pt.status NOT IN ('resolved', 'abandoned')
            ORDER BY pt.priority DESC
        """, (self.project_id,)).fetchall()
        return [dict(r) for r in rows]
    
    def get_active_clues(self) -> list:
        """Pistas activas sin resolver."""
        rows = self.conn.execute("""
            SELECT cl.description, cl.clue_type, cl.subtlety, cl.status,
                   cl.planted_in_chapter, cl.mechanism, cl.intended_resolution,
                   cl.reinforced_in_chapters,
                   pt.name as thread_name
            FROM clues cl
            LEFT JOIN plot_threads pt ON cl.thread_id = pt.id
            WHERE cl.project_id = ? AND cl.status IN ('active', 'reinforced')
            ORDER BY cl.planted_in_chapter ASC
        """, (self.project_id,)).fetchall()
        return [dict(r) for r in rows]
    
    def get_pacing_analysis(self, up_to_chapter: int, lookback: int = 5) -> dict:
        """Análisis de ritmo de los últimos N capítulos."""
        rows = self.conn.execute("""
            SELECT chapter_number, title, scene_type, tension_level, pacing, emotional_tone
            FROM chapters
            WHERE project_id = ? AND chapter_number < ? AND status != 'planned'
            ORDER BY chapter_number DESC
            LIMIT ?
        """, (self.project_id, up_to_chapter, lookback)).fetchall()
        
        recent = [dict(r) for r in rows]
        recent.reverse()  # Orden cronológico
        
        # Sugerencia de ritmo
        suggestion = self._suggest_pacing(recent)
        
        return {
            "recent_chapters": recent,
            "suggestion": suggestion
        }
    
    def _suggest_pacing(self, recent: list) -> dict:
        """Sugiere ritmo para el siguiente capítulo basado en los recientes."""
        if not recent:
            return {"scene_type": "any", "reason": "Primer capítulo — libertad total"}
        
        # Detectar patrones
        scene_types = [c.get("scene_type") for c in recent if c.get("scene_type")]
        tension_levels = [c.get("tension_level") for c in recent if c.get("tension_level")]
        
        suggestion = {}
        
        # Verificar monotonía
        if len(scene_types) >= 3 and len(set(scene_types[-3:])) == 1:
            suggestion["warning"] = f"Llevas 3 capítulos de '{scene_types[-1]}'. Varía el ritmo."
            contrasts = {
                "action": "reflection", "reflection": "action",
                "dialogue": "investigation", "investigation": "revelation",
                "revelation": "dialogue"
            }
            suggestion["suggested_type"] = contrasts.get(scene_types[-1], "action")
        
        # Verificar tensión
        if tension_levels:
            avg_tension = sum(tension_levels) / len(tension_levels)
            last_tension = tension_levels[-1]
            
            if last_tension >= 8:
                suggestion["tension_note"] = "Tensión muy alta — considera un momento de calma antes de la siguiente escalada."
            elif last_tension <= 3 and len(tension_levels) >= 2 and tension_levels[-2] <= 3:
                suggestion["tension_note"] = "Tensión baja prolongada — es momento de introducir conflicto o revelación."
        
        return suggestion
    
    def get_thread_dependencies_warnings(self, chapter_number: int) -> list:
        """Warnings sobre dependencias de hilos que están en riesgo."""
        rows = self.conn.execute("""
            SELECT td.description,
                   dep.name as dependent_thread, dep.status as dependent_status,
                   req.name as required_thread, req.status as required_status,
                   td.required_status
            FROM thread_dependencies td
            JOIN plot_threads dep ON td.dependent_thread_id = dep.id
            JOIN plot_threads req ON td.required_thread_id = req.id
            WHERE dep.project_id = ?
              AND dep.status NOT IN ('resolved', 'abandoned', 'planned')
              AND req.status != td.required_status
        """, (self.project_id,)).fetchall()
        return [dict(r) for r in rows]
    
    def get_stale_clues(self, current_chapter: int, stale_threshold: int = 10) -> list:
        """Pistas que llevan demasiados capítulos sin refuerzo."""
        rows = self.conn.execute("""
            SELECT description, planted_in_chapter, clue_type, thread_id
            FROM clues
            WHERE project_id = ? AND status = 'active'
              AND CAST(planted_in_chapter AS INTEGER) <= ?
        """, (self.project_id, current_chapter - stale_threshold)).fetchall()
        return [dict(r) for r in rows]
    
    def get_dormant_characters(self, current_chapter: int, threshold: int = 5) -> list:
        """Personajes que no aparecen hace muchos capítulos."""
        rows = self.conn.execute("""
            SELECT c.name, c.role, MAX(s.scene_number) as last_scene,
                   ch.chapter_number as last_chapter
            FROM characters c
            LEFT JOIN scenes s ON s.characters_present LIKE '%' || c.id || '%'
            LEFT JOIN chapters ch ON s.chapter_id = ch.id
            WHERE c.project_id = ? AND c.status = 'alive' AND c.role IN ('protagonist', 'antagonist', 'secondary')
            GROUP BY c.id
            HAVING last_chapter IS NULL OR last_chapter <= ?
        """, (self.project_id, current_chapter - threshold)).fetchall()
        return [dict(r) for r in rows]
    
    def generate_context_package(self, chapter_number: int) -> dict:
        """Genera el context package completo para un capítulo."""
        
        project = self.get_project()
        
        package = {
            "project": {
                "name": project.get("name"),
                "genre": project.get("genre"),
                "voice": project.get("narrative_voice"),
                "current_word_count": project.get("current_word_count")
            },
            "chapter_number": chapter_number,
            "narrative_rules": self.get_narrative_rules(),
            "style_references": self.get_style_references(),
            "world_state": self.get_world_state(chapter_number),
            "epistemic_matrix": self.get_epistemic_state(),
            "active_threads": self.get_active_threads(),
            "active_clues": self.get_active_clues(),
            "pacing": self.get_pacing_analysis(chapter_number),
            "warnings": {
                "dependency_violations": self.get_thread_dependencies_warnings(chapter_number),
                "stale_clues": self.get_stale_clues(chapter_number),
                "dormant_characters": self.get_dormant_characters(chapter_number)
            }
        }
        
        return package


def main():
    parser = argparse.ArgumentParser(description="Generar context package para un capítulo")
    parser.add_argument("--chapter", type=int, required=True, help="Número de capítulo a escribir")
    parser.add_argument("--project", default=None, help="ID del proyecto (usa el más reciente si no se especifica)")
    parser.add_argument("--db", required=True, help="Ruta a la base de datos SQLite")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.db):
        print(json.dumps({"status": "error", "message": f"DB no encontrada: {args.db}"}))
        sys.exit(1)
    
    generator = ContextGenerator(args.db, args.project)
    package = generator.generate_context_package(args.chapter)
    
    print(json.dumps(package, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
