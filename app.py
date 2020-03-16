import os
from flask import Flask, render_template, jsonify, request
from models import db, db_path, setup_db, Game, Member, Location, Event
from forms import *

SECRET_KEY=os.urandom(32)

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = db_path
app.config['SECRET_KEY']=SECRET_KEY

setup_db(app, db_path)

#HELPERS#
def get_current_user_auth0_id(): #######################implement this function later, for now it returns a fixed auth0userid string,
  return 'auth0|5e29ce15b8c4470f0791790b'
#


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

@app.route('/members/create', methods=["POST"])
def create_user():
  try:
    username=request.form.get('username')
    auth0_user_id=get_current_user_auth0_id()
    
    img_link=request.form.get('img_link')
    description=request.form.get('description')
    
    first_name=request.form.get('first_name')
    last_name=request.form.get('last_name')
    phone=request.form.get('phone')
    email=request.form.get('email')
    #####TODO:get home address data
    new_user=Member(username=username,img_link=img_link,auth0_user_id=auth0_user_id,description=description,first_name=first_name,last_name=last_name,phone=phone,email=email)
    db.session.add(new_user)
    #####TODO:create a new location ,naming it 'member's home if it doesnt exist already and set it as member's home address
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    db.session.close()
    return render_template('pages/user.html', member=Member.query.filter_by(auth0_user_id=auth0_user_id).one_or_none())
    
    
    
    
    
    



if __name__ == '__main__':
    app.run()