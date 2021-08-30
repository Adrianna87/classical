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
    """User in the system."""

    __tablename__ = 'playlists'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    playlist_name = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )

    playlist_desc = db.Column(
        db.String(100),
        nullable=True,
        unique=False,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
    )

    playlist_piece = db.relationship('PlaylistPiece',
                                     backref='playlist')
    pieces = db.relationship('Piece',
                             secondary='playlists_pieces',
                             backref='playlists')


class Piece(db.Model):
    """User in the system."""

    __tablename__ = 'pieces'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    composer = db.Column(
        db.Text,
        nullable=False,
    )

    title = db.Column(
        db.Text,
        nullable=False,
    )

    genre = db.Column(
        db.Text,
        nullable=False,
    )

    era = db.Column(
        db.Text,
        nullable=False,
    )

    playlist_piece = db.relationship('PlaylistPiece',
                                     backref='piece')
    playlist = db.relationship('Playlist',
                               secondary='playlists_pieces',
                               backref='pieces')


class PlaylistPiece(db.Model):
    """User in the system."""

    __tablename__ = 'playlists_works'

    playlist_id = db.Column(db.Integer,
                            db.ForeignKey("playlists.id"),
                            primary_key=True)
    piece_id = db.Column(db.Text,
                         db.ForeignKey("pieces.id"),
                         primary_key=True)
