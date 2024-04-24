from urllib import request

from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, OrderForm, DriverRegistrationForm
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Order, Driver
from werkzeug.urls import url_parse
from app.utils import login_required


@app.route('/')
def choice():
    return render_template('choice.html')


@app.route('/index')
@login_required(('user',))
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password!')
            return redirect(url_for('login'))
        logout_user()
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html',  title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/order', methods=['GET', 'POST'])
@login_required(('user',))
def order():
    form = OrderForm()
    if form.validate_on_submit():
        order = Order(place_start=form.place_start.data, place_end=form.place_end.data, user_id=current_user.id)
        order.set_order_time()
        order.set_price(form.place_start.data, form.place_end.data)
        db.session.add(order)
        db.session.commit()
        flash('Thanks for your order, Taxi is on the way!')
        return redirect(url_for('index'))
    return render_template('order.html', title='Order', form=form)


@app.route('/driver_register', methods=['GET', 'POST'])
def driver_register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = DriverRegistrationForm()
    if form.validate_on_submit():
        driver = Driver(first_name=form.first_name.data, last_name=form.last_name.data, middle_name=form.middle_name.data, car_model=form.car_model.data, license_plate=form.license_plate.data, email=form.email.data)
        driver.set_password(form.password.data)
        db.session.add(driver)
        db.session.commit()
        flash('Thanks for registering!')
        return redirect(url_for('login'))
    return render_template('driver_register.html', title='Register', form=form)


@app.route('/driver_login', methods=['GET', 'POST'])
def driver_login():
    if current_user.is_authenticated:
        return redirect("driver_main")
    form = LoginForm()
    if form.validate_on_submit():
        driver = Driver.query.filter_by(email=form.email.data).first()
        if driver is None or not driver.check_password(form.password.data):
            flash('Invalid email or password!')
            return redirect(url_for('driver_login'))
        logout_user()
        login_user(driver, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('driver_main')
        return redirect(next_page)
    return render_template('driver_login.html', title='Sign In', form=form)


@app.route('/driver_main')
@login_required('driver')
def driver_main():
    return render_template('driver_main.html', title='Home')
