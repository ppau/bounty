from functools import wraps
from tornado.escape import url_escape, json_decode
import logging

def require_rank(rank):

    def decorator(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            cookie = self.get_secure_cookie('bounty')
            cookie_data = json_decode(cookie)
            if cookie_data['rank'] != rank:
                error_msg = u'?error=' + url_escape('You do not have permission to do that')
                self.redirect('/login' + error_msg)
            return f(self, *args, **kwargs)

        return wrapper

    return decorator
