#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 18 01:20:19 2025

@author: mariusz
"""
from flask import request, render_template, redirect, url_for

from models.page_model import PageModel
from services.comment_service import CommentService
from services.home_service import HomeService

class PageService:
    """ Service for pages in my Micro CMS """
    def __init__(self):
        self.page_model = PageModel()
        self.comment_service = CommentService()
        self.home_service = HomeService()

    def add(self, page: str, locale: str, position: int, content: str):
        return self.page_model.add(page, locale, position, content)   
        
    def get(self, page, locale):
        return self.page_model.get(page, locale)
    
    def get_pages_list(self):
        return self.page_model.get_pages_list()
    
    def _site_title(self) -> str | None:
        return self.home_service.get_param('title')
    
    def render_page(self, page: str):
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
                                   footer_data=footer_data
                                   )

        # GET
        return render_template('add_page.html',
                               locale=locale,
                               site_title=site_title,
                               pages=pages,
                               comments=comments,
                               footer_data=footer_data
                               )

    def delete(self, page_id: int) -> int:
        return self.page_model.delete(page_id)