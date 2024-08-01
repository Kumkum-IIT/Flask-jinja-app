from flask import Flask, request
from os import path
from applications.models import *
from applications.database import db
from applications.config import Config

app = None 

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        if not path.exists("C:/Users/DELL/Desktop/influ_mad1/instance/database.sqlite3"):
            db.create_all()
            adminUser = User(username="admin", email="admin@gmail.com", password="password", roles = "Admin")
            db.session.add(adminUser)
            db.session.commit()

        import applications.controllers

    return app

app = create_app()
app.app_context().push()
# from applications.controllers import *

if __name__ == '__main__':
    app.run(debug=True)