from flask import Flask, request
from os import path
from applications.models import *
from applications.database import db
from applications.config import Config
from flask_login import LoginManager

app = None 
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        if not path.exists("/home/snakescipt/Projects/flask-jinja/Flask-jinja-app/instance/database.sqlite3"):
            db.create_all()
            adminUser = User(username="admin", password="password", roles = "Admin")
            db.session.add(adminUser)
            db.session.commit()

        import applications.controllers

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

app = create_app()
app.app_context().push()
# from applications.controllers import *

if __name__ == '__main__':
    app.run(debug=True)