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

    def __init__(self, exception, code=500):
        super(ErrorResult, self).__init__(True, exception)
        self.code = code

    def get_code(self):
        return self.code


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

    def __init__(self, locations, details, default_location):
        super(PickupLocationsResult, self).__init__(False, None, None)
        self.locations = locations
        self.details = details
        self.default_location = default_location

    def get_locations(self):
        return self.locations

    def get_details(self):
        return self.details

    def get_default(self):
        return self.default_location


class RenewResult(RequestResult):

    def __init__(self, msg):
        super(RenewResult, self).__init__(False, None, None)
        self.msg = msg

    def get_message(self):
        return self.msg


class HoldsResult(RequestResult):

    def __init__(self, holds):
        super(HoldsResult, self).__init__(False, None, None)
        self.holds = holds

    def get_holds(self):
        return self.holds,


class LibInfoRequest(RequestResult):

    def __init__(self, libs):
        super(LibInfoRequest, self).__init__(False, None, None)
        self.libs = libs

    def get_libs(self):
        return self.libs


class SearchRequest(RequestResult):

    def __init__(self, results, count):
        super(SearchRequest, self).__init__(False, None, None)
        self.results = results
        self.count = count

    def get_count(self):
        return self.count

    def get_results(self):
        return self.results


class DetailsRequest(RequestResult):

    def __init__(self, details):
        super(DetailsRequest, self).__init__(False, None, None)
        self.details = details

    def get_details(self):
        return self.details


class PickupLocationRequest(RequestResult):

    def __init__(self, location):
        super(PickupLocationRequest, self).__init__(False, None, None)
        self.location = location

    def get_location(self):
        return self.location


class FeesRequest(RequestResult):

    def __init__(self, fees):
        super(FeesRequest, self).__init__(False, None, None)
        self.fees = fees

    def get_Fees(self):
        return self.fees


class HashKeyRequest(RequestResult):

    def __init__(self, hashkey):
        super(HashKeyRequest, self).__init__(False, None, None)
        self.hashkey = hashkey

    def get_key(self):
        return self.hashkey


class CSRFResult(RequestResult):

    def __init__(self, csrf):
        super(CSRFResult, self).__init__(False, None, None)
        self.csrf = csrf

    def get_csrf(self):
        return self.csrf
