from app import db
from passlib.hash import pbkdf2_sha256


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Define notes relationship
    notes = db.relationship('Note', back_populates='user')

    @classmethod
    def save_to_db(cls):
        db.session.add(cls)
        db.session.commit()

    def set_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)
