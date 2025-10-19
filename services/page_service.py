#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 18 01:20:19 2025

@author: mariusz
"""
import os, mimetypes, datetime
from pathlib import Path
from flask import request, render_template, redirect, url_for

from models.page_model import PageModel
from services.comment_service import CommentService
from services.home_service import HomeService
from services.media_service import MediaService

ALLOWED_EXT = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
STATIC_ROOT = 'static'
UPLOAD_BASE = 'uploads'  # will be: static/uploads/YYYY/MM/DD/...

class PageService:
    """ Service for pages in my Micro CMS """
    def __init__(self):
        self.page_model = PageModel()
        self.comment_service = CommentService()
        self.home_service = HomeService()
        self.media_service = MediaService()

    def add(self, page: str, locale: str, position: int, content: str):
        return self.page_model.add(page, locale, position, content)   
        
    def get(self, page, locale):
        return self.page_model.get(page, locale)
    
    def get_pages_list(self):
        return self.page_model.get_pages_list()
    
    def _site_title(self) -> str | None:
        return self.home_service.get_param('title')
    
    def render_page(self, page: str):
        if page and page == 'admin':
            return self.render_admin_page(page)
        locale = self.detect_locale()
        site_title = self.home_service.get_param('title')
        if not site_title:
            return redirect(url_for('add_page', lang=locale))
        blocks = self.get(page, locale)
        comments, footer_data = self.get_comments_and_footer()
        pages = self.get_pages_list()
        return render_template(
                'page.html',
                page=page,
                locale=locale,
                blocks=blocks,
                site_title=site_title,
                comments=comments,
                footer_data=footer_data,
               pages = pages
       )
    
    def render_admin_page(self, page: str):
        locale = self.detect_locale()
        site_title = self.home_service.get_param('title')
        if not site_title:
            return redirect(url_for('add_page', lang=locale))
        footer_data = self.home_service.get_footer_data()
        pages = self.get_pages_list()
        return render_template(
                'admin.html',
                page=page,
                locale=locale,
                site_title=site_title,
                footer_data=footer_data,
                pages = pages
                )
    
    def get_comments_and_footer(self):
        comments = self.comment_service.get_all()
        footer_data = self.home_service.get_footer_data()
        return comments, footer_data
    
    def detect_locale(self) -> str:
        return 'en'
        lang = request.args.get('lang')
        if lang:
            return lang
        try:
            return request.accept_languages.best_match(['en', 'pl']) or 'en'
        except Exception:
            return 'en'
    
    def add_page_response(self):
        """
        GET: if there's no title -> title form; if title exists -> adding content form.
        POST: if there's no title -> saves title; if title exists-> add block and redirect.
        Returns HTTP response (render or redirect).
        """
        locale = self.detect_locale()
        site_title = self._site_title()
        pages = self.page_model.get_pages_list()
        comments = self.comment_service.get_all()
        footer_data = self.home_service.get_footer_data()
        recent_media = [
            {"url": f"/static/{m['rel_path']}", "mime": m["mime"], "uploaded_at": m["uploaded_at"]}
            for m in self.media_service.recent_from_today_and_yesterday()
        ]

        if request.method == 'POST':
            # if there's not title, try to set it up
            if not site_title:
                new_title = (request.form.get('title') or '').strip()
                if new_title:
                    self.home_service.set_param('title', new_title)
                    site_title = new_title
                else:
                    # no title -> show our form again
                    return render_template('add_page.html',
                                           locale=locale,
                                           site_title=None,
                                           pages=pages,
                                           comments=comments,
                                           recent_media=recent_media,
                                           footer_data=footer_data
                                           )

            # if title exists let's work with content
            page = (request.form.get('page') or '').strip()
            position = (request.form.get('position') or '').strip()
            content = (request.form.get('content') or '').strip()
            page_order = (request.form.get('page_order') or '').strip()
            if page and position.isdigit() and page_order.isdigit() and content:
                self.page_model.add(page, locale, int(position), int(page_order), content)
                return redirect(url_for('show_page', page=page, lang=locale))

            # no content -> show form
            return render_template('add_page.html',
                                   locale=locale,
                                   site_title=site_title,
                                   pages=pages,
                                   comments=comments,
                                   recent_media=recent_media,
                                   footer_data=footer_data
                                   )

        # GET
        return render_template('add_page.html',
                               locale=locale,
                               site_title=site_title,
                               pages=pages,
                               comments=comments,
                               recent_media=recent_media,
                               footer_data=footer_data
                               )

    def delete(self, page_id: int) -> int:
        return self.page_model.delete(page_id)
    
    def delete_by_name(self, page_name: str):
        self.page_model.delete_by_name(page_name)
        locale = self.detect_locale()
        return redirect(url_for('admin_page', lang=locale))
    
    def render_edit_page(self, page: str):
        """Render edit pagei: list of blocks + forms."""
        locale = self.detect_locale()
        site_title = self.home_service.get_param('title')
        if not site_title:
            return redirect(url_for('add_page', lang=locale))

        # context data
        pages = self.page_model.get_pages_list()
        comments = self.comment_service.get_all()
        footer_data = self.home_service.get_footer_data()

        blocks = self.page_model.get_blocks_for_page(page, locale)

        return render_template(
            'edit_page.html',
            page=page,
            locale=locale,
            site_title=site_title,
            pages=pages,
            comments=comments,
            footer_data=footer_data,
            blocks=blocks
        )
    
    def save_block(self, block_id: int):
        """Save of one block (position + content) and return to edit this page."""
        page = (request.form.get('page') or '').strip()
        locale = (request.form.get('locale') or '').strip() or self.detect_locale()
        pos_raw = (request.form.get('position') or '').strip()
        content = request.form.get('content') or ''

        if not page or not pos_raw.isdigit():
            return redirect(url_for('edit_page', page=page or 'home', lang=locale))

        self.page_model.update_block(block_id=int(block_id), position=int(pos_raw), content=content)
        return redirect(url_for('edit_page', page=page, lang=locale))

    def delete_block(self, block_id: int):
        """Delete one block and return to edit this page."""
        page = (request.form.get('page') or '').strip()
        locale = (request.form.get('locale') or '').strip() or self.detect_locale()
        self.page_model.delete_block_by_id(int(block_id))
        return redirect(url_for('edit_page', page=page or 'home', lang=locale))
    
    def media_upload_response(self):
        locale = self.detect_locale()
        pages = self.page_model.get_pages_list()
        comments = self.comment_service.get_all()
        footer_data = self.home_service.get_footer_data() or {}
        site_title = self.home_service.home_model.get_param('title')

        file = request.files.get('file')
        media_result = None
        error = None
    
        if not file or not file.filename:
            error = "No file selected."
        else:
            original = self.media_service._norm_filename(file.filename)
            name, ext = os.path.splitext(original)
            if ext not in ALLOWED_EXT:
                error = "Unsupported extension."
            else:
                sha = self.media_service._calc_sha256(file)
                existing = self.media_service.get_by_hash(sha)
                if existing:
                    url = f"/static/{existing['rel_path']}"
                    media_result = {"url": url, "sha256": sha, "mime": existing['mime'], "deduplicated": True}
                else:
                    rel_dir = self._date_rel_dir()
                    prefix = sha[:12]
                    rel_name = f"{prefix}_{name}{ext}"
                    rel_path = f"{rel_dir}/{rel_name}"
                    abs_dir = Path(STATIC_ROOT) / rel_dir
                    abs_dir.mkdir(parents=True, exist_ok=True)
                    abs_path = Path(STATIC_ROOT) / rel_path
    
                    file.save(abs_path)
    
                    mime = mimetypes.types_map.get(ext, 'application/octet-stream')
    
                    self.media_service.insert(sha, rel_path, mime)
                    url = f"/static/{rel_path}"
                    media_result = {"url": url, "sha256": sha, "mime": mime, "deduplicated": False}
    
        recent_media = [
            {"url": f"/static/{m['rel_path']}", "mime": m["mime"], "uploaded_at": m["uploaded_at"]}
            for m in self.media_service.recent_from_today_and_yesterday()
        ]
        return render_template(
            'add_page.html',
            locale=locale,
            site_title=site_title,
            pages=pages,
            comments=comments,
            footer_data=footer_data,
            media_result=media_result,
            media_error=error,
            recent_media=recent_media
            )
    
    def _date_rel_dir(self) -> str:
        now = datetime.datetime.now()
        return f"{UPLOAD_BASE}/{now.year:04d}/{now.month:02d}/{now.day:02d}"