import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, make_response, abort
from models import db, db_path, setup_db, Game, Member, Location, Event, Club
from forms import *
from auth import AuthError, requires_auth, get_auth0_user_id_from_cookie_token, check_auth

SECRET_KEY=os.urandom(32)###


app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = db_path
app.config['SECRET_KEY']=SECRET_KEY

setup_db(app, db_path)
##
CLUB_NAME=Club.query.first().name
##
app.jinja_env.globals['CLUB_NAME']=CLUB_NAME

#HELPERS#
def get_current_member_object():
  current_user=Member.query.filter_by(auth0_user_id=get_auth0_user_id_from_cookie_token()).one_or_none()
  return current_user

#

@app.route('/login')
def get_continue_button():
  return render_template('pages/login.html')

@app.route('/login', methods=["POST"])
def store_token_as_a_cookie():
  try:
    after_hash=request.form.get('after_hash')
    hash_split=after_hash.split('&')[0]
    token_string=hash_split.split('=')[1]
    token='Bearer '+token_string
    response=make_response(redirect('/'))
    response.set_cookie('token',token)
    return response
  except:
    abort(401)

@app.route('/')
def index():
  club=Club.query.first()
  current_user=get_current_member_object()
  newer_games=Game.query.order_by(Game.id.desc()).limit(5)
  admins=Member.query.filter_by(admin=True).all()
  past_events = Event.query.filter(Event.time <= datetime.now()).order_by(Event.time.desc()).limit(5)
  future_events = Event.query.filter(Event.time > datetime.now()).order_by(Event.time).limit(5)
  return render_template('pages/home.html',club=club,current_user=current_user,newer_games=newer_games,admins=admins,past=past_events,future=future_events)

@app.route('/games/all')
def get_all_games():
  current_user=get_current_member_object()
  games=Game.query.order_by(Game.title).all()
  games_num=len(games) #### would games.count() be better?
  return render_template('pages/allgames.html', games=games,games_num=games_num,current_user=current_user)

@app.route('/members/all')
def get_all_members():
  current_user=get_current_member_object()
  members=Member.query.filter_by(member=True).order_by(Member.username).all() #### change this later to ignore guests(users not granted member status yet)
  members_num=len(members)
  guests=Member.query.filter_by(member=False).order_by(Member.username).all()
  guests_num=len(guests)
  return render_template('pages/members.html',members=members,members_num=members_num,guests=guests, guests_num=guests_num, current_user=current_user)

@app.route('/events/all')
def get_all_events():
  current_user=get_current_member_object()
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
  return render_template('pages/events.html',past=past_events, future=future_events, joined=players_num,current_user=current_user)

@app.route('/events/<int:event_id>')
def get_event_page(event_id):
  current_user=get_current_member_object()
  event=Event.query.filter_by(id=event_id).one_or_none()
  if event is None:
    abort(404)
  did_join=False
  if current_user in event.players:
    did_join=True
  is_host=False
  if current_user==event.host:
    is_host=True
  current_players=event.players
  current_players_num=len(current_players)
  return render_template('pages/event.html', event=event, current_players_num=current_players_num,did_join=did_join,is_host=is_host,current_user=current_user)

@app.route('/events/<int:event_id>/edit')
def get_event_edit_form(event_id):
  current_user=get_current_member_object()
  event=Event.query.filter_by(id=event_id).one_or_none()
  host=event.host
  if host is None:
    abort(403)
  if host!=current_user:
    abort(403)
  form=EditEventForm()
  form.location.choices=[(l.id, l.name) for l in Location.query.all()]
  form.location.choices.append((0,'a new location'))
  form.games.choices=[(g.id, g.title) for g in Game.query.all()]
  form.location.default=event.location_id
  form.games.default=[g.id for g in event.games]
  form.process()
  form.description.data=event.description
  return render_template('forms/edit_event.html', event=event, form=form,current_user=current_user)


@app.route('/events/<int:event_id>/join', methods=["PATCH"])
@requires_auth(permission='join:events')
def join_event(event_id):
  try:
    event=Event.query.filter_by(id=event_id).one_or_none()
    current_user=get_current_member_object()
    if current_user not in event.players and len(event.players)<event.max_players:
      event.players.append(current_user)
    else:
      if len(event.players)>=event.max_players:
        return jsonify({'success':False,'message':'This event has already reached maximum capacity'}),400 ###############not sure which code should I respond with here
    db.session.commit()
    db.session.close()
    return jsonify({'success':True}), 200
  except Exception as e:
    db.session.rollback()
    print(e)
    db.session.close()
    return jsonify({'success':False}),500 ########################### change status code

@app.route('/events/<int:event_id>/unjoin', methods=['PATCH'])
def leave_event(event_id):
  try:
    event=Event.query.filter_by(id=event_id).one_or_none()
    current_user=get_current_member_object()
    if current_user is None:
      abort(401)
    if current_user in event.players:
      event.players.remove(current_user)
    db.session.commit()
    db.session.close()
    return jsonify({'success':True}), 200
  except Exception as e:
    db.session.rollback()
    print(e)
    db.session.close()
    return jsonify({'success':False}),500 ###########################




@app.route('/events/<int:event_id>/edit', methods=["POST"])
def edit_event(event_id):
  current_user=get_current_member_object()
  event=Event.query.filter_by(id=event_id).one_or_none()
  if current_user!=event.host:
    abort(401)
  try:
    name=request.form.get('name')
    description=request.form.get('description')
    time=request.form.get('time')
    games=[Game.query.filter_by(id=game_id).one_or_none() for game_id in request.form.getlist('games')]
    max_players=request.form.get('max_players')
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
  current_user=get_current_member_object()
  member=Member.query.filter_by(id=member_id).first()
  games_count=len(member.ownership)
  return render_template('pages/user.html', member=member, games_count=games_count, current_user=current_user)

@app.route('/members/<int:member_id>/detailed')
@requires_auth('read:member-details')
def get_userpage_with_details(member_id):
  current_user=get_current_member_object()
  member=Member.query.filter_by(id=member_id).first()
  games_count=len(member.ownership)
  return render_template('pages/user_detailed.html', member=member, games_count=games_count,current_user=current_user)

@app.route('/members/me/edit')
def get_user_edit_form():
  current_user=get_current_member_object()
  if current_user is None:
    abort(401)
  form = MemberForm()
  form.description.data=current_user.description
  return render_template('forms/edit_user.html', form=form, member=current_user, current_user=current_user)

@app.route('/members/me/edit', methods=["POST"])
def edit_user():
  try:
    user=get_current_member_object()
    if user is None:
      abort(401)
    username=request.form.get('username')
    img_link=request.form.get('img_link')
    description=request.form.get('description')
    
    id_for_redirect=user.id

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
          home_name=user.username +"'s home"
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
    return redirect(f"/members/{id_for_redirect}")

@app.route('/games/create')
@requires_auth('add:games')
def get_game_form():
  current_user=get_current_member_object()
  form=GameForm()
  form.game.choices=[(g.id, g.title) for g in Game.query.all()]
  form.game.choices.append((0,"new game"))
  form.game.default=0
  form.process()
  return render_template('forms/new_game.html', form=form, current_user=current_user)

@app.route('/games/create', methods=['POST'])
@requires_auth('add:games')
def add_game():
  try:
    current_user=get_current_member_object()
    game_id=request.form.get('game')
    title=request.form.get('title')
    link=request.form.get('link')
    if game_id is not '0':
      game=Game.query.filter_by(id=game_id).one_or_none()
      if game not in current_user.ownership:
        current_user.ownership.append(game)
        db.session.commit()
    else:
      new_game=Game(title=title,link=link)
      db.session.add(new_game)
      current_user.ownership.append(new_game)
      db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    current_user_id=current_user.id
    db.session.close()
    return redirect(f'/members/{current_user_id}')

@app.route('/members/create')
@requires_auth()
def get_user_form():
  form=MemberForm()
  return render_template('forms/new_user.html', form=form)

@app.route('/members/create', methods=["POST"])
@requires_auth()
def create_user():
  try:
    username=request.form.get('username')
    auth0_user_id=get_auth0_user_id_from_cookie_token()
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
@requires_auth('create:events')
def get_event_form():
  current_user=get_current_member_object()
  form=EventForm()
  form.location.choices=[(l.id, l.name) for l in Location.query.all()]
  form.location.choices.append((0,'a new location'))
  form.games.choices=[(g.id, g.title) for g in Game.query.all()]
  return render_template('forms/new_event.html', form=form,current_user=current_user)

@app.route('/events/create', methods=["POST"])
@requires_auth('create:events')
def create_event():
  try:
    name=request.form.get('name')
    time=request.form.get('time')
    max_players=request.form.get('max_players')
    description=request.form.get('description')
    host=get_current_member_object()
    host_id=host.id
    players=[host]
    
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
@requires_auth('edit:club')
def get_club_form():
  current_user=get_current_member_object()
  form=ClubForm()
  old_club=Club.query.first()
  form.welcoming_text.data=old_club.welcoming_text
  return render_template('forms/edit_club.html', form=form, club=old_club,current_user=current_user)


@app.route('/home/edit', methods=['POST'])
@requires_auth('edit:club')
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

@app.route('/games/<int:game_id>/own', methods=['PATCH'])########################do I need this endpoint?
@requires_auth('add:games')
def declare_ownership_of_existing_game(game_id):
  try:
    game=Game.query.filter_by(id=game_id).one_or_none()
    current_user=get_current_member_object()
    if game not in current_user.ownership:
      current_user.ownership.append(game)
      db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    db.session.close()
  return redirect('/games/all')

@app.route('/games/<int:game_id>/unown', methods=['DELETE'])###################no need for auth (?), should this be delete or patch?
def cancel_ownage_of_game(game_id):
  try:
    current_user=get_current_member_object()
    if current_user is None:
      abort(401)
    game=Game.query.filter_by(id=game_id).one_or_none()
    games_of_user=current_user.ownership
    if game in games_of_user:
      games_of_user.remove(game)
      if len(game.owners)==0:
        db.session.delete(game)
        db.session.commit()
        db.session.close()
        return jsonify({'success': True}), 200
      else:
        db.session.commit()
        db.session.close()
        return jsonify({'success': True}), 200
  except Exception as e:
    db.session.rollback()
    print(e)
    db.session.close()
    return jsonify({'success': False}), 400
      

@app.route('/games/<int:game_id>/edit')
@requires_auth(permission='edit:games')
def get_game_edit_form(game_id):
  current_user=get_current_member_object()
  game=Game.query.filter_by(id=game_id).one_or_none()
  form=GameForm()
  return render_template('forms/edit_game.html',game=game,form=form,current_user=current_user)

@app.route('/games/<int:game_id>/edit',methods=["POST"])
@requires_auth(permission='edit:games')
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
  current_user=get_current_member_object()
  search=request.form.get('search_term')
  results=Member.query.filter(Member.username.ilike(f'%{search}%')).all()
  count=len(results)
  return render_template('pages/search_member.html', search=search, results=results, count=count,current_user=current_user)

@app.route('/events/search', methods=["POST"])
def search_results_event():
  current_user=get_current_member_object()
  search=request.form.get('search_term')
  results=Event.query.filter(Event.name.ilike(f'%{search}%')).order_by(Event.time).all()
  count=len(results)
  return render_template('pages/search_event.html', search=search, results=results, count=count, current_user=current_user)

@app.route('/games/search', methods=["POST"])
def search_results_game():
  current_user=get_current_member_object()
  search=request.form.get('search_term')
  results=Game.query.filter(Game.title.ilike(f'%{search}%')).all()
  count=len(results)
  return render_template('pages/search_game.html', search=search, results=results, count=count, current_user=current_user)

@app.route('/games/<int:game_id>/delete', methods=["DELETE"])
@requires_auth('delete:games')
def delete_game(game_id):
  try:
    game=Game.query.filter_by(id=game_id).one_or_none()
    if game is None:
      abort(404)
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
    if event is None:
      abort(404)
    host=event.host
    if host is None: #in case of host not existing anymore #########################
      if check_auth(permission='delete:events'):
        db.session.delete(event)
        db.session.commit()
        return jsonify({'success': True}), 200
      else:
        abort(403)
    if get_current_member_object()==host:
      db.session.delete(event)
      db.session.commit()
      return jsonify({'success': True}), 200
    else:
      if check_auth(permission='delete:events'):
        db.session.delete(event)
        db.session.commit()
        return jsonify({'success': True}), 200
      else:
        abort(403)

  except Exception as e:
    db.session.rollback()
    print(e)
    db.session.close()
    return jsonify({'success': False}),500
    

@app.route('/members/<int:member_id>/delete', methods=["DELETE"])
@requires_auth('delete:members')
def delete_member(member_id):
  try:
    member=Member.query.filter_by(id=member_id).one_or_none()
    if member is None:
      abort(404)
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


#Error handling
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        'error': 404,
        'message': "resource not found"
    }), 404


@app.errorhandler(AuthError)
def authorization_failed(error):
    return jsonify({
        "success": False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'success': False,
                    'error': 500,
                    'message': 'internal server error'
                    }), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'success': False,
                    'error': 400,
                    'message': 'bad request'
                    }), 400    



if __name__ == '__main__':
    app.run()