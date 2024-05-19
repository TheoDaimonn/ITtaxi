from urllib import request

from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, OrderForm, DriverRegistrationForm, TakeOrderForm
from flask_login import login_user, logout_user, current_user
from app.models import User, Order, Driver
from app.utils import login_required, encrypt_data, decrypt_data
from sqlalchemy import func
from datetime import datetime

@app.route('/')
def choice():
    return render_template('choice.html')

@app.route('/index')
@login_required('user')
def index():
    user_orders = current_user.orders.all()
    return render_template('index.html', title='Home', orders=user_orders)

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
        if not next_page:
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

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
        user = User(
            first_name=encrypt_data(form.first_name.data),
            last_name=encrypt_data(form.last_name.data),
            email=encrypt_data(form.email.data)
        )
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
        order = Order(
            place_start=encrypt_data(form.place_start.data),
            place_end=encrypt_data(form.place_end.data),
            user_id=current_user.id
        )
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
        driver = Driver(
            first_name=encrypt_data(form.first_name.data),
            last_name=encrypt_data(form.last_name.data),
            middle_name=encrypt_data(form.middle_name.data),
            car_model=encrypt_data(form.car_model.data),
            license_plate=encrypt_data(form.license_plate.data),
            email=encrypt_data(form.email.data)
        )
        driver.set_password(form.password.data)
        max_id = db.session.query(func.max(Driver.id)).scalar() or 0
        new_id = 1 + max_id
        driver.id = new_id
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
        driver = Driver.query.filter_by(email=encrypt_data(form.email.data)).first()
        if driver is None or not driver.check_password(form.password.data):
            flash('Invalid email or password!')
            return redirect(url_for('driver_login'))
        if driver is None or not driver.check_email(encrypt_data(form.email.data)):
            flash('Invalid email or password!')
            return redirect(url_for('driver_login'))
        logout_user()
        login_user(driver, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page:
            next_page = url_for('driver_main')
        return redirect(next_page)
    return render_template('driver_login.html', title='Sign In', form=form)

@app.route('/driver_main')
@login_required('driver')
def driver_main():
    user_orders = current_user.orders.all()
    return render_template('driver_main.html', title='Home', user_orders=user_orders)

@app.route('/orders')
@login_required('driver')
def show_orders():
    orders = Order.query.filter_by(driver_id=None).all()
    return render_template('choose-order.html', orders=orders)

@app.route('/take_order/<int:order_id>', methods=['POST'])
@login_required('driver')
def take_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.driver_id is not None:
        flash('This order has already been taken.', 'warning')
        return redirect(url_for('show_orders'))
    order.driver_id = current_user.id
    order.order_taked = datetime.utcnow()
    db.session.commit()
    flash('Order taken successfully!', 'success')
    return redirect(url_for('show_orders'))

@app.context_processor
def inject_user_data():
    if current_user.is_authenticated:
        if isinstance(current_user, User):
            first_name = decrypt_data(current_user.first_name)
            last_name = decrypt_data(current_user.last_name)
            email = decrypt_data(current_user.email)
            return {'user_first_name': first_name, 'user_last_name': last_name, 'user_email': email}
        elif isinstance(current_user, Driver):
            first_name = decrypt_data(current_user.first_name)
            last_name = decrypt_data(current_user.last_name)
            middle_name = decrypt_data(current_user.middle_name)
            car_model = decrypt_data(current_user.car_model)
            license_plate = decrypt_data(current_user.license_plate)
            email = decrypt_data(current_user.email)
            return {
                'driver_first_name': first_name,
                'driver_last_name': last_name,
                'driver_middle_name': middle_name,
                'driver_car_model': car_model,
                'driver_license_plate': license_plate,
                'driver_email': email
            }
    return {}








