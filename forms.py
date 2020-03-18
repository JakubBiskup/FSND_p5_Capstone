from flask_wtf import Form
from wtforms import IntegerField, StringField, SelectField, SelectMultipleField, BooleanField, SubmitField
from wtforms.validators import DataRequired, URL
from wtforms.fields.html5 import DateTimeField

class GameForm(Form):
    title=StringField('Title', validators=[DataRequired()])
    link=StringField('Link', validators=[URL(), DataRequired()])
    submit=SubmitField('Add game to your collection')

class MemberForm(Form):
    username=StringField('Username', validators=[DataRequired()])
    img_link=StringField('Profile image link', validators=[URL()])
    description=StringField('Description')
    
    first_name=StringField('First Name')
    last_name=StringField('Last Name')
    phone=StringField('Phone')
    email=StringField('E-mail')
    
    country=StringField('Country')
    city=StringField('City')
    street=StringField('Street')
    house_num=StringField('House Number')
    appartment_num=StringField('Appartment Number')

    submit=SubmitField('Create your account')

class EventForm(Form):
    name=StringField('Event name', validators=[DataRequired()])
    time=DateTimeField('Time',  format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    location=SelectField('Location', choices=[])
    max_players=IntegerField('Players max number',validators=[DataRequired()])
    games=SelectMultipleField('Games (ctrl+click to choose multiple)', choices=[])
    description=StringField('Description')
    
    location_name=StringField('Name of the new location')
    country=StringField('Country')
    city=StringField('City')
    street=StringField('Street')
    house_num=StringField('House Number')
    appartment_num=IntegerField('Appartment Number')

    submit=SubmitField('Create event')




