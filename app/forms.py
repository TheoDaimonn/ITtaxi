from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange
from app.models import User, Driver, Order


class LoginForm(FlaskForm):
    """
    Form for user login.

    Attributes
    ----------
    email : StringField
        Email field for user login.
    password : PasswordField
        Password field for user login.
    remember_me : BooleanField
        Checkbox for remembering the user login session.
    submit : SubmitField
        Submit button for the form.
    """
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """
    Form for user registration.

    Attributes
    ----------
    first_name : StringField
        First name field for user registration.
    last_name : StringField
        Last name field for user registration.
    email : StringField
        Email field for user registration.
    password : PasswordField
        Password field for user registration.
    password_2 : PasswordField
        Password confirmation field for user registration.
    submit : SubmitField
        Submit button for the form.

    Methods
    -------
    validate_email(self, email):
        Validates if the email is already in use.
    """
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        """
        Validate if the email is already in use.

        Parameters
        ----------
        email : str
            The email to be validated.

        Raises
        ------
        ValidationError
            If the email is already in use.
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email is currently used')


class OrderForm(FlaskForm):
    """
    Form for placing an order.

    Attributes
    ----------
    place_start : StringField
        Field for the start place of the order.
    place_end : StringField
        Field for the end place of the order.
    submit : SubmitField
        Submit button for the form.
    """
    place_start = StringField('Start Place', validators=[DataRequired()])
    place_end = StringField('Finish place', validators=[DataRequired()])
    submit = SubmitField('order')


class DriverRegistrationForm(FlaskForm):
    """
    Form for driver registration.

    Attributes
    ----------
    first_name : StringField
        First name field for driver registration.
    last_name : StringField
        Last name field for driver registration.
    middle_name : StringField
        Middle name field for driver registration.
    email : StringField
        Email field for driver registration.
    password : PasswordField
        Password field for driver registration.
    password_2 : PasswordField
        Password confirmation field for driver registration.
    car_model : StringField
        Car model field for driver registration.
    license_plate : StringField
        License plate field for driver registration.
    submit : SubmitField
        Submit button for the form.

    Methods
    -------
    validate_email(self, email):
        Validates if the email is already in use.
    """
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
        """
        Validate if the email is already in use.

        Parameters
        ----------
        email : str
            The email to be validated.

        Raises
        ------
        ValidationError
            If the email is already in use.
        """
        driver = Driver.query.filter_by(email=email.data).first()
        if driver is not None:
            raise ValidationError("This email is currently used")


class TakeOrderForm(FlaskForm):
    """
    Form for taking an order.

    Attributes
    ----------
    submit : SubmitField
        Submit button for the form.
    """
    submit = SubmitField('Take Order')


class RateOrderForm(FlaskForm):
    """
    Form for rating an order.

    Attributes
    ----------
    rating : IntegerField
        Rating field for the order.
    submit : SubmitField
        Submit button for the form.
    """
    rating = IntegerField('Rating', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Submit')


class UpdateProfileForm(FlaskForm):
    """
    Form for updating user profile.

    Attributes
    ----------
    first_name : StringField
        First name field for updating profile.
    last_name : StringField
        Last name field for updating profile.
    middle_name : StringField
        Middle name field for updating profile.
    submit : SubmitField
        Submit button for the form.
    """
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    middle_name = StringField('Middle Name')
    submit = SubmitField('Update Name')


class ChangePasswordForm(FlaskForm):
    """
    Form for changing user password.

    Attributes
    ----------
    old_password : PasswordField
        Field for the old password.
    new_password : PasswordField
        Field for the new password.
    new_password2 : PasswordField
        Field for confirming the new password.
    submit : SubmitField
        Submit button for the form.
    """
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    new_password2 = PasswordField('Repeat New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')