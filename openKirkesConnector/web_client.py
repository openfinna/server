#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

import json
from urllib.parse import urlparse

import requests

from openKirkesAuth.classes import UserAuthentication
from openKirkesConverter.converter import *
from .classes import *


class KirkesClient:

    def __init__(self, user_auth, language="en-gb", user_object=None, kirkes_base_url="https://kirkes.finna.fi",
                 kirkes_sessioncheck_url="/AJAX/JSON?method=getUserTransactions"):
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

    def clean_get_request(self, url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            r = self.sessionHttp.get(url, headers=headers)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def authenticated_get_request(self, url, followRedirects=True):
        sessionCookie = requests.cookies.create_cookie(domain=self.getBaseURLDomainName(), name='PHPSESSID',
                                                       value=self.user_auth.session)
        self.sessionHttp.cookies.set_cookie(sessionCookie)
        headers = {'Referer': self.baseUrl + "/", 'Origin': self.baseUrl + "/", 'User-Agent': 'Mozilla/5.0'}
        try:
            r = self.sessionHttp.get(self.baseUrl + url, headers=headers, allow_redirects=followRedirects)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def post_request(self, url, data, headers=None, followRedirects=True):
        if headers is None:
            headers = {'Referer': self.baseUrl + "/", 'Origin': self.baseUrl + "/", 'User-Agent': 'Mozilla/5.0'}
        try:
            r = self.sessionHttp.post(self.baseUrl + url, data=data, headers=headers, allow_redirects=followRedirects)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def authenticated_post_request(self, url, data, headers=None, followRedirects=True):
        sessionCookie = requests.cookies.create_cookie(domain=self.getBaseURLDomainName(), name='PHPSESSID',
                                                       value=self.user_auth.session)
        self.sessionHttp.cookies.set_cookie(sessionCookie)
        if headers is None:
            headers = {'Referer': self.baseUrl + "/", 'Origin': self.baseUrl + "/", 'User-Agent': 'Mozilla/5.0'}
        try:
            r = self.sessionHttp.post(self.baseUrl + url, data=data, headers=headers,
                                      allow_redirects=followRedirects)
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

    # Requests start here
    def login(self, username, password, user_details=False):
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

        post_result = self.post_request(
            "/MyResearch/Home?layout=lightbox&lbreferer=https%3A%2F%2Fkirkes.finna.fi%2FMyResearch%2FUserLogin",
            post_data)
        if not post_result.is_error():
            if post_result.get_response().status_code is 205:
                cookies = self.sessionHttp.cookies
                session = cookies.get("PHPSESSID", None)
                if session is None:
                    return ErrorResult(Exception("Cannot retrieve Session ID"))
                else:
                    if user_details:
                        self.user_auth = UserAuthentication(session, None, None, datetime.datetime.now())
                        self.user_object = {}
                        details = self.getAccountDetails()
                        return LoginResult(session, details.get_user_details())
                    else:
                        return LoginResult(session)
            else:
                return ErrorResult(Exception("Invalid credentials"), 403)
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

    def pickupLocations(self, id, type=None):
        checkResult = self.preCheck()
        if checkResult is not None:
            return checkResult
        type_req = "0"
        if type is not None:
            type_req = type
        requestResult = self.authenticated_get_request(
            "/AJAX/JSON?method={0}&id={1}&requestGroupId={2}".format("getRequestGroupPickupLocations", id, type_req))
        if not requestResult.is_error():
            response = requestResult.get_response()
            try:
                jsonResponse = json.loads(response.text)
            except:
                jsonResponse = None
            if response.status_code == 200:
                if jsonResponse is None:
                    return ErrorResult(Exception("JSON Parsing failed"))
                else:
                    hashKey = self.resource_hash_key(id, False)
                    if hashKey.is_error():
                        return hashKey
                    holding_details_req = self.authenticated_get_request(
                        "/Record/{0}/Hold?id={0}&level=title&hashKey={1}&layout=lightbox#tabnav".format(id,
                                                                                                        hashKey.get_key()),
                        False)
                    if not holding_details_req.is_error():
                        if holding_details_req.get_response().status_code == 200:
                            holding_details = extract_holing_details(holding_details_req.get_response().text)
                            default_location = self.getDefaultPickupLocation()
                            if default_location.is_error():
                                return default_location
                            return PickupLocationsResult(jsonResponse['data']['locations'], holding_details,
                                                         default_location.get_location())
                        else:
                            return ErrorResult(Exception("Response code " + str(response.status_code)))
                    else:
                        return holding_details_req
            else:
                if jsonResponse is not None:
                    errorMsg = str(jsonResponse['data'])
                    return ErrorResult(Exception(errorMsg))
                else:
                    return ErrorResult(Exception("Response code " + str(response.status_code)))
        else:
            return requestResult

    def changePickupLocation(self, actionId, locationId):
        checkResult = self.preCheck()
        if checkResult is not None:
            return checkResult
        requestResult = self.authenticated_get_request(
            "/AJAX/JSON?method={0}&requestId={1}&pickupLocationId={2}".format("changePickupLocation", actionId,
                                                                              locationId))
        if not requestResult.is_error():
            response = requestResult.get_response()
            try:
                jsonResponse = json.loads(response.text)
            except:
                jsonResponse = None
            if response.status_code == 200:
                if jsonResponse is None:
                    return ErrorResult(Exception("JSON Parsing failed"))
                else:
                    if jsonResponse['data']['success']:
                        return RequestResult(False)
                    else:
                        print(jsonResponse['data']['sysMessage'])
                        return ErrorResult(Exception("Kirkes error: " + str(jsonResponse['data']['sysMessage'])))
            else:
                return ErrorResult(Exception("Response code " + str(response.status_code)))
        else:
            return requestResult

    def changeDefaultPickupLocation(self, locationId):
        checkResult = self.preCheck()
        if checkResult is not None:
            return checkResult
        requestResult = self.authenticated_post_request(
            "/MyResearch/Profile", {
                'home_library': locationId
            })
        if not requestResult.is_error():
            response = requestResult.get_response()
            if response.status_code == 200:
                result = getHomeLibraryResult(response.text)
                if result:
                    return RequestResult(False)
                else:
                    return ErrorResult("Default pickup library changing failed")
            else:
                return ErrorResult(Exception("Response code " + str(response.status_code)))
        else:
            return requestResult

    def getDefaultPickupLocation(self):
        checkResult = self.preCheck()
        if checkResult is not None:
            return checkResult
        requestResult = self.authenticated_get_request(
            "/MyResearch/Profile")
        if not requestResult.is_error():
            response = requestResult.get_response()
            if response.status_code == 200:
                result = getHomeLibrary(response.text)
                return PickupLocationRequest(result)
            else:
                return ErrorResult(Exception("Response code " + str(response.status_code)))
        else:
            return requestResult

    def getAccountDetails(self):
        checkResult = self.preCheck()
        if checkResult is not None:
            return checkResult
        requestResult = self.authenticated_get_request(
            "/MyResearch/Profile")
        if not requestResult.is_error():
            response = requestResult.get_response()
            if response.status_code == 200:
                user_details = getUserDetails(response.text)
                return UserDetailsRequest(user_details)
            else:
                return ErrorResult(Exception("Response code " + str(response.status_code)))
        else:
            return requestResult

    def getFines(self):
        checkResult = self.preCheck()
        if checkResult is not None:
            return checkResult
        requestResult = self.authenticated_get_request(
            "/MyResearch/Fines")
        if not requestResult.is_error():
            response = requestResult.get_response()
            if response.status_code == 200:
                result = getFines(response.text)
                return FeesRequest(result)
            else:
                return ErrorResult(Exception("Response code " + str(response.status_code)))
        else:
            return requestResult

    def renew_loan(self, renewId):
        checkResult = self.preCheck()
        if checkResult is not None:
            return checkResult
        data = {
            "selectAllIDS[]": renewId,
            "renewAllIDS[]": renewId,
            "renewSelectedIDS[]": renewId,
            "renewSelected": "this should not be empty, at least it's working :-)"
        }
        requestResult = self.authenticated_post_request("/MyResearch/CheckedOut", data)
        if not requestResult.is_error():
            response = requestResult.get_response()
            if response.status_code == 200:
                parsedLoans = checkRenewResult(response.text, renewId)
                return parsedLoans
            else:
                return ErrorResult("Response code " + str(response.status_code))
        else:
            return requestResult

    def lib_info(self):
        requestResult = self.get_request(
            "/AJAX/JSON?method=getOrganisationInfo&parent%5Bid%5D=Kirkes&params%5Baction%5D=consortium")
        if not requestResult.is_error():
            response = requestResult.get_response()
            try:
                jsonResponse = json.loads(response.text)
            except:
                jsonResponse = None
            if response.status_code == 200:
                if jsonResponse is None:
                    return ErrorResult(Exception("JSON Parsing failed"))
                else:
                    if jsonResponse['data'] is not None:
                        parsedItems = convertLibraryDetails(jsonResponse['data'], self)
                        return LibInfoRequest(parsedItems)
                    else:
                        return ErrorResult(Exception("Something unexpected happened"))
            else:
                return ErrorResult(Exception("Response code " + str(response.status_code)))
        else:
            return requestResult

    def get_library_full_details(self, library_id):
        requestResult = self.get_request(
            "/AJAX/JSON?method=getOrganisationInfo&parent%5Bid%5D=Kirkes&params%5Baction%5D=details&params%5Bid%5D=" + str(
                library_id) + "&params%5BfullDetails%5D=1&params%5BallServices%5D=0")
        if not requestResult.is_error():
            response = requestResult.get_response()
            try:
                jsonResponse = json.loads(response.text)
            except:
                jsonResponse = None
            if response.status_code == 200:
                if jsonResponse is None:
                    return ErrorResult(Exception("JSON Parsing failed"))
                else:
                    if jsonResponse['data'] is not None:
                        return ExtraLibInfoRequest(jsonResponse['data'])
                    else:
                        return ErrorResult(Exception("Something unexpected happened"))
            else:
                return ErrorResult(Exception("Response code " + str(response.status_code)))
        else:
            return requestResult

    def raw_resource_details(self, res_id):
        requestResult = self.post_request("/Record/" + res_id + "/AjaxTab", {'tab': 'details'})
        if not requestResult.is_error():
            response = requestResult.get_response()
            if response.status_code == 200:
                htmlCode = response.text
                parsedDetails = convertResourceDetails(htmlCode)
                if parsedDetails is None:
                    return ErrorResult('Details parsing failed')
                return DetailsRequest(parsedDetails)
            elif response.status_code == 404:
                return ErrorResult('Resource not found, check the ID and try again', 404)
            else:
                return ErrorResult(Exception("Response code " + str(response.status_code)))

    def resource_hash_key(self, res_id, check_auth=True):
        if check_auth:
            checkResult = self.preCheck()
            if checkResult is not None:
                return checkResult
        requestResult = self.authenticated_post_request("/Record/" + res_id + "/AjaxTab", {'tab': 'holdings'})
        if not requestResult.is_error():
            response = requestResult.get_response()
            if response.status_code == 200:
                htmlCode = response.text
                parsedDetails = extractHashKey(htmlCode)
                if parsedDetails is None:
                    return ErrorResult('Hash Key parsing failed')
                return HashKeyRequest(parsedDetails)
            elif response.status_code == 404:
                return ErrorResult('Resource not found, check the ID and try again', 404)
            else:
                return ErrorResult(Exception("Response code " + str(response.status_code)))

    def search(self, query, page="1"):
        requestResult = self.clean_get_request(
            "https://api.finna.fi/api/v1/search?lookfor=" + query + "&filter[]=~building%3A%220%2FKirkes%2F%22&lng=" + self.language + "&page=" + page + "&limit=5")
        if not requestResult.is_error():
            response = requestResult.get_response()
            try:
                jsonResponse = json.loads(response.text)
            except:
                jsonResponse = None
            if response.status_code == 200:
                if jsonResponse is None:
                    return ErrorResult(Exception("JSON Parsing failed"))
                else:
                    if jsonResponse.get('resultCount', None) is not None:
                        results = []
                        itemsCount = jsonResponse['resultCount']
                        if itemsCount > 0 and jsonResponse.get('records', None) is not None:
                            items = jsonResponse['records']
                            for item in items:
                                search_object = {
                                    'id': item.get('id', None),
                                    'title': item.get('title', None),
                                    'languages': item.get('languages', None),
                                    'authors': item.get('nonPresenterAuthors', None),
                                    'tags': None,
                                    'type': None,
                                    'isbn': None,
                                    'image': None,
                                    'publisher': None,
                                    'publication_date': None,
                                    'call_numbers': None
                                }
                                if search_object['id'] is not None:
                                    detailsFetch = self.raw_resource_details(search_object['id'])
                                    if not detailsFetch.is_error():
                                        details = detailsFetch.get_details()
                                        isbn = details.get('isbn', None)
                                        search_object[
                                            'image'] = "https://www.finna.fi/Cover/Show?recordid=" + search_object.get(
                                            'id', '') + "&isbn=" + details.get('isbn', '')
                                        search_object['isbn'] = isbn
                                        search_object['publisher'] = details.get('publisher', None)
                                        raw_date = details.get('main_date', None)
                                        if raw_date is not None:
                                            publication_date = datetime.datetime.strptime(raw_date,
                                                                                          "%Y-%m-%dT%H:%M:%SZ").strftime(
                                                "%Y/%m/%d %H:%M:%S")
                                            search_object['publication_date'] = publication_date
                                        callnum = details.get('callnumber-search')
                                        if callnum is not None:
                                            search_object['call_numbers'] = callnum.split("\n")

                                tags = []
                                for tag_array in item.get('subjects', []):
                                    for tag in tag_array:
                                        tags.append(tag)
                                search_object['tags'] = tags
                                formats = item.get('formats', None)
                                if formats is not None and len(formats) > 0:
                                    search_object['type'] = formats[len(formats) - 1]
                                results.append(search_object)

                        return SearchRequest(results, itemsCount)
                    else:
                        return ErrorResult(Exception("Something unexpected happened"))
            else:
                return ErrorResult(Exception("Response code " + str(response.status_code)))
        else:
            return requestResult

    def resource_details(self, res_id):
        requestResult = self.clean_get_request(
            "https://api.finna.fi/api/v1/record?id=" + res_id + "&lng=" + self.language)
        if not requestResult.is_error():
            response = requestResult.get_response()
            try:
                jsonResponse = json.loads(response.text)
            except:
                jsonResponse = None
            if response.status_code == 200:
                if jsonResponse is None:
                    return ErrorResult(Exception("JSON Parsing failed"))
                else:
                    if jsonResponse.get('resultCount', None) is not None:
                        itemsCount = jsonResponse['resultCount']
                        if itemsCount > 0:
                            item = jsonResponse['records'][0]
                            search_object = {
                                'id': item.get('id', None),
                                'title': item.get('title', None),
                                'languages': item.get('languages', None),
                                'authors': item.get('nonPresenterAuthors', None),
                                'tags': None,
                                'type': None,
                                'isbn': None,
                                'image': None,
                                'publisher': None,
                                'publication_date': None,
                                'call_numbers': None
                            }
                            if search_object['id'] is not None:
                                detailsFetch = self.raw_resource_details(search_object['id'])
                                if not detailsFetch.is_error():
                                    details = detailsFetch.get_details()
                                    isbn = details.get('isbn', None)
                                    search_object[
                                        'image'] = "https://www.finna.fi/Cover/Show?recordid=" + search_object.get('id',
                                                                                                                   '') + "&isbn=" + details.get(
                                        'isbn', '')
                                    search_object['isbn'] = isbn
                                    search_object['publisher'] = details.get('publisher', None)
                                    raw_date = details.get('main_date', None)
                                    if raw_date is not None:
                                        publication_date = datetime.datetime.strptime(raw_date,
                                                                                      "%Y-%m-%dT%H:%M:%SZ").strftime(
                                            "%Y/%m/%d %H:%M:%S")
                                        search_object['publication_date'] = publication_date
                                    callnum = details.get('callnumber-search')
                                    if callnum is not None:
                                        search_object['call_numbers'] = callnum.split("\n")

                            tags = []
                            for tag_array in item.get('subjects', []):
                                for tag in tag_array:
                                    tags.append(tag)
                            search_object['tags'] = tags
                            formats = item.get('formats', None)
                            if formats is not None and len(formats) > 0:
                                search_object['type'] = formats[len(formats) - 1]
                            return DetailsRequest(search_object)
                        return ErrorResult('Resource not found')
                    else:
                        return ErrorResult(Exception("Something unexpected happened"))
            else:
                return ErrorResult(Exception("Response code " + str(response.status_code)))
        else:
            return requestResult

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
                return ErrorResult("Response code " + str(response.status_code))
        else:
            return requestResult

    def holds(self):
        checkResult = self.preCheck()
        if checkResult is not None:
            return checkResult
        requestResult = self.authenticated_get_request("/MyResearch/Holds")
        if not requestResult.is_error():
            response = requestResult.get_response()
            if response.status_code == 200:
                parsedLoans = extractHolds(self.baseUrl, response.text)
                if parsedLoans is None:
                    return ErrorResult('Holds parsing failed')
                else:
                    return HoldsResult(parsedLoans)
            else:
                return ErrorResult("Response code " + str(response.status_code))
        else:
            return requestResult

    def hold(self, res_id, req_type, location_id):
        checkResult = self.preCheck()
        if checkResult is not None:
            return checkResult
        get_hashkey = self.resource_hash_key(res_id, False)
        if get_hashkey.is_error():
            return get_hashkey
        hashKey = get_hashkey.get_key()
        requestResult = self.authenticated_post_request(
            "/Record/" + res_id + "/Hold?id=" + res_id + "&level=title&hashKey=" + hashKey + "&layout=lightbox", {
                "gatheredDetails[requestGroupId]": req_type,
                "gatheredDetails[pickUpLocation]": location_id,
                "layout": "lightbox",
                "placeHold": ""
            }, None, False)
        if not requestResult.is_error():
            response = requestResult.get_response()
            if response.status_code == 302:
                return RequestResult(False)
            else:
                return ErrorResult("Unable to make a hold, " + str(response.status_code))
        else:
            return requestResult

    def cancel_hold(self, action_id):
        checkResult = self.preCheck()
        if checkResult is not None:
            return checkResult
        requestResult = self.authenticated_post_request(
            "/MyResearch/Holds", {
                "cancelSelected": "1",
                "confirm": "1",
                "cancelSelectedIDS[]": action_id
            }, None, False)
        if not requestResult.is_error():
            response = requestResult.get_response()
            if response.status_code == 200:
                if getHomeLibraryResult(response.text):
                    return RequestResult(False)
                else:
                    return ErrorResult(getError(response.text))
            else:
                return ErrorResult("Unable to cancel the hold, " + str(response.status_code))
        else:
            return requestResult

    def check_session_life(self):
        last_used = self.user_auth.lastusage.replace(tzinfo=None)
        diff = datetime.datetime.now() - last_used
        datetime.timedelta(0, 8, 562000)
        return diff.seconds >= 600
