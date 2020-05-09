#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

import datetime

import requests

from openKirkesConverter.converter import *
from .classes import *


class KirkesClient:

    def __init__(self, user_auth, kirkes_base_url="https://kirkes.finna.fi/"):
        self.user_auth = user_auth
        self.baseUrl = kirkes_base_url

    def get_request(self, url):
        try:
            r = requests.get(self.baseUrl + url)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def post_request(self, url, data):
        try:
            r = requests.post(self.baseUrl + url, data=data)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def getLoginCSRF(self):
        result = self.get_request("/MyResearch/UserLogin?layout=lightbox")
        if not result.is_error():
            response = result.get_response()
            if result.status_code == 200:
                csrf = extractCSRF(response.text)
                if csrf is not None:
                    return CSRFResult(csrf)
            return ErrorResult(Exception("Unable to find CSRF token"))
        else:
            return result

    def login(self, username, password):
        csrf_token = self.getLoginCSRF()
        if csrf_token.is_error():
            return csrf_token
        post_data = {
            "username": username,
            "password": password,
            "target": "kirkes",
            "auth_method": "MultiILS",
            "layout": "lightbox",
            "csrf": csrf_token.get_csrf()
        }
        post_result = self.post_request("/MyResearch/Home", post_data)
        if not post_result.is_error():
            if post_result.get_response().status_code is 205:
                cookies = post_result.cookies
                print(cookies)
                return LoginResult("")
            else:
                return ErrorResult(Exception("Invalid credentials"))
        else:
            return post_result

    def confirmAuthExists(self):
        if self.user_auth is None:
            raise Exception("user_auth should not be None!")

    def check_session_life(self):
        last_used = self.user_auth.lastusage
        return (datetime.time() - last_used) >= 3600
