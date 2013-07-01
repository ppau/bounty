# -*- coding: utf-8 -*-
from tornado.web import HTTPError
#from tornado.web import asynchronous
from tornado.web import authenticated
#import tornado.ioloop
from bson.objectid import ObjectId

#from tornado.escape import json_decode
import datetime
import json
import unicodedata
import re
import os
import logging

from base import BaseHandler
from celery_mixin import CeleryHandler
from auth import require_staff

from config import FUNDRAISERS_PER_PAGE

#from chip.tasks import fundraiser_countdown
#from chip.celery import celery


class FundraiserBase(BaseHandler):

    @property
    def fundraisers(self):
        fundraisers = self.db.fundraisers
        return fundraisers

    @property
    def backers(self):
        backers = self.db.backers
        return backers


class FundraiserIndexHandler(FundraiserBase):

    """
        At this stage this is an exact duplicate of the IndexHandler.
        Maybe change them, so front page has less per page
        and has other info too or remove this one?
    """

    def get(self):
        page = self.get_argument('page', None)
        if page:
            page = int(page)
        else:
            page = 1
        fundraisers_all = self.fundraisers.find({'status': 'Live'})
        if page > 1:
            recent = fundraisers_all.sort([('launched', -1)]) \
                .skip(FUNDRAISERS_PER_PAGE*(int(page)-1)).limit(FUNDRAISERS_PER_PAGE)
        else:
            recent = fundraisers_all.sort([('launched', -1)]).limit(FUNDRAISERS_PER_PAGE)
        total = fundraisers_all.count()
        #total = int(ceil(float(total)/float(FUNDRAISERS_PER_PAGE)))
        self.render('fundraiser/list.html', recent=recent,
                    total=total, page=page,
                    page_size=FUNDRAISERS_PER_PAGE)


# class FundraiserPaginationHandler(FundraiserBase):

#     def get(self, page):
#         fundraisers_all = self.fundraisers.find()
#         paginated = fundraisers_all.sort('-launched'). \
#             skip(FUNDRAISERS_PER_PAGE*(int(page)-1)).limit(FUNDRAISERS_PER_PAGE)
#         total = fundraisers_all.count()
#         self.render('index.html', recent=paginated,
#                     total=total)


class FundraiserCreateHandler(FundraiserBase, CeleryHandler):

    @authenticated
    @require_staff
    def get(self):
        template_list = []
        for i in os.listdir(os.path.join(os.path.dirname(__file__), 'templates/fundraiser/user_templates'),):
            if os.path.splitext(i)[1].lower() == '.html':
                template_list.append(i)

        self.render('fundraiser/create.html',
                    fundraiser=None,
                    template_list=template_list,
                    error=None)

    #@asynchronous  # do I need async on this?
    @authenticated
    @require_staff
    def post(self):
        title = self.get_argument('title', None)
        slug = self.get_argument('slug', None)
        goal = self.get_argument('goal', None)
        template = self.get_argument('template', None)
        deadline = self.get_argument('deadline', None)
        description = self.get_argument('description', None)
        status = self.get_argument('statusRadios', None)

        slug = unicodedata.normalize('NFKD', slug).encode('ascii', 'ignore')
        slug = re.sub(r'[^\w]+', ' ', slug)
        slug = slug.replace(' ', '_').lower().strip()

        #deadline = datetime.datetime.strptime(deadline, '%a, %d %B %Y %H:%M:%S %Z')
        ## TESTING ONLY
        deadline = datetime.datetime.utcnow() + datetime.timedelta(minutes=2)
        ##
        template_list = []
        for i in os.listdir(os.path.join(os.path.dirname(__file__), 'templates/fundraiser/user_templates'),):
            if os.path.splitext(i)[1].lower() == '.html':
                template_list.append(i)

        fundraiser = {'title': title, 'slug': slug,
                      'goal': goal, 'deadline': deadline,
                      'description': description,
                      'status': status, 'template': template}

        if None in fundraiser.values():
            self.render('fundraiser/create.html', fundraiser=fundraiser,
                        template_list=template_list, error=1)

        if self.fundraisers.find_one({'slug': fundraiser['slug']}):
            self.render('fundraiser/create.html', fundraiser=fundraiser,
                        template_list=template_list, error=2)

        if self.fundraisers.find_one({'title': fundraiser['title']}):
            self.render('fundraiser/create.html', fundraiser=fundraiser,
                        template_list=template_list, error=3)

        fundraiser['launched'] = datetime.datetime.utcnow()
        #fundraiser['status'] = 'Live'
        fundraiser['current_funding'] = 0.0
        fundraiser['backers_count'] = 0
        # generate the primary key manually
        # the below method of querying it from the db sometimes failed as it hadn't been
        # saved before the query
        fundraiser['_id'] = ObjectId.from_datetime(fundraiser['launched'])

        self.fundraisers.save(fundraiser)
        #saved_fundraiser = self.fundraisers.find_one({'slug': fundraiser['slug']})
        if status == 'Live' and deadline:
            self.fundraiser_deadline(fundraiser['_id'], deadline)
        #fundraiser_countdown(saved_fundraiser['_id'], deadline)
        #tornado.ioloop.IOLoop().instance().add_callback(fundraiser_countdown(saved_fundraiser['_id'], deadline))
        #self.add_task(fundraiser_countdown, saved_fundraiser['_id'], deadline, callback=self._on_result)
        self.redirect('{}'.format(slug))


class FundraiserEditHandler(FundraiserBase):

    @authenticated
    @require_staff
    def get(self, fundraiser_slug):
        fundraiser = self.fundraisers.find_one({'slug': fundraiser_slug})
        if fundraiser:
            self.render('fundraiser/detail.html',
                        fundraiser=fundraiser)
        else:
            raise HTTPError(404)

    @authenticated
    @require_staff
    def post(self):
        _id = self.get_argument('_id', None)
        title = self.get_argument('title', None)
        slug = self.get_argument('slug', None)
        goal = self.get_argument('goal', None)
        #Should people be allowed to change the deadline?
        #deadline = self.get_argument('deadline', None)
        description = self.get_argument('description', None)
        status = self.get_argument('status', None)

        slug = unicodedata.normalize('NFKD', slug).encode('ascii', 'ignore')
        slug = re.sub(r'[^\w]+', ' ', slug)
        slug = slug.replace(' ', '_').lower().strip()

        fundraiser = self.fundraisers.find_one({'_id': _id})
        if fundraiser:
            fundraiser = {'_id': _id, 'title': title, 'slug': slug,
                          'goal': goal, 'status': status,
                          'description': description}

            self.fundraisers.save(fundraiser)
            self.redirect('{}'.format(slug))
        else:
            raise HTTPError(404)


class FundraiserDeleteHandler(FundraiserBase):

    #when we delete, maybe clean up the backers table too?
    @authenticated
    @require_staff
    def get(self, fundraiser_slug):
        fundraiser = self.fundraisers.find_one({'slug': fundraiser_slug})
        if fundraiser:
            self.fundraisers.remove(fundraiser)
            self.redirect('/admin')
        else:
            raise HTTPError(404)


class FundraiserDetailHandler(FundraiserBase, CeleryHandler):

    def get(self, fundraiser_slug):
        fundraiser = self.fundraisers.find_one({'slug': fundraiser_slug})
        message = self.get_argument('message', None)
        fundraiser_backers = self.backers.find({'fundraiser': fundraiser['_id']})
        if fundraiser:
            if 'template' in fundraiser:
                self.render('fundraiser/user_templates/{}'.format(fundraiser['template']),
                            fundraiser=fundraiser,
                            fundraiser_backers=fundraiser_backers,
                            message=message)
            else:
                self.render('fundraiser/detail.html',
                            fundraiser=fundraiser,
                            fundraiser_backers=fundraiser_backers,
                            message=message)
        else:
            raise HTTPError(404)

    def post(self, fundraiser_slug):
        fundraiser = self.fundraisers.find_one({'slug': fundraiser_slug})
        if fundraiser:
            fundraiser_id = fundraiser['_id']
            card_token = self.get_argument('card_token', None)
            ip_address = self.get_argument('ip_address', None)
            #Some kind of profanity check or something?
            first_name = self.get_argument('firstname', None)
            last_name = self.get_argument('lastname', None)
            name = '{} {}'.format(first_name, last_name[0])
            email = self.get_argument('email', None)
            state = self.get_argument('address-state', None)
            city = self.get_argument('address-city', None)
            amount = self.get_argument('amount', None)
            fundraiser['current_funding'] += float(amount)
            fundraiser['backers_count'] += 1
            self.fundraisers.save(fundraiser)
            backer = {'fundraiser': fundraiser_id,
                      'user': name,
                      'email': email,
                      'state': state,
                      'city': city,
                      'card_token': card_token,
                      'ip_address': ip_address,
                      'amount': float(amount),
                      'created_at': datetime.datetime.utcnow(),
                      'status': 'Pending',
                      '_id': ObjectId.from_datetime(datetime.datetime.utcnow())}
            self.backers.save(backer)
            description = 'Bounty - {}'.format(fundraiser['title'])
            self.fundraiser_charge(backer['_id'], description)
            #do charge here
            self.redirect(u'/fundraiser/{}?message=success'.format(fundraiser_slug))
        else:
            raise HTTPError(404)


class FundraiserBackHandler(FundraiserBase):

    @authenticated
    def get(self, fundraiser_slug):
        fundraiser = self.fundraisers.find_one({'slug': fundraiser_slug})
        if fundraiser:
            self.render('fundraiser/back.html',
                        fundraiser=fundraiser)
        else:
            raise HTTPError(404)

    @authenticated
    def post(self, fundraiser_slug):

        fundraiser = self.fundraisers.find_one({'slug': fundraiser_slug})
        if fundraiser:
            fundraiser_id = fundraiser['_id']
            card_token = self.get_argument('card_token', None)
            ip_address = self.get_argument('ip_address', None)
            #user id as well
            amount = self.get_argument('amount', None)
            fundraiser['current_funding'] += float(amount)
            fundraiser['backers_count'] += 1
            self.fundraisers.save(fundraiser)
            backer = {'fundraiser': fundraiser_id,
                      'user': self.current_user['username'],
                      'card_token': card_token,
                      'ip_address': ip_address,
                      'amount': float(amount),
                      'created_at': datetime.datetime.utcnow(),
                      'status': 'Pending'}
            self.backers.save(backer)
            self.redirect(u'/fundraiser/{}?message=success'.format(fundraiser_slug))
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
