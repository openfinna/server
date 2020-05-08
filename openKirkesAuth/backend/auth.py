from django.contrib.auth.backends import BaseBackend


class OpenKirkesBackend(BaseBackend):
    def authenticate(self, request, token=None):
        ...
