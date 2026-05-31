"""
database.py — SQLite orqali barcha ma'lumotlarni saqlash
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.environ.get("DB_PATH", "bot_data.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            username    TEXT,
            full_name   TEXT,
            lang        TEXT DEFAULT 'uz',
            quality     TEXT DEFAULT '720',
            is_banned   INTEGER DEFAULT 0,
            joined_at   TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS downloads (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            url         TEXT,
            quality     TEXT,
            status      TEXT,   -- 'ok' | 'error' | 'size'
            platform    TEXT,   -- 'youtube' | 'tiktok' | 'instagram' | 'other'
            file_size   INTEGER DEFAULT 0,
            created_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS broadcast_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id    INTEGER,
            message     TEXT,
            sent_count  INTEGER DEFAULT 0,
            created_at  TEXT DEFAULT (datetime('now'))
        );
        """)


# ─── USER ────────────────────────────────────────────────────────
def upsert_user(user_id: int, username: str, full_name: str):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO users (user_id, username, full_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username  = excluded.username,
                full_name = excluded.full_name
        """, (user_id, username or "", full_name or ""))


def get_user(user_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def set_user_lang(user_id: int, lang: str):
    with get_conn() as conn:
        conn.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))


def set_user_quality(user_id: int, quality: str):
    with get_conn() as conn:
        conn.execute("UPDATE users SET quality = ? WHERE user_id = ?", (quality, user_id))


def ban_user(user_id: int, ban: bool):
    with get_conn() as conn:
        conn.execute("UPDATE users SET is_banned = ? WHERE user_id = ?", (int(ban), user_id))


def is_banned(user_id: int) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT is_banned FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return bool(row["is_banned"]) if row else False


# ─── DOWNLOADS ───────────────────────────────────────────────────
def detect_platform(url: str) -> str:
    url_lower = url.lower()
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    if "tiktok.com" in url_lower:
        return "tiktok"
    if "instagram.com" in url_lower:
        return "instagram"
    return "other"


def log_download(user_id: int, url: str, quality: str,
                 status: str, file_size: int = 0):
    platform = detect_platform(url)
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO downloads (user_id, url, quality, status, platform, file_size)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, url, quality, status, platform, file_size))


# ─── STATS ───────────────────────────────────────────────────────
def get_global_stats() -> dict:
    with get_conn() as conn:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        active_today = conn.execute("""
            SELECT COUNT(DISTINCT user_id) FROM downloads
            WHERE date(created_at) = date('now')
        """).fetchone()[0]
        total_downloads = conn.execute(
            "SELECT COUNT(*) FROM downloads WHERE status = 'ok'"
        ).fetchone()[0]
        by_platform = conn.execute("""
            SELECT platform, COUNT(*) as cnt
            FROM downloads WHERE status = 'ok'
            GROUP BY platform ORDER BY cnt DESC
        """).fetchall()
        by_quality = conn.execute("""
            SELECT quality, COUNT(*) as cnt
            FROM downloads WHERE status = 'ok'
            GROUP BY quality ORDER BY cnt DESC
        """).fetchall()
        errors = conn.execute(
            "SELECT COUNT(*) FROM downloads WHERE status != 'ok'"
        ).fetchone()[0]
        total_size = conn.execute(
            "SELECT COALESCE(SUM(file_size),0) FROM downloads WHERE status='ok'"
        ).fetchone()[0]

    return {
        "total_users": total_users,
        "active_today": active_today,
        "total_downloads": total_downloads,
        "by_platform": [dict(r) for r in by_platform],
        "by_quality": [dict(r) for r in by_quality],
        "errors": errors,
        "total_size_mb": round(total_size / (1024 * 1024), 1),
    }


def get_user_stats(user_id: int) -> dict:
    with get_conn() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM downloads WHERE user_id=? AND status='ok'",
            (user_id,)
        ).fetchone()[0]
        by_platform = conn.execute("""
            SELECT platform, COUNT(*) as cnt
            FROM downloads WHERE user_id=? AND status='ok'
            GROUP BY platform ORDER BY cnt DESC
        """, (user_id,)).fetchall()
    return {
        "total": total,
        "by_platform": [dict(r) for r in by_platform],
    }


# ─── ADMIN ───────────────────────────────────────────────────────
def get_all_users(limit: int = 50, offset: int = 0) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT u.user_id, u.username, u.full_name, u.lang,
                   u.is_banned, u.joined_at,
                   COUNT(d.id) as dl_count
            FROM users u
            LEFT JOIN downloads d ON d.user_id = u.user_id AND d.status = 'ok'
            GROUP BY u.user_id
            ORDER BY dl_count DESC
            LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()
        return [dict(r) for r in rows]


def get_active_user_ids() -> list[int]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT user_id FROM users WHERE is_banned = 0"
        ).fetchall()
        return [r["user_id"] for r in rows]
