import getpass
import sys
import datetime

from config import VERSION


def get_admin_details():

    # renamed raw_input to just input in Python 3.x
    admin_name = raw_input('Input Admin User Name: ')
    # from http://stackoverflow.com/questions/1761744/python-read-password-from-stdin/1761754#1761754
    pprompt = lambda: (getpass.getpass('Input Admin Password: '), getpass.getpass('Retype password: '))

    p1, p2 = pprompt()

    while p1 != p2:
        print('Passwords do match. Try again.')
        p1, p2 = pprompt()

    admin_email = raw_input('Input Admin Email Address: ')

    admin_pass = pbkdf2_sha256.encrypt(p1)

    return admin_name, admin_pass, admin_email


def create_admin(admin_name, admin_pass, admin_email):

    conn = pymongo.Connection()
    db = conn.bounty
    users = db.users
    saved = False

    while saved is False:
        if users.find_one({'username': admin_name}):
            print 'User already exists!'
            print 'Try again...'
            admin_name, admin_pass, admin_email = get_admin_details()
        else:
            admin = {'username': admin_name,
                     'password': admin_pass,
                     'email': admin_email,
                     'created_at': datetime.datetime.utcnow(),
                     'rank': 'admin'}
            users.save(admin)
            saved = True
            print 'Admin account successfully created!'


if __name__ == '__main__':

    print '=== Bounty Setup v{} ==='.format(VERSION)

    try:
        import pymongo
    except ImportError:
        print 'PyMongo not installed! Exiting...'
        sys.exit()

    try:
        from passlib.hash import pbkdf2_sha256
    except ImportError:
        print 'Passlib not installed! Exiting...'
        sys.exit()

    admin_name, admin_pass, admin_email = get_admin_details()
    create_admin(admin_name, admin_pass, admin_email)

    print 'Setup finished. You can now run application.py and login to begin.'
