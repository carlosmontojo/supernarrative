#!/bin/bash
# SuperNarrative — Quickstart Demo
# Run this from the project root: bash examples/quickstart.sh

set -e

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║  SuperNarrative — Quickstart Demo        ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

DB="db/demo.db"

# Clean previous demo
rm -f "$DB"

# 1. Initialize database
echo "→ Creating database..."
sqlite3 "$DB" < db/schema.sql

# 2. Create project
echo "→ Initializing project..."
python3 supernarrative.py init --name "Murder at the Museum" --genre mystery --db "$DB"
echo ""

# 3. Add characters
echo "→ Adding characters..."
python3 scripts/db_ops.py --db "$DB" --action add_character --data '{
  "name": "Detective Mara Cole",
  "role": "protagonist",
  "description_psychological": "Sharp, methodical, reads people like crime scenes. Dry humor under pressure.",
  "motivation": "Solve the murder. Protect the witness.",
  "secret": "She knew the victim — they were college friends.",
  "flaw": "Trust issues. Pushes people away."
}'

python3 scripts/db_ops.py --db "$DB" --action add_character --data '{
  "name": "Dr. James Whitfield",
  "role": "secondary",
  "description_psychological": "Museum curator. Charming, evasive. Knows more than he says.",
  "motivation": "Protect the museums reputation.",
  "secret": "He was having an affair with the victims wife.",
  "flaw": "Vanity. Cannot stand being seen as anything less than brilliant."
}'

python3 scripts/db_ops.py --db "$DB" --action add_character --data '{
  "name": "Sofia Reyes",
  "role": "secondary",
  "description_psychological": "Security guard. Quiet, observant. Former military.",
  "motivation": "Keep her job. Hide what she saw that night.",
  "secret": "She saw someone enter the restricted wing but is being threatened to stay silent.",
  "flaw": "Fear of authority."
}'
echo ""

# 4. Add story facts + epistemic states
echo "→ Building epistemic matrix..."
python3 scripts/db_ops.py --db "$DB" --action add_fact --data '{
  "category": "event",
  "description": "Dr. Whitfield entered the restricted wing at 11:47 PM, 12 minutes before the murder.",
  "significance": 9
}'

python3 scripts/db_ops.py --db "$DB" --action add_fact --data '{
  "category": "secret",
  "description": "Sofia Reyes saw Whitfield enter but is being blackmailed to stay silent.",
  "significance": 8
}'

python3 scripts/db_ops.py --db "$DB" --action add_fact --data '{
  "category": "identity",
  "description": "Detective Cole and the victim were college roommates.",
  "significance": 7
}'
echo ""

# 5. Run dashboard
echo "→ Dashboard:"
echo ""
python3 supernarrative.py dashboard --format terminal --db "$DB"

# 6. Search
echo "→ Searching 'Whitfield':"
python3 supernarrative.py search --action search_all --query "Whitfield" --db "$DB"
echo ""

# 7. Verify
echo ""
echo "→ Running consistency check..."
python3 supernarrative.py verify --db "$DB"

echo ""
echo "  ✓ Demo complete! The database is at $DB"
echo "  ✓ Try: python3 supernarrative.py search --action character_info --query 'Cole' --db $DB"
echo ""

# Cleanup
rm -f "$DB"
echo "  (Demo database cleaned up)"
