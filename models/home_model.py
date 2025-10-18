#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 17 20:48:47 2025

@author: mariusz
"""

import sqlite3


class HomeModel():
    """ Home data model """

    def __init__(self, db_name='qcms.db'):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        """
        Initialization of db and table
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='params'")
            exists = cursor.fetchone()

            if not exists:
                cursor.executescript('''
                      CREATE TABLE IF NOT EXISTS params(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT NOT NULL UNIQUE,
                          value TEXT);
                      INSERT INTO params(name, value) VALUES('creation_date', '17.10.2025 21:30');
                      INSERT INTO params(name, value) VALUES('modification_date', strftime('%d.%m.%Y %H:%M', 'now', 'localtime'));
                      INSERT INTO params(name, value) VALUES('version', '0.2.0');
                ''')

    def get_param(self, name: str) -> str | None:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute('SELECT value FROM params WHERE name = ?', (name,))
            row = cur.fetchone()
            return row[0] if row else None

    def set_param(self, name: str, value: str) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO params(name, value) VALUES(?, ?) '
                'ON CONFLICT(name) DO UPDATE SET value=excluded.value',
                (name, value)
            )

    def get_footer_data(self):
        """
        Get page version, date of creation and date of last modification
        Returns
        -------
        version
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            footer_data = {}
            for name in ('version', 'creation_date', 'modification_date'):
                cursor.execute('SELECT value FROM params WHERE name = ?', (name,))
                row = cursor.fetchone()
                footer_data[name] = row[0] if row else None
            return footer_data or None
