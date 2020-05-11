#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

from django.contrib.auth.backends import BaseBackend
import uuid
from openKirkesAuth.utils import hashToken
from openKirkesAuth.models import *
from rest_framework import exceptions
from rest_framework import authentication


def new_token(session, username, password):
    # Generating Random Token
    randomToken = uuid.uuid4()
    # Encrypting values
    encryptedSession = AESCipher(session, randomToken.bytes).encrypt()
    encryptedUsername = AESCipher(username, randomToken.bytes).encrypt()
    encryptedPassword = AESCipher(password, randomToken.bytes).encrypt()
    # Saving values
    newUserToken = ApiUserToken()
    newUserToken.token = hashToken(str(randomToken.hex))
    newUserToken.username = encryptedUsername
    newUserToken.password = encryptedPassword
    newUserToken.session = encryptedSession
    newUserToken.save()
    return str(randomToken)


class OpenKirkesBackend(BaseBackend):
    def authenticate(self, request, token=None):
        hashedToken = hashToken(token)
        if hashedToken is None:
            return None
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
            if tokenHash is None:
                raise exceptions.AuthenticationFailed('Invalid token')
            user = ApiUserToken.objects.get(token=tokenHash)
            user.encryption_key = token
        except ApiUserToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        return user, None
