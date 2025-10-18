#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 18 23:19:16 2025

@author: mariusz
"""
# auth.py
import os
from functools import wraps
from flask import request, Response
from werkzeug.security import check_password_hash

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
# wygeneruj hash np. w pythonie:
# >>> from werkzeug.security import generate_password_hash
# >>> generate_password_hash("yourStrongPassword")
ADMIN_PASS_HASH = os.getenv("ADMIN_PASS_HASH", "pbkdf2:sha256:260000$...")

def _auth_failed():
    return Response(
        "Authentication required",
        401,
        {"WWW-Authenticate": 'Basic realm="Restricted"'}
    )

def requires_basic_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != ADMIN_USER:
            return _auth_failed()
        if not check_password_hash(ADMIN_PASS_HASH, auth.password):
            return _auth_failed()
        return f(*args, **kwargs)
    return wrapper
