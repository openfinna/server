#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

import hashlib


def hashToken(token):
    return hashlib.sha512(token)