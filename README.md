Bounty
================================

A funding platform for PPAU

Something to keep in mind;
- "If a card token is not used within 1 month it is automatically expired."
- Considering the merchant fee charged, increase the goal to absorb it?
- PIN requires that pages be HTTPS?
- Implement a donation ID? --- just use the db id?
- Hide Country? Default to Australia
- Remove requirement on Address line 2?
- Add search for order ID

DEVELOPER SETUP:

1. copy secret_example.py to secret.py and configure
2. Configure python environment and download requirements

    pip install -r requirements.txt
3. Ensure MongoDB is running
4. Ensure RabbitMQ (or other message broker service is running)
5. To begin Celery service, cd to bounty directory add run this

    celery worker --app=chip -l info
6. Finally run the application, cd to bounty directory

    python application.py

TO DO:

Each project will have:

    Admin?

    Goal √

    Launched √

    Deadline √

    Current funding √

    Number of backers/sponsors √

    Description √

    Backer rewards?

    Can have updates?

    Allow comments?

    Categories?

Needs pagination too √

Add in user pages for Admin √

Finish fundraiser editing handler

CVC doesn't get tested by PIN?
