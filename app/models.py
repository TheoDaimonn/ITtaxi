from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime
from flask_login import UserMixin
from app import login
import random
from sqlalchemy import event
from sqlalchemy.schema import DDL


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, nullable=False)
    last_name= db.Column(db.String(64), index=True, nullable=False)
    email = db.Column(db.String(128), unique=True, index=True, nullable=False)
    password_hashed = db.Column(db.String(200), nullable=False)
    first_name_hashed = db.Column(db.String(200))
    last_name_hashed = db.Column(db.String(200))
    email_hashed = db.Column(db.String(200))
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    role = db.Column(db.String(64), default='user')

    def set_password(self, password):
        self.password_hashed = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hashed, password)
    
    def set_first_name(self, first_name):
        self.first_name_hashed = generate_password_hash(first_name)

    def set_last_name(self, last_name):
        self.last_name_hashed = generate_password_hash(last_name)

    def set_email(self, email):
        self.email_hashed = generate_password_hash(email)

    def check_first_name(self, first_name):
        return check_password_hash(self.first_name_hashed, first_name)

    def check_last_name(self, last_name):
        return check_password_hash(self.last_name_hashed, last_name)
    
    def check_email(self, email):
        return check_password_hash(self.email_hashed, email)

    def __repr__(self):
        return '<User {}, {}, {}, {}>'.format(self.first_name, self.last_name, self.email, self.password_hashed)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place_start = db.Column(db.String(140), nullable=False)
    place_end = db.Column(db.String(140), nullable=False)
    price = db.Column(db.String(140), nullable=False)
    order_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    order_taked = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=True)

    def __repr__(self):
        return '<Order: start - {}, finish - {}, price - {}, time - {}>'.format(self.place_start, self.place_end, self.price, self.order_time)

    def set_price(self, start, end):
        self.price = random.randint(1, 200)

    def set_order_time(self):
        self.order_time = datetime.now()


@login.user_loader
def load_user(id):
    driver = Driver.query.get(int(id))
    if driver:
        return driver
    return User.query.get(int(id))


class Driver(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, nullable=False)
    last_name = db.Column(db.String(64), index=True, nullable=False)
    middle_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(128), unique=True, index=True, nullable=False)
    car_model = db.Column(db.String(64), index=True, nullable=False)
    license_plate = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hashed = db.Column(db.String(200), nullable=False)
    first_name_hashed = db.Column(db.String(200))
    last_name_hashed = db.Column(db.String(200))
    middle_name_hashed = db.Column(db.String(200))
    email_hashed = db.Column(db.String(200))
    car_model_hashed = db.Column(db.String(200))
    license_plate_hashed = db.Column(db.String(200))

    orders = db.relationship('Order', backref='driver', lazy='dynamic')
    role = db.Column(db.String(20), default='driver')

    def set_password(self, password):
        self.password_hashed = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hashed, password)
    
    def set_first_name(self, first_name):
        self.first_name_hashed = generate_password_hash(first_name)

    def set_last_name(self, last_name):
        self.last_name_hashed = generate_password_hash(last_name)
    
    def set_middle_name(self, middle_name):
        self.middle_name_hashed = generate_password_hash(middle_name)

    def set_car_model(self, car_model):
        self.car_model_hashed = generate_password_hash(car_model)
    
    def set_license_plate(self, license_plate):
        self.license_plate_hashed = generate_password_hash(license_plate)

    def set_email(self, email):
        self.email_hashed = generate_password_hash(email)

    def check_first_name(self, first_name):
        return check_password_hash(self.first_name_hashed, first_name)

    def check_last_name(self, last_name):
        return check_password_hash(self.last_name_hashed, last_name)
    
    def check_email(self, email):
        return check_password_hash(self.email_hashed, email)
    
    def check_middle_name(self, middle_name):
        return check_password_hash(self.middle_name_hashed, middle_name)
    
    def check_car_model(self, car_model):
        return check_password_hash(self.car_model_hashed, car_model)
    
    def check_license_plate(self, license_plate):
        return check_password_hash(self.license_plate_hashed, license_plate)

    def __repr__(self):
        return '<Driver {}, {}, {}, {}, {}>'.format(self.first_name_hashed, self.last_name_hashed, \
                                                    self.middle_name_hashed, self.email_hashed, self.password_hashed)