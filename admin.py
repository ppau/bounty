# -*- coding: utf-8 -*-
from base import BaseHandler
from tornado.web import HTTPError
from tornado.web import authenticated


class AdminBase(BaseHandler):

    @property
    def fundraisers(self):
        fundraisers = self.db.fundraisers
        return fundraisers

    @property
    def backers(self):
        backers = self.db.backers
        return backers


class AdminHandler(AdminBase):

    @authenticated
    def get(self):
        recent = self.fundraisers.find().sort('-launched').limit(30)
        self.render('admin/admin.html', recent=recent)


class AdminFundraiserHandler(AdminBase):

    @authenticated
    def get(self, fundraiser_slug):
        fundraiser = self.fundraisers.find_one({'slug': fundraiser_slug})
        fundraiser_backers = self.backers.find({'fundraiser': fundraiser['_id']})
        if fundraiser:
            self.render('admin/fundraiser.html',
                        fundraiser=fundraiser,
                        fundraiser_backers=fundraiser_backers)
        else:
            raise HTTPError(404)
