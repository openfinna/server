# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from openKirkesAuth.encryption import AESCipher
from openKirkesAuth.classes import UserAuthentication
from hashlib import *
from datetime import datetime


class ApiUserToken(models.Model):
    readonly_fields = ('created', 'last_accessed')
    user_id = models.UUIDField(primary_key=True)
    # This is the authentication Hash (sha512)
    token = models.CharField(max_length=128)
    session = models.TextField(editable=False)
    username = models.TextField(editable=False)
    password = models.TextField(editable=False)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    last_accessed = models.DateTimeField(editable=False, auto_now=True)

    def updateUsageTime(self):
        self.modified = datetime.now()
        self.save()

    def verifyToken(self, user_provided_token):
        userProvidedTokenHash = sha512(user_provided_token).hexdigest()
        tokenDigest = self.token
        return userProvidedTokenHash == tokenDigest

    def getAuthenticationObject(self, user_provided_token):
        try:
            session = AESCipher(self.session, user_provided_token).decrypt()
            username = AESCipher(self.username, user_provided_token).decrypt()
            password = AESCipher(self.password, user_provided_token).decrypt()
            return UserAuthentication(session, username, password, self.last_accessed)
        except:
            return None
