# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models
from openKirkesAuth.encryption import AESCipher
from openKirkesAuth.classes import UserAuthentication
from hashlib import *
from datetime import datetime
from django.contrib.auth.models import AbstractUser


class ApiUserToken(AbstractUser):
    readonly_fields = ('created', 'last_accessed')
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # This is the authentication Hash (sha512)
    token = models.CharField(max_length=128, editable=False)
    session = models.TextField(editable=False)
    username = models.TextField(editable=False)
    basic_name = models.TextField(editable=False, unique=True, null=True)
    password = models.TextField(editable=False)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    last_accessed = models.DateTimeField(editable=False, auto_now=True)
    REQUIRED_FIELDS = 'username',
    USERNAME_FIELD = 'basic_name'

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

    @property
    def is_anonymous(self):
        return False
