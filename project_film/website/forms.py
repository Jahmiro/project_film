from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from website.models import User, Post, Acteur, Regisseur, Film, Rol

class RegistrationForm(FlaskForm):
    name = StringField("Naam", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Wachtwoord", validators=[DataRequired(), Length(min=7, max=60)]
    )
    confirm_password = PasswordField(
        "Herhaal wachtwoord",
        validators=[DataRequired(), Length(min=7, max=60), EqualTo("password")],
    )
    submit = SubmitField("Maak account")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is al in gebruik')


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Wachtwoord", validators=[DataRequired(), Length(min=7, max=60)]
    )
    remember = BooleanField("Remember Me")
    submit = SubmitField("Mijn account")

class UpdateAccountForm(FlaskForm):
    name = StringField('Naam',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

titel = [
('Black Panther'),
('Guardians of the Galaxy Vol.2'),
('Avengers Infinity War'),
('Thor Ragnarok'),
('Captain America Civil War'),
('Ant-Man and the Wasp')]

class PostForm(FlaskForm):
    title = SelectField('Titel', choices=titel, validators=[DataRequired()])
    content = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField('Opmerking toevoegen')

class ActeurForm(FlaskForm):
    first_name = StringField('Voornaam', validators=[DataRequired()])
    last_name = StringField('Achternaam', validators=[DataRequired()])
    title = SelectField('Titel', choices=titel, validators=[DataRequired()])
    rol = StringField('Rol', validators=[DataRequired()]) 
    submit = SubmitField('Acteur toevoegen')

class RegisseurForm(FlaskForm):
    first_name = StringField('Voornaam', validators=[DataRequired()])
    last_name = StringField('Achternaam', validators=[DataRequired()])
    title = SelectField('Titel', choices=titel, validators=[DataRequired()])
    submit = SubmitField('Regisseur toevoegen')
