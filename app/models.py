from db import db
from passlib.hash import pbkdf2_sha256


class Note(db.Model):
    # Fields for the Note model
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class User(db.Model):
    # Fields for the User model
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    # Method to set the hashed password using Passlib
    def set_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    # Method to check if the provided password matches the hashed password using Passlib
    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)
