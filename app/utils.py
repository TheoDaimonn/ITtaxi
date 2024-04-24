from flask_login import current_user
from functools import wraps
from flask import redirect, url_for, abort


def login_required(role):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('choice'))

            if current_user.role != role:
                print(f"Пользователь {current_user.email} имеет роль {current_user.role}, а ожидалось {role}")
                return abort(403)

            return func(*args, **kwargs)

        return decorated_view

    return wrapper

