from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import smtplib

from config import SMTP_SERVER, SMTP_PORT
from secret import email_credentials

FROM = 'helpdesk@myleadpoint.com'


def send(to_address, from_address, message):

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.ehlo()
    server.starttls()
    server.login(email_credentials['username'], email_credentials['password'])
    server.sendmail(to_address, from_address, message)
    server.quit()


def send_receipt(recepient, fundraiser_name, amount, donation_date):

    message = MIMEText("""
The Australian Pirate Party - Bounty

Thank you for your donation.

DONATION DETAILS

Email: {}
Fundraiser: {}
Date: {}
Donation ID:
Amount: {}

""".format(recepient, fundraiser_name, donation_date, amount))

    message['Subject'] = '{} - Donation Receipt'.format(fundraiser_name)
    message['From'] = FROM
    message['To'] = recepient

    send(recepient, FROM, message.as_string())
