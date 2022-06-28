#!/usr/bin/env python
# coding: utf-8

import re
import json
import datetime
import itertools
from time import sleep
from pprint import pprint
from bs4 import BeautifulSoup
from requests import Request, Session
from pydantic import BaseModel
from typing import Dict, Optional

_exp_regex = "\d+[+|/|*|-]\d+"

OKAY = 'OK'
NOT_OKAY = 'NOT_FOUND'

class PANDetailsData(BaseModel):
    name: str = "PAN Details"
    description: Optional[str]
    raw_data: dict
    status: Optional[str]

class PANDetails():
    def __init__(self):
        #initializing custom headers
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36'}

        #initializing some parameters
        self.home_url = 'https://ird.gov.np/pan-search'
        self.post_url = "https://ird.gov.np/statstics/getPanSearch"
        
        self.session = Session()
    
    def parseParams(self):
        #getting home page and extracting parameters
        home = self.session.get(self.home_url, headers = self.headers)
        home_soup = BeautifulSoup(home.text, 'html.parser')
        _token = home_soup.find('input', {'name': '_token'}).get('value')
        self.params["_token"] = _token
        _expression_text = home_soup.select("#mid label")[0].text.strip()
        self.params["_expression_text"] = _expression_text
        if not _expression_text:
            return self.params
        _expression = re.search(_exp_regex, _expression_text).group()
        self.params["_expression"] = _expression
        _expression_value = eval(_expression)
        self.params["_expression_value"] = _expression_value
        return True
    
    def format(self, details):
        if details == 0:
            return PANDetailsData(
                raw_data = {},
                status = NOT_OKAY
            )
        return PANDetailsData(
            raw_data = details,
            status = OKAY
        )
    
    def getDetails(self, pan_no):
        self.params = {
            "pan_no": pan_no
        }
        if self.parseParams():
            post_data = {
                "_token": self.params["_token"],
                "pan": pan_no,
                "captcha": self.params["_expression_value"]
            }
            details = self.session.post(self.post_url, headers=self.headers, data=post_data).json()
            return self.format(details)
            
        