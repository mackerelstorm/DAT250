from flask import render_template, flash, redirect, url_for, request
from app import app, database
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm
from datetime import datetime
import os

# this file contains all the different routes, and the logic for communicating with the database

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = IndexForm()

    if form.login.is_submitted() and form.login.submit.data:
        user = database.query_user(form.login.username.data)
        if user == None:
            flash('Sorry, this user does not exist!')
        elif user['password'] == form.login.password.data:
            return redirect(url_for('stream', username=form.login.username.data))
        else:
            flash('Sorry, wrong password!')

    elif form.register.is_submitted() and form.register.submit.data:
        database.submit_user(form.register.username.data, form.register.first_name.data,
         form.register.last_name.data, form.register.password.data)
        return redirect(url_for('index'))
    return render_template('index.html', title='Welcome', form=form)


# content stream page
@app.route('/stream/<username>', methods=['GET', 'POST'])
def stream(username):
    form = PostForm()
    user = database.query_user(username)
    if form.is_submitted():
        if form.image.data:
            path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
            form.image.data.save(path)

        database.submit_post(user['id'], form.content.data, form.image.data.filename, datetime.now())
        return redirect(url_for('stream', username=username))

    posts = database.query_posts(user['id'])
    return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)

# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
def comments(username, p_id):
    form = CommentsForm()
    if form.is_submitted():
        user = database.query_user(username)
        database.submit_comment(p_id, user['id'], form.comment.data, datetime.now())

    post = database.query_post(p_id)
    all_comments = database.query_comments(p_id)
    return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)

# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
def friends(username):
    form = FriendsForm()
    user = database.query_user(username)
    if form.is_submitted():
        friend = database.query_user(form.username.data)
        if friend is None:
            flash('User does not exist')
        else:
            database.submit_friend(user['id'], friend['id'])
    
    all_friends = database.query_friends(user['id'])
    return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)

# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    form = ProfileForm()
    if form.is_submitted():
        database.update_profile(
            form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data, form.birthday.data, username
        )
        return redirect(url_for('profile', username=username))
    
    user = database.query_user(username)
    return render_template('profile.html', title='profile', username=username, user=user, form=form)
