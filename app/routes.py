from urllib import request

from flask import Flask, render_template, redirect, url_for, flash
from app import app
from app.forms import RegistrationForm, LoginForm
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("hi!.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data)
        first_name = form.first_name.data
        last_name = form.last_name.data
        Email = form.Email.data
        password = form.password.data

        return redirect('/index')  # Перенаправление на главную страницу
    return render_template('regs.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect((url_for('index')))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template("login.html", title='Sign In', form=form)


@app.route('/success!')
@login_required
def success():
    return redirect(url_for('index'))


@app.route('/register_page')
def register_page():
    form = RegistrationForm()
    return render_template("regs.html", form=form)


@app.route('/log_out')
def logout_page():
    logout_user()
    return redirect(url_for('login'))