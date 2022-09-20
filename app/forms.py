from flask_wtf import FlaskForm
from flask import session
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField
from wtforms.validators import InputRequired, EqualTo, Length #Importert funksjoner for validering
from flask_wtf.file import FileField  
from app import database
from wtforms.fields import DateField

# defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields
# TODO: Add validation, maybe use wtforms.validators??
# TODO: There was some important security feature that wtforms provides, but I don't remember what; implement it


class LoginForm(FlaskForm):
    class Meta:
        csrf = False
    username = StringField('Username', render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', render_kw={'placeholder': 'Password'})
    remember_me = BooleanField('Remember me') # TODO: It would be nice to have this feature implemented, probably by using cookies
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    class Meta:
        csrf = False
    first_name = StringField('First Name',validators=[InputRequired(message='Need to enter a first name')], render_kw={'placeholder': 'First Name'})
    last_name = StringField('Last Name',validators=[InputRequired(message='Need to enter a last name')], render_kw={'placeholder': 'Last Name'})
    username = StringField('Username',validators=[InputRequired(message='Need to enter a username')], render_kw={'placeholder': 'Username'})
    password = PasswordField('Password',validators=[InputRequired(),Length(min=8, max=40,message='Password must be at least 8 characters long!'),EqualTo('confirm_password', message='Passwords must match')], render_kw={'placeholder': 'Password'})
    confirm_password = PasswordField('Confirm Password', render_kw={'placeholder': 'Confirm Password'})
    submit = SubmitField('Sign Up')


    def username_check(self, username):
        bruker = database.query_user(username)
        if bruker == None:
            return True
        else:
            return False

    def pwdcheck(self, s): #Lagte passwordchecker for å sjekke om det er store og små bosktaver pluss tall.
        checker = 0
        if any('a' <= c <= 'z' for c in s):
            checker += 1
        if any('A' <= c <= 'Z' for c in s):
            checker += 1
        if any(c.isdigit() for c in s):
            checker += 1

        if checker == 3:
            return True
        elif checker < 3:
            return False
        
        


class IndexForm(FlaskForm):
    class Meta:
        csrf = False
    login = FormField(LoginForm)
    register = FormField(RegisterForm)

class PostForm(FlaskForm):
    class Meta:
        csrf = False
    content = TextAreaField('New Post', render_kw={'placeholder': 'What are you thinking about?'})
    image = FileField('Image') 
    submit = SubmitField('Post')

class CommentsForm(FlaskForm):
    comment = TextAreaField('New Comment', render_kw={'placeholder': 'What do you have to say?'})
    submit = SubmitField('Comment')

class FriendsForm(FlaskForm):
    username = StringField('Friend\'s username', render_kw={'placeholder': 'Username'})
    submit = SubmitField('Add Friend')

class ProfileForm(FlaskForm):
    education = StringField('Education', render_kw={'placeholder': 'Highest education'})
    employment = StringField('Employment', render_kw={'placeholder': 'Current employment'})
    music = StringField('Favorite song', render_kw={'placeholder': 'Favorite song'})
    movie = StringField('Favorite movie', render_kw={'placeholder': 'Favorite movie'})
    nationality = StringField('Nationality', render_kw={'placeholder': 'Your nationality'})
    birthday = DateField('Birthday')
    submit = SubmitField('Update Profile')
