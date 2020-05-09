#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

class UserAuthentication:

    def __init__(self, session, username, password, last_usage):
        self.session = session
        self.username = username
        self.password = password
        self.lastusage = last_usage
