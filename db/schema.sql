-- ============================================================
-- NARRATIUM — Schema de Memoria Narrativa
-- ============================================================

-- ============================================================
-- PROYECTO Y CONFIGURACIÓN
-- ============================================================

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    name TEXT NOT NULL,
    description TEXT,
    genre TEXT,
    target_word_count INTEGER,
    current_word_count INTEGER DEFAULT 0,
    narrative_voice TEXT DEFAULT 'third_person',   -- "first_person", "third_person", "third_omniscient"
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS narrative_rules (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    category TEXT NOT NULL,              -- "style", "voice", "structure", "pov", "forbidden", "rhythm"
    rule TEXT NOT NULL,
    priority INTEGER DEFAULT 5,         -- 1-10
    active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS style_references (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    author TEXT NOT NULL,
    work TEXT,
    technique TEXT NOT NULL,             -- "Tensión intelectual via debates filosóficos"
    example_description TEXT,            -- Descripción del ejemplo (nunca texto copiado)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- CAPA 1: ESTADO DEL MUNDO
-- ============================================================

CREATE TABLE IF NOT EXISTS locations (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    parent_location_id TEXT REFERENCES locations(id),
    attributes TEXT,                     -- JSON: {"accesible": true, "secreto": false}
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS objects (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    current_location_id TEXT REFERENCES locations(id),
    current_holder_id TEXT,              -- character id
    status TEXT DEFAULT 'active',        -- "active", "destroyed", "hidden", "lost", "unknown"
    significance TEXT,                   -- por qué importa narrativamente
    introduced_in_chapter TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS world_events (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    chapter_id TEXT NOT NULL,
    event_type TEXT NOT NULL,            -- "movement", "death", "discovery", "destruction", "transformation", "revelation", "encounter"
    description TEXT NOT NULL,
    story_timestamp TEXT,                -- "14 marzo, 22:30" (tiempo diegético)
    affected_entities TEXT,              -- JSON array de IDs
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- CAPA 2: PERSONAJES Y ESTADO EPISTÉMICO
-- ============================================================

CREATE TABLE IF NOT EXISTS characters (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    full_name TEXT,
    aliases TEXT,                        -- JSON array: ["il Dottore", "el hombre del abrigo"]
    role TEXT NOT NULL,                  -- "protagonist", "antagonist", "secondary", "tertiary", "mentioned"
    description_physical TEXT,
    description_psychological TEXT,
    backstory TEXT,
    motivation TEXT,                     -- Qué quiere este personaje
    secret TEXT,                         -- Qué oculta
    flaw TEXT,                           -- Su defecto principal
    arc_summary TEXT,                    -- Resumen de su arco previsto
    voice_notes TEXT,                    -- Cómo habla: registro, muletillas, nivel cultural
    speech_patterns TEXT,                -- Ejemplos de cómo se expresa
    status TEXT DEFAULT 'alive',         -- "alive", "dead", "unknown", "missing", "presumed_dead"
    introduced_in_chapter TEXT,
    current_location_id TEXT REFERENCES locations(id),
    emotional_state TEXT,                -- Estado emocional actual
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS character_relationships (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    character_a_id TEXT NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    character_b_id TEXT NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL,     -- "ally", "enemy", "lover", "family", "mentor", "rival", "colleague", "unknown"
    description TEXT,
    public_perception TEXT,              -- Cómo se percibe públicamente
    private_reality TEXT,                -- La verdad
    status TEXT DEFAULT 'active',        -- "active", "broken", "secret", "evolving", "dormant"
    established_in_chapter TEXT,
    evolution_notes TEXT,                -- Cómo ha cambiado
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_a_id, character_b_id, relationship_type)
);

-- HECHOS NARRATIVOS — verdades (y mentiras) de la historia
CREATE TABLE IF NOT EXISTS story_facts (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    category TEXT NOT NULL,              -- "identity", "event", "location", "motive", "relationship", "secret", "historical", "object"
    description TEXT NOT NULL,           -- "Benedetta es la madre biológica de Lucrezia"
    is_true BOOLEAN DEFAULT 1,          -- Permite hechos falsos que personajes creen verdaderos
    contradiction_of TEXT REFERENCES story_facts(id), -- Si es falso, qué hecho verdadero contradice
    established_in_chapter TEXT,
    revealed_to_reader_in TEXT,          -- NULL si el lector aún no lo sabe
    significance INTEGER DEFAULT 5,     -- 1-10
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- MATRIZ EPISTÉMICA — quién sabe qué
CREATE TABLE IF NOT EXISTS knowledge_states (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    knower_id TEXT NOT NULL,             -- character ID o "__reader__" para el lector
    fact_id TEXT NOT NULL REFERENCES story_facts(id) ON DELETE CASCADE,
    knowledge_level TEXT NOT NULL,       -- "knows", "suspects", "unaware", "wrong_belief", "partial", "forgot"
    wrong_belief_detail TEXT,            -- Si wrong_belief, qué cree erróneamente
    how_learned TEXT,                    -- "witnessed", "told_by:character_id", "deduced", "read", "overheard", "reader_inference"
    learned_in_chapter TEXT,
    confidence TEXT DEFAULT 'certain',   -- "certain", "probable", "speculative"
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(knower_id, fact_id)
);

-- ============================================================
-- CAPA 3: HILOS NARRATIVOS Y DEPENDENCIAS
-- ============================================================

CREATE TABLE IF NOT EXISTS plot_threads (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    thread_type TEXT NOT NULL,           -- "main_plot", "subplot", "mystery", "romance", "character_arc", "thematic", "red_herring"
    status TEXT DEFAULT 'planned',       -- "planned", "planted", "developing", "climax", "resolved", "abandoned"
    planted_in_chapter TEXT,
    target_resolution_chapter TEXT,      -- Capítulo estimado de resolución
    resolved_in_chapter TEXT,
    priority INTEGER DEFAULT 5,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS thread_beats (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    thread_id TEXT NOT NULL REFERENCES plot_threads(id) ON DELETE CASCADE,
    chapter_id TEXT NOT NULL,
    beat_type TEXT NOT NULL,             -- "plant", "reinforce", "complicate", "twist", "escalate", "near_reveal", "reveal", "resolve", "subvert"
    description TEXT NOT NULL,
    impact_level INTEGER DEFAULT 5,     -- 1-10
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS thread_dependencies (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    dependent_thread_id TEXT NOT NULL REFERENCES plot_threads(id) ON DELETE CASCADE,
    required_thread_id TEXT NOT NULL REFERENCES plot_threads(id) ON DELETE CASCADE,
    required_status TEXT NOT NULL,       -- Estado que debe tener el hilo requerido
    description TEXT,
    UNIQUE(dependent_thread_id, required_thread_id)
);

-- PISTAS (CLUES)
CREATE TABLE IF NOT EXISTS clues (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    thread_id TEXT REFERENCES plot_threads(id),
    description TEXT NOT NULL,
    planted_in_chapter TEXT NOT NULL,
    clue_type TEXT NOT NULL,             -- "verbal", "visual", "object", "behavioral", "environmental", "structural", "intertextual"
    subtlety INTEGER NOT NULL,           -- 1-10 (10 = invisible en primera lectura)
    mechanism TEXT,                      -- Cómo funciona la pista narrativamente
    intended_resolution TEXT,            -- Cuándo/cómo cobra sentido
    resolved_in_chapter TEXT,
    reinforced_in_chapters TEXT,         -- JSON array de chapter IDs donde se refuerza
    status TEXT DEFAULT 'active',        -- "active", "reinforced", "resolved", "red_herring", "abandoned"
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- CAPA 4: CAPÍTULOS, ESCENAS, RITMO
-- ============================================================

CREATE TABLE IF NOT EXISTS chapters (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    chapter_number INTEGER NOT NULL,
    title TEXT,
    summary TEXT,
    word_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'planned',       -- "planned", "outlined", "draft", "revised", "final"
    pov_character_id TEXT REFERENCES characters(id),

    -- Ritmo y tono
    scene_type TEXT,                     -- "action", "dialogue", "reflection", "revelation", "transition", "flashback", "confrontation", "investigation"
    tension_level INTEGER,               -- 1-10
    pacing TEXT,                         -- "slow", "medium", "fast", "frantic"
    emotional_tone TEXT,                 -- "hopeful", "dread", "melancholy", "triumphant", "neutral", "paranoid", "intimate", "chaotic"

    -- Tiempo diegético
    story_date TEXT,
    story_time_start TEXT,
    story_time_end TEXT,

    -- Estructura
    opening_hook TEXT,
    closing_hook TEXT,
    key_events TEXT,                     -- JSON array resumen de eventos clave

    chapter_order INTEGER NOT NULL,
    file_path TEXT,                      -- Ruta al .md del capítulo
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, chapter_number)
);

CREATE TABLE IF NOT EXISTS scenes (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    chapter_id TEXT NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    scene_number INTEGER NOT NULL,
    location_id TEXT REFERENCES locations(id),
    characters_present TEXT,             -- JSON array de character IDs
    summary TEXT,
    purpose TEXT,                        -- "advance_plot", "develop_character", "plant_clue", "build_tension", "provide_relief", "worldbuilding"
    scene_order INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- CAPA 5: VERIFICACIÓN Y CONSISTENCIA
-- ============================================================

CREATE TABLE IF NOT EXISTS consistency_issues (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    chapter_id TEXT,
    issue_type TEXT NOT NULL,            -- "continuity", "epistemic", "timeline", "voice", "dependency", "clue", "plot_hole", "pacing"
    severity TEXT NOT NULL,              -- "critical", "warning", "suggestion"
    description TEXT NOT NULL,
    location_in_text TEXT,               -- Fragmento o referencia al punto problemático
    suggestion TEXT,
    resolved BOOLEAN DEFAULT 0,
    resolved_note TEXT,
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME
);

-- ============================================================
-- NOTAS Y ANOTACIONES DEL AUTOR
-- ============================================================

CREATE TABLE IF NOT EXISTS author_notes (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    chapter_id TEXT REFERENCES chapters(id),
    character_id TEXT REFERENCES characters(id),
    thread_id TEXT REFERENCES plot_threads(id),
    note_type TEXT DEFAULT 'general',    -- "general", "todo", "idea", "research", "revision"
    content TEXT NOT NULL,
    resolved BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- ÍNDICES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_chapters_project ON chapters(project_id, chapter_order);
CREATE INDEX IF NOT EXISTS idx_characters_project ON characters(project_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_knower ON knowledge_states(knower_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_fact ON knowledge_states(fact_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_chapter ON knowledge_states(learned_in_chapter);
CREATE INDEX IF NOT EXISTS idx_threads_project ON plot_threads(project_id, status);
CREATE INDEX IF NOT EXISTS idx_thread_beats_chapter ON thread_beats(chapter_id);
CREATE INDEX IF NOT EXISTS idx_thread_beats_thread ON thread_beats(thread_id);
CREATE INDEX IF NOT EXISTS idx_clues_thread ON clues(thread_id, status);
CREATE INDEX IF NOT EXISTS idx_clues_project ON clues(project_id, status);
CREATE INDEX IF NOT EXISTS idx_world_events_chapter ON world_events(chapter_id);
CREATE INDEX IF NOT EXISTS idx_consistency_issues ON consistency_issues(project_id, resolved, severity);
CREATE INDEX IF NOT EXISTS idx_scenes_chapter ON scenes(chapter_id, scene_order);
CREATE INDEX IF NOT EXISTS idx_story_facts_project ON story_facts(project_id, category);
CREATE INDEX IF NOT EXISTS idx_objects_project ON objects(project_id, status);
CREATE INDEX IF NOT EXISTS idx_author_notes ON author_notes(project_id, resolved);
CREATE INDEX IF NOT EXISTS idx_narrative_rules ON narrative_rules(project_id, active, priority);
