# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import tornado.options
import tornado.httpserver
import logging
import datetime
import os
import re

#from tornado import gen
#from math import ceil
from passlib.hash import pbkdf2_sha256

from secret import cookie_secret
from config import FUNDRAISERS_PER_PAGE

#Admin views
from admin import AdminHandler
from admin import AdminFundraiserHandler
from admin import AdminUserEditHander
from admin import AdminBackerDeleteHandler

from base import BaseHandler

#Fundraiser views
from fundraiser import FundraiserIndexHandler
from fundraiser import PetitionIndexHandler
from fundraiser import FundraiserCreateHandler
from fundraiser import FundraiserEditHandler
from fundraiser import FundraiserDeleteHandler
from fundraiser import FundraiserDetailHandler
from fundraiser import FundraiserBackHandler
from fundraiser import FundraiserDetailJSONHandler

import uimodules.pagination


class IndexHandler(BaseHandler):

    def get(self):
        page = self.get_argument('page', None)
        if page:
            page = int(page)
        else:
            page = 1
        fundraisers_all = self.db.fundraisers.find({'status': 'Live'})
        if page > 1:
            recent = fundraisers_all.sort([('launched', -1)]) \
                .skip(FUNDRAISERS_PER_PAGE*(int(page)-1)).limit(FUNDRAISERS_PER_PAGE)
        else:
            recent = fundraisers_all.sort([('launched', -1)]).limit(FUNDRAISERS_PER_PAGE)
        total = fundraisers_all.count()
        #total = int(ceil(float(total)/float(FUNDRAISERS_PER_PAGE)))
        self.render('index.html', recent=recent,
                    total=total, page=page,
                    page_size=FUNDRAISERS_PER_PAGE)


class LoginHandler(BaseHandler):

    def get(self):
        error = self.get_argument('error', None)
        self.render('login.html',
                    error=error)

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
                                           tornado.escape.json_encode({'username': username,
                                                                       'rank': logging_in_user['rank']}),
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
        username = re.sub('[^a-zA-Z0-9_\.]', '', username)
        password = self.get_argument('password', None)
        #validate email?
        email = self.get_argument('email', None)
        password = pbkdf2_sha256.encrypt(password)
        if username is not None and password is not None and email is not None:
            if self.users_db.find_one({'username': username}):
                error_msg = u"?error=" + tornado.escape.url_escape("Login name already exists")
                self.redirect('/create' + error_msg)
            user = {'username': username,
                    'password': password,
                    'email': email,
                    'created_at': datetime.datetime.utcnow(),
                    'rank': 'user'}
            self.users_db.save(user)
            self.set_secure_cookie('bounty',
                                   tornado.escape.json_encode({'username': username,
                                                               'rank': user['rank']}),
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
                    (r'/admin/user/([^/]+)', AdminUserEditHander),
                    (r'/admin/backers/([^/]+)/delete', AdminBackerDeleteHandler),
                    (r'/admin/fundraiser/([^/]+)', AdminFundraiserHandler),
                    (r'/fundraiser', FundraiserIndexHandler),
                    (r'/petition', PetitionIndexHandler),
                    (r'/fundraiser/create', FundraiserCreateHandler),
                    (r'/fundraiser/([^/]+)/edit', FundraiserEditHandler),
                    (r'/fundraiser/([^/]+)/delete', FundraiserDeleteHandler),
                    (r'/fundraiser/([^/]+)', FundraiserDetailHandler),
                    (r'/fundraiser/back/([^/]+)', FundraiserBackHandler),
                    (r'/fundraiser/([^/]+)/json', FundraiserDetailJSONHandler),
                   ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            debug=True,
            xsrf_cookies=True,
            #generate cookie secret: print base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
            cookie_secret=cookie_secret,
            login_url='/login',
            ui_modules=uimodules.pagination,
            )

        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':

    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    logging.info('Starting up')
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
