#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 17 17:40:24 2025

@author: mariusz
"""

from models.home_model import HomeModel

class HomeService:
    """ Home page service """
    def __init__(self):
        """ Default constructor """
        self.home_model = HomeModel()
        
    def get_footer_data(self):
        """ Gets version of the page, date of creation and date of last modification """
        return self.home_model.get_footer_data()

    def get_param(self, name):
        return self.home_model.get_param(name)
    
    def set_param(self, name, value):
        return self.home_model.set_param(name, value)