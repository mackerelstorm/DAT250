from flask import Flask, g
from config import Config
from flask_bootstrap import Bootstrap
from flask_login  import LoginManager, UserMixin
import sqlite3
import os

# create and configure app
app = Flask(__name__)
app.secret_key = 'secret'
Bootstrap(app)
app.config.from_object(Config)

login = LoginManager(app)
login.init_app(app)

class User(UserMixin):
    pass

@login.user_loader 
def load(user_id):
    thisuser = database.query_user_id(user_id)
    if thisuser != None:
        user = User()
        user.id = user_id
        return user
    return None
    

# get an instance of the db
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

# initialize db for the first time
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# automatically called when application is closed, and closes db connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# initialize db if it does not exist
if not os.path.exists(app.config['DATABASE']):
    init_db()

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.mkdir(app.config['UPLOAD_PATH'])

from app import routes
