from __future__ import absolute_import

from datetime import datetime
from time import sleep
import pymongo

from chip.celery import celery


@celery.task
def add(x, y):
    return x + y


@celery.task
def fundraiser_countdown(fundraiser_id, finish_time):

    # Finish time must be datetime

    while finish_time > datetime.utcnow():
        sleep(1)
    #do charges
    conn = pymongo.Connection()
    db = conn.bounty
    fundraisers = db.fundraisers
    fundraiser = fundraisers.find_one({'_id': fundraiser_id})
    fundraiser['description'] = 'Finished!'
    fundraisers.save(fundraiser)

    return True
