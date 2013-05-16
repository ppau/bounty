from functools import wraps
from tornado.escape import url_escape, json_decode
import logging


def require_staff(f):

    #logging.info(self)

    #def decorator(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            cookie = self.get_secure_cookie('bounty')
            cookie_data = json_decode(cookie)
            logging.info(cookie_data['rank'])
            if (cookie_data['rank'] in ('staff', 'admin')) is False:
                error_msg = u'?error=' + url_escape('You do not have permission to do that')
                self.redirect('/login' + error_msg)
            return f(self, *args, **kwargs)

        return wrapper

    #return decorator


def require_admin(f):

    #def decorator(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            cookie = self.get_secure_cookie('bounty')
            cookie_data = json_decode(cookie)
            if cookie_data['rank'] != 'admin':
                error_msg = u'?error=' + url_escape('You do not have permission to do that')
                self.redirect('/login' + error_msg)
            return f(self, *args, **kwargs)

        return wrapper

    #return decorator
