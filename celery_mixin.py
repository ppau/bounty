#import os
#import socket
#from uuid import uuid4
#import functools
#from tornado.web import asynchronous, RequestHandler
from tornado.web import asynchronous
import datetime
import tornado.ioloop
#from tornado import gen
import logging

from base import BaseHandler

#from chip.tasks import celery_notify
from chip.tasks import fundraiser_countdown
from chip.tasks import perform_charge


class CeleryHandler(BaseHandler):

    # Based off this http://stackoverflow.com/a/8214009
    # And a blog post that's dead
    # Might be worth making it more generic so it can be re-used

    @asynchronous
    def fundraiser_deadline(self, _id, deadline):

        # So this works and it doesn't block
        deadline_task = fundraiser_countdown.delay(_id, deadline)
        wait_time = deadline - datetime.datetime.utcnow()
        logging.info('In fundraiser_deadline')

        def check_celery_task():
            if deadline_task.ready():
                #do something to mark our success here somewhere
                fundraisers = self.db.fundraisers
                fundraiser = self.fundraisers.find_one({'_id': _id})
                fundraiser['status'] = 'Finished'
                fundraisers.save(fundraiser)
                #self.finish()
            else:
                tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(0.00001), check_celery_task)

        tornado.ioloop.IOLoop.instance().add_timeout(wait_time, check_celery_task)

    @asynchronous
    def fundraiser_charge(self, _id, description):
        logging.info('Begin charge')
        charge_task = perform_charge.delay(_id, description)

        def check_celery_task():
            if charge_task.ready():
                logging.info('Success')
                #do something to mark our success here somewhere
                #RuntimeError: Cannot write() after finish(). May be caused by using async operations
                # without the @asynchronous decorator.
                # redirect, render, and send_error all call finish() ?
                #self.write({'success': True})
                #self.set_header("Content-Type", "application/json")
                #self.finish()
                pass
            else:
                tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(0.00001), check_celery_task)

        tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(0.00001), check_celery_task)

    #@gen.engine
    # wait_time = deadline - datetime.datetime.utcnow()
    # yield gen.Task(tornado.ioloop.IOLoop().instance().add_timeout, wait_time)
    # conn = pymongo.Connection()
    # db = conn.bounty
    # fundraisers = db.fundraisers
    # fundraiser = fundraisers.find_one({'_id': _id})
    # fundraiser['description'] = 'Finished!'
    # fundraisers.save(fundraiser)
    # Charge cards here...


## Modified from https://github.com/eguven/tornadoist/
## Despite modifications this doesn't work on Windows, can't select sockets
## This way may be better, check if it's not Windows then use this way?
# class CeleryMixin(object):

#     def add_task(self, taskname, *args, **kwargs):

#         ioloop = tornado.ioloop.IOLoop().instance()
#         user_cb = kwargs.pop('callback')
#         callback = functools.partial(self._on_complete, user_cb)
#         if os.name == 'nt':
#             sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             sock.bind(('', 0))
#             sock_no = sock.getsockname()[1]
#             logging.info(sock_no)
#             ioloop.add_handler(sock_no, callback, ioloop.READ)
#             link = celery_notify.subtask(args=(sock_no,), immutable=True)
#             self.celery_result = taskname.apply_async(args, kwargs, link=link)
#             self.celery_socket = sock
#         elif os.name == 'posix':
#             pass

#     def _on_complete(self, callback, *args):
#         ioloop = tornado.ioloop.IOLoop().instance()
#         if os.name == 'nt':
#             ioloop.remove_handler(self.celery_socket.getsockname()[1])
#         elif os.name == 'posix':
#             ioloop.remove_handler(self.celery_socket.fileno())
#         self.celery_socket.close()
#         callback(self.celery_result.result)
