#!/usr/bin/env python3
"""
SuperNarrative — Tests end-to-end del pipeline completo.

Sin dependencias: stdlib + los propios scripts, ejercitados por su interfaz
CLI real (igual que los usaría un autor o Claude Code).

Ejecutar:  python3 tests/test_pipeline.py
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, "supernarrative.py")


def run(args, expect_ok=True):
    """Ejecuta el CLI y devuelve el JSON del stdout."""
    result = subprocess.run([sys.executable, CLI] + args,
                            capture_output=True, text=True, cwd=ROOT)
    if expect_ok and result.returncode != 0:
        raise AssertionError(
            f"Comando falló: {args}\nstdout: {result.stdout}\nstderr: {result.stderr}")
    out = result.stdout.strip()
    # El CLI imprime JSON; tolerar líneas de aviso previas
    start = out.find("{")
    return json.loads(out[start:]) if start >= 0 else {}


class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db = os.path.join(cls.tmp.name, "test.db")

        # init crea la DB automáticamente desde el schema
        out = run(["init", "--db", cls.db, "--name", "Test Novel",
                   "--genre", "mystery", "--target-words", "80000"])
        assert out["status"] == "success", out
        cls.project_id = out["project_id"]

        def ops(action, data=None):
            args = ["ops", "--db", cls.db, "--action", action]
            if data is not None:
                args += ["--data", json.dumps(data)]
            return run(args)

        cls.ops = staticmethod(ops)
        ops("add_character", {"name": "Alice", "full_name": "Alice Moreau",
                              "role": "protagonist", "aliases": ["la detective"]})
        ops("add_character", {"name": "Bob", "role": "antagonist"})
        ops("add_character", {"name": "Clara", "role": "secondary"})
        ops("add_fact", {"description": "Bob mató a la víctima", "category": "event",
                         "significance": 9})
        ops("set_knowledge", {"character": "Alice", "fact": "Bob mató a la víctima",
                              "knowledge_level": "suspects"})
        ops("set_knowledge", {"character": "lector", "fact": "Bob mató a la víctima",
                              "knowledge_level": "knows"})
        ops("add_thread", {"name": "El misterio del faro", "thread_type": "mystery",
                           "priority": 9})
        ops("add_thread", {"name": "La revelación final", "thread_type": "main_plot",
                           "priority": 10, "status": "developing"})
        ops("add_dependency", {"dependent": "La revelación final",
                               "required": "El misterio del faro",
                               "required_status": "resolved"})

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def analysis_for_chapter(self, extra=None):
        analysis = {
            "summary": "Alice encuentra el cuaderno del faro.",
            "events": [{"type": "discovery",
                        "description": "Alice encuentra un cuaderno oculto",
                        "affected_characters": ["Alice"],
                        "affected_objects": ["cuaderno"]}],
            "knowledge_changes": [{"character_name": "Alice",
                                   "fact": "El farero dejó un cuaderno con fechas",
                                   "new_knowledge_level": "knows",
                                   "how_learned": "witnessed"}],
            "reader_knowledge_changes": [{"fact": "El cuaderno menciona a Bob",
                                          "new_knowledge_level": "suspects"}],
            "thread_beats": [{"thread_name": "El misterio del faro",
                              "beat_type": "plant",
                              "description": "Aparece el cuaderno"}],
            "clues": [{"description": "La tinta del cuaderno es reciente",
                       "type": "object", "subtlety": 8,
                       "related_thread": "El misterio del faro"}],
            "character_locations_end": [{"character_name": "Alice", "location": "El faro"}],
            "character_emotional_states": [{"character_name": "Alice",
                                            "emotional_state": "intrigada"}],
            "scenes": [{"scene_number": 1, "location": "El faro",
                        "characters_present": ["Alice", "Clara"],
                        "summary": "Registro del faro", "purpose": "plant_clue"}],
            "tension_level": 6, "scene_type": "investigation",
            "pacing": "medium", "emotional_tone": "paranoid",
            "opening_hook": "La puerta del faro está abierta",
            "closing_hook": "Una fecha del cuaderno es mañana",
            "word_count": 2500,
        }
        if extra:
            analysis.update(extra)
        return analysis

    def apply_chapter(self, number, analysis):
        path = os.path.join(self.tmp.name, f"analysis_{number}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False)
        out = run(["analyze", "--db", self.db, "--chapter", str(number),
                   "--analysis-json", path])
        self.assertEqual(out["status"], "pending", out)
        return run(["update", "--db", self.db, "--chapter", str(number), "--confirm"])

    def test_01_full_chapter_cycle(self):
        out = self.apply_chapter(1, self.analysis_for_chapter())
        self.assertIn(out["status"], ("success", "success_with_warnings"), out)
        self.assertNotIn("unmatched", out, "No debería haber nombres sin resolver")
        self.assertTrue(any("scenes" in c for c in out["changes_applied"]), out)
        self.assertTrue(any("emotional_states" in c for c in out["changes_applied"]), out)

    def test_02_unmatched_names_are_reported(self):
        analysis = self.analysis_for_chapter(
            {"knowledge_changes": [{"character_name": "PersonajeInexistente",
                                    "fact": "algo", "new_knowledge_level": "knows"}]})
        out = self.apply_chapter(2, analysis)
        self.assertEqual(out["status"], "success_with_warnings", out)
        self.assertIn("PersonajeInexistente", out["unmatched"]["characters"])

    def test_03_chapter_numbers_not_ids(self):
        """Las columnas *_in_chapter deben guardar números, no IDs hex."""
        out = run(["ops", "--db", self.db, "--action", "query", "--sql",
                   "SELECT planted_in_chapter FROM clues"])
        for row in out["rows"]:
            self.assertTrue(str(row["planted_in_chapter"]).isdigit(), row)

    def test_04_context_package(self):
        out = run(["context", "--db", self.db, "--chapter", "3"])
        self.assertIn("epistemic_matrix", out)
        self.assertIn("character_sheets", out)
        self.assertIn("recent_events", out)
        self.assertIn("Alice", out["epistemic_matrix"])
        self.assertIn("LECTOR", out["epistemic_matrix"])
        self.assertTrue(len(out["recent_events"]) >= 1, "Los eventos deben llegar al contexto")

    def test_05_dependency_check_fires(self):
        """'La revelación final' está developing con su requisito sin resolver:
        el chequeo (muerto en v0.1) debe saltar."""
        out = run(["verify", "--db", self.db])
        dep_issues = [i for i in out["issues"] if i["type"] == "dependency"]
        self.assertTrue(dep_issues, f"El chequeo de dependencias no saltó: {out}")

    def test_06_verify_does_not_duplicate(self):
        first = run(["verify", "--db", self.db])["total_issues"]
        second = run(["verify", "--db", self.db])["total_issues"]
        self.assertEqual(first, second)
        out = run(["ops", "--db", self.db, "--action", "query", "--sql",
                   "SELECT COUNT(*) as n FROM consistency_issues WHERE resolved = 0"])
        self.assertEqual(out["rows"][0]["n"], second,
                         "La DB no debe acumular issues duplicados")

    def test_07_dead_character_reappearing(self):
        self.apply_chapter(3, self.analysis_for_chapter(
            {"events": [{"type": "death", "description": "Clara muere",
                         "affected_characters": ["Clara"]}],
             "scenes": [], "clues": [], "thread_beats": []}))
        self.apply_chapter(4, self.analysis_for_chapter(
            {"scenes": [{"scene_number": 1, "location": "El faro",
                         "characters_present": ["Clara"],
                         "summary": "Clara reaparece", "purpose": "advance_plot"}],
             "clues": [], "thread_beats": [], "events": []}))
        out = run(["verify", "--db", self.db])
        critical = [i for i in out["issues"]
                    if i["severity"] == "critical" and "Clara" in i["description"]]
        self.assertTrue(critical, f"No detectó al personaje muerto reapareciendo: {out}")

    def test_08_search(self):
        out = run(["search", "--db", self.db, "--action", "who_knows",
                   "--query", "cuaderno"])
        self.assertTrue(out["results"], out)
        out = run(["search", "--db", self.db, "--action", "who_knows_about",
                   "--query", "Alice"])
        self.assertGreaterEqual(out["total_facts"], 2)
        out = run(["search", "--db", self.db, "--action", "active_clues"])
        self.assertGreaterEqual(out["total"], 1)

    def test_09_dashboard_and_alias_resolution(self):
        out = run(["dashboard", "--db", self.db])
        self.assertEqual(out["status"], "success")
        self.assertGreaterEqual(out["chapters"]["written"], 1)
        # Resolución por alias
        analysis = self.analysis_for_chapter(
            {"knowledge_changes": [{"character_name": "la detective",
                                    "fact": "Los aliases funcionan",
                                    "new_knowledge_level": "knows"}],
             "scenes": [], "clues": [], "thread_beats": [], "events": []})
        out = self.apply_chapter(5, analysis)
        self.assertNotIn("unmatched", out, f"El alias debería resolverse: {out}")

    def test_10_snapshot_and_export(self):
        out = run(["snapshot", "--db", self.db])
        self.assertEqual(out["status"], "success")
        out = run(["snapshot", "--db", self.db, "--list"])
        self.assertGreaterEqual(out["total"], 1)

        chapter_file = os.path.join(self.tmp.name, "cap1.md")
        with open(chapter_file, "w", encoding="utf-8") as f:
            f.write("La puerta del faro estaba abierta cuando Alice llegó.")
        run(["ops", "--db", self.db, "--action", "query", "--sql", "SELECT 1"])
        import sqlite3
        conn = sqlite3.connect(self.db)
        conn.execute("UPDATE chapters SET file_path = ? WHERE chapter_number = 1",
                     (chapter_file,))
        conn.commit()
        conn.close()
        out = run(["export", "--db", self.db,
                   "--output", os.path.join(self.tmp.name, "novela.md")])
        self.assertIn(out["status"], ("success", "success_with_warnings"))
        with open(os.path.join(self.tmp.name, "novela.md"), encoding="utf-8") as f:
            manuscript = f.read()
        self.assertIn("La puerta del faro", manuscript)

    def test_11_migrate_legacy_db(self):
        """Una DB con IDs hex en *_in_chapter (formato v0.1) queda corregida."""
        import sqlite3
        conn = sqlite3.connect(self.db)
        ch_id = conn.execute(
            "SELECT id FROM chapters WHERE chapter_number = 1").fetchone()[0]
        conn.execute(
            "UPDATE clues SET planted_in_chapter = ? WHERE planted_in_chapter = 1",
            (ch_id,))
        conn.commit()
        conn.close()
        out = run(["migrate", "--db", self.db])
        self.assertEqual(out["status"], "success")
        self.assertTrue(out["total_values_fixed"] >= 1, out)
        check = run(["ops", "--db", self.db, "--action", "query", "--sql",
                     "SELECT planted_in_chapter FROM clues"])
        for row in check["rows"]:
            self.assertTrue(str(row["planted_in_chapter"]).isdigit(), row)


if __name__ == "__main__":
    unittest.main(verbosity=2)
