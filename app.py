import os
from flask import Flask, render_template, jsonify, request
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

@app.route('/games/create', methods=['POST'])
def create_game():
  try:
    title=request.form.get('title')
    link=request.form.get('link')
    new_game=Game(title=title,link=link)
    current_user=Member.query.first()#####Change this query to get a user that is currently logged in 
    new_game.owners.append(current_user)
    db.session.add(new_game)
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    db.session.close()
    return render_template('pages/user.html',member=Member.query.first())

@app.route('/members/create')
def get_user_form():
  form=MemberForm()
  return render_template('forms/new_user.html', form=form)


if __name__ == '__main__':
    app.run()