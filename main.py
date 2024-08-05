# main.py
from flask import Flask
from os import path
from applications.models import *
from applications.database import db
from applications.config import Config
from flask_jwt_extended import JWTManager

app = None 

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)
    db.init_app(app)
    jwt = JWTManager(app)

    with app.app_context():
        if not path.exists("instance/database.sqlite3"):
            db.create_all()
            adminUser = User(username="admin", password="password", roles="Admin")
            db.session.add(adminUser)
            db.session.commit()

        import applications.controllers

    return app

app = create_app()
app.app_context().push()

if __name__ == '__main__':
    app.run(debug=True)
