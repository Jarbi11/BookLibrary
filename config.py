import os

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(basedir, 'app.db')

MAX_CONTENT_LENGTH = 1024 * 1024

UPLOADS_DEFAULT_DEST = os.path.join(basedir, 'upload/')

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE

SECRET_KEY = 'you-will-never-guess'

REGISTRATION_EMAIL_PATTERN = r".*@.*\.com$"

FLASKY_ADMIN = [
    'admin@library.com',
]

DOUBAN_TRANS_SERVER = "http://127.0.0.1:3000"

SQLALCHEMY_TRACK_MODIFICATIONS = False

MAX_BORROWED_BOOK_PER_PERSON = 3
