from flask import Flask, render_template, redirect, url_for
from app import app
from app.forms import RegistrationForm, LoginForm
from flask_login import login_user, logout_user, current_user

from app.models import User


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        Email = form.Email.data
        password = form.password.data

        # Создание объекта пользователя

        return redirect('/')  # Перенаправление на главную страницу
    return render_template('regs.html', form=form)


@app.route('/')
def index():
    return render_template("hi!.html")


@app.route('/login')
def login_page():
    if current_user.is_authenticated:
        return redirect((url_for('index')))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form)
    return render_template("log-in.html")


@app.route('/register_page')
def register_page():
    form = RegistrationForm()
    return render_template("regs.html", form=form)
