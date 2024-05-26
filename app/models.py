from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime, timedelta
from flask_login import UserMixin
from app import login
import random
from sqlalchemy import event
from sqlalchemy.schema import DDL
import pytz


class User(UserMixin, db.Model):
    """
    A class used to represent a User.

    Attributes
    ----------
    id : int
        unique identifier for the user
    first_name : str
        first name of the user
    last_name : str
        last name of the user
    email : str
        email address of the user
    password_hashed : str
        hashed password of the user
    orders : relationship
        relationship to Order
    role : str
        role of the user (default is 'user')

    Methods
    -------
    set_password(password)
        Sets the user's password to a hashed password.
    check_password(password)
        Checks if the provided password matches the stored hashed password.
    """

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, nullable=False)
    last_name = db.Column(db.String(64), index=True, nullable=False)
    email = db.Column(db.String(128), unique=True, index=True, nullable=False)
    password_hashed = db.Column(db.String(200), nullable=False)
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    role = db.Column(db.String(64), default='user')

    def set_password(self, password):
        """
        Sets the user's password to a hashed password.

        Parameters
        ----------
        password : str
            The password to be hashed and set for the user.
        """
        self.password_hashed = generate_password_hash(password)

    def check_password(self, password):
        """
        Checks if the provided password matches the stored hashed password.

        Parameters
        ----------
        password : str
            The password to be checked.

        Returns
        -------
        bool
            True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hashed, password)

    def __repr__(self):
        """
        Provides a string representation of the user.

        Returns
        -------
        str
            String representation of the user.
        """
        return '<User {}, {}, {}, {}>'.format(self.first_name, self.last_name, self.email, self.password_hashed)


class Order(db.Model):
    """
    A class used to represent an Order.

    Attributes
    ----------
    id : int
        unique identifier for the order
    place_start : str
        starting place of the order
    place_end : str
        ending place of the order
    price : str
        price of the order
    order_time : datetime
        time when the order was placed
    order_taked : datetime
        time when the order was taken
    order_finished : datetime
        time when the order was finished
    user_id : int
        foreign key to the user
    driver_id : int
        foreign key to the driver
    driver : relationship
        relationship to Driver
    score : int
        score of the order

    Methods
    -------
    set_price(start, end)
        Sets the price of the order.
    set_order_time()
        Sets the time the order was placed.
    set_order_taked_time()
        Sets the time the order was taken.
    set_order_finished_time()
        Sets the time the order was finished.
    """

    id = db.Column(db.Integer, primary_key=True)
    place_start = db.Column(db.String(140), nullable=False)
    place_end = db.Column(db.String(140), nullable=False)
    price = db.Column(db.String(140), nullable=False)
    order_time = db.Column(db.DateTime, index=True, nullable=True)
    order_taked = db.Column(db.DateTime, index=True, nullable=True)
    order_finished = db.Column(db.DateTime, index=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=True)
    driver = db.relationship('Driver', back_populates='orders')
    score = db.Column(db.Integer, default=0)

    def __repr__(self):
        """
        Provides a string representation of the order.

        Returns
        -------
        str
            String representation of the order.
        """
        return '<Order: start - {}, finish - {}, price - {}, time - {}>'.format(self.place_start, self.place_end, self.price, self.order_time)

    def set_price(self, start, end):
        """
        Sets the price of the order.

        Parameters
        ----------
        start : str
            The starting place of the order.
        end : str
            The ending place of the order.
        """
        self.price = random.randint(1, 200)

    def set_order_time(self):
        """
        Sets the time the order was placed.
        """
        self.order_time = datetime.now(pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
    
    def set_order_taked_time(self):
        """
        Sets the time the order was taken.
        """
        self.order_taked = datetime.now(pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))

    def set_order_finished_time(self):
        """
        Sets the time the order was finished.
        """
        self.order_finished = datetime.now(pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))


@login.user_loader
def load_user(id):
    """
    Loads the user or driver based on the provided ID.

    Parameters
    ----------
    id : int
        The ID of the user or driver to be loaded.

    Returns
    -------
    User or Driver
        The user or driver object.
    """
    driver = Driver.query.get(int(id))
    if driver:
        return driver
    return User.query.get(int(id))


class Driver(UserMixin, db.Model):
    """
    A class used to represent a Driver.

    Attributes
    ----------
    id : int
        unique identifier for the driver
    first_name : str
        first name of the driver
    last_name : str
        last name of the driver
    middle_name : str
        middle name of the driver
    email : str
        email address of the driver
    car_model : str
        car model of the driver
    license_plate : str
        license plate of the driver's car
    password_hashed : str
        hashed password of the driver
    orders : relationship
        relationship to Order
    role : str
        role of the driver (default is 'driver')
    status : str
        status of the driver (default is 'inactive')
    number_of_ratings : int
        number of ratings the driver has received
    rating : float
        rating of the driver

    Methods
    -------
    update_rating(score)
        Updates the driver's rating based on a new score.
    change_status()
        Changes the status of the driver between 'inactive' and 'active'.
    set_password(password)
        Sets the driver's password to a hashed password.
    check_password(password)
        Checks if the provided password matches the stored hashed password.
    get_last_order()
        Returns the last order taken by the driver.
    """

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, nullable=False)
    last_name = db.Column(db.String(64), index=True, nullable=False)
    middle_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(128), unique=True, index=True, nullable=False)
    car_model = db.Column(db.String(64), index=True, nullable=False)
    license_plate = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hashed = db.Column(db.String(200), nullable=False)
    orders = db.relationship('Order', backref='driver', lazy='dynamic')
    role = db.Column(db.String(20), default='driver')
    status = db.Column(db.String(20), default='inactive', nullable=False)
    number_of_ratings = db.Column(db.Integer, default=0, nullable=False)
    rating = db.Column(db.Float, default=0.0, nullable=False)
    orders = db.relationship('Order', back_populates='driver')


    def update_rating(self, score):
        """
        Updates the driver's rating based on a new score.

        Parameters
        ----------
        score : int
            The score to be used for updating the rating.
        """
        self.rating = (self.number_of_ratings * self.rating + score) / (self.number_of_ratings + 1)
        self.number_of_ratings += 1

    def change_status(self):
        """
        Changes the status of the driver between 'inactive' and 'active'.
        """
        if self.status == 'inactive':
            self.status = 'active'
        else:
            self.status = 'inactive'

    def set_password(self, password):
        """
        Sets the driver's password to a hashed password.

        Parameters
        ----------
        password : str
            The password to be hashed and set for the driver.
        """
        self.password_hashed = generate_password_hash(password)

    def check_password(self, password):
        """
        Checks if the provided password matches the stored hashed password.

        Parameters
        ----------
        password : str
            The password to be checked.

        Returns
        -------
        bool
            True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hashed, password)

    def get_last_order(self):
        """
        Returns the last order taken by the driver.

        Returns
        -------
        Order
            The last order taken by the driver.
        """
        return Order.query.filter_by(driver_id=self.id).order_by(Order.order_time.desc()).first()

    def __repr__(self):
        """
        Provides a string representation of the driver.

        Returns
        -------
        str
            String representation of the driver.
        """
        return '<Driver {}, {}, {}, {}, {}>'.format(self.first_name, self.last_name, self.middle_name, self.email, self.password_hashed)