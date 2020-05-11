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


class LoansResult(RequestResult):

    def __init__(self, loans):
        super(LoansResult, self).__init__(False, None, None)
        self.loans = loans

    def get_loans(self):
        return self.loans


class PickupLocationsResult(RequestResult):

    def __init__(self, locations):
        super(PickupLocationsResult, self).__init__(False, None, None)
        self.locations = locations

    def get_locations(self):
        return self.locations


class HoldsResult(RequestResult):

    def __init__(self, holds):
        super(HoldsResult, self).__init__(False, None, None)
        self.holds = holds

    def get_holds(self):
        return self.holds


class CSRFResult(RequestResult):

    def __init__(self, csrf):
        super(CSRFResult, self).__init__(False, None, None)
        self.csrf = csrf

    def get_csrf(self):
        return self.csrf
