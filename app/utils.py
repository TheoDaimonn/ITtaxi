from flask_login import current_user
from functools import wraps
from flask import redirect, url_for, abort
from cryptography.fernet import Fernet


def login_required(role):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('choice'))

            if current_user.role != role:
                print(f"Пользователь {current_user.email} имеет роль {current_user.role}, а ожидалось {role}")
                return abort(403)
            print(f"Пользователь {current_user.email} имеет роль {current_user.role}, а ожидалось {role}")

            return func(*args, **kwargs)

        return decorated_view

    return wrapper

def load_key():
    return open("secret.key", "rb").read()

def encrypt_data(data):
    key = load_key()
    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(data.encode('utf-8'))
    return encrypted_data

def decrypt_data(encrypted_data):
    key = load_key()
    cipher_suite = Fernet(key)
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    return decrypted_data.decode('utf-8')