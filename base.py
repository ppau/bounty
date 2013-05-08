import pymongo
from tornado.web import RequestHandler


class BaseHandler(RequestHandler):

    @property
    def db(self):
        conn = pymongo.Connection()
        db = conn.bounty
        return db
