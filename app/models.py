from . import db


class Note(db.Model):
    # Fields for the Note model
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=db.func.now(), nullable=False)


class User(db.Model):
    # Fields for the User model
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
