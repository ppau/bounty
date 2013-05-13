# -*- coding: utf-8 -*-
from base import BaseHandler


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

    def get(self):
        recent = self.fundraisers.find().sort('-launched').limit(30)
        self.render('admin/admin.html', recent=recent)


class AdminFundraiserHandler(AdminBase):

    def get(self, fundraiser_slug):
        fundraiser = self.fundraisers.find_one({'slug': fundraiser_slug})
        if fundraiser:
            self.render('admin/fundraiser.html',
                        fundraiser=fundraiser)
        else:
            raise HTTPError(404)
