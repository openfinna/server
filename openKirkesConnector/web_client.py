#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

import datetime

import requests

from openKirkesConverter.converter import *
from .classes import *
from urllib.parse import urlparse


class KirkesClient:


    def __init__(self, user_auth, language="en-gb", user_object=None, kirkes_base_url="https://kirkes.finna.fi", kirkes_sessioncheck_url="/AJAX/JSON?method=getUserTransactions"):
        self.user_auth = user_auth
        self.language = language
        self.baseUrl = kirkes_base_url
        self.user_object = user_object
        self.sessionCheck_path = kirkes_sessioncheck_url
        self.sessionHttp = requests.Session()
        cookie_obj = requests.cookies.create_cookie(domain=self.getBaseURLDomainName(), name='language',
                                                    value=self.language)
        self.sessionHttp.cookies.set_cookie(cookie_obj)


    def getBaseURLDomainName(self):
        return '{uri.netloc}'.format(uri=urlparse(self.baseUrl))

    def get_request(self, url):
        headers = {'Referer': self.baseUrl + "/", 'Origin': self.baseUrl + "/", 'User-Agent': 'Mozilla/5.0'}
        try:
            r = self.sessionHttp.get(self.baseUrl + url, headers=headers)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def authenticated_get_request(self, url):
        sessionCookie = requests.cookies.create_cookie(domain=self.getBaseURLDomainName(), name='PHPSESSID',
                                                    value=self.user_auth.session)
        self.sessionHttp.cookies.set_cookie(sessionCookie)
        headers = {'Referer': self.baseUrl + "/", 'Origin': self.baseUrl + "/", 'User-Agent': 'Mozilla/5.0'}
        try:
            r = self.sessionHttp.get(self.baseUrl + url, headers=headers)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def post_request(self, url, data, headers=None, followRedirects=True):
        self.sessionHttp.cookies.set(**{'name': "language", 'value': self.language})
        if headers is None:
            headers = {'Referer': self.baseUrl + "/", 'Origin': self.baseUrl + "/", 'User-Agent': 'Mozilla/5.0'}
        try:
            r = self.sessionHttp.post(self.baseUrl + url, data=data, headers=headers, allow_redirects=followRedirects)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def getLoginCSRF(self):
        result = self.get_request("/MyResearch/UserLogin?layout=lightbox")
        if not result.is_error():
            response = result.get_response()
            if response.status_code == 200:
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
            "csrf": csrf_token.get_csrf(),
            "processLogin": "Kirjaudu",
            "secondary_username": ""
        }

        print(post_data)
        post_result = self.post_request(
            "/MyResearch/Home?layout=lightbox&lbreferer=https%3A%2F%2Fkirkes.finna.fi%2FMyResearch%2FUserLogin",
            post_data)
        if not post_result.is_error():
            print(post_result.get_response())
            if post_result.get_response().status_code is 205:
                cookies = self.sessionHttp.cookies
                session = cookies.get("PHPSESSID", None)
                if session is None:
                    return ErrorResult(Exception("Cannot retrieve Session ID"))
                else:
                    return LoginResult(session)
            else:
                return ErrorResult(Exception("Invalid credentials"))
        else:
            return post_result

    def confirmAuthExists(self):
        if self.user_auth is None:
            raise Exception("user_auth should not be None!")
        if self.user_object is None:
            raise Exception("user_object should not be None!")

    def preCheck(self):
        self.confirmAuthExists()
        if self.check_session_life():
            loginResult = self.login(self.user_auth.username, self.user_auth.password)
            if not loginResult.is_error():
                self.user_auth.session = loginResult.get_session()
                self.user_object.updateAuthentication(self.user_auth, self.user_object.encryption_key)
                result = self.validate_session()
                if result.is_error():
                    return result
            else:
                return loginResult
        return None

    def validate_session(self):
        result = self.authenticated_get_request(self.sessionCheck_path)
        if not result.is_error():
            if result.get_response().status_code == 200:
                return RequestResult(False)
            else:
                return ErrorResult(Exception("Unable to log in to kirkes"))
        else:
            return result

    def loans(self):
        checkResult = self.preCheck()
        if checkResult is not None:
            return checkResult
        requestResult = self.authenticated_get_request("/MyResearch/CheckedOut")
        if not requestResult.is_error():
            response = requestResult.get_response()
            if response.status_code == 200:
                parsedLoans = extractLoans(self.baseUrl, response.text)
                if parsedLoans is None:
                    return ErrorResult('Loans parsing failed')
                else:
                    return LoansResult(parsedLoans)
            else:
                return ErrorResult("Response code "+response.status_code)
        else:
            return requestResult

    def check_session_life(self):
        last_used = self.user_auth.lastusage.replace(tzinfo=None)
        diff = datetime.datetime.now() - last_used
        datetime.timedelta(0, 8, 562000)
        return diff.seconds >= 600
