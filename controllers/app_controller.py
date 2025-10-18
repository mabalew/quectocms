#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 17 16:52:51 2025

@author: mariusz
"""
from flask import  request, jsonify, redirect, url_for
from services.comment_service import CommentService
from services.home_service import HomeService
from services.page_service import PageService

class AppController:
    """ Application controller """
    
    def __init__(self, app):
        self.app = app
        self.comment_service = CommentService()
        self.home_service = HomeService()
        self.page_service = PageService()
        self.setup_routes()

    def setup_routes(self):
        """ Routes """
        @self.app.route('/')
        def home():
            """ Start point """
            return self.page_service.render_page('home')
 
        @self.app.route('/pages_list')
        def get_pages_list():
            return jsonify({'pages': self.page_service.get_pages_list()})
    
        @self.app.route('/page/<page>')
        def show_page(page):
            return self.page_service.render_page(page)
        
        @self.app.route('/add_page', methods=['GET', 'POST'])
        def add_page():
            return self.page_service.add_page_response()
        
        @self.app.route('/del_page/<page_id>')
        def del_page(page_id: int):
            return self.page_service.delete(page_id)
        
        @self.app.route('/add_comment', methods=['POST'])
        def add_comment():
            """ Adding new comment """
            comment = request.form.get('comment', '')
            user = request.form.get('user', '')
            ip = request.remote_addr
            result, message = self.comment_service.add(ip, user, comment)
            return redirect(url_for('home'))
        
        @self.app.route('/get_comments')
        def get_comments():
            comments = self.comment_service.get_all()
            return jsonify({ 'comments': comments })
        
        @self.app.route('/upload_media', methods=['POST'])
        def upload_media():
            return self.page_service.media_upload_response()

    

