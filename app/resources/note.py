from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

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

    @jwt_required()  # Protect this route with JWT
    def get(self, note_id):
        current_user = get_jwt_identity()
        note = Note.query.get_or_404(note_id)

        if note.user_id != current_user:
            return '', 403  # Forbidden

        note_schema = NoteSchema()
        return note_schema.dump(note), 200

    @jwt_required()  # Protect this route with JWT
    def put(self, note_id):
        current_user = get_jwt_identity()
        note = Note.query.get_or_404(note_id)
        data = request.get_json()

        if note.user_id != current_user:
            return '', 403  # Forbidden

        note_schema = NoteSchema()
        note = note_schema.load(data, instance=note)
        db.session.commit()
        return note_schema.dump(note), 200

    @jwt_required()  # Protect this route with JWT
    def delete(self, note_id):
        current_user = get_jwt_identity()
        note = Note.query.get_or_404(note_id)

        if note.user_id != current_user:
            return '', 403  # Forbidden

        db.session.delete(note)
        db.session.commit()
        return '', 204


note_bp.add_url_rule('', view_func=NoteResource.as_view('note'))
note_bp.add_url_rule('/<int:note_id>', view_func=NoteResource.as_view('single_note'))
