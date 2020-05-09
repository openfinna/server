#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

from django.contrib.auth.backends import BaseBackend
from rest_framework import authentication

from openKirkesAuth.utils import hashToken
from openKirkesAuth.models import *
from rest_framework import exceptions
from rest_framework import authentication


class OpenKirkesBackend(BaseBackend):
    def authenticate(self, request, token=None):
        hashedToken = hashToken(token)
        try:
            return ApiUserToken.objects.get(token=hashedToken)
        except ApiUserToken.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return ApiUserToken.objects.get(pk=user_id)
        except ApiUserToken.DoesNotExist:
            return None


class OpenKirkesTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = authentication.get_authorization_header(request)
        if not token:
            return None

        try:
            tokenHash = hashToken(token)
            user = ApiUserToken.objects.get(token=tokenHash)
        except ApiUserToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        return user, None
