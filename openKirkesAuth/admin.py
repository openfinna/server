# -*- coding: utf-8 -*-

#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

from __future__ import unicode_literals

from django.contrib import admin
from openKirkesAuth.models import ApiUserToken
# Register your models here.
@admin.register(ApiUserToken)
class SecurityAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'token', 'created', 'last_accessed']