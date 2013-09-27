# -*- coding: utf-8 -*-
from base import BaseHandler
from tornado.web import HTTPError
from tornado.web import authenticated
from bson.objectid import ObjectId

from auth import require_staff
#from auth import require_admin
from config import FUNDRAISERS_PER_PAGE
from secret import pub_key


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
        page = self.get_argument('page', None)
        if page:
            page = int(page)
        else:
            page = 1

        fundraisers_all = self.fundraisers.find()
        if page > 1:
            recent = fundraisers_all.sort([('launched', -1)]) \
                .skip(FUNDRAISERS_PER_PAGE*(int(page)-1)).limit(FUNDRAISERS_PER_PAGE)
        else:
            recent = fundraisers_all.sort([('launched', -1)]).limit(FUNDRAISERS_PER_PAGE)
        total = fundraisers_all.count()

        #recent = self.fundraisers.find().sort([('launched', -1)]).limit(30)
        #Depending on rank, show users of below your rank only?
        users = self.users_db.find().sort([('created_at', -1)]).limit(30)
        self.render('admin/admin.html', recent=recent,
                    total=total, page=page,
                    page_size=FUNDRAISERS_PER_PAGE,
                    users=users,
                    pin_public_key=pub_key)


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
        user_list = self.users_db.find().sort([('created_at', -1)]).limit(30)
        self.render('admin/user_list.html',
                    user_list=user_list)


class AdminUserEditHander(AdminBase):

    @authenticated
    @require_staff
    def get(self, username):
        user = self.users_db.find_one({'username': username})
        if user:
            backed = self.backers.find({'user': username})
            backed_fundraisers = {}
            if backed:
                for i in backed:
                    if self.fundraisers.find_one({'_id': i['fundraiser']}):
                        backed_fundraisers[i['fundraiser']] = self.fundraisers.find_one({'_id': i['fundraiser']})
            self.render('admin/user.html',
                        user=user,
                        backed=self.backers.find({'user': username}),
                        backed_fundraisers=backed_fundraisers)
        else:
            raise HTTPError(404)


class AdminBackerListHandler(AdminBase):

    @authenticated
    @require_staff
    def get(self):
        backer_list = self.backers.find().sort([('created_at', -1)]).limit(30)
        fundraisers = self.fundraisers.find()
        fundraiser_list = {}
        for i in fundraisers:
            fundraiser_list[str(i['_id'])] = {'title': i['title'], 'slug': i['slug']}
        self.render('admin/backer_list.html',
                    backer_list=backer_list,
                    fundraiser_list=fundraiser_list,
                    tab='users')


class AdminBackerDeleteHandler(AdminBase):

    @authenticated
    @require_staff
    def get(self, _id):
        backer = self.backers.find_one({'_id': ObjectId(_id)})
        if backer:
            user = backer['user']
            self.backers.remove(backer)
            self.redirect(u'/admin/user/{}?message=success'.format(user))
        else:
            raise HTTPError(404)


class AdminBackerDetailHandler(AdminBase):

    @authenticated
    @require_staff
    def get(self, _id):
        backer = self.backers.find_one({'_id': ObjectId(_id)})
        fundraiser = self.fundraisers.find_one({'_id': ObjectId(backer['fundraiser'])})
        if backer:
            self.render('admin/backer.html',
                        backer=backer,
                        fundraiser=fundraiser)
        else:
            raise HTTPError(404)

class AdminBackerPostMessageHandler(AdminBase):

    @authenticated
    @require_staff
    def post(self):
        backer_id = self.get_argument('backer_id', None)
        status = self.get_argument('status', None)
        message = self.get_argument('message', None)
        backer = self.backers.find_one({'_id': ObjectId(_id)})
        if backer:
            backer['messages'].append({'status': status,
                                       'message': message,
                                       'staff': self.get_current_user(),
                                       'date': datetime.datetime.utcnow(),})
            self.backers.save(backer)
