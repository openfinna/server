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
    loans = getKirkesClientFromRequest(request).loans()
    if loans.is_error():
        return generateErrorResponse(loans)
    content = {
        'loans': loans.get_loans()
    }
    return generateResponse(content)


def getKirkesClientFromRequest(request):
    enc_key = request.user.encryption_key
    authObject = request.user.getAuthenticationObject(enc_key)
    return KirkesClient(authObject, request.user)


@api_view(['POST'])
@permission_classes([])
def login(request):
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    if username is None:
        return generateError('Username is missing!')
    if password is None:
        return generateError('Password is missing!')

    if request.user.is_anonymous and not request.user.is_authenticated:
        login_result = KirkesClient(None).login(username, password)
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
