"""Lightweight SQLite persistence for users, chat progress, and learning resources."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "chemistry_app.db"


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_user_store() -> None:
    with _conn() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password TEXT
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                file_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS question_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS learning_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )


def get_or_create_user(email: str, password: str) -> Optional[int]:
    normalized = email.strip().lower()
    with _conn() as con:
        row = con.execute("SELECT id, password FROM users WHERE email = ?", (normalized,)).fetchone()
        if row:
            if row["password"] == password:
                return int(row["id"])
            else:
                return None  # Incorrect password
        
        # Create new user if not exists
        cur = con.execute("INSERT INTO users(email, password) VALUES (?, ?)", (normalized, password))
        return int(cur.lastrowid)


def save_chat_event(user_id: int, role: str, content: str, file_name: Optional[str] = None) -> None:
    with _conn() as con:
        con.execute(
            "INSERT INTO chat_events(user_id, role, content, file_name) VALUES (?, ?, ?, ?)",
            (user_id, role, content, file_name),
        )


def load_chat_events(user_id: int, limit: int = 60) -> List[Dict[str, str]]:
    with _conn() as con:
        rows = con.execute(
            """
            SELECT role, content, file_name
            FROM chat_events
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    events = []
    for row in reversed(rows):
        item = {"role": row["role"], "content": row["content"]}
        if row["file_name"]:
            item["file_name"] = row["file_name"]
        events.append(item)
    return events


def save_question(user_id: int, question: str) -> None:
    with _conn() as con:
        con.execute(
            "INSERT INTO question_history(user_id, question) VALUES (?, ?)",
            (user_id, question),
        )


def load_questions(user_id: int, limit: int = 40) -> List[str]:
    with _conn() as con:
        rows = con.execute(
            """
            SELECT question
            FROM question_history
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    return [str(r["question"]) for r in rows]


def add_learning_resource(user_id: int, title: str, link: str, notes: str = "") -> None:
    with _conn() as con:
        con.execute(
            "INSERT INTO learning_resources(user_id, title, link, notes) VALUES (?, ?, ?, ?)",
            (user_id, title.strip(), link.strip(), notes.strip()),
        )


def load_learning_resources(user_id: int, limit: int = 100) -> List[Dict[str, str]]:
    with _conn() as con:
        rows = con.execute(
            """
            SELECT id, title, link, notes
            FROM learning_resources
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    return [
        {
            "id": int(r["id"]),
            "title": str(r["title"]),
            "link": str(r["link"]),
            "notes": str(r["notes"] or ""),
        }
        for r in rows
    ]


def delete_learning_resource(user_id: int, resource_id: int) -> None:
    with _conn() as con:
        con.execute(
            "DELETE FROM learning_resources WHERE id = ? AND user_id = ?",
            (resource_id, user_id),
        )
