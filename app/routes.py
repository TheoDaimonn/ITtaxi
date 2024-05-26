from urllib import request

from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, OrderForm, DriverRegistrationForm, TakeOrderForm, RateOrderForm, UpdateProfileForm, ChangePasswordForm
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
    """
    Route to render the choice of login page.

    Returns
    -------
    Rendered HTML
        Rendered HTML template for the choice of login page.
    """
    return render_template('choice_of_login.html')


@app.route('/index')
@login_required('user')
def index():
    """
    Route to render the index page for a user.

    Returns
    -------
    Rendered HTML
        Rendered HTML template for the index page with user's active orders.
    """
    orders = Order.query.filter(
        Order.user_id == current_user.id,
        db.or_(Order.order_taked.is_(None), Order.order_finished.is_(None))
    ).all()
    return render_template('index.html', orders=orders)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Route to handle user login.

    Returns
    -------
    Rendered HTML
        Rendered HTML template for the login page or a redirect to the index page.
    """
    if current_user.is_authenticated:
        if current_user.role == 'user':
            return redirect(url_for('index'))
        else:
            logout_user()
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password!', 'danger')
            return redirect(url_for('login'))
        logout_user()
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout', methods=['POST'])
def logout():
    """
    Route to handle user logout.

    Returns
    -------
    Rendered HTML
        Redirect to the choice page.
    """
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('choice'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Route to handle user registration.

    Returns
    -------
    Rendered HTML
        Rendered HTML template for the registration page or a redirect to the login page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
            flash('Thanks for registering!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your request.', 'danger')
            print(f"Error: {e}")
    elif form.errors:
        flash('Please fill out all fields correctly.', 'danger')
    return render_template('register.html', title='Register', form=form)


@app.route('/order', methods=['GET', 'POST'])
@login_required('user')
def order():
    """
    Route to handle creating a new order.

    Returns
    -------
    Rendered HTML
        Rendered HTML template for creating a new order or a redirect to the index page.
    """
    form = OrderForm()
    if form.validate_on_submit():
        # Проверка количества активных заказов пользователя
        active_orders_count = Order.query.filter(
            Order.user_id == current_user.id,
            Order.order_taked.is_(None)
        ).count()

        if active_orders_count >= 5:
            flash('You have reached the limit of active orders.', 'danger')
            return redirect(url_for('order'))

        # Проверка наличия свободных водителей
        available_driver = Driver.query.filter_by(status='inactive').first()
        if available_driver is None:
            flash('No available drivers. Please wait.', 'danger')
            return redirect(url_for('order'))

        # Создание заказа
        new_order = Order(
            place_start=form.place_start.data,
            place_end=form.place_end.data,
            user_id=current_user.id
        )
        new_order.set_price(form.place_start.data, form.place_end.data)
        new_order.set_order_time()
        db.session.add(new_order)
        try:
            db.session.commit()
            flash('Your order has been created successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your request.', 'danger')
            print(f"Error: {e}")

        return redirect(url_for('index'))
    return render_template('new-order.html', title='New Order', form=form)


@app.route('/driver_register', methods=['GET', 'POST'])
def driver_register():
    """
    Route to handle driver registration.

    Returns
    -------
    Rendered HTML
        Rendered HTML template for the driver registration page or a redirect to the driver login page.
    """
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
        try:
            db.session.commit()
            flash('Thanks for registering!', 'success')
            return redirect(url_for('driver_login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your request.', 'danger')
            print(f"Error: {e}")        
    elif form.errors:
        flash('Please fill out all fields correctly.', 'danger')
    return render_template('driver_register.html', title='Register', form=form)


@app.route('/driver_login', methods=['GET', 'POST'])
def driver_login():
    """
    Route to handle driver login.

    Returns
    -------
    Rendered HTML
        Rendered HTML template for the driver login page or a redirect to the driver main page.
    """
    if current_user.is_authenticated:
        if current_user.role == 'driver':
            return redirect("driver_main")
        else:
            logout_user()
    form = LoginForm()
    if form.validate_on_submit():
        driver = Driver.query.filter_by(email=form.email.data).first()
        if driver is None or not driver.check_password(form.password.data):
            flash('Invalid email or password!', 'danger')
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
    """
    Route to render the main page for a driver.

    Returns
    -------
    Rendered HTML
        Rendered HTML template for the driver's main page.
    """
    active_order = Order.query.filter_by(driver_id=current_user.id, order_finished=None).first()
    available_orders = []
    if not active_order:
        available_orders = Order.query.filter_by(driver_id=None).all()
    return render_template('driver_main.html', active_order=active_order, available_orders=available_orders)


@app.route('/history_of_driver')
@login_required('driver')
def history_of_driver():
    """
    Route to render the driver's order history page.

    Returns
    -------
    Rendered HTML
        Rendered HTML template for the driver's order history page.
    """
    user_orders = Order.query.filter(Order.driver_id == current_user.id, Order.order_finished.isnot(None)).all()
    return render_template('history_of_driver.html', title='History', orders=user_orders)


@app.route('/complete_order/<int:order_id>', methods=['POST'])
@login_required('driver')
def complete_order(order_id):
    """
    Route to mark an order as completed by the driver.

    Parameters
    ----------
    order_id : int
        ID of the order to be completed.

    Returns
    -------
    Rendered HTML
        Redirect to the driver's main page.
    """
    order = Order.query.get_or_404(order_id)
    if order.driver_id != current_user.id:
        flash('You cannot complete this order.', 'danger')
        return redirect(url_for('driver_main'))
    
    order.set_order_finished_time()
    current_user.status = 'inactive'
    try:
        db.session.commit()
        flash('Order completed.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while processing your request.', 'danger')
        print(f"Error: {e}")                
    return redirect(url_for('driver_main'))


@app.route('/history_of_user_orders')
@login_required('user')
def history_of_user_orders():
    """
    Route to render the user's order history page.

    Returns
    -------
    Rendered HTML
        Rendered HTML template for the user's order history page.
    """
    orders = Order.query.filter_by(user_id=current_user.id).filter(Order.order_finished.isnot(None)).all()
    return render_template('history_of_user_orders.html', title='История заказов', orders=orders)


@app.route('/rate_order/<int:order_id>', methods=['GET', 'POST'])
@login_required('user')
def rate_order(order_id):
    """
    Route to rate a completed order.

    Parameters
    ----------
    order_id : int
        ID of the order to be rated.

    Returns
    -------
    Rendered HTML
        Rendered HTML template for rating the order or a redirect to the user's order history page.
    """
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
            driver.update_rating(form.rating.data)
            order.score = form.rating.data
            try:
                db.session.commit()
                flash('Order has been rated.', 'success')
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while processing your request.', 'danger')
                print(f"Error: {e}")      
        else:
            flash('Driver not found for this order.', 'danger')
        return redirect(url_for('history_of_user_orders'))
    return render_template('rate_order.html', title='Rate Order', form=form, order=order)


@app.route('/profile', methods=['GET', 'POST'])
@login_required('user')
def profile():
    """
    Route to render and update the user's profile.

    Returns
    -------
    Rendered HTML
        Rendered HTML template for the user's profile page.
    """
    update_form = UpdateProfileForm()
    change_password_form = ChangePasswordForm()

    if update_form.validate_on_submit() and update_form.submit.data:
        current_user.first_name = update_form.first_name.data
        current_user.last_name = update_form.last_name.data
        try:
            db.session.commit()
            flash('Name updated successfully', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your request.', 'danger')
            print(f"Error: {e}")

    if change_password_form.validate_on_submit() and change_password_form.submit.data:
        if not current_user.check_password(change_password_form.old_password.data):
            flash('Incorrect old password', 'danger')
            return render_template('profile.html', user=current_user, trip_count=Order.query.filter(Order.user_id == current_user.id, Order.order_finished.isnot(None)).count(), update_form=update_form, change_password_form=change_password_form)
        else:
            current_user.set_password(change_password_form.new_password.data)
            try:
                db.session.commit()
                flash('Password changed successfully', 'success')
                return redirect(url_for('profile'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while processing your request.', 'danger')
                print(f"Error: {e}")

    trip_count = Order.query.filter(Order.user_id == current_user.id, Order.order_finished.isnot(None)).count()
    update_form.first_name.data = current_user.first_name
    update_form.last_name.data = current_user.last_name

    return render_template('profile.html', user=current_user, trip_count=trip_count, update_form=update_form, change_password_form=change_password_form)


@app.route('/update_profile', methods=['POST'])
def update_profile():
    """
    Route to update the user's profile information.

    Returns
    -------
    Rendered HTML
        Redirect to the appropriate profile page.
    """
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        try:
            db.session.commit()
            flash('Profile updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your request.', 'danger')
            print(f"Error: {e}")
    if current_user.role == 'user':
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('driver_profile'))


@app.route('/change_password', methods=['POST'])
def change_password():
    """
    Route to change the user's password.

    Returns
    -------
    Rendered HTML
        Redirect to the appropriate profile page.
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('Incorrect old password.', 'danger')
            if current_user.role == 'user':
                return redirect(url_for('profile'))
            else:
                return redirect(url_for('driver_profile'))
        current_user.set_password(form.new_password.data)
        try:
            db.session.commit()
            flash('Password changed successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your request.', 'danger')
            print(f"Error: {e}")
    if current_user.role == 'user':
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('driver_profile'))


@app.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required('user')
def cancel_order(order_id):
    """
    Route to cancel an order.

    Parameters
    ----------
    order_id : int
        ID of the order to be canceled.

    Returns
    -------
    Rendered HTML
        Redirect to the index page.
    """
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('You do not have permission to cancel this order.', 'danger')
        return redirect(url_for('index'))
    if order.order_taked:
        flash('This order has already been taken and cannot be canceled.', 'danger')
        return redirect(url_for('index'))

    db.session.delete(order)
    try:
        db.session.commit()
        flash('Order canceled successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while processing your request.', 'danger')
        print(f"Error: {e}")
    return redirect(url_for('index'))


@app.route('/driver_profile', methods=['GET', 'POST'])
@login_required('driver')
def driver_profile():
    """
    Route to render and update the driver's profile.

    Returns
    -------
    Rendered HTML
        Rendered HTML template for the driver's profile page.
    """
    update_form = UpdateProfileForm()
    change_password_form = ChangePasswordForm()

    if update_form.validate_on_submit() and update_form.submit.data:
        current_user.first_name = update_form.first_name.data
        current_user.last_name = update_form.last_name.data
        current_user.middle_name = update_form.middle_name.data
        try:
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('driver_profile'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your request.', 'danger')
            print(f"Error: {e}")

    if change_password_form.validate_on_submit() and change_password_form.submit.data:
        if not current_user.check_password(change_password_form.old_password.data):
            flash('Incorrect old password', 'danger')
            return render_template('driver_profile.html', user=current_user, trip_count=Order.query.filter(Order.driver_id == current_user.id, Order.order_finished.isnot(None)).count(), update_form=update_form, change_password_form=change_password_form)
        else:
            current_user.set_password(change_password_form.new_password.data)
            try:
                db.session.commit()
                flash('Password changed successfully', 'success')
                return redirect(url_for('driver_profile'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while processing your request.', 'danger')
                print(f"Error: {e}")

    trip_count = Order.query.filter(Order.driver_id == current_user.id, Order.order_finished.isnot(None)).count()
    update_form.first_name.data = current_user.first_name
    update_form.last_name.data = current_user.last_name
    update_form.middle_name.data = current_user.middle_name

    return render_template('driver_profile.html', user=current_user, trip_count=trip_count, update_form=update_form, change_password_form=change_password_form)


@app.route('/take_order/<int:order_id>', methods=['POST'])
@login_required('driver')
def take_order(order_id):
    """
    Route to take an available order.

    Parameters
    ----------
    order_id : int
        ID of the order to be taken.

    Returns
    -------
    Rendered HTML
        Redirect to the driver's main page.
    """
    order = Order.query.get_or_404(order_id)

    # Проверка, не занят ли водитель уже заказом
    active_order = Order.query.filter_by(driver_id=current_user.id, order_finished=None).first()
    if active_order:
        flash("You already have an active order.", 'warning')
        return redirect(url_for('driver_main'))

    if order.driver_id is not None:
        flash('This order has already been taken.', 'warning')
        return redirect(url_for('driver_main'))

    current_user.status = 'active'
    order.driver_id = current_user.id
    order.set_order_taked_time()
    try:
        db.session.commit()
        flash('Order taken successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while processing your request.', 'danger')
        print(f"Error: {e}")
    return redirect(url_for('driver_main'))

