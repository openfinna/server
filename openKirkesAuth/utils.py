#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

import hashlib
import uuid



def hashToken(token):
    try:
        if type(token) is bytes:
            token = token.decode("utf-8")
        bytesToken = uuid.UUID(token)
        return hashlib.sha512(bytesToken.hex.encode('utf-8')).digest().hex()
    except:
        return None

def getUUIDFromToken(token):
    try:
        if type(token) is bytes:
            token = token.decode("utf-8")
        bytesToken = uuid.UUID(token)
        return bytesToken
    except:
        return None