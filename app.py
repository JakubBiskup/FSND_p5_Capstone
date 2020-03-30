import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect
from models import db, db_path, setup_db, Game, Member, Location, Event, Club
from forms import *

SECRET_KEY=os.urandom(32)


app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = db_path
app.config['SECRET_KEY']=SECRET_KEY

setup_db(app, db_path)
##
CLUB_NAME=Club.query.first().name
##
app.jinja_env.globals['CLUB_NAME']=CLUB_NAME
#HELPERS#
def get_current_user_auth0_id(user_id=1): #######################implement this function later, for now it returns auth0userid of given id's member,
  currmember=Member.query.filter_by(id=user_id).one_or_none()
  auth0_user_id=currmember.auth0_user_id
  return auth0_user_id
#


@app.route('/')
def index():
  club=Club.query.first()
  return render_template('pages/home.html',club=club)

@app.route('/games/all')
def get_all_games():
  games=Game.query.all()
  games_num=str(len(games))
  return render_template('pages/allgames.html', games=games,games_num=games_num)

@app.route('/members/all')
def get_all_members():
  members=Member.query.order_by(Member.username).all() #### change this later to ignore guests(users not granted member status yet)
  members_num=str(len(members))
  return render_template('pages/members.html',members=members,members_num=members_num)

@app.route('/events/all')
def get_all_events():
  events=Event.query.order_by(Event.time).all()
  past_events=[]
  future_events=[]
  players_num={}
  
  for e in events:
    if e.time<datetime.now():
      past_events.append(e)
    else:
      future_events.append(e)
    players_num[e.name]=len(e.players)
  past_events.reverse()
  return render_template('pages/events.html',past=past_events, future=future_events, joined=players_num)

@app.route('/events/<int:event_id>')
def get_event_page(event_id):
  event=Event.query.filter_by(id=event_id).first()
  current_players=event.players####
  current_players_num=len(current_players)####
  return render_template('pages/event.html', event=event, current_players_num=current_players_num)

@app.route('/events/<int:event_id>/edit')
def get_event_edit_form(event_id):
  event=Event.query.filter_by(id=event_id).one_or_none()
  form=EditEventForm()
  form.location.choices=[(l.id, l.name) for l in Location.query.all()]
  form.location.choices.append((0,'a new location'))
  form.games.choices=[(g.id, g.title) for g in Game.query.all()]
  return render_template('forms/edit_event.html', event=event, form=form)

@app.route('/events/<int:event_id>/join', methods=["PATCH"])
def join_event(event_id):
  try:
    event=Event.query.filter_by(id=event_id).one_or_none()
    current_user=Member.query.filter_by(auth0_user_id=get_current_user_auth0_id(5)).one_or_none()#####
    if current_user not in event.players and len(event.players)<event.max_players:
      event.players.append(current_user)
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    db.session.close()
    return redirect(f"/events/{event_id}")



@app.route('/events/<int:event_id>/edit', methods=["POST"])
def edit_event(event_id):
  try:
    name=request.form.get('name')
    description=request.form.get('description')
    time=request.form.get('time')
    games=[Game.query.filter_by(id=game_id).one_or_none() for game_id in request.form.getlist('games')]
    max_players=request.form.get('max_players')
    event=Event.query.filter_by(id=event_id).one_or_none()
    if request.form.get('location')=='0': #this will run when user chose 'a new location'
      location_name=request.form.get('location_name')
      country=request.form.get('country')
      city=request.form.get('city')
      street=request.form.get('street')
      house_num=request.form.get('house_num')
      appartment_num=request.form.get('appartment_num')
      if appartment_num=='':
        appartment_num=None
      new_location=Location(name=location_name,country=country,city=city,street=street,house_num=house_num,appartment_num=appartment_num)
      db.session.add(new_location)
      location_id=Location.query.filter_by(name=location_name).one_or_none().id
    else:
      location_id=request.form.get('location')
    if name:
      event.name=name
    if description:
      event.description=description
    if time:
      event.time=time
    if games:
      event.games=games
    if max_players:
      event.max_players=max_players
    event.location_id=location_id
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    db.session.close()
    return redirect(f"/events/{event_id}")
    
@app.route('/members/<int:member_id>')
def get_userpage(member_id):
  member=Member.query.filter_by(id=member_id).first()
  return render_template('pages/user.html', member=member)

@app.route('/members/<int:member_id>/detailed')
def get_userpage_with_details(member_id):
  member=Member.query.filter_by(id=member_id).first()
  return render_template('pages/detaileduser.html', member=member)

@app.route('/members/<int:member_id>/edit')
def get_user_edit_form(member_id):
  user_before_edit=Member.query.filter_by(id=member_id).one_or_none()
  form = MemberForm()
  return render_template('forms/edit_user.html', form=form, member=user_before_edit)

@app.route('/members/<int:member_id>/edit', methods=["POST"])
def edit_user(member_id):
  try:
    user=Member.query.filter_by(id=member_id).one_or_none()
    username=request.form.get('username')
    img_link=request.form.get('img_link')
    description=request.form.get('description')
    
    first_name=request.form.get('first_name')
    last_name=request.form.get('last_name')
    phone=request.form.get('phone')
    email=request.form.get('email')

    country=request.form.get('country')
    city=request.form.get('city')
    street=request.form.get('street')
    house_num=request.form.get('house_num')
    appartment_num=request.form.get('appartment_num')
    if username:
      user.username=username
      if user.home_address!=None:
        user.home_address.name=username+"'s home"
    if img_link:
      user.img_link=img_link
    if description:
      user.description=description
    if first_name:
      user.first_name=first_name
    if last_name:
      user.last_name=last_name
    if phone:
      user.phone=phone
    if email:
      user.email=email
    if user.home_address!=None:
      if country:
        user.home_address.country=country
      if city:
        user.home_address.city=city
      if street:
        user.home_address.street=street
      if house_num:
        user.home_address.house_num=house_num
      if appartment_num:
        user.home_address.appartment_num=appartment_num
    else:
      if country and city and street and house_num:
        if username:
          home_name=username+"'s home"
        else:
          home_name=Member.query.filter_by(id=member_id).one_or_none().username +"'s home"
        if appartment_num=='':
          appartment_num=None
        new_home=Location(name=home_name,country=country,city=city,street=street,house_num=house_num,appartment_num=appartment_num)
        db.session.add(new_home)
        user.home_address=new_home
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    db.session.close()
    return redirect(f"/members/{member_id}")

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
    current_user=Member.query.filter_by(auth0_user_id=get_current_user_auth0_id(5)).one_or_none()#####
    new_game.owners.append(current_user)
    db.session.add(new_game)
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    db.session.close()
    return redirect('/games/all')

@app.route('/members/create')
def get_user_form():
  form=MemberForm()
  return render_template('forms/new_user.html', form=form)

@app.route('/members/create', methods=["POST"])
def create_user():
  try:
    username=request.form.get('username')
    #auth0_user_id=get_current_user_auth0_id()
    auth0_user_id='thisisnotrealauth0idbutshoulddoitfornow123'####
    img_link=request.form.get('img_link')
    description=request.form.get('description')
    
    first_name=request.form.get('first_name')
    last_name=request.form.get('last_name')
    phone=request.form.get('phone')
    email=request.form.get('email')
    new_user=Member(username=username,img_link=img_link,auth0_user_id=auth0_user_id,description=description,first_name=first_name,last_name=last_name,phone=phone,email=email)
    db.session.add(new_user)

    country=request.form.get('country')
    city=request.form.get('city')
    street=request.form.get('street')
    house_num=request.form.get('house_num')
    appartment_num=request.form.get('appartment_num')
    if appartment_num=='':
      appartment_num=None
    if country and city and street and house_num:
      home_name=username+"'s home"
      new_home=Location(name=home_name,country=country,city=city,street=street,house_num=house_num,appartment_num=appartment_num)
      db.session.add(new_home)
      new_user.home_address=new_home
    
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    db.session.close()
    return render_template('pages/user.html', member=Member.query.filter_by(auth0_user_id=auth0_user_id).one_or_none())
    
@app.route('/events/create')
def get_event_form():
  form=EventForm()
  form.location.choices=[(l.id, l.name) for l in Location.query.all()]
  form.location.choices.append((0,'a new location'))
  form.games.choices=[(g.id, g.title) for g in Game.query.all()]
  return render_template('forms/new_event.html', form=form)

@app.route('/events/create', methods=["POST"])
def create_event():
  try:
    name=request.form.get('name')
    time=request.form.get('time')
    max_players=request.form.get('max_players')
    description=request.form.get('description')
    host_id=Member.query.filter_by(auth0_user_id=get_current_user_auth0_id(5)).one_or_none().id#####
    players=[Member.query.filter_by(auth0_user_id=get_current_user_auth0_id(5)).one_or_none()]#####
    
    if request.form.get('location')=='0': #this will run when user chose 'a new location'
      location_name=request.form.get('location_name')
      country=request.form.get('country')
      city=request.form.get('city')
      street=request.form.get('street')
      house_num=request.form.get('house_num')
      appartment_num=request.form.get('appartment_num')
      if appartment_num=='':
        appartment_num=None
      new_location=Location(name=location_name,country=country,city=city,street=street,house_num=house_num,appartment_num=appartment_num)
      db.session.add(new_location)
      location_id=Location.query.filter_by(name=location_name).one_or_none().id
    else:
      location_id=request.form.get('location')

    games=[Game.query.filter_by(id=game_id).one_or_none() for game_id in request.form.getlist('games')]
    
    new_event=Event(name=name,time=time,max_players=max_players,host_id=host_id,location_id=location_id,description=description)
    db.session.add(new_event)
    new_event.players=players
    new_event.games=games
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    db.session.close()
    return redirect('/events/all')

@app.route('/home/edit')
def get_club_form():
  form=ClubForm()
  return render_template('forms/edit_club.html', form=form)


@app.route('/home/edit', methods=['POST'])
def edit_club_info():
  try:
    name=request.form.get('name')
    img_link=request.form.get('img_link')
    h1=request.form.get('h1')
    welcoming_text=request.form.get('welcoming_text')
    club_info=Club.query.first()
    
    if img_link:
      club_info.img_link=img_link
    if h1:
      club_info.h1=h1
    if welcoming_text:
      club_info.welcoming_text=welcoming_text
    if name:
      club_info.name=name
      app.jinja_env.globals['CLUB_NAME']=name
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    db.session.close()
  return redirect('/')

@app.route('/games/<int:game_id>/own', methods=['PATCH'])
def declare_ownership_of_existing_game(game_id):
  try:
    game=Game.query.filter_by(id=game_id).one_or_none()
    current_user=Member.query.filter_by(auth0_user_id=get_current_user_auth0_id()).one_or_none()####
    if game not in current_user.ownership:
      current_user.ownership.append(game)
      db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    db.session.close()
  return redirect('/games/all')

@app.route('/games/<int:game_id>/edit')
def get_game_edit_form(game_id):
  game=Game.query.filter_by(id=game_id).one_or_none()
  form=GameForm()
  return render_template('forms/edit_game.html',game=game,form=form)

@app.route('/games/<int:game_id>/edit',methods=["POST"])
def edit_game(game_id):
  try:
    game=Game.query.filter_by(id=game_id).one_or_none()
    game.title=request.form.get('title')
    game.link=request.form.get('link')
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    db.session.close()
  return redirect('/games/all')

  
@app.route('/members/search', methods=["POST"])
def search_results_member():
  search=request.form.get('search_term')
  results=Member.query.filter(Member.username.ilike(f'%{search}%')).all()
  count=len(results)
  return render_template('pages/search_member.html', search=search, results=results, count=count)

@app.route('/events/search', methods=["POST"])
def search_results_event():
  search=request.form.get('search_term')
  results=Event.query.filter(Event.name.ilike(f'%{search}%')).all()
  count=len(results)
  return render_template('pages/search_event.html', search=search, results=results, count=count)

@app.route('/games/search', methods=["POST"])
def search_results_game():
  search=request.form.get('search_term')
  results=Game.query.filter(Game.title.ilike(f'%{search}%')).all()
  count=len(results)
  return render_template('pages/search_game.html', search=search, results=results, count=count)

@app.route('/games/<int:game_id>/delete', methods=["DELETE"])
def delete_game(game_id):
  try:
    game=Game.query.filter_by(id=game_id).one_or_none()
    db.session.delete(game)
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    db.session.close()
    return redirect('/games/all')

@app.route('/events/<int:event_id>/delete', methods=["DELETE"])
def delete_event(event_id):
  try:
    event=Event.query.filter_by(id=event_id).one_or_none()
    db.session.delete(event)
    db.session.commit()
    return jsonify({'success': True}), 200
  except Exception as e:
    db.session.rollback()
    print(e)
    db.session.close()
    return jsonify({'success': False})
    

@app.route('/members/<int:member_id>/delete', methods=["DELETE"])
def delete_member(member_id):
  try:
    member=Member.query.filter_by(id=member_id).one_or_none()
    for game in member.ownership: # This will delete games if they are no longer owned by any user 
      if len(game.owners)==1:
        db.session.delete(game)
    db.session.delete(member)
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    db.session.close()
    return redirect('/members/all')
  
    



if __name__ == '__main__':
    app.run()