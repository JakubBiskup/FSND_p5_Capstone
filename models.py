import os
from flask_sqlalchemy import SQLAlchemy

# db_name = 'bishopgamingdb'
# db_path = "postgres://postgres:123@{}/{}".format('localhost:5432', db_name)
db_path = os.environ['DATABASE_URL']
# comment out the line above and uncomment the line below to prepare for testing locally
# db_path='dummy value'
db = SQLAlchemy()


def setup_db(app, database_path=db_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


game_ownership = db.Table(
    'member_game', db.Column(
        'member_id', db.Integer, db.ForeignKey('member.id')), db.Column(
            'game_id', db.Integer, db.ForeignKey('game.id')))

games_at_event = db.Table(
    'game_event', db.Column(
        'event_id', db.Integer, db.ForeignKey('event.id')), db.Column(
            'game_id', db.Integer, db.ForeignKey('game.id')))

players_at_event = db.Table(
    'member_event', db.Column(
        'member_id', db.Integer, db.ForeignKey('member.id')), db.Column(
            'event_id', db.Integer, db.ForeignKey('event.id')))


class Club(db.Model):
    __tablename__ = 'club'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    img_link = db.Column(db.String(200), nullable=True)
    h1 = db.Column(db.String(120), nullable=True)
    welcoming_text = db.Column(db.String(1000), nullable=True)


class Game(db.Model):
    __tablename__ = 'game'
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(120), nullable=False, unique=True)

    games_to_be_played = db.relationship(
        'Event',
        secondary=games_at_event,
        backref=db.backref('games'))


class Member(db.Model):
    __tablename__ = 'member'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    img_link = db.Column(db.String(200), nullable=True)
    admin = db.Column(db.Boolean, default=False)
    member = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(1000), nullable=True)
    auth0_user_id = db.Column(db.String(64), unique=True, nullable=False)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(64), nullable=True)

    address = db.Column(
        db.Integer,
        db.ForeignKey('location.id'),
        nullable=True)

    event_creation = db.relationship('Event', backref=db.backref('host'))

    ownership = db.relationship(
        'Game',
        secondary=game_ownership,
        backref=db.backref('owners'))
    participation = db.relationship(
        'Event',
        secondary=players_at_event,
        backref=db.backref('players'))


class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    max_players = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), nullable=True)

    host_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)
    location_id = db.Column(
        db.Integer,
        db.ForeignKey('location.id'),
        nullable=False)


class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    country = db.Column(db.String(64), nullable=False)
    city = db.Column(db.String(32), nullable=False)
    street = db.Column(db.String(64), nullable=False)
    house_num = db.Column(db.String(10), nullable=False)
    appartment_num = db.Column(db.Integer, nullable=True)

    habitat = db.relationship('Member', backref=db.backref('home_address'))
    place = db.relationship('Event', backref=db.backref('location'))
