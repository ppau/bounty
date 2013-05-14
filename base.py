import pymongo
from tornado.web import RequestHandler
import tornado.escape


class BaseHandler(RequestHandler):

    @property
    def db(self):
        conn = pymongo.Connection()
        db = conn.bounty
        return db

    @property
    def users_db(self):
        return self.db.users

    def get_current_user(self):
        user_json = self.get_secure_cookie('bounty')
        if not user_json:
            return None
        return tornado.escape.json_decode(user_json)
