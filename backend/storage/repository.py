import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from uuid import uuid4

from backend.config import DB_PATH, GRAPHS_STORE


def _get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS graphs (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            params TEXT,
            created_at TEXT,
            nodes_count INTEGER,
            edges_count INTEGER
        )
        """
    )
    conn.commit()
    conn.close()


def create_graph_entry(graph_id: str, filename: str, params: Optional[Dict], nodes_count: int, edges_count: int):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO graphs (id, filename, params, created_at, nodes_count, edges_count) VALUES (?, ?, ?, ?, ?, ?)",
        (graph_id, filename, json.dumps(params or {}), datetime.utcnow().isoformat(), nodes_count, edges_count),
    )
    conn.commit()
    conn.close()


def get_graph_entry(graph_id: str) -> Optional[Dict]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM graphs WHERE id = ?", (graph_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def list_graph_entries(offset: int = 0, limit: int = 20) -> List[Dict]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM graphs ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def count_graph_entries() -> int:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM graphs")
    row = cur.fetchone()
    conn.close()
    return int(row[0])


def delete_graph_entry(graph_id: str) -> bool:
    entry = get_graph_entry(graph_id)
    if not entry:
        return False
    # delete file
    file_path = Path(entry['filename'])
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM graphs WHERE id = ?", (graph_id,))
    conn.commit()
    conn.close()
    return True


def ensure_init():
    init_db()
