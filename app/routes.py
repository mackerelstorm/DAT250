from flask import render_template, flash, redirect, url_for, request, abort
from app import app, User 
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm
from datetime import datetime
import os
from app.database import query_user, query_friend, query_friends, query_comments, \
    query_post, query_posts, query_user_id, query_user_id, submit_user, submit_post, \
    submit_comment, submit_friend, update_profile


# this file contains all the different routes, and the logic for communicating with the database

#Funksjon for å sjekke om filnavnet inneholder korrekte extensions fra configs ALLOWED_EXTENSIONS
import flask_login
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
# this file contains all the different routes, and the logic for communicating with the database

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@limiter.limit('10/minute')
def index():
    form = IndexForm()

    if form.login.is_submitted() and form.login.submit.data:
        user = query_user(form.login.username.data)
        if user == None:
            flash('Wrong password or username')          #Istedenfor å kunne sjekke om brukeren allerede finnes
        elif check_password_hash(user['password'], form.login.password.data):
            f_user = User()
            f_user.id = user['id']
            flask_login.login_user(f_user)
            return redirect(url_for('stream'))
        else:
            flash('Wrong password or username!')
    elif form.register.validate_on_submit():
        if form.register.username_check(form.register.username.data):
            if form.register.pwdcheck(form.register.password.data):
                submit_user(form.register.username.data, form.register.first_name.data,
                 form.register.last_name.data, generate_password_hash(form.register.password.data))
                return redirect(url_for('index'))
            elif not form.register.pwdcheck(form.register.password.data):
                flash("Password must contain an uppercase letter and a number!")
        elif not form.register.username_check(form.register.username.data):
            flash("Username already taken!")
        return redirect(url_for('index'))

    return render_template('index.html', title='Welcome', form=form)


# content stream page
@app.route('/stream', methods=['GET', 'POST'])
@flask_login.login_required
def stream():
    form = PostForm()
    user_id = flask_login.current_user.id
    user = query_user_id(user_id)
    if form.is_submitted() and allowed_file(form.image.data.filename): #Sjekker korrekt filtype
        if form.image.data:
            path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
            form.image.data.save(path)


        submit_post(user['id'], form.content.data, form.image.data.filename, datetime.now())
        return redirect(url_for('stream'))
    elif form.is_submitted() and not allowed_file(form.image.data.filename): #Gir beskjed dersom fila ikke er av riktig type
        flash("You can only upload images!")
    posts = query_posts(user['id'])
    return render_template('stream.html', title='Stream', username=user['username'], form=form, posts=posts)
    

# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
@flask_login.login_required
def comments(username, p_id):
    form = CommentsForm()
    user_id = flask_login.current_user.id
    user = query_user_id(user_id)
    if username != user['username']: # brukes til å nekte brukeren i å endre url 
        return abort(403)
    if form.is_submitted():
        submit_comment(p_id, user_id, form.comment.data, datetime.now())
    post = query_post(p_id)
    all_comments = query_comments(p_id)
    return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)

# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
@flask_login.login_required
def friends(username):
    form = FriendsForm()
    user_id = flask_login.current_user.id
    user = query_user_id(user_id)
    if username != user['username']: 
        return abort(403)
    if form.is_submitted():
        friend = query_user(form.username.data)
        if friend is None:
            flash('User does not exist')
        else:
            submit_friend(user['id'], friend['id'])
    all_friends = query_friends(user['id'])
    return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)

# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@flask_login.login_required
def profile(username):
    user_id = flask_login.current_user.id
    user = query_user_id(user_id)
    friend = query_friend(user_id, username)
    form = ProfileForm()
    if friend and username == friend['username'] : # brukes til å nekte brukeren i å se andre sine sider 
        user = query_user(friend['username'])
        return render_template('profile.html', title='profile', username=username, user=user, form=form)
    elif username == user['username']:
        if form.is_submitted():
            update_profile(form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data, form.birthday.data, username)
            return redirect(url_for('profile', username=username))
        return render_template('profile.html', title='profile', username=username, user=user, form=form)
    else:
        abort(403)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    flask_login.logout_user()
    return redirect(url_for('index'))
