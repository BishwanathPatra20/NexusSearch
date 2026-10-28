import sqlite3


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    tags_json TEXT NOT NULL DEFAULT '[]',
    source_type TEXT NOT NULL DEFAULT 'upload',
    source_uri TEXT,
    source_link TEXT,
    upload_date TEXT NOT NULL DEFAULT (datetime('now')),
    view_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',
    related_document_ids_json TEXT NOT NULL DEFAULT '[]',
    content_fingerprint TEXT,
    version_label TEXT
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    section TEXT,
    content TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chunks_document
    ON document_chunks(document_id);

CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    results_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS ingestion_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    payload_json TEXT NOT NULL,
    result_json TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS search_clicks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_history_id INTEGER,
    query TEXT NOT NULL,
    chunk_id INTEGER NOT NULL,
    click_position INTEGER NOT NULL,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (search_history_id) REFERENCES search_history(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS review_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    draft_answer TEXT NOT NULL,
    final_answer TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    confidence_score REAL NOT NULL DEFAULT 0,
    validator_notes_json TEXT NOT NULL DEFAULT '[]',
    plan_json TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS review_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_item_id INTEGER NOT NULL,
    chunk_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    relevance_score REAL NOT NULL,
    snippet TEXT,
    FOREIGN KEY (review_item_id) REFERENCES review_items(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS review_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_item_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    reviewer TEXT NOT NULL,
    comment TEXT,
    previous_answer TEXT,
    new_answer TEXT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (review_item_id) REFERENCES review_items(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS approved_knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_item_id INTEGER NOT NULL,
    query TEXT NOT NULL,
    approved_answer TEXT NOT NULL,
    reviewer TEXT NOT NULL,
    approved_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (review_item_id) REFERENCES review_items(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_review_items_status ON review_items(status);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    content,
    chunk_id UNINDEXED,
    document_id UNINDEXED,
    tokenize = 'porter unicode61'
);
"""


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    _ensure_fts_triggers(conn)
    from backend.app.db.migrations import apply_migrations

    apply_migrations(conn)


def _ensure_fts_triggers(conn: sqlite3.Connection) -> None:
    from backend.app.db.fts_index import ensure_fts_triggers

    ensure_fts_triggers(conn)
