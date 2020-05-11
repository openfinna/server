# -*- coding: utf-8 -*-

#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

from __future__ import unicode_literals

from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import *
from openKirkesAuth.backend.auth import new_token
from openKirkesConnector.web_client import *


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def loans(request):
    lang = request.query_params.get('lang', "en-gb")
    loans = getKirkesClientFromRequest(request, lang).loans()
    if loans.is_error():
        return generateErrorResponse(loans, lang)
    content = {
        'loans': loans.get_loans()
    }
    return generateResponse(content)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def holds(request):
    lang = request.query_params.get('lang', "en-gb")
    holds = getKirkesClientFromRequest(request, lang).holds()
    if holds.is_error():
        return generateErrorResponse(loans)
    content = {
        'holds': holds.get_holds()
    }
    return generateResponse(content)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pickupLocations(request):
    lang = request.query_params.get('lang', "en-gb")
    id = request.query_params.get("id", None)
    if id is None:
        return generateError(Exception("Query parameter 'id' is missing"))
    locations = getKirkesClientFromRequest(request, lang).pickupLocations(id)
    if locations.is_error():
        return generateErrorResponse(locations)
    content = {
        'pickup_locations': locations.get_locations()
    }
    return generateResponse(content)


def getKirkesClientFromRequest(request, language="en-gb"):
    enc_key = request.user.encryption_key
    authObject = request.user.getAuthenticationObject(enc_key)
    return KirkesClient(authObject, language, request.user)


@api_view(['POST'])
@permission_classes([])
def login(request):
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    language = request.data.get('lang', "fi-fi")
    if username is None:
        return generateError('Username is missing!')
    if password is None:
        return generateError('Password is missing!')

    if request.user.is_anonymous and not request.user.is_authenticated:
        login_result = KirkesClient(None, language).login(username, password)
        if login_result.is_error():
            return generateErrorResponse(login_result)
        else:
            token = new_token(login_result.get_session(), username, password)
            return generateResponse({'token': token})
    else:
        return generateError("You're already logged in")


def generateErrorResponse(error_result):
    return Response(generateError(str(error_result.get_exception())))


def generateError(cause):
    base = baseResponse()
    base.update({'cause': cause})
    return Response(base)


def generateResponse(data):
    base = baseResponse(True)
    base.update(data)
    return Response(base)


def baseResponse(status=False):
    return {
        'status': status
    }
