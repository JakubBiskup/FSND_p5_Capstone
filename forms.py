from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, SubmitField
from wtforms.validators import DataRequired, URL

class GameForm(Form):
    title=StringField('Title', validators=[DataRequired()])
    link=StringField('Link', validators=[URL()])
    submit=SubmitField('Add game to your collection')
