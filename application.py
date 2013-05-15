# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import tornado.options
import tornado.httpserver
import logging
import datetime
import os

#from tornado import gen
from passlib.hash import pbkdf2_sha256

from secret import cookie_secret

#Admin views
from admin import AdminHandler
from admin import AdminFundraiserHandler

from base import BaseHandler

#Fundraiser views
from fundraiser import FundraiserIndexHandler
from fundraiser import FundraiserCreateHandler
from fundraiser import FundraiserEditHandler
from fundraiser import FundraiserDeleteHandler
from fundraiser import FundraiserDetailHandler
from fundraiser import FundraiserBackHandler
#from fundraiser import FundraiserBackSuccessHandler
from fundraiser import FundraiserDetailJSONHandler


class IndexHandler(BaseHandler):

    def get(self):
        recent = self.db.fundraisers.find().sort('-launched').limit(15)
        self.render('index.html', recent=recent)


class LoginHandler(BaseHandler):

    def get(self):
        self.render('login.html')

    @tornado.web.asynchronous
    #@gen.coroutine
    def post(self):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        if username is not None and password is not None:
            #user = yield self.get_authenticated_user()
            logging_in_user = self.users_db.find_one({'username': username})
            if logging_in_user:
                if pbkdf2_sha256.verify(password, logging_in_user['password']):
                    self.set_secure_cookie('bounty',
                                           tornado.escape.json_encode(username),
                                           httponly=True)
                    self.redirect('/')
                    return
        error_msg = u'?error=' + tornado.escape.url_escape('Login incorrect.')
        self.redirect('/login' + error_msg)


class LogoutHandler(BaseHandler):

    def get(self):
        self.clear_cookie('bounty')
        self.redirect("/")


class CreateUserHandler(BaseHandler):

    def get(self):
        error = self.get_argument('error', None)
        self.render('create_user.html',
                    error=error)

    def post(self):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        password = pbkdf2_sha256.encrypt(password)
        if username is not None and password is not None:
            if self.users_db.find_one({'username': username}):
                error_msg = u"?error=" + tornado.escape.url_escape("Login name already taken")
                self.redirect('/create' + error_msg)
            user = {'username': username,
                    'password': password,
                    'created_at': datetime.datetime.utcnow()}
            self.users_db.save(user)
            self.set_secure_cookie('bounty',
                                   tornado.escape.json_encode(username),
                                   httponly=True)
            self.redirect("/")


class Application(tornado.web.Application):

    def __init__(self):

        handlers = [
                    (r'/', IndexHandler),
                    (r'/login', LoginHandler),
                    (r'/logout', LogoutHandler),
                    (r'/create', CreateUserHandler),
                    (r'/admin', AdminHandler),
                    (r'/admin/fundraiser/([^/]+)', AdminFundraiserHandler),
                    (r'/fundraiser', FundraiserIndexHandler),
                    (r'/fundraiser/create', FundraiserCreateHandler),
                    (r'/fundraiser/([^/]+)/edit', FundraiserEditHandler),
                    (r'/fundraiser/([^/]+)/delete', FundraiserDeleteHandler),
                    (r'/fundraiser/([^/]+)', FundraiserDetailHandler),
                    (r'/fundraiser/back/([^/]+)', FundraiserBackHandler),
                    #(r'/fundraiser/([^/]+)/success', FundraiserBackSuccessHandler),
                    (r'/fundraiser/([^/]+)/json', FundraiserDetailJSONHandler),
                   ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            debug=True,
            xsrf_cookies=True,
            #generate secret cookie: print base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
            cookie_secret=cookie_secret,
            login_url='/login',
            )

        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':

    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    logging.info('Starting up')
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
