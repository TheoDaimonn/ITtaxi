from urllib import request

from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, OrderForm, DriverRegistrationForm, TakeOrderForm, RateOrderForm
from flask_login import login_user, logout_user, current_user
from app.models import User, Order, Driver
from werkzeug.urls import url_parse
from app.utils import login_required
from sqlalchemy import func
from datetime import datetime, timedelta
import pytz


@app.route('/')
@app.route('/choice')
def choice():
    return render_template('choice_of_login.html')


@app.route('/index')
@app.route('/profile')
@login_required('user')
def index():

    user_orders = current_user.orders.all()
    return render_template('index.html', title='Home', orders=user_orders)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'user':
            return redirect(url_for('index'))
        else:
            logout_user()
    
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
    return redirect(url_for('choice'))


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
@login_required('user')
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
    return render_template('new-order.html', title='Order', form=form)


@app.route('/driver_register', methods=['GET', 'POST'])
def driver_register():
    if current_user.is_authenticated:
        return redirect(url_for('driver_main'))
    form = DriverRegistrationForm()
    if form.validate_on_submit():
        driver = Driver(first_name=form.first_name.data, last_name=form.last_name.data, middle_name=form.middle_name.data, car_model=form.car_model.data, license_plate=form.license_plate.data, email=form.email.data)
        driver.set_password(form.password.data)
        max_id = db.session.query(func.max(Driver.id)).scalar() or 0
        new_id = 1 + max_id
        driver.id = new_id
        db.session.add(driver)
        db.session.commit()
        flash('Thanks for registering!')
        return redirect(url_for('driver_login'))
    return render_template('driver_register.html', title='Register', form=form)


@app.route('/driver_login', methods=['GET', 'POST'])
def driver_login():
    if current_user.is_authenticated:
        if current_user.role == 'driver':
            return redirect("driver_main")
        else:
            logout_user()
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
    return render_template('NEW_driver_login.html', title='Sign In', form=form)


@app.route('/driver_main')
@login_required('driver')
def driver_main():
    user_orders = current_user.orders.all()
    return render_template('driver_main.html', title='Home', user_orders=user_orders)


@app.route('/show_orders')
@login_required('driver')
def show_orders():
    orders = Order.query.filter_by(driver_id=None).all()
    return render_template('choose-order.html', orders=orders)


@app.route('/take_order/<int:order_id>', methods=['POST'])
@login_required('driver')
def take_order(order_id):
    order = Order.query.get_or_404(order_id)
    if current_user.status == "active":
        flash("You already have order", 'warning')
        return redirect(url_for('show_orders'))
    if order.driver_id is not None:
        flash('This order has already been taken.', 'warning')
        return redirect(url_for('show_orders'))
    current_user.change_status()
    order.driver_id = current_user.id
    order.set_order_taked_time()
    db.session.commit()
    flash('Order taken successfully!', 'success')
    return redirect(url_for('show_orders'))


@app.route('/history_of_driver')
@login_required('driver')
def history_of_driver():
    user_orders = current_user.orders.all()
    return render_template('history_of_driver.html', title='History', orders=user_orders)


@app.route('/active_order')
@login_required('driver')
def active_order():
    order = current_user.get_last_order()
    status = current_user.status
    if status == 'inactive':
        return redirect(url_for('driver_main'))
    return render_template('active_order.html', title='Active Order', active_order=order)


@app.route('/complete_order/<int:order_id>', methods=['POST'])
@login_required('driver')
def complete_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.driver_id != current_user.id:
        flash('Вы не можете завершить этот заказ.', 'danger')
        return redirect(url_for('active_order'))
    order.set_order_finished_time()
    current_user.change_status()
    db.session.commit()
    flash('Заказ завершен.', 'success')
    return redirect(url_for('active_order'))


@app.route('/history_of_user_orders')
@login_required('user')
def history_of_user_orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('history_of_user_orders.html', title='История заказов', orders=orders)


@app.route('/rate_order/<int:order_id>', methods=['GET', 'POST'])
@login_required('user')
def rate_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('You cannot rate this order.', 'danger')
        return redirect(url_for('history_of_user_orders'))
    if order.score > 0:
        return redirect(url_for('index'))
    form = RateOrderForm()
    if form.validate_on_submit():
        driver = Driver.query.get(order.driver_id)
        if driver:
            driver.rating = (driver.rating * driver.number_of_ratings + form.rating.data) / (driver.number_of_ratings + 1)
            driver.number_of_ratings += 1
            order.score = form.rating.data
            db.session.commit()
            flash('Order has been rated.', 'success')
        else:
            flash('Driver not found for this order.', 'danger')
        return redirect(url_for('history_of_user_orders'))
    return render_template('rate_order.html', title='Rate Order', form=form, order=order)