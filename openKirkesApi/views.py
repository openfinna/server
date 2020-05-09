# -*- coding: utf-8 -*-

#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import *
from openKirkesConnector.web_client import *


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def example_view(request, format=None):
    content = {
        'status': 'request was permitted'
    }
    return Response(content)


@api_view(['POST'])
@permission_classes([])
def login(request):
    content = {
        'status': 'request was permitted'
    }
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    if username is None:
        return Response(generateError('Username is missing!'))
    if password is None:
        return Response(generateError('Password is missing!'))

    if request.user.is_anonymous and not request.user.is_authenticated:
        return Response(content)
    else:
        return Response(generateError("You're already logged in"))


def generateError(cause):
    base = baseResponse()
    base.update({'cause': cause})
    return base


def baseResponse():
    return {
        'status': False
    }
