#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 18 00:49:38 2025

@author: mariusz
"""

import sqlite3

class PageModel:
    """ Micro CMS page model """
    def __init__(self, db_name = 'qcms.db'):
        self.db_name = db_name
        self.init_db()
        
    def init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                       CREATE TABLE IF NOT EXISTS pages (
                           id            INTEGER PRIMARY KEY AUTOINCREMENT,
                          page          TEXT    NOT NULL,               -- np. 'home', 'about'
                          page_order INTEGER NOT NULL,
                          locale        TEXT    NOT NULL DEFAULT 'pl',  -- opcjonalnie i18n
                          content       TEXT    NOT NULL,               -- TEXT zamiast BLOB dla HTML/Markdown
                          position      INTEGER NOT NULL DEFAULT 0,     -- jeśli chcesz sortowanie segmentów
                          UNIQUE(page, locale, position)                 -- klucz naturalny
                          )
                       """)

    def _resolve_page_order(self, page: str) -> int:
         """Returns existing page_order for a given page or assigns a new one."""
         with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("SELECT MIN(page_order) FROM pages WHERE page=?", (page,))
            row = cur.fetchone()
            if row and row[0] is not None:
                return int(row[0])
            cur.execute("SELECT COALESCE(MAX(page_order), -1) + 1 FROM pages")
            nxt = cur.fetchone()[0]
            return int(nxt)

    def add(self, page: str, locale: str, position: int, page_order: int, content: str) -> int:
        if page_order == 0:
            po = self._resolve_page_order(page)
        else:
            po = page_order
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO pages(page, page_order, locale, content, position)
                VALUES(?, ?, ?, ?, ?)
            """, (page, po, locale, content, int(position)))
            return cur.lastrowid

    def get(self, page: str, locale: str = 'en') -> list[str]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute('''
                              SELECT content
                              FROM pages
                              WHERE page=? AND locale=?
                              ORDER BY position
                        ''', (page, locale ))
            return [line[0] for line in cursor.fetchall()]
    
    def delete(self, page_id: int) -> int:
        with sqlite3.connect(self.db_name) as conn:
            conn.execute('DELETE FROM pages WHERE id=?', (page_id,))
        return {'deleted_id': page_id}
    
    def get_pages_list(self) -> list[str]:
        with sqlite3.connect(self.db_name) as conn:
            #cursor = conn.execute('SELECT DISTINCT page FROM pages ORDER BY page_order ASC')
            cursor = conn.execute("""
                                  SELECT page, MIN(page_order) AS ord
                                  FROM pages
                                  GROUP BY page
                                  ORDER BY ord ASC
                         """)
            return [page[0] for page in cursor.fetchall()]