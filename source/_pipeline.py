#!/usr/bin/env python3
"""Post-chapter pipeline: lint -> analyze -> update -> extras (word count, scenes,
status changes, object moves) -> verify. Usage: _pipeline.py N"""
import json, re, subprocess, sqlite3, sys
n = int(sys.argv[1]); db = "db/narratium.db"
chf = f"source/chapter_{n:02d}.md"; an = f"source/analysis/ch{n:02d}.json"
text = open(chf).read(); wc = len(text.split())
lint = {"words": wc, "em_dashes": text.count("—"), "like_a": len(re.findall(r" like an? ", text)), "as_if": text.count(" as if ")}
a = json.load(open(an)); a["word_count"] = wc; json.dump(a, open(an, "w"), indent=1, ensure_ascii=False)
r = subprocess.run([sys.executable, "scripts/analyze.py", "--chapter", str(n), "--db", db, "--analysis-json", an, "--chapter-file", chf], capture_output=True, text=True)
if '"status": "error"' in r.stdout: print(r.stdout); sys.exit(1)
r = subprocess.run([sys.executable, "scripts/update.py", "--chapter", str(n), "--db", db, "--confirm"], capture_output=True, text=True)
upd = json.loads(r.stdout)
c = sqlite3.connect(db)
c.execute("UPDATE chapters SET word_count=?, status='draft', file_path=?, title=COALESCE(title,?) WHERE chapter_number=?", (wc, chf, a.get("title"), n))
if a.get("story_date"): c.execute("UPDATE chapters SET story_date=? WHERE chapter_number=?", (a["story_date"], n))
sc = a.get("status_changes", {}); sc = {d["character_name"]: d["status"] for d in sc} if isinstance(sc, list) else sc
for nm, st in sc.items(): c.execute("UPDATE characters SET status=? WHERE name=?", (st, nm))
for es in a.get("character_emotional_states", []): c.execute("UPDATE characters SET emotional_state=? WHERE name=?", (es["emotional_state"], es["character_name"]))
for ob in a.get("object_updates", []):
    hid = c.execute("SELECT id FROM characters WHERE name=?", (ob["holder"],)).fetchone() if ob.get("holder") else None
    lid = c.execute("SELECT id FROM locations WHERE name=?", (ob["location"],)).fetchone() if ob.get("location") else None
    c.execute("UPDATE objects SET status=COALESCE(?,status), current_holder_id=COALESCE(?,current_holder_id), current_location_id=COALESCE(?,current_location_id), updated_at=CURRENT_TIMESTAMP WHERE name=?", (ob.get("status"), hid[0] if hid else None, lid[0] if lid else None, ob["name"]))
for ob in a.get("new_objects", []):
    P = c.execute("SELECT id FROM projects").fetchone()[0]
    hid = c.execute("SELECT id FROM characters WHERE name=?", (ob.get("holder"),)).fetchone()
    lid = c.execute("SELECT id FROM locations WHERE name=?", (ob.get("location"),)).fetchone()
    c.execute("INSERT INTO objects (project_id,name,description,current_holder_id,current_location_id,status,significance,introduced_in_chapter) VALUES (?,?,?,?,?,?,?,?)", (P, ob["name"], ob.get("description"), hid[0] if hid else None, lid[0] if lid else None, "active", ob.get("significance"), str(n)))
chid = c.execute("SELECT id FROM chapters WHERE chapter_number=?", (n,)).fetchone()[0]
c.execute("DELETE FROM scenes WHERE chapter_id=?", (chid,))
for i, sc in enumerate(a.get("scenes", []), 1):
    lid = c.execute("SELECT id FROM locations WHERE name=?", (sc["location"],)).fetchone()
    if not lid:
        P = c.execute("SELECT id FROM projects").fetchone()[0]
        c.execute("INSERT INTO locations (project_id,name) VALUES (?,?)", (P, sc["location"])); lid = c.execute("SELECT id FROM locations WHERE name=?", (sc["location"],)).fetchone()
    ids = [r[0] for nm in sc["characters"] for r in [c.execute("SELECT id FROM characters WHERE name=?", (nm,)).fetchone()] if r]
    c.execute("INSERT INTO scenes (chapter_id,scene_number,location_id,characters_present,summary,purpose,scene_order) VALUES (?,?,?,?,?,?,?)", (chid, i, lid[0], json.dumps(ids), sc.get("summary"), sc.get("purpose", "advance_plot"), i))
for cl in a.get("clue_resolutions", []):
    c.execute("UPDATE clues SET status=?, resolved_in_chapter=CASE WHEN ?='resolved' THEN ? ELSE resolved_in_chapter END, reinforced_in_chapters=CASE WHEN ?='reinforced' THEN COALESCE(reinforced_in_chapters,'[]') ELSE reinforced_in_chapters END WHERE description LIKE ?", (cl["status"], cl["status"], str(n), cl["status"], cl["match"] + "%"))
for th in a.get("thread_status", []): c.execute("UPDATE plot_threads SET status=? WHERE name=?", (th["status"], th["name"]))
c.execute("UPDATE projects SET current_word_count=(SELECT COALESCE(SUM(word_count),0) FROM chapters), updated_at=CURRENT_TIMESTAMP")
c.commit()
total = c.execute("SELECT current_word_count FROM projects").fetchone()[0]
r = subprocess.run([sys.executable, "scripts/verify.py", "--chapter", str(n), "--db", db], capture_output=True, text=True)
v = json.loads(r.stdout)
print(json.dumps({"chapter": n, "lint": lint, "applied": upd.get("changes_applied"), "novel_words": total,
  "verify": {k: v[k] for k in ("critical", "warnings", "suggestions")},
  "issues": [i["description"][:150] for i in v["issues"] if i["severity"] != "suggestion"]}, indent=1, ensure_ascii=False))
