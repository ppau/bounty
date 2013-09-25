from __future__ import absolute_import

from datetime import datetime
from time import sleep
import requests
import pymongo
from celery.utils.log import get_task_logger

from chip.celery import celery
from chip.chip_email import send_receipt, send_thanks

from secret import charge_url, priv_key

logger = get_task_logger(__name__)


## NEED TO REFACTOR THIS STUFF
def charge(backer, backers_db, description):
    payload = {'description': description,
               'ip': backer['ip_address'],
               'currency': 'AUD',
               'amount': int(backer['amount']*100),  # need to send it in cents
               'card_token': backer['card_token'],
               'email': backer['email']}  # get the user email from the user
    logger.debug(payload)
    r = requests.post(charge_url, auth=(priv_key, ''), data=payload)
    logger.debug(r.status_code)
    logger.debug(r.content)
    if r.status_code == 201:
        r_json = r.json()
        if r_json['response']['success'] is True:
            #backer['status'] = 'Charged'
            backer['messages'].append({'date': datetime.datetime.utcnow(),
                                       'status': 'Charged', 'messages': ''})
            backer['charged_when'] = datetime.utcnow()
            backers_db.save(backer)
            send_receipt(backer['email'], description[9:], backer['amount'], backer['charged_when'], backer['_id'])
            send_thanks(backer['email'], description[9:], backer['amount'], backer['charged_when'])
    else:
        #backer['status'] = 'Error'
        backer['messages'].append({'date': datetime.datetime.utcnow(),
                                   'status': 'Error', 'messages': ''})
        if r_json['response']['status_message']:
            backer['status_message'] = r_json['response']['status_message']
        if r_json['response']['error_message']:
            backer['error_message'] = r_json['response']['error_message']
        backers_db.save(backer)


@celery.task
def fundraiser_countdown(fundraiser_id, finish_time):

    # Finish time must be datetime

    while finish_time > datetime.utcnow():
        sleep(1)
    #before doing charges, check to see if funding goal reached?
    conn = pymongo.Connection()
    db = conn.bounty
    backers_db = db.backers
    fundraisers = db.fundraisers
    #users = db.users
    backers = backers_db.find({'fundraiser': fundraiser_id})
    fundraiser = fundraisers.find_one({'_id': fundraiser_id})
    description = 'Bounty - {}'.format(fundraiser['title'])
    for i in backers:
        charge(i, backers_db, description)
        # user = users.find_one({'username': i['user']})
        # payload = {'description': description,
        #            'ip': i['ip_address'],
        #            'currency': 'AUD',
        #            'amount': int(i['amount']*100),  # need to send it in cents
        #            'card_token': i['card_token'],
        #            'email': user['email']}  # get the user email from the user
        # logger.debug(payload)
        # r = requests.post(charge_url, auth=(priv_key, ''), data=payload)
        # logger.debug(r.status_code)
        # logger.debug(r.content)
        # if r.status_code == 201:
        #     r_json = r.json()
        #     if r_json['response']['success'] is True:
        #         #i['status'] = 'Charged'
        #         i['messages'] = {'status': 'Charged', 'messages': ''}
        #         i['charged_when'] = datetime.utcnow()
        #         backers_db.save(i)
        # else:
        #     #i['status'] = 'Error'
        #     i['messages'] = {'status': 'Error', 'messages': ''}
        #     if r_json['response']['status_message']:
        #         i['status_message'] = r_json['response']['status_message']
        #     if r_json['response']['error_message']:
        #         i['error_message'] = r_json['response']['error_message']
        #     backers_db.save(i)
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


@celery.task
def perform_charge(backer_id, description):
    logger.debug('Begin charge in Celery')
    conn = pymongo.Connection()
    db = conn.bounty
    backers_db = db.backers
    backer = backers_db.find_one({'_id': backer_id})
    charge(backer, backers_db, description)

    return True
