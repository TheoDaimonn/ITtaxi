from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app.models import User, Driver


class LoginForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email is currently used')


class OrderForm(FlaskForm):
    place_start = StringField('Start Place', validators=[DataRequired()])
    place_end = StringField('Finish place', validators=[DataRequired()])
    submit = SubmitField('order')


class DriverRegistrationForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    middle_name = StringField("Middle Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password_2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    car_model = StringField("Car Model", validators=[DataRequired()])
    license_plate = StringField("Car Template", validators=[DataRequired()])

    submit = SubmitField("Register")

    def validate_email(self, email):
        driver = Driver.query.filter_by(email=email.data).first() #Обращаемся в таблицу водителей
        if driver is not None:
            raise ValidationError("This email is currently used")


class TakeOrderForm(FlaskForm):
    submit = SubmitField('Take Order')