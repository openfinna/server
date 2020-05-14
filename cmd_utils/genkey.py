#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

# This file generates a Secret Key for the Settings

from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())