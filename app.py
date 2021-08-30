from flask import Flask, render_template, jsonify, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

import requests

from forms import UserAddForm, LoginForm, UserEditForm
from models import db, connect_db, User

CURR_USER_KEY = "curr_user"
API_BASE_URL = "https://api.openopus.org"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///classical'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "it's a secret"
toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.route("/")
def homepage():
    """Show homepage."""

    return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404
##########
# User signup/login/logout
##########


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """
    Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If the there already is a user with that username: flash message
    and re-present form.
    """
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/profile")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("Goodbye")
    return redirect("/")

# ##########
# # General user routes:
# ##########


@app.route('/search')
def search_form():
    return render_template("search.html")


@app.route('/searchname')
def search_composers():
    "Seach for composers"

    composer = request.args["search"]
    url = f"{API_BASE_URL}/composer/list/search/{composer}.json"

    resp = requests.get(url)
    info = resp.json()
    composer_info = info['composers']
    composer_full_name = list(map(lambda a: a['complete_name'], composer_info))

    return render_template("search.html", info=composer_full_name)

# @app.route('/users/<int:user_id>')
# def users_show(user_id):
#     """Show user profile."""

#     user = User.query.get_or_404(user_id)

#     return render_template('users/show.html', user=user)


# @app.route('/users/profile', methods=["GET", "POST"])
# def profile():
#     """Update profile for current user."""

#     if not g.user:
#         flash("Only logged in users can edit their profile!")
#         return redirect("/")

#     user = g.user
#     form = UserEditForm(obj=user)

#     if form.validate_on_submit():
#         if User.authenticate(user.username, form.password.data):
#             user.username = form.username.data
#             user.email = form.email.data
#             user.image_url = form.image_url.data or "/static/images/default-pic.png"
#             user.header_image_url = form.header_image_url.data or "/static/images/warbler-hero.jpg"
#             user.bio = form.bio.data

#             db.session.commit()
#             return redirect(f"/users/{user.id}")

#         flash("Wrong password, please try again.", 'danger')

#     return render_template('users/edit.html', form=form, user_id=user.id)


# @app.route('/users/delete', methods=["POST"])
# def delete_user():
#     """Delete user."""

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     do_logout()

#     db.session.delete(g.user)
#     db.session.commit()

#     return redirect("/signup")
