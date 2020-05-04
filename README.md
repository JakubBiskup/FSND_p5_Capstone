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
< TODO: endpoints here>

## Getting started with local development

### Basic Requirements

In order to successfully set up the app, you need to have Python3, pip and PostgreSQL (12.1) already installed on your local machine

### Installing dependencies

Install dependencies by navigating to the project directory and running:

```bash
pip install -r requirements.txt
```

### Database Setup

<TODO: text here>

### Running the server

To run the server, execute these three lines from within the `/backend` directory:
```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

### Hosting instructions

<TODO: text here>

