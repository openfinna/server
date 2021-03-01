#  Copyright (c) 2021 openKirkes, developed by Developer From Jokela
import json

from openKirkes.settings import FCM_SERVER_KEY, PUB_FCM_KEY
from .classes import *
from .web_client import FCMHttpClient


def checkForFCMError(response):
    if response.status_code != 200:
        jsonResponse = json.loads(response.text)
        errorBody = jsonResponse.get('error', None)
        if errorBody is not None:
            return ErrorResult(Exception(errorBody['message']))
        else:
            return ErrorResult(Exception("Unable to parse error code: " + str(response.status_code)))
    else:
        return None


class FCMClient:

    def __init__(self, public=False):
        token = FCM_SERVER_KEY
        if public:
            token = PUB_FCM_KEY
        self.http_client = FCMHttpClient(token)

    def sendPush(self, to, data, ttl="86400"):
        requestResult = self.http_client.post_json_request("fcm/send", {
            "to": to, "ttl": ttl, "data": data
        })
        if requestResult.is_error():
            return requestResult
        error_check = checkForFCMError(requestResult.get_response())
        if error_check is not None:
            return error_check
        return PushSendRequest(True)
