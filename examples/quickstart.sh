#!/bin/bash
# SuperNarrative — Quickstart Demo
# Run this from the project root: bash examples/quickstart.sh
# Requires only Python 3 — no sqlite3 binary, no pip installs.

set -e

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║  SuperNarrative — Quickstart Demo        ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

DB="db/demo.db"
rm -f "$DB"

# 1. Initialize project (creates the database automatically)
echo "→ Initializing project..."
python3 supernarrative.py init --name "Murder at the Museum" --genre mystery --target-words 80000 --db "$DB"
echo ""

# 2. Add characters
echo "→ Adding characters..."
python3 supernarrative.py ops --db "$DB" --action add_character --data '{
  "name": "Detective Mara Cole",
  "aliases": ["Cole", "the detective"],
  "role": "protagonist",
  "description_psychological": "Sharp, methodical, reads people like crime scenes. Dry humor under pressure.",
  "motivation": "Solve the murder. Protect the witness.",
  "secret": "She knew the victim — they were college friends.",
  "flaw": "Trust issues. Pushes people away."
}' > /dev/null

python3 supernarrative.py ops --db "$DB" --action add_character --data '{
  "name": "Dr. James Whitfield",
  "aliases": ["Whitfield"],
  "role": "secondary",
  "description_psychological": "Museum curator. Charming, evasive. Knows more than he says.",
  "secret": "He was having an affair with the victims wife."
}' > /dev/null

python3 supernarrative.py ops --db "$DB" --action add_character --data '{
  "name": "Sofia Reyes",
  "role": "secondary",
  "description_psychological": "Security guard. Quiet, observant. Former military.",
  "secret": "She saw someone enter the restricted wing but is being threatened to stay silent."
}' > /dev/null
echo "  3 characters added."

# 3. Facts + epistemic matrix
echo "→ Building epistemic matrix..."
python3 supernarrative.py ops --db "$DB" --action add_fact --data '{
  "category": "event",
  "description": "Dr. Whitfield entered the restricted wing at 11:47 PM, 12 minutes before the murder.",
  "significance": 9
}' > /dev/null
python3 supernarrative.py ops --db "$DB" --action set_knowledge --data '{
  "character": "Sofia Reyes",
  "fact": "Dr. Whitfield entered the restricted wing at 11:47 PM, 12 minutes before the murder.",
  "knowledge_level": "knows", "how_learned": "witnessed"
}' > /dev/null
python3 supernarrative.py ops --db "$DB" --action set_knowledge --data '{
  "character": "Detective Mara Cole",
  "fact": "Dr. Whitfield entered the restricted wing at 11:47 PM, 12 minutes before the murder.",
  "knowledge_level": "unaware"
}' > /dev/null
echo "  Sofia knows what the detective doesn't. The system will never let you forget it."

# 4. Threads with a dependency
echo "→ Creating plot threads with a dependency..."
python3 supernarrative.py ops --db "$DB" --action add_thread --data '{
  "name": "Who killed the archivist", "thread_type": "mystery", "priority": 10
}' > /dev/null
python3 supernarrative.py ops --db "$DB" --action add_thread --data '{
  "name": "The confrontation with Whitfield", "thread_type": "main_plot", "priority": 9
}' > /dev/null
python3 supernarrative.py ops --db "$DB" --action add_dependency --data '{
  "dependent": "The confrontation with Whitfield",
  "required": "Who killed the archivist",
  "required_status": "developing",
  "description": "Cole cannot confront Whitfield before she has evidence."
}' > /dev/null
echo "  Dependency set: the confrontation cannot happen before the mystery develops."

# 5. Simulate the full writing cycle: analysis JSON → update
echo "→ Simulating chapter 1 analysis (what the LLM produces after writing)..."
cat > /tmp/sn_demo_analysis.json <<'EOF'
{
  "summary": "Cole examines the crime scene and finds a security log with a torn page.",
  "events": [
    {"type": "discovery", "description": "Cole finds the security log with a missing page",
     "affected_characters": ["Detective Mara Cole"], "affected_objects": ["security log"]}
  ],
  "knowledge_changes": [
    {"character_name": "Cole", "fact": "The security log page for 11-12 PM is missing",
     "new_knowledge_level": "knows", "how_learned": "witnessed"}
  ],
  "reader_knowledge_changes": [
    {"fact": "Someone tampered with the security records", "new_knowledge_level": "suspects"}
  ],
  "thread_beats": [
    {"thread_name": "Who killed the archivist", "beat_type": "plant",
     "description": "The tampered log opens the investigation"}
  ],
  "clues": [
    {"description": "The torn edge of the log page is fresh", "type": "object",
     "subtlety": 7, "related_thread": "Who killed the archivist"}
  ],
  "character_locations_end": [
    {"character_name": "Detective Mara Cole", "location": "Museum archive room"}
  ],
  "character_emotional_states": [
    {"character_name": "Detective Mara Cole", "emotional_state": "focused, suspicious"}
  ],
  "scenes": [
    {"scene_number": 1, "location": "Museum archive room",
     "characters_present": ["Detective Mara Cole", "Sofia Reyes"],
     "summary": "Cole inspects the scene while Sofia watches nervously",
     "purpose": "plant_clue"}
  ],
  "tension_level": 6, "scene_type": "investigation", "pacing": "medium",
  "emotional_tone": "paranoid",
  "opening_hook": "The archive door was already open",
  "closing_hook": "The missing page covers exactly the murder window",
  "word_count": 3100
}
EOF
python3 supernarrative.py analyze --db "$DB" --chapter 1 --analysis-json /tmp/sn_demo_analysis.json > /dev/null
python3 supernarrative.py update --db "$DB" --chapter 1 --confirm
echo ""

# 6. Context package for the next chapter
echo "→ Context package for chapter 2 (this is what the LLM sees before writing):"
python3 supernarrative.py context --db "$DB" --chapter 2 | python3 -c "
import json, sys
pkg = json.load(sys.stdin)
print('   Rules:', len(pkg['narrative_rules']), '| Characters:', len(pkg['character_sheets']),
      '| Active threads:', len(pkg['active_threads']), '| Active clues:', len(pkg['active_clues']),
      '| Recent events:', len(pkg['recent_events']))
cole = pkg['epistemic_matrix'].get('Detective Mara Cole', {})
print('   Cole knows:', len(cole.get('knows', [])), 'facts | unaware of:', len(cole.get('unaware', [])))
"

# 7. Dashboard + verify
echo ""
echo "→ Dashboard:"
python3 supernarrative.py dashboard --format terminal --db "$DB"
echo "→ Running consistency check..."
python3 supernarrative.py verify --db "$DB" | python3 -c "
import json, sys
v = json.load(sys.stdin)
print(f'   {v[\"total_issues\"]} issues: {v[\"critical\"]} critical, {v[\"warnings\"]} warnings, {v[\"suggestions\"]} suggestions')
for i in v['issues'][:3]:
    print(f'   [{i[\"severity\"]}] {i[\"description\"][:90]}')
"

echo ""
echo "  ✓ Demo complete! Try:"
echo "    python3 supernarrative.py search --action who_knows --query 'restricted wing' --db $DB"
echo "    python3 supernarrative.py search --action character_info --query 'Cole' --db $DB"
echo ""

rm -f "$DB" /tmp/sn_demo_analysis.json
echo "  (Demo database cleaned up)"
