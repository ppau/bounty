# -*- coding: utf-8 -*-

# Where we hold our private key for PIN and the charge url (currently the test url)
# as well as the secret key for the cookies and the login credentials for the
# email server

pub_key = ''  # Your Pin.js Publishable API Key

priv_key = ''  # Your Pin.js secret API Key

charge_url = 'https://api.pin.net.au/1/charges'
dev_charge_url = 'https://test-api.pin.net.au/1/charges'

cookie_secret = ''

email_credentials = {'username': '', 'password': ''}
