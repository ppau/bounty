from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
#from email.MIMEImage import MIMEImage
import smtplib
from datetime import timedelta
from tornado.template import Template
import os

from config import SMTP_SERVER, SMTP_PORT
from secret import email_credentials

FROM = email_credentials['username']


def send(to_address, from_address, message):

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.ehlo()
    server.starttls()
    server.login(email_credentials['username'], email_credentials['password'])
    server.sendmail(from_address, to_address, message)
    server.quit()


def send_receipt(recepient, fundraiser_name, amount, donation_date):

    # bit messy, make this cleaner
    donation_date = (donation_date + timedelta(hours=10)).strftime('%H:%M:%S %Y-%m-%d  AEST')

    message = MIMEText("""
The Australian Pirate Party - Bounty

Thank you for your donation.

DONATION DETAILS

Email: {}
Fundraiser: {}
Date: {}
Donation ID:
Amount: ${}

""".format(recepient, fundraiser_name, donation_date, '{:.2f}'.format(amount)))

    message['Subject'] = '{} - Donation Receipt'.format(fundraiser_name)
    message['From'] = FROM
    message['To'] = recepient

    send(recepient, FROM, message.as_string())


def send_thanks(recepient, fundraiser_name, amount, donation_date):

    # bit messy, make this cleaner
    donation_date = (donation_date + timedelta(hours=10)).strftime('%H:%M:%S %Y-%m-%d  AEST')
    basepath = os.path.dirname(__file__)
    filepath = os.path.join(basepath, 'email.html')

    with open(filepath) as f:
        raw_template = f.read()

    t = Template(raw_template)
    parsed_template = t.generate(title='{} - Thank you'.format(fundraiser_name),
                                 donation_date=donation_date,
                                 fundraiser_name=fundraiser_name)

    message = MIMEMultipart('related')
    msg_html = MIMEText(parsed_template, 'html')

    message.attach(msg_html)

    message['Subject'] = '{} - Thank you'.format(fundraiser_name)
    message['From'] = FROM
    message['To'] = recepient

    send(recepient, FROM, message.as_string())
