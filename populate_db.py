from app import create_app
from app.models.user import User
from app.models.note import Note
from app.models.tag import Tag
from app.models.note_tags import note_tags
from faker import Faker
import random

# Create a Flask app context
app = create_app()

# Initialize the app context
app.app_context().push()

# Initialize the database
from db import db

# Create a Faker instance for generating fake data
fake = Faker()

# Create users and add notes for each user
for _ in range(5):  # Create 5 users
    user = User(
        username=fake.user_name(),
        email=fake.email(),
        full_name=fake.name(),
        password=fake.password(),
    )
    db.session.add(user)

    for _ in range(random.randint(1, 5)):  # Add random notes for each user
        note = Note(
            title=fake.sentence(),
            content=fake.paragraph(),
            user=user,
        )
        db.session.add(note)

        # Add random tags to the note
        for _ in range(random.randint(1, 3)):
            tag_name = fake.word()
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
            note.tags.append(tag)

# Commit the changes to the database
db.session.commit()
