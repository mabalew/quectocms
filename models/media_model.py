#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 18 18:54:20 2025

@author: mariusz
"""

import sqlite3
from typing import Optional, List, Dict

class MediaModel:
    def __init__(self, db_name: str = 'qcms.db'):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS media (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    sha256      TEXT NOT NULL UNIQUE,
                    rel_path    TEXT NOT NULL UNIQUE,    -- np. uploads/2025/10/18/abcd1234_name.jpg
                    mime        TEXT NOT NULL,
                    uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_media_sha256 ON media(sha256);
                CREATE INDEX IF NOT EXISTS idx_media_uploaded_at ON media(uploaded_at);
            """)

    def get_by_hash(self, sha256: str) -> Optional[Dict]:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.execute("SELECT id, sha256, rel_path, mime, uploaded_at FROM media WHERE sha256=?", (sha256,))
            row = cur.fetchone()
        if not row:
            return None
        return {"id": row[0], "sha256": row[1], "rel_path": row[2], "mime": row[3], "uploaded_at": row[4]}

    def insert(self, sha256: str, rel_path: str, mime: str) -> int:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.execute("""
                INSERT INTO media(sha256, rel_path, mime) VALUES(?,?,?)
            """, (sha256, rel_path, mime))
            return cur.lastrowid
        
    def delete(self, rel_path: str) -> int:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.execute("""
                              DELETE FROM media WHERE rel_path=?;
            """, (rel_path,))
            return cur.rowcount

    def recent(self) -> List[Dict]:
        # rekordy z dzisiaj i wczoraj wg czasu lokalnego
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.execute("""
                SELECT id, sha256, rel_path, mime, uploaded_at
                FROM media
                ORDER BY uploaded_at DESC
                LIMIT 25
            """)
            rows = cur.fetchall()
            print(rows)
        return [{"id": r[0], "sha256": r[1], "rel_path": r[2], "mime": r[3], "uploaded_at": r[4]} for r in rows]
    

