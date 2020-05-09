#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela


class RequestResult:

    def __init__(self, error, exception=None, response=None):
        self.error = error
        self.exception = exception
        self.response = response
        if error and exception is None:
            raise Exception("Exception cannot be None when error is True")

    def get_exception(self):
        return self.exception

    def is_error(self):
        return self.error

    def get_response(self):
        return self.response


class ErrorResult(RequestResult):

    def __init__(self, exception):
        super(ErrorResult, self).__init__(True, exception)


class LoginResult(RequestResult):

    def __init__(self, session):
        super(LoginResult, self).__init__(False, None, None)
        self.session = session

    def get_session(self):
        return self.session


class CSRFResult(RequestResult):

    def __init__(self, csrf):
        super(CSRFResult, self).__init__(False, None, None)
        self.csrf = csrf

    def get_csrf(self):
        return self.csrf
