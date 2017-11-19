from flask import render_template, redirect, url_for, request, g, flash, session
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators

from passlib.hash import sha256_crypt

from app import webapp, login_required, get_dbresource

from pymysql import escape_string

from boto3.dynamodb.conditions import Key

import gc


# define login form
class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=20, message="Username should be 4-20 characters long")])
    password = PasswordField('Password', [validators.DataRequired()])

# login page
@webapp.route("/Login", methods=['GET', 'POST'])
def login_form():
    error = ''
    try:
        form = LoginForm(request.form)
        dynamodb = get_dbresource()
        usertable = dynamodb.Table('users')

        if request.method == "POST":
            # check if form is validated
            if not form.validate_on_submit():
                error = "request is invalidated"
                return render_template("login-form.html", title='Login', form=form, error=error)

            response = usertable.query(
                IndexName= 'UIDIndex',
                KeyConditionExpression= Key('UserID').eq(escape_string(form.username.data))
            )

            if response['Count'] == 0:
                error = "Username does not exist"
                return render_template("login-form.html", title='Login', form=form, error=error)

            items = response['Items'][0]

            if sha256_crypt.verify(form.password.data, items['Password']):
                session['logged_in'] = True
                session['username'] = form.username.data
                session['nickname'] = items['Nickname']
                flash("You are now logged in")
                return redirect(url_for("main"))
            else:
                error = "Invalid credentials, try again."
                return render_template("login-form.html", title='Login', form=form, error=error)

        gc.collect()
        return render_template("login-form.html", title='Login', form=form, error=error)

    except Exception as e:
        return str(e)


# define sign up form
class SignUpForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=20, message="Username should be 4-20 characters long")])
    nickname = StringField('Nickname', [validators.Length(min=1, max=20, message="Nickname should be 1-20 characters long")])
    email = StringField('Email Address', [validators.Length(min=6, max=50, message="Email should be 6-50 characters long")])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message="Password must match")])
    confirm = PasswordField('Repeat Password')
#    accept_tos = BooleanField('I accept the <a href="/tos"> Terms of Service</a> '
#                              'and the <a href="/privacy"> Privacy Notice</a>', [validators.DataRequired()])


# signup page
@webapp.route("/Signup", methods=['GET', 'POST'])
def signup_form():
    error = ''
    try:
        form = SignUpForm(request.form)

        if request.method == "POST":
            # check if form is validated
            if not form.validate_on_submit():
                error = "request is invalidated"
                return render_template("signup-form.html", title='sign up', form=form, error=error)

            username = form.username.data
            nickname = form.nickname.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))

            dynamodb = get_dbresource()
            usertable = dynamodb.Table('users')

            # check if username is taken
            response = usertable.query(
                IndexName='UIDIndex',
                KeyConditionExpression=Key('UserID').eq(escape_string(username))
            )
            if response['Count'] > 0:
                error = "That username is already taken"
                return render_template('signup-form.html', title='sign up', form=form, error=error)
            else:
                usertable.put_item(
                    Item={
                        'UserID': escape_string(username),
                        'Nickname': escape_string(nickname),
                        'Email': escape_string(email),
                        'Password': escape_string(password)
                    }
                )
                flash("Thanks for signing up!")
                gc.collect()

                # record in session as a cookie
                session['logged_in'] = True
                session['username'] = username
                session['nickname'] = nickname

                return redirect(url_for('main'))

        return render_template("signup-form.html", title='sign up', form=form, error=error)

    except Exception as e:
        return str(e)


# logout page
@webapp.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('main'))

