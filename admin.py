# -*- coding: utf-8 -*-
from base import BaseHandler
from tornado.web import HTTPError
from tornado.web import authenticated

from auth import require_staff
#from auth import require_admin


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
    @require_staff
    def get(self):
        recent = self.fundraisers.find().sort('-launched').limit(30)
        self.render('admin/admin.html', recent=recent)


class AdminFundraiserHandler(AdminBase):

    @authenticated
    @require_staff
    def get(self, fundraiser_slug):
        fundraiser = self.fundraisers.find_one({'slug': fundraiser_slug})
        fundraiser_backers = self.backers.find({'fundraiser': fundraiser['_id']})
        if fundraiser:
            self.render('admin/fundraiser.html',
                        fundraiser=fundraiser,
                        fundraiser_backers=fundraiser_backers)
        else:
            raise HTTPError(404)


class AdminUserListHandler(AdminBase):

    @authenticated
    @require_staff
    def get(self):
        user_list = self.users_db.find().sort('-created_at').limit(30)
        self.render('admin/users.html',
                    user_list=user_list)
