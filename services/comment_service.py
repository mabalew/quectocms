#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 17 17:28:55 2025

@author: mariusz
"""

from models.comment_model import CommentModel

class CommentService:
    """ Comment service class """
    def __init__(self):
        self.comment_model = CommentModel()
        
    def add(self, ip, user, comment):
        """ Adds new comment """
        if not user or not user.strip():
            return False, "USER_CANT_BE_EMPTY"
        if not ip or not ip.strip():
            return False, "IP_CANT_BE_EMPTY"
        if not comment or not comment.strip():
            return False, "COMMENT_CANT_BE_EMPTY"
        comment_id = self.comment_model.add(ip, user, comment)
        if not comment_id:
            return False, "UNKNOWN_ERROR"
        
        return True, comment_id

    def get_all(self):
        """ Get all comments """
        return self.comment_model.get_all()
    