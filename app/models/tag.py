from app import db


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    # Define notes relationship (many-to-many)
    notes = db.relationship('Note', secondary='note_tags', back_populates='tags')
