from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.String(20),
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    favorites = db.relationship('Playlist', backref='user')

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Playlist(db.Model):
    """favorites"""

    __tablename__ = 'playlists'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
    )

    works_id = db.Column(
        db.Integer,
        db.ForeignKey('works.id', ondelete="cascade")
    )

    # @classmethod
    # def make(cls, playlist_name, playlist_desc):
    #     """make a playlist"""
    #     playlist = Playlist(
    #         playlist_name=playlist_name,
    #         playlist_desc=playlist_desc,
    #     )

    #     db.session.add(playlist)
    #     return playlist


class Works(db.Model):
    """Works by composer"""

    __tablename__ = 'works'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    title = db.Column(
        db.Text,
        nullable=False,
    )

    genre = db.Column(
        db.Text,
        nullable=False,
    )

    composer_id = db.Column(
        db.Integer,
        db.ForeignKey('composers.id', ondelete="cascade")
    )

    # composer = db.relationship('Composer', backref='works')
    favorites = db.relationship('Playlist', backref='works')


class Composer(db.Model):
    """Composer info"""

    __tablename__ = 'composers'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    epoch = db.Column(
        db.Text,
        nullable=False,
    )
    works = db.relationship('Works')

    @classmethod
    def composer_info(cls, id, name, epoch):
        """Add composer info to database"""
        composer_info = Composer(id=id, name=name, epoch=epoch)
        db.session.add(composer_info)
        return composer_info
