#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 18 18:55:54 2025

@author: mariusz
"""
import hashlib
from typing import Optional, List, Dict
from werkzeug.utils import secure_filename
from flask import redirect, url_for
from urllib.parse import unquote
from pathlib import Path

from models.media_model import MediaModel

class MediaService:
    
    def __init__(self):
        self.media_model = MediaModel()
    
    def get_by_hash(self, sha256: str) -> Optional[Dict]:
        return self.media_model.get_by_hash(sha256)
    
    def recent(self) -> List[Dict]:
        return self.media_model.recent()
    
    def _norm_filename(self, filename: str) -> str:
        fn = secure_filename(filename or '').lower()
        return fn.replace(' ', '-')

    def _calc_sha256(self, file_storage) -> str:
        h = hashlib.sha256()
        for chunk in iter(lambda: file_storage.stream.read(8192), b''):
            h.update(chunk)
        file_storage.stream.seek(0)
        return h.hexdigest()
    
    def insert(self, sha256: str, rel_path: str, mime: str) -> int:
        return self.media_model.insert(sha256, rel_path, mime)
    
    def delete(self, rel_path: str, locale: str) -> int:
        STATIC_ROOT = 'static'

        rel_path = unquote(rel_path)
        if rel_path.startswith('/static/'):
            rel_path = rel_path[len('/static/'):]
        elif rel_path.startswith('static/'):
            rel_path = rel_path[len('static/'):]
            
        # delete file from disk
        abs_path = Path(STATIC_ROOT) / rel_path
        try:
            abs_path.unlink()
        except FileNotFoundError:
            pass
        self.media_model.delete(rel_path)
        return redirect(url_for('admin_page', lang=locale))