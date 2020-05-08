import hashlib


def hashToken(token):
    return hashlib.sha512(token)