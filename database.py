"""
SQLite persistence layer for TalentForge AI.
Every other module talks to the database only through these functions —
no raw SQL anywhere else in the app.
"""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

from config import DB_PATH


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _ensure_columns(conn, table: str, columns: dict):
    """Adds any missing columns to an existing table (simple migration helper,
    so upgrading the code doesn't require deleting your existing .db file).
    columns: {column_name: sql_type_and_default}
    """
    existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    for col_name, col_def in columns.items():
        if col_name not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")


def create_tables():
    with get_connection() as conn:
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'candidate',
                full_name TEXT,
                target_role TEXT,
                bio TEXT,
                created_at TEXT NOT NULL
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT,
                raw_text TEXT,
                skills TEXT,
                score REAL,
                feedback TEXT,
                uploaded_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS interview_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT,
                question TEXT,
                answer TEXT,
                sentiment_label TEXT,
                sentiment_score REAL,
                relevance_score REAL,
                specificity_score REAL,
                overall_score REAL,
                feedback TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        _ensure_columns(conn, "interview_sessions", {
            "specificity_score": "REAL",
            "feedback": "TEXT",
        })

        c.execute("""
            CREATE TABLE IF NOT EXISTS emotion_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                source TEXT,
                emotion TEXT,
                confidence REAL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS voice_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                transcript TEXT,
                duration_seconds REAL,
                words_per_minute REAL,
                filler_word_count INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recruiter_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (recruiter_id) REFERENCES users (id)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                match_score REAL,
                status TEXT DEFAULT 'applied',
                created_at TEXT NOT NULL,
                FOREIGN KEY (job_id) REFERENCES jobs (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS coding_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                problem_title TEXT,
                code TEXT,
                passed INTEGER,
                output TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)


def now():
    return datetime.utcnow().isoformat()


# ---------------- Users ----------------

def create_user(username, email, password_hash, role="candidate", full_name=""):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO users (username, email, password_hash, role, full_name, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (username, email, password_hash, role, full_name, now()),
        )


def get_user_by_username(username):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def update_user_profile(user_id, full_name, target_role, bio):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET full_name = ?, target_role = ?, bio = ? WHERE id = ?",
            (full_name, target_role, bio, user_id),
        )


# ---------------- Resumes ----------------

def save_resume(user_id, filename, raw_text, skills, score, feedback):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO resumes (user_id, filename, raw_text, skills, score, feedback, uploaded_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, filename, raw_text, json.dumps(skills), score, feedback, now()),
        )


def get_resumes_by_user(user_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM resumes WHERE user_id = ? ORDER BY uploaded_at DESC", (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_latest_resume(user_id):
    resumes = get_resumes_by_user(user_id)
    return resumes[0] if resumes else None


# ---------------- Interviews ----------------

def save_interview_result(user_id, role, question, answer, sentiment_label,
                           sentiment_score, relevance_score, overall_score,
                           specificity_score=None, feedback=None):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO interview_sessions
               (user_id, role, question, answer, sentiment_label, sentiment_score,
                relevance_score, specificity_score, overall_score, feedback, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, role, question, answer, sentiment_label, sentiment_score,
             relevance_score, specificity_score, overall_score, feedback, now()),
        )


def get_interview_history(user_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM interview_sessions WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------- Emotion ----------------

def save_emotion_log(user_id, source, emotion, confidence):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO emotion_logs (user_id, source, emotion, confidence, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, source, emotion, confidence, now()),
        )


def get_emotion_history(user_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM emotion_logs WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------- Voice ----------------

def save_voice_log(user_id, transcript, duration_seconds, words_per_minute, filler_word_count):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO voice_logs
               (user_id, transcript, duration_seconds, words_per_minute, filler_word_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, transcript, duration_seconds, words_per_minute, filler_word_count, now()),
        )


def get_voice_history(user_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM voice_logs WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------- Jobs / Recruiter ----------------

def create_job(recruiter_id, title, description, location=""):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO jobs (recruiter_id, title, description, location, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (recruiter_id, title, description, location, now()),
        )


def get_jobs_by_recruiter(recruiter_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs WHERE recruiter_id = ? ORDER BY created_at DESC", (recruiter_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_jobs():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def apply_to_job(job_id, user_id, match_score):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO applications (job_id, user_id, match_score, created_at)
               VALUES (?, ?, ?, ?)""",
            (job_id, user_id, match_score, now()),
        )


def get_applications_for_job(job_id):
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT applications.*, users.username, users.full_name
               FROM applications JOIN users ON applications.user_id = users.id
               WHERE job_id = ? ORDER BY match_score DESC""",
            (job_id,),
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------- Coding ----------------

def save_coding_submission(user_id, problem_title, code, passed, output):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO coding_submissions
               (user_id, problem_title, code, passed, output, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, problem_title, code, int(passed), output, now()),
        )


def get_coding_history(user_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM coding_submissions WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
