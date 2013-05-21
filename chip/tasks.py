from __future__ import absolute_import

from datetime import datetime
from time import sleep
import requests
import pymongo
from celery.utils.log import get_task_logger

from chip.celery import celery

from secret import charge_url, priv_key

logger = get_task_logger(__name__)


@celery.task
def add(x, y):
    return x + y


@celery.task
def fundraiser_countdown(fundraiser_id, finish_time):

    # Finish time must be datetime

    while finish_time > datetime.utcnow():
        sleep(1)
    #before doing charges, check to see if funding goal reached?
    conn = pymongo.Connection()
    db = conn.bounty
    backers_db = db.backers
    backers = backers_db.find({'fundraiser': fundraiser_id})
    for i in backers:
        payload = {'description': 'test charge',  # get this description from the fundraiser?
                   'ip': i['ip_address'],
                   'currency': 'AUD',
                   'amount': int(i['amount']*100),  # need to send it in cents
                   'card_token': i['card_token'],
                   'email': 'test@test.com'}  # get the user email from the user
        logger.debug(payload)
        r = requests.post(charge_url, auth=(priv_key, ''), data=payload)
        logger.debug(r.status_code)
        logger.debug(r.content)
        if r.status_code == 201:
            r_json = r.json()
            if r_json['response']['success'] is True:
                i['status'] = 'Charged'
                i['charged_when'] = datetime.utcnow()
                backers_db.save(i)
        else:
            i['status'] = 'Error'
            if r_json['response']['status_message']:
                i['status_message'] = r_json['response']['status_message']
            if r_json['response']['error_message']:
                i['error_message'] = r_json['response']['error_message']
            backers_db.save(i)
        """
        Example response
        '{"response":{"token":"ch_9Ef6EWj1eSs-84OA-K8OlA","success":true,
        "amount":100,"currency":"AUD","description":"test charge",
        "email":"test@test.com","ip_address":null,"created_at":"2013-05-07T08:15:45Z",
        "status_message":"Success!","error_message":null,
        "card":{"token":"card_D7pAOWN15bLrivfbEBoPjw",
        "display_number":"XXXX-XXXX-XXXX-0000","scheme": "master",
        "address_line1":"","address_line2":"","address_city":"",
        "address_postcode":"","address_state":"","address_country":""},
        "transfer":[],"amount_refunded":0,"total_fees":33,"merchant_entitlement":67,
        "refund_pending":false}}'
        """

    return True

# @celery.task
# def celery_notify(sock_no):

#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.connect(('', sock_no))
#     sock.close()
