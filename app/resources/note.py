from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from app.models import Note
from app.schamas import NoteSchema, NoteUpdateSchema

note_blp = Blueprint("Notes", "notes", description="Operations on notes")


@note_blp.route("/note/<int:note_id>")
class NoteResource(MethodView):
    @note_blp.response(200, NoteSchema)
    def get(self, note_id):
        note = Note.query.get_or_404(note_id)
        return note

    def delete(self, note_id):
        note = Note.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()
        return {"message": "Note deleted."}

    @note_blp.arguments(NoteUpdateSchema)
    @note_blp.response(200, NoteSchema)
    def put(self, note_data, note_id):
        note = Note.query.get(note_id)

        if note:
            note.title = note_data["title"]
            note.content = note_data["content"]
        else:
            note = Note(id=note_id, **note_data)

        db.session.add(note)
        db.session.commit()

        return note


@note_blp.route("/note")
class NoteList(MethodView):
    @note_blp.response(200, NoteSchema(many=True))
    def get(self):
        return Note.query.all()

    @note_blp.arguments(NoteSchema)
    @note_blp.response(201, NoteSchema)
    def post(self, note_data):
        note = Note(**note_data)

        try:
            db.session.add(note)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the note.")

        return note
