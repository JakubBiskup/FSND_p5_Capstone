from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, SubmitField
from wtforms.validators import DataRequired, URL


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


