# BishopGaming
Bishop Gaming is a flask app designed for a single board game club (club as a group of people). It can be used to set up and schedule board game meetings of club members and keep track of game collection of the whole club and each of its members. This project is also the Capstone Project for Full-Stack Nanodegree at Udacity.

## Database structure
![https://app.quickdatabasediagrams.com/#/d/XO5g4p](/static/img/QuickDBD.png)
## Role Based Access Control

##### User that is NOT logged in through Auth0 is allowed to:
- view homepage
- view all members page
- view particular member page (without details)
- view all events page
- view particular event page 
- view club's game collection
- search for game
- search for event
- search for member

##### User that is logged in through Auth0 but does not have a role is allowed to:
- view homepage
- view all members page
- view particular member page (without details)
- view all events page
- view particular event page 
- view club's game collection
- search for game
- search for event
- search for member
- create his/her member object (if user does not yet have it)
- edit his/her member object

##### Club member is allowed to:
- view homepage
- view all members page
- view particular member page (with and without details)
- view all events page
- view particular event page 
- view club's game collection
- search for game
- search for event
- search for member
- edit his/her member object
- create event
- edit hosted event
- delete hosted event
- join event
- withdraw from event
- add game
- delete game (only if he/she is the only owner of the title)

##### Club admin is allowed to:
- view homepage
- edit homepage
- view all members page
- view particular member page (with and without details)
- view all events page
- view particular event page 
- view club's game collection
- search for game
- search for event
- search for member
- edit his/her member object
- delete member object
- create event
- edit hosted event
- delete any event
- join event
- withdraw from event
- add game
- delete any game
- edit game

## API Reference

### Base URL
This app is currently hosted at http://bishopgaming.herokuapp.com/
### Error Handling
Errors are returned as JSON objects with "success" set to False, "error" set to the error's number and a "message" describing the error

The API may return these error types when requests fail:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Resource Not Found
- 500: Internal Server Error

### Endpoints

##### PATCH /events/<int:event_id>/join
This endpoint accepts only requests with PATCH method. It is used to declare that currently logged in member will participate in an event (or to declare that he has participated in an event if the event is in the past).
Only members and admins are authorized to use this endpoint.
On successful request, the API will append currently logged in member to event's player list and return http status code 200.
If event has already reached max players number, this endpoint will return a 400 http status code and a json object with "success" set to False and "message" saying that 'This event has already reached maximum capacity'.

##### PATCH /events/<int:event_id>/unjoin
This endpoint accepts only requests with PATCH method. It is used to withdraw from an event.
On successful request, the API will remove currently logged in member from event's player list and return http status code 200.

##### DELETE /events/<int:event_id>/delete
This endpoint accepts only requests with DELETE method. It is used to delete an event of that id entirely.
Only admins are authorized to delete any event. Members are authorized to delete the events where they are the host.
On successful request, the API will delete the event and return http status code 200.


##### DELETE /games/<int:game_id>/unown
This endpoint accepts only requests with DELETE method. It is used to declare that currently logged in member no longer owns a game of that id.
On successful request, the API will return http status code 200 and remove the game from currently logged in member's collection. In case when that member is the only owner of that game, the game will be deleted entirely (and also removed from club's collection).

#### Other endpoints
All the other endpoints return either http status code 200 and a page rendered from template (usually filled with the data from the database) or http status code 302 and a redirect to another endpoint that renders a page

## Getting started with local development

### Basic Requirements

In order to successfully set up the app, you need to have Python3, pip and PostgreSQL (12.1) already installed on your local machine

### Installing dependencies

Install dependencies by navigating to the project directory and running:

```bash
pip install -r requirements.txt
```

### Database Setup

There is a file named "bgstartntestdb.bak" in project directory. It contains an example database.
Restore the database from that file 
```bash
psql bgstartntestdb < bgstartntestdb.bak
```

If you want to run the app locally, you will have to comment out line 5 and uncomment line 8 in models.py, providing path to your local database

### Running the server

To run the server, execute these three lines from within the project directory:
```bash
export FLASK_ENV=development
export FLASK_APP=app
flask run
```

### Running the tests
To run the tests you will also need to change TEST_DB_PATH (line 9 and 10) in test_app.py to match the path to your database. Note that running the tests will affect your database.
To run the tests, execute this line from the project directory:
```bash
python test_app.py
```

### Hosting instructions

The app is prepared to be deployed to Heroku.
You need to have a Heroku account and Heroku CLI installed on your machine.

Log in to your Heroku account
```bash
heroku login
```
Create Heroku app
```
heroku create app_name
```
The output will include a git url. Copy it and add git remote for Heroku to your local repository
```
git remote add heroku heroku_git_url
```
Add postgresql add-on 
```
heroku addons:create heroku-postgresql:hobby-dev --app app_name
```
Push the app to Heroku
```
git push heroku master
```

