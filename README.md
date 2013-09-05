Bounty
================================

A funding platform for PPAU

Development work will continue in the Development Branch. Master is considered _fairly_ stable.

Something to keep in mind;
- "If a card token is not used within 1 month it is automatically expired."
- Considering the merchant fee charged, increase the goal to absorb it?
- PIN requires that pages be HTTPS?
- Implement a donation ID? --- just use the db id?
- Hide Country? Default to Australia
- Remove requirement on Address line 2?
- Add search for order ID

At the moment Tornado serves the static files... probably not a good idea to leave in when this goes live

DEVELOPER SETUP:

1. copy secret_example.py to secret.py and configure
2. Configure python environment (2.7.x) and download requirements

    ```pip install -r requirements.txt```
3. Ensure MongoDB is running
4. Ensure RabbitMQ (or other message broker service although currently configured for Rabbit) is running
5. To setup the Admin user, cd to bounty directory and run setup

    ```python setup.py```
6. To begin Celery service, cd to bounty directory and run this

    ```celery worker --app=chip -l info```
7. Finally run the application, cd to bounty directory

    ```python application.py```

TO DO:

Each project will have:

    Backer rewards?

    Can have updates?

    Allow comments?

    Categories?


Finish fundraiser editing handler

CVC doesn't get tested by PIN?

Allow changes to Status by staff and the option to send messages to the Backer

Keep history of status changes and messages. Keep these independent from one another?
