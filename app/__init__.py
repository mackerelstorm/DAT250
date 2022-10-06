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
    thisuser = database.query_user(user_id)
    if thisuser != None:
        user = User()
        user.id = user_id
        return user
    return "User not found"
    

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

# perform generic query, not very secure yet
def query_db(query, one=False):
    db = get_db()
    cursor = db.execute(query)
    rv = cursor.fetchall()
    cursor.close()
    db.commit()
    return (rv[0] if rv else None) if one else rv

class Database():
    def query_user(self, username):
        db = get_db()
        sql = 'SELECT * FROM Users WHERE username=?;'
        cur = db.execute(sql, [username])
        rv = cur.fetchone()
        cur.close()
        db.commit()
        return rv
    
    def query_friends(self, u_id):
        db = get_db()
        sql = 'SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id=? AND f.f_id!=? ;'
        cur = db.execute(sql, (u_id, u_id))
        rv = cur.fetchall()
        cur.close()
        db.commit()
        return rv
    
    def query_post(self, p_id):
        db = get_db()
        sql = 'SELECT * FROM Posts WHERE id=?;'
        cur = db.execute(sql, [p_id])
        rv = cur.fetchone()
        cur.close()
        db.commit()
        return rv
    
    def query_posts(self, u_id):
        db = get_db()
        sql = 'SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id=?) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id=?) OR p.u_id=? ORDER BY p.creation_time DESC;'
        cur = db.execute(sql, (u_id, u_id, u_id))
        rv = cur.fetchall()
        cur.close()
        db.commit()
        return rv

    def query_comments(self, p_id):
        db = get_db()
        sql = 'SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id=? ORDER BY c.creation_time DESC;'
        cur = db.execute(sql, [p_id])
        rv = cur.fetchall()
        cur.close()
        db.commit()
        return rv
 
    
    def submit_user(self, username, first_name, last_name, password):
        db = get_db()
        sql = 'INSERT INTO Users (username, first_name, last_name, password) VALUES(?, ?, ?, ?);'
        cur = db.execute(sql, (username, first_name,last_name,password))
        rv = cur.fetchone()
        cur.close()
        db.commit()
        return rv

    def submit_friend(self, user, friend):
        db = get_db()
        sql = 'INSERT INTO Friends (u_id, f_id) VALUES(?, ?);'
        cur = db.execute(sql, (user, friend))
        cur.close()
        db.commit()
    
    def submit_post(self, u_id, content, image, creation_time):
        db = get_db()
        sql = 'INSERT INTO Posts (u_id, content, image, creation_time) VALUES(?, ?, ?, ?);'
        cur = db.execute(sql, (u_id, content,image,creation_time))
        cur.close()
        db.commit()

    def submit_comment(self, p_id, u_id, comment, creation_time):
        db = get_db()
        sql = 'INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES(?, ?, ?, ?);'
        cur = db.execute(sql, (p_id, u_id, comment,creation_time))
        cur.close()
        db.commit()
    
    def update_profile(self, education, employment, music, movie, nationality, birthday, username):
        db = get_db()
        sql = 'UPDATE Users SET education=?, employment=?, music=?, movie=?, nationality=?, birthday=? WHERE username=? ;'
        cur = db.execute(sql, (education, employment, music, movie, nationality, birthday, username))
        cur.close()
        db.commit()
    
database = Database()


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
