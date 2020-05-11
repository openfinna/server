# -*- coding: utf-8 -*-

#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

from __future__ import unicode_literals

import uuid

from django.db import models
from openKirkesAuth.encryption import AESCipher
from openKirkesAuth.classes import UserAuthentication
from hashlib import *
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from openKirkesAuth.utils import getUUIDFromToken


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

    def updateAuthentication(self, user_auth, encryption_key):
        uuidFromKey = getUUIDFromToken(encryption_key)
        self.session = AESCipher(user_auth.session, uuidFromKey.bytes).encrypt()
        self.username = AESCipher(user_auth.username, uuidFromKey.bytes).encrypt()
        self.password = AESCipher(user_auth.password, uuidFromKey.bytes).encrypt()
        self.modified = datetime.now()
        self.save()

    def updateUsageTime(self):
        self.modified = datetime.now()
        self.save()

    def verifyToken(self, user_provided_token):
        userProvidedTokenHash = sha512(user_provided_token).hexdigest()
        tokenDigest = self.token
        return userProvidedTokenHash == tokenDigest

    def getAuthenticationObject(self, user_provided_token):
        try:
            uuidFromKey = getUUIDFromToken(user_provided_token)
            session = AESCipher(self.session, uuidFromKey.bytes).decrypt()
            username = AESCipher(self.username, uuidFromKey.bytes).decrypt()
            password = AESCipher(self.password, uuidFromKey.bytes).decrypt()
            return UserAuthentication(session, username, password, self.last_accessed)
        except:
            return None

    @property
    def is_anonymous(self):
        return False
