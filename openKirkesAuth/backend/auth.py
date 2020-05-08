from django.contrib.auth.backends import BaseBackend
from openKirkesAuth.utils import hashToken
from openKirkesAuth.models import *


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
