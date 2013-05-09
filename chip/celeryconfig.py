

BROKER_URL = 'amqp://guest@localhost//'

CELERY_RESULT_BACKEND = 'mongodb'
CELERY_MONGODB_BACKEND_SETTINGS = { "host" : "localhost", "port" : 27017, "database" : "celery_try",
"taskmeta_collection": "my_taskmeta" }
CELERY_IMPORTS = ('chip.tasks', )
