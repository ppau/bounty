# -*- coding: utf-8 -*-
from tornado.web import HTTPError
#from tornado.web import asynchronous
#import tornado.ioloop

#from tornado.escape import json_decode
import datetime
import json
import unicodedata
import re
import logging

from base import BaseHandler
from celery_mixin import CeleryHandler

#from chip.tasks import fundraiser_countdown
#from chip.celery import celery


class FundraiserBase(BaseHandler):

    @property
    def fundraisers(self):
        fundraisers = self.db.fundraisers
        return fundraisers


class FundraiserIndexHandler(FundraiserBase):

    def get(self):
        recent = self.fundraisers.find().sort('-launched').limit(30)
        self.render('index.html', recent=recent)


class FundraiserCreateHandler(FundraiserBase, CeleryHandler):

    def get(self):
        self.render('fundraiser/create.html',
                    fundraiser=None,
                    error=None)

    #@asynchronous
    def post(self):
        title = self.get_argument('title', None)
        slug = self.get_argument('slug', None)
        goal = self.get_argument('goal', None)
        deadline = self.get_argument('deadline', None)
        description = self.get_argument('description', None)

        slug = unicodedata.normalize('NFKD', slug).encode('ascii', 'ignore')
        slug = re.sub(r'[^\w]+', ' ', slug)
        slug = slug.replace(' ', '_').lower().strip()

        #deadline = datetime.datetime.strptime(deadline, '%a, %d %B %Y %H:%M:%S %Z')
        ## TESTING ONLY
        deadline = datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
        ##

        fundraiser = {'title': title, 'slug': slug,
                      'goal': goal, 'deadline': deadline,
                      'description': description}

        if None in fundraiser.values():
            self.render('fundraiser/create.html', fundraiser=fundraiser,
                        error=1)

        if self.fundraisers.find_one({'slug': fundraiser['slug']}):
            self.render('fundraiser/create.html', fundraiser=fundraiser,
                        error=2)

        if self.fundraisers.find_one({'title': fundraiser['title']}):
            self.render('fundraiser/create.html', fundraiser=fundraiser,
                        error=3)

        fundraiser['launched'] = datetime.datetime.utcnow()
        fundraiser['current_funding'] = 0
        fundraiser['backers_count'] = 0

        self.fundraisers.save(fundraiser)
        saved_fundraiser = self.fundraisers.find_one({'slug': fundraiser['slug']})
        self.fundraiser_deadline(saved_fundraiser['_id'], deadline)
        #fundraiser_countdown(saved_fundraiser['_id'], deadline)
        #tornado.ioloop.IOLoop().instance().add_callback(fundraiser_countdown(saved_fundraiser['_id'], deadline))
        #self.add_task(fundraiser_countdown, saved_fundraiser['_id'], deadline, callback=self._on_result)
        self.redirect('{}'.format(slug))


class FundraiserEditHandler(FundraiserBase):

    def get(self, fundraiser_slug):
        fundraiser = self.fundraisers.find_one({'slug': fundraiser_slug})
        if fundraiser:
            self.render('fundraiser/detail.html',
                        fundraiser=fundraiser)
        else:
            raise HTTPError(404)


class FundraiserDeleteHandler(FundraiserBase):

    def get(self, fundraiser_slug):
        fundraiser = self.fundraisers.find_one({'slug': fundraiser_slug})
        if fundraiser:
            self.fundraisers.remove(fundraiser)
            self.redirect('/admin')
        else:
            raise HTTPError(404)


class FundraiserDetailHandler(FundraiserBase):

    def get(self, fundraiser_slug):
        logging.info('Detail')
        fundraiser = self.fundraisers.find_one({'slug': fundraiser_slug})
        if fundraiser:
            self.render('fundraiser/detail.html',
                        fundraiser=fundraiser)
        else:
            raise HTTPError(404)


class FundraiserBackHandler(FundraiserBase):

    def get(self, fundraiser_slug):
        fundraiser = self.fundraisers.find_one({'slug': fundraiser_slug})
        if fundraiser:
            self.render('fundraiser/back.html',
                        fundraiser=fundraiser)
        else:
            raise HTTPError(404)

    def post(self, fundraiser_slug):

        #self.json_args.get("foo")
        #self.write(self.json_args)
        fundraiser = self.fundraisers.find_one({'slug': fundraiser_slug})
        if fundraiser:
            fundraiser_id = fundraiser['_id']
            card_token = self.get_argument('card_token', None)
            ip_address = self.get_argument('ip_address', None)
            amount = self.get_argument('amount', None)
            fundraiser['current_funding'] += int(amount)
            fundraiser['backers_count'] += 1
            self.fundraisers.save(fundraiser)
            #self.set_header('Content-Type', 'application/json')
            #self.write(json.dumps({'card': card_token, 'ip': ip_address, 'amount': amount}))
            self.redirect('/fundraiser/{}/success'.format(fundraiser_slug))
        else:
            raise HTTPError(404)


class FundraiserBackSuccessHandler(FundraiserBase):

    def get(self, fundraiser_slug):
        fundraiser = self.fundraisers.find_one({'slug': fundraiser_slug})
        if fundraiser:
            self.render('fundraiser/detail.html',
                        fundraiser=fundraiser,
                        success=True)
        else:
            raise HTTPError(404)


class FundraiserDetailJSONHandler(FundraiserBase):

    def get(self, fundraiser_slug):
        fundraiser = self.fundraisers.find_one({'slug': fundraiser_slug})
        if fundraiser:
            datetime_handler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(fundraiser, default=datetime_handler))
        else:
            raise HTTPError(404)


# class AsyncHandler(FundraiserBase):

#     @asynchronous
#     def get(self, _id, deadline):

#         tcelery.setup_nonblocking_producer()

#         fundraiser_countdown.apply_async(args=[_id, deadline],
#             callback=self.on_result)
#         self.redirect('{}'.format(slug))
#         #tasks.echo.apply_async(args=['Hello world!'], callback=self.on_result)

#     def on_result(self, response):
#         self.write(str(response.result))
#         self.finish()
