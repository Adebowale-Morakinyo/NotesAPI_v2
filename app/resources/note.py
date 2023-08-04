from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request

from app import db
from app.models import Note
from app.schemas.note import NoteSchema

note_bp = Blueprint('notes', 'notes', url_prefix='/notes')


class NoteResource(MethodView):

    def post(self):
        data = request.get_json()
        note_schema = NoteSchema()
        note = note_schema.load(data)
        db.session.add(note)
        db.session.commit()
        return note_schema.dump(note), 201

    def get(self, note_id):
        note = Note.query.get_or_404(note_id)
        note_schema = NoteSchema()
        return note_schema.dump(note), 200

    def put(self, note_id):
        note = Note.query.get_or_404(note_id)
        data = request.get_json()
        note_schema = NoteSchema()
        note = note_schema.load(data, instance=note)
        db.session.commit()
        return note_schema.dump(note), 200

    def delete(self, note_id):
        note = Note.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()
        return '', 204


note_bp.add_url_rule('', view_func=NoteResource.as_view('note'))
note_bp.add_url_rule('/<int:note_id>', view_func=NoteResource.as_view('single_note'))
