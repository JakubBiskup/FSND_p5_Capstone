import os
from flask import Flask, render_template, jsonify
from models import db, db_path, setup_db, Game, Member, Location, Event
from forms import *

SECRET_KEY=os.urandom(32)

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = db_path
app.config['SECRET_KEY']=SECRET_KEY

setup_db(app, db_path)

@app.route('/')
def index():
  return render_template('pages/home.html')

@app.route('/games/all')
def get_all_games():
  return render_template('pages/allgames.html')

@app.route('/members/all')
def get_all_members():
  return render_template('pages/members.html')

@app.route('/events/all')
def get_all_events():
  return render_template('pages/events.html')

@app.route('/members/<int:member_id>')
def get_userpage(member_id):
  member=Member.query.filter_by(id=member_id).first()
  return render_template('pages/user.html', member=member)

@app.route('/members/<int:member_id>/detailed')
def get_userpage_with_details(member_id):
  member=Member.query.filter_by(id=member_id).first()
  return render_template('pages/detaileduser.html', member=member)

@app.route('/games/create')
def get_game_form():
  form=GameForm()
  return render_template('forms/new_game.html', form=form)



if __name__ == '__main__':
    app.run()