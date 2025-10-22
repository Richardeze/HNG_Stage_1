import sqlite3
import json
from typing import Dict, Any, Optional

DB_PATH = "database.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS analyzed_strings (
    id TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    length INTEGER NOT NULL,
    is_palindrome INTEGER NOT NULL,
    unique_characters INTEGER NOT NULL,
    word_count INTEGER NOT NULL,
    sha256_hash TEXT NOT NULL,
    character_frequency_map TEXT NOT NULL,
    created_at TEXT NOT NULL )
    """)
    conn.commit()
    conn.close()

def insert_string(record: Dict[str, Any]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO analyzed_strings (
    id, value, length, is_palindrome, unique_characters, word_count, sha256_hash,
    character_frequency_map, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
      record["id"],
      record["value"],
      record["length"],
      1 if record["is_palindrome"] else 0,
      record["unique_characters"],
      record["word_count"],
      record["sha256_hash"],
      json.dumps(record["character_frequency_map"]),
      record["created_at"]
    ) )
    conn.commit()
    conn.close()

def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "value": row["value"],
        "properties": {
            "length": row["length"],
            "is_palindrome": bool(row["is_palindrome"]),
            "unique_characters": row["unique_characters"],
            "word_count": row["word_count"],
            "sha256_hash": row["sha256_hash"],
            "character_frequency_map": json.loads(row["character_frequency_map"])
        },
        "created_at": row["created_at"]
    }

def get_by_hash(hash_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM analyzed_strings WHERE id = ?", (hash_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    else:
        return row_to_dict(row)

def get_by_value(value: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM analyzed_strings WHERE value = ?", (value,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row_to_dict(row)
    else:
        return None

def list_all() -> list:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM analyzed_strings ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    records = []
    for row in rows:
        dict_row = row_to_dict(row)
        records.append(dict_row)
    return records

def delete_by_value(value: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM analyzed_strings WHERE value = ?", (value,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted > 0