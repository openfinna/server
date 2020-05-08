# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class ApiUserToken:
    readonly_fields = ('created', 'last_accessed')
    user_id = models.UUIDField()