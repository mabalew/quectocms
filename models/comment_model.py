#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 17 21:00:21 2025

@author: mariusz
"""
import sqlite3


class CommentModel:
    """ Comments data model """

    def __init__(self, db_name='qbrack.db'):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        """
        Initialization of db and table
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
                      CREATE TABLE IF NOT EXISTS comments(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          ip TEXT NOT NULL,
                          creation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                          user TEXT,
                          comment TEXT NOT NULL
                          )
                      ''')
        conn.commit()
        conn.close()

    def add(self, ip, user, comment):
        """
        Parameters
        ----------
        ip : TYPE
            IP address: xxx.xxx.xxx.xxx.
        user : TYPE
            the name or email provided by the user.
        comment : TYPE
            comment itself.

        Returns
        -------
        comment_id : TYPE
            id of the newly inserted comment.
        None: in case of unexpected problems

        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO comments(ip, user, comment) VALUES(?, ?, ?)', (ip, user, comment,))
        conn.commit()
        comment_id = cursor.lastrowid
        conn.close()
        if comment_id:
            return comment_id
        return None

    def get_all(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, ip, user, comment, datetime(creation_date, 'localtime') FROM comments")
        comments = cursor.fetchall()
        conn.close()
        return [{'id': comment[0], 'ip': comment[1], 'user': comment[2], 'comment': comment[3], 'creation_date': comment[4]} for comment in comments]
