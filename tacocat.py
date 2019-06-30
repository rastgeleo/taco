from flask import (Flask, g, render_template, flash, redirect, url_for, abort)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user, login_required, current_user)

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'asdfkjhweui12,dfointergwe'


# login manager setting
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# load user
@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.route('/')
def index():
    tacos = models.Taco.select().limit(100)
    return render_template('index.html', tacos=tacos)


@app.route('/login', methods=('GET', 'POST'))
def login():
    """ Login view"""
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)


@app.route('/logout', methods=('GET', 'POST'))
@login_required
def logout():
    logout_user()
    flash("You have logged out", "success")
    return redirect(url_for('index'))


@app.route('/register', methods=('GET', 'POST'))
def register():
    """ Register view"""
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Yay, you registered!", "success")
        models.User.create_user(
            email=form.email.data,
            password=form.password.data,
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/new_taco', methods=('GET', 'POST'))
@login_required
def new_taco():
    form = forms.TacoForm()
    if form.validate_on_submit():
        models.Taco.create(
            user=g.user._get_current_object(),
            protein=form.protein.data.strip(),
            cheese=form.cheese.data,
            shell=form.shell.data.strip(),
            extras=form.extras.data.strip()
        )
        flash("You have added a new taco!", "success")
        return redirect(url_for('index'))
    return render_template('taco.html', form=form)


@app.route('/delete_taco/<int:taco_id>', methods=('GET', 'POST'))
@login_required
def delete_taco(taco_id):
    try:
        taco = models.Taco.select().where(models.Taco.id == taco_id).get()
    except models.DoesNotExist:
        pass
    else:
        taco.delete_instance()
        flash("the selected taco has been deleted")
    return redirect(url_for('index'))


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


if __name__ == '__main__':

    models.initialize()
    """ Create admin user
    try:
        models.User.create_user(
            email='archieJ@hotmail.com',
            password='password',
            admin=True
        )
    except ValueError:
        pass
    """
    app.run(debug=DEBUG, host=HOST, port=PORT)
