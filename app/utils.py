from flask_login import current_user
from functools import wraps
from flask import redirect, url_for, abort


def login_required(role):
    """
    Decorator that checks if the current user is authenticated and has the specified role.

    Parameters
    ----------
    role : str
        The role required to access the decorated view.

    Returns
    -------
    function
        The decorated view function if the user is authenticated and has the correct role, otherwise redirects to the login page or aborts with a 403 error.
    """
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            """
            Inner function that performs the actual role check.

            Parameters
            ----------
            *args : list
                Positional arguments passed to the decorated view function.
            **kwargs : dict
                Keyword arguments passed to the decorated view function.

            Returns
            -------
            Response
                The response object to be returned by the view function or a redirect/abort response.
            """
            if not current_user.is_authenticated:
                return redirect(url_for('choice'))

            if current_user.role != role:
                print(f"Пользователь {current_user.email} имеет роль {current_user.role}, а ожидалось {role}")
                return abort(403)
            print(f"Пользователь {current_user.email} имеет роль {current_user.role}")

            return func(*args, **kwargs)

        return decorated_view

    return wrapper
