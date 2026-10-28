"""FTS5 triggers: index document title + file name with chunk text (not shown in snippets)."""

import sqlite3

# SQL subquery: enriched text for a chunk row (alias `new` or `c`)
_FTS_CONTENT_SELECT = """
    SELECT trim(
        d.title || ' ' ||
        replace(replace(replace(d.file_name, '-', ' '), '_', ' '), '.', ' ') || ' ' ||
        coalesce({chunk_ref}.content, '')
    )
    FROM documents d
    WHERE d.id = {chunk_ref}.document_id
"""

FTS_TRIGGER_SQL = f"""
DROP TRIGGER IF EXISTS chunks_ai;
DROP TRIGGER IF EXISTS chunks_ad;
DROP TRIGGER IF EXISTS chunks_au;

CREATE TRIGGER chunks_ai AFTER INSERT ON document_chunks BEGIN
    INSERT INTO chunks_fts(rowid, content, chunk_id, document_id)
    VALUES (
        new.id,
        ({_FTS_CONTENT_SELECT.format(chunk_ref="new")}),
        new.id,
        new.document_id
    );
END;

CREATE TRIGGER chunks_ad AFTER DELETE ON document_chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, content, chunk_id, document_id)
    VALUES ('delete', old.id, old.content, old.id, old.document_id);
END;

CREATE TRIGGER chunks_au AFTER UPDATE ON document_chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, content, chunk_id, document_id)
    VALUES ('delete', old.id, old.content, old.id, old.document_id);
    INSERT INTO chunks_fts(rowid, content, chunk_id, document_id)
    VALUES (
        new.id,
        ({_FTS_CONTENT_SELECT.format(chunk_ref="new")}),
        new.id,
        new.document_id
    );
END;
"""


def rebuild_chunks_fts(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM chunks_fts")
    conn.execute(
        f"""
        INSERT INTO chunks_fts(rowid, content, chunk_id, document_id)
        SELECT
            c.id,
            ({_FTS_CONTENT_SELECT.format(chunk_ref="c")}),
            c.id,
            c.document_id
        FROM document_chunks c
        """
    )


def ensure_fts_triggers(conn: sqlite3.Connection) -> None:
    conn.executescript(FTS_TRIGGER_SQL)
