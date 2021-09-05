from flask import Flask, render_template, jsonify, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

import requests

from forms import UserAddForm, LoginForm, UserEditForm, ComposerForm
from models import db, connect_db, User, Favorite

CURR_USER_KEY = "curr_user"
API_BASE_URL = "https://api.openopus.org"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///classical'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "secretsecret"
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
    if g.user:
        flash("Already logged in!", "danger")
        return redirect("/profile")

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
            # add logic for email already in use
            return redirect('/signup')

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""
    if g.user:
        flash("Already logged in!", "danger")
        return redirect("/profile")

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
    if not g.user:
        flash("Please log in first", "danger")
        return redirect("/login")

    do_logout()
    flash("Goodbye")
    return redirect("/")

# ##########
# # Search routes:
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

    return render_template("search.html", info=composer_info)


@app.route('/composer/<int:composer_id>')
def works_info(composer_id):
    """List of composer's works"""

    composer = composer_id
    url = f"{API_BASE_URL}/work/list/composer/{composer}/genre/all.json"
    resp = requests.get(url)
    info = resp.json()
    works = info['works']
    composer = info['composer']

    return render_template("composer.html", works=works, info=info, composer=composer)


# @app.route('/workinfo/<int:work_id>')
# def add_work(work_id):
#     """add work to database"""
#     work = work_id
#     url = f"{API_BASE_URL}/work/detail/{work}.json"
#     resp = requests.get(url)
#     info = resp.json()
#     return jsonify(info['composer'], info['work'])


@app.route('/favorites')
def show_playlist():
    """show playlist"""
    if not g.user:
        flash("please login first", "danger")
        return redirect("/login")

    return render_template('users/playlists.html')


@app.route('/addfavorite/<int:work_id>')
def add_favorite(work_id):
    """add to favorites"""
    if not g.user:
        flash("please login first", "danger")
        return redirect("/login")

    work = work_id
    url = f"{API_BASE_URL}/work/detail/{work}.json"
    resp = requests.get(url)
    info = resp.json()
    favorite = Favorite(user_id=g.user.id,
                        composer_id=info['composer']['id'],
                        opus_work_id=info['work']['id'],
                        title=info['work']['title'],
                        genre=info['work']['genre'])
    db.session.add(favorite)
    db.session.commit()

    return redirect('/playlists')

##########
# User routes
##########


@app.route('/profile')
def profile_page():
    """User's profile page only viewable if logged in"""
    if not g.user:
        flash("Please log in first", "danger")
        return redirect("/login")

    return render_template("users/profile.html")


@app.route('/profile/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    return render_template('users/profile.html', user=user)


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
##########
# Playlist routes
##########

@app.route('/playlists')
def playlist_page():
    if not g.user:
        flash("please login first", "danger")
        return redirect("/login")

    favorites = Favorite.query.all()

    return render_template("users/playlists.html", favorites=favorites)


@app.route('/removefavorite/<int:work_id>', methods=["POST"])
def delete_favorite(work_id):
    """add to favorites"""
    if not g.user:
        flash("please login first", "danger")
        return redirect("/login")

    favorite = Favorite.query.get_or_404(work_id)
    db.session.delete(favorite)
    db.session.commit()
    return redirect('/playlists')

# @app.route('makeplaylist')
# def make_playlist():
#   """Make playlist for user"""
#   if not g.user:
#       flash("please login first", "danger")
#       return redirect("/login")
