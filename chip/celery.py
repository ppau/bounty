from __future__ import absolute_import

from celery import Celery

#celery.config_from_object('celeryconfig')

celery = Celery('chip.celery',
                broker='amqp://guest@localhost//',
                #backend='amqp://',
                include=['chip.tasks'])

# Optional configuration, see the application user guide.
# celery.conf.update(
#    CELERY_RESULT_BACKEND='mongodb',
#    CELERY_MONGODB_BACKEND_SETTINGS={
#     'host': 'localhost',
#     'port': 27017
#     'database': 'bounty-celery',
#     'taskmeta_collection': 'my_taskmeta_collection',
#     },
# )

if __name__ == '__main__':
    celery.start()
