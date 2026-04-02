# SuperNarrative

**Persistent narrative memory for long-form fiction. Treats your novel like software.**

> Everything Sudowrite, NovelCrafter, and Novelium charge you for — but free, local, and yours. Like SuperMemory, but for fiction.

---

## The Problem

You're writing a 300-page thriller with 12 characters, 8 plot threads, and 40 planted clues. In chapter 22, your detective acts on information she doesn't have yet. Your reader notices. Your novel is broken.

LLMs forget. Context windows overflow. SaaS tools lock your data behind subscriptions. None of them can answer: *"What does character X know at this exact point in the story?"*

## The Solution

SuperNarrative is a **narrative memory system** that persists between sessions, tracks what every character knows, verifies consistency automatically, and never forgets a planted clue.

It treats your novel like a software project:
- **State** — Where is everyone? What do they know? What's changed?
- **Dependencies** — This thread can't resolve until that one is planted
- **Verification** — Automated checks for plot holes, epistemic violations, timeline errors
- **Version control** — Snapshot and restore your narrative database

```
novel = software project
characters = services with state
plot threads = feature branches
clues = promises that must be resolved
epistemic matrix = access control (who knows what)
verify.py = your test suite
```

---

## Key Features

**Epistemic Matrix** — Tracks what every character knows, suspects, or wrongly believes at every point in the story. No other tool does this. When your character acts on information they don't have, `verify` catches it.

**Consistency Verification** — Automated checks for continuity errors, epistemic violations, timeline impossibilities, abandoned clues, pacing monotony, and plot dependency violations.

**Plot Thread Tracking** — Named threads (mystery, romance, subplot) with beats (plant, reinforce, complicate, twist, reveal, resolve). Dependency graph prevents premature resolutions.

**Clue Management** — Every clue tracked with subtlety rating (1-10), planting mechanism, intended resolution, and reinforcement history. Stale clues trigger warnings.

**LLM-Agnostic** — Works with Claude, GPT, Gemini, local models, or no LLM at all. The memory is in SQLite, not in a context window.

**Zero Dependencies** — Python 3 + SQLite. That's it. No pip install, no API keys, no subscriptions.

---

## Quick Start

```bash
# Clone
git clone https://github.com/carlosmontojo/supernarrative.git
cd supernarrative

# Initialize a project
sqlite3 db/supernarrative.db < db/schema.sql
python3 supernarrative.py init --name "My Novel" --genre thriller

# See your dashboard
python3 supernarrative.py dashboard --format terminal

# Run the full demo
bash examples/quickstart.sh
```

---

## Writing Workflow

```
┌─────────┐     ┌──────────┐     ┌─────────┐     ┌──────────┐     ┌──────────┐
│ context  │────▶│  write   │────▶│ analyze │────▶│  update  │────▶│  verify  │
│          │     │ chapter  │     │         │     │          │     │          │
│ Get what │     │ With full│     │ Extract │     │ Apply to │     │ Check    │
│ everyone │     │ context  │     │ events, │     │ database │     │ for plot │
│ knows    │     │ injected │     │ clues,  │     │ (author  │     │ holes    │
│          │     │          │     │ changes │     │ confirms)│     │          │
└─────────┘     └──────────┘     └─────────┘     └──────────┘     └──────────┘
                                                                        │
                                                                        ▼
                                                                  ┌──────────┐
                                                                  │dashboard │
                                                                  │          │
                                                                  │ Overall  │
                                                                  │ status   │
                                                                  └──────────┘
```

### Before writing a chapter
```bash
python3 supernarrative.py context --chapter 5
```
Returns: world state, epistemic matrix, active threads, clues to reinforce, pacing suggestions.

### After writing a chapter
```bash
python3 supernarrative.py analyze --chapter 5 --analysis-json analysis.json
python3 supernarrative.py update --chapter 5 --confirm
python3 supernarrative.py verify --chapter 5
```

### Monitor your novel
```bash
python3 supernarrative.py dashboard --format terminal
python3 supernarrative.py search --action who_knows --query "the murder"
python3 supernarrative.py search --action character_info --query "Detective"
python3 supernarrative.py snapshot  # backup before big changes
```

---

## Commands

| Command | Description |
|---------|-------------|
| `init` | Create a new novel project |
| `import` | Import existing novel (bible, chapters, continuity docs) |
| `context` | Generate context package before writing |
| `analyze` | Extract narrative data from a written chapter |
| `update` | Apply confirmed analysis to database |
| `verify` | Check for consistency issues |
| `dashboard` | Project overview (terminal or JSON) |
| `search` | Query the narrative database |
| `snapshot` | Create/list/restore database backups |
| `ops` | Direct database operations |

### Search Actions

```bash
supernarrative search --action who_knows --query "secret"     # Who knows a fact?
supernarrative search --action who_knows_about --query "Alice" # What does Alice know?
supernarrative search --action where_is --query "Bob"          # Where is Bob?
supernarrative search --action character_info --query "Alice"  # Full character sheet
supernarrative search --action active_clues                    # All unresolved clues
supernarrative search --action thread_status --query "romance" # Thread with beats
supernarrative search --action timeline                        # Chronological events
supernarrative search --action search_all --query "poison"     # Global text search
```

---

## Architecture

```
supernarrative/
├── supernarrative.py          # Unified CLI entry point
├── db/
│   └── schema.sql             # 18-table narrative schema
├── scripts/
│   ├── init_project.py        # Project initialization
│   ├── import_existing.py     # Novel import
│   ├── context.py             # Pre-chapter context generator
│   ├── analyze.py             # Post-chapter analysis
│   ├── update.py              # Database updater
│   ├── verify.py              # Consistency checker
│   ├── dashboard.py           # Project dashboard
│   ├── search.py              # Narrative search
│   ├── snapshot.py            # Database backup/restore
│   └── db_ops.py              # CRUD operations
├── prompts/
│   ├── generation.md          # Chapter writing prompt template
│   ├── analysis.md            # Post-chapter analysis prompt
│   └── verification.md        # Consistency check prompt
├── source/                    # Your novel files (gitignored)
└── SKILL.md                   # Full system documentation
```

### Database Schema (5 layers)

```
Layer 1: World State        → locations, objects, world_events
Layer 2: Characters         → characters, relationships, story_facts, knowledge_states
Layer 3: Plot              → plot_threads, thread_beats, thread_dependencies, clues
Layer 4: Chapters          → chapters, scenes
Layer 5: Verification     → consistency_issues, author_notes, narrative_rules
```

The **epistemic matrix** (`knowledge_states` table) is the core innovation. Every character has a knowledge level for every story fact:

| Level | Meaning |
|-------|---------|
| `knows` | Character has confirmed knowledge |
| `suspects` | Character suspects but isn't sure |
| `unaware` | Character has no idea |
| `wrong_belief` | Character believes something false |
| `partial` | Character knows part of the truth |
| `forgot` | Character knew but has forgotten |

A special knower `__reader__` tracks what the reader knows, enabling dramatic irony tracking.

---

## How It Compares

| Feature | SuperNarrative | Sudowrite | NovelCrafter | Novelium |
|---------|---------------|-----------|-------------|---------|
| Epistemic matrix | Yes | No | No | No |
| Consistency verification | Automated | No | No | Basic |
| Plot thread dependencies | Yes | No | No | No |
| Clue tracking with subtlety | Yes | No | Partial | Partial |
| Character knowledge tracking | Per-fact, per-chapter | Session-based | Codex notes | Basic |
| LLM-agnostic | Yes | Proprietary | Multi-LLM | Proprietary |
| Local/offline | Yes | No | Partial | No |
| Open source | MIT | No | No | No |
| Price | Free | $19-29/mo | $18-25/mo | $15-30/mo |

---

## Use as Claude Code Skill

SuperNarrative was originally built as a Claude Code skill. To use it with Claude Code, add a `CLAUDE.md` to your project:

```markdown
# SuperNarrative

- Always read SKILL.md at startup
- Always check the database for current novel state before doing anything
- Before writing any chapter, run `context.py` for the context package
- After writing any chapter, run `analyze.py` and `verify.py`
- Never update the database without showing me the changes first
- Novel files are in source/
```

---

## Contributing

Contributions welcome! Areas where help is needed:

- **Visualization** — Web dashboard, tension curve graphs, relationship maps
- **Integrations** — Cursor, VS Code, Obsidian plugins
- **Prompt templates** — Genre-specific prompts (fantasy, sci-fi, romance)
- **Importers** — Scrivener, Google Docs, Notion import
- **Languages** — Translations of prompts and documentation

---

## License

MIT. Your novels are yours. Your data stays local. No telemetry, no cloud, no lock-in.
