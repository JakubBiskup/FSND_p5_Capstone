from flask_wtf import Form
from wtforms import (IntegerField,
                     StringField,
                     SelectField,
                     SelectMultipleField,
                     BooleanField,
                     SubmitField)
from wtforms.validators import DataRequired, URL
from wtforms.fields.html5 import DateTimeField
from wtforms.widgets import TextArea


class GameForm(Form):
    title = StringField('Title')
    link = StringField('Link', validators=[URL()])
    game = SelectField('Game', choices=[], validators=[DataRequired()])
    submit = SubmitField('Save')


class MemberForm(Form):
    username = StringField('Username')
    img_link = StringField('Profile image link', validators=[URL()])
    description = StringField('Description', widget=TextArea())

    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    phone = StringField('Phone')
    email = StringField('E-mail')

    country = StringField('Country')
    city = StringField('City')
    street = StringField('Street')
    house_num = StringField('House Number')
    appartment_num = StringField('Appartment Number')

    submit = SubmitField('Save and apply')


class EventForm(Form):
    name = StringField('Event name', validators=[DataRequired()])
    time = DateTimeField(
        'Time',
        format='%Y-%m-%d %H:%M',
        validators=[
            DataRequired()])
    location = SelectField('Location', choices=[], validators=[DataRequired()])
    max_players = IntegerField(
        'Players max number', validators=[
            DataRequired()])
    games = SelectMultipleField(
        'Games (ctrl+click to choose multiple)',
        choices=[])
    description = StringField('Description', widget=TextArea())

    location_name = StringField('Name of the new location')
    country = StringField('Country')
    city = StringField('City')
    street = StringField('Street')
    house_num = StringField('House Number')
    appartment_num = IntegerField('Appartment Number')

    submit = SubmitField('Create event')


class ClubForm(Form):
    name = StringField('Club name')
    img_link = StringField('Link to image on homepage')
    h1 = StringField('Header')
    welcoming_text = StringField(
        'Welcoming text or club description',
        widget=TextArea())

    submit = SubmitField('Save and apply changes')


class EditEventForm(Form):
    name = StringField('Event name')
    time = DateTimeField('Time', format='%Y-%m-%d %H:%M')
    location = SelectField('Location', choices=[])
    max_players = IntegerField('Players max number')
    games = SelectMultipleField(
        'Games (ctrl+click to choose multiple)',
        choices=[])
    description = StringField('Description', widget=TextArea())

    location_name = StringField('Name of the new location')
    country = StringField('Country')
    city = StringField('City')
    street = StringField('Street')
    house_num = StringField('House Number')
    appartment_num = IntegerField('Appartment Number')

    submit = SubmitField('Edit event')
