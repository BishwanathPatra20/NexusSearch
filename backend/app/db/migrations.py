import sqlite3


def _has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row[1] == column for row in rows)


def apply_migrations(conn: sqlite3.Connection) -> None:
    """Lightweight schema evolution for existing SQLite databases."""
    if _has_column(conn, "documents", "status") is False:
        conn.execute(
            "ALTER TABLE documents ADD COLUMN status TEXT NOT NULL DEFAULT 'active'"
        )
    if _has_column(conn, "documents", "related_document_ids_json") is False:
        conn.execute(
            "ALTER TABLE documents ADD COLUMN related_document_ids_json TEXT NOT NULL DEFAULT '[]'"
        )
    if _has_column(conn, "documents", "content_fingerprint") is False:
        conn.execute("ALTER TABLE documents ADD COLUMN content_fingerprint TEXT")
    if _has_column(conn, "documents", "version_label") is False:
        conn.execute("ALTER TABLE documents ADD COLUMN version_label TEXT")
    if _has_column(conn, "documents", "source_link") is False:
        conn.execute("ALTER TABLE documents ADD COLUMN source_link TEXT")

    conn.executescript(
        """
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

        CREATE TABLE IF NOT EXISTS app_schema_flags (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS agent_runs (
            execution_id TEXT PRIMARY KEY,
            agent_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'running',
            trigger TEXT NOT NULL DEFAULT 'manual',
            result_json TEXT,
            error_message TEXT,
            started_at TEXT NOT NULL DEFAULT (datetime('now')),
            finished_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_agent_runs_agent ON agent_runs(agent_name, started_at DESC);

        CREATE TABLE IF NOT EXISTS synonym_proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            canonical_key TEXT NOT NULL,
            suggested_term TEXT NOT NULL,
            sample_query TEXT,
            hit_count INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS automation_schedules (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            enabled INTEGER NOT NULL DEFAULT 0,
            day_pattern TEXT NOT NULL DEFAULT 'monday',
            hour INTEGER NOT NULL DEFAULT 8,
            minute INTEGER NOT NULL DEFAULT 0,
            agents_json TEXT NOT NULL DEFAULT '[]',
            last_run_at TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )

    if _has_column(conn, "automation_schedules", "timezone") is False:
        conn.execute(
            "ALTER TABLE automation_schedules ADD COLUMN timezone TEXT NOT NULL DEFAULT 'UTC'"
        )

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS governance_audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            actor TEXT NOT NULL DEFAULT 'local-user',
            resource_type TEXT NOT NULL DEFAULT 'system',
            resource_id TEXT,
            detail_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_governance_audit_type
            ON governance_audit_events(event_type, created_at DESC);

        CREATE TABLE IF NOT EXISTS confluence_sync_schedules (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            enabled INTEGER NOT NULL DEFAULT 0,
            space_key TEXT,
            parent_page_id TEXT,
            max_pages INTEGER NOT NULL DEFAULT 50,
            last_run_at TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )

    if _has_column(conn, "approved_knowledge", "content_hash") is False:
        conn.execute("ALTER TABLE approved_knowledge ADD COLUMN content_hash TEXT")
    if _has_column(conn, "approved_knowledge", "source_chunk_ids_json") is False:
        conn.execute(
            "ALTER TABLE approved_knowledge ADD COLUMN source_chunk_ids_json TEXT NOT NULL DEFAULT '[]'"
        )

    _migrate_fts_document_metadata(conn)


def _schema_flag(conn: sqlite3.Connection, key: str) -> bool:
    row = conn.execute(
        "SELECT value FROM app_schema_flags WHERE key = ?",
        (key,),
    ).fetchone()
    return row is not None and row[0] == "1"


def _set_schema_flag(conn: sqlite3.Connection, key: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO app_schema_flags (key, value) VALUES (?, '1')",
        (key,),
    )


def _migrate_fts_document_metadata(conn: sqlite3.Connection) -> None:
    """Index title + file name in FTS (search by filename, not only body text)."""
    if _schema_flag(conn, "fts_document_metadata_v1"):
        return
    from backend.app.db.fts_index import ensure_fts_triggers, rebuild_chunks_fts

    ensure_fts_triggers(conn)
    rebuild_chunks_fts(conn)
    _set_schema_flag(conn, "fts_document_metadata_v1")
