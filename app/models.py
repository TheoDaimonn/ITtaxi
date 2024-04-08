from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, nullable=False)
    last_name = db.Column(db.String(64), index=True, nullable=False)
    email = db.Column(db.String(128), unique=True, index=True, nullable=False)
    password_hashed = db.Column(db.String(200), nullable=False)
    orders = db.relationship('Order', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hashed = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hashed, password)

    def __repr__(self):
        return '<User {}, {}, {}>'.format(self.first_name, self.last_name, self.email)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place_start = db.Column(db.String(140), nullable=False)
    place_end = db.Column(db.String(140), nullable=False)
    price = db.Column(db.String(140), nullable=False)
    order_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#>>> from app import app, db
#>>> app_context = app.app_context()
#>>> app_context.push()

    def __repr__(self):
        return '<Order: start - {}, finish - {}, price - {}, time - {}>'.format(self.place_start, self.place_end, self.price, self.order_time)