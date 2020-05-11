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
    content = {
        'status': 'request was permitted'
    }
    return Response(content)


@api_view(['POST'])
@permission_classes([])
def login(request):
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    if username is None:
        return Response(generateError('Username is missing!'))
    if password is None:
        return Response(generateError('Password is missing!'))

    if request.user.is_anonymous and not request.user.is_authenticated:
        login_result = KirkesClient(None).login(username, password)
        if login_result.is_error():
            return Response(generateError(str(login_result.get_exception())))
        else:
            token = new_token(login_result.get_session(), username, password)
            return Response(generateResponse({'token': token}))
    else:
        return Response(generateError("You're already logged in"))


def generateError(cause):
    base = baseResponse()
    base.update({'cause': cause})
    return base


def generateResponse(data):
    base = baseResponse(True)
    base.update(data)
    return base


def baseResponse(status=False):
    return {
        'status': status
    }
