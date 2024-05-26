from app import app, db
from app.models import User, Order, Driver


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Order': Order}


if __name__ == "__main__":
    app.run()