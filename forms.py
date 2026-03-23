from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, TextAreaField,
                     SelectField, SubmitField)
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit   = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(3, 80)])
    email    = StringField('Email',
                           validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(6)])
    confirm  = PasswordField('Confirm Password',
                             validators=[DataRequired(),
                                         EqualTo('password')])
    submit   = SubmitField('Register')


class DeviceForm(FlaskForm):
    name        = StringField('Device Name',
                              validators=[DataRequired(), Length(1, 100)])
    host        = StringField('IP / Domain',
                              validators=[DataRequired(), Length(1, 255)])
    description = StringField('Description', validators=[Optional(), Length(max=255)])
    submit      = SubmitField('Add Device')


class TicketForm(FlaskForm):
    title       = StringField('Title',
                              validators=[DataRequired(), Length(1, 200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    priority    = SelectField('Priority',
                              choices=[('Low','Low'), ('Medium','Medium'),
                                       ('High','High'), ('Critical','Critical')],
                              default='Medium')
    device_id   = SelectField('Related Device (optional)',
                              coerce=int, validators=[Optional()])
    submit      = SubmitField('Submit Ticket')


class CommentForm(FlaskForm):
    comment = TextAreaField('Add Comment', validators=[DataRequired()])
    submit  = SubmitField('Post Comment')


class UpdateTicketForm(FlaskForm):
    status  = SelectField('Status',
                          choices=[('Open','Open'),
                                   ('In Progress','In Progress'),
                                   ('Closed','Closed')])
    submit  = SubmitField('Update Status')
