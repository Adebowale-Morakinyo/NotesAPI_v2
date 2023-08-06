from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import Note
from app.schemas.note import NoteSchema

note_bp = Blueprint('notes', 'notes', url_prefix='/notes')


class NoteResource(MethodView):

    @jwt_required()  # Protect this route with JWT
    def post(self):
        try:
            current_user = get_jwt_identity()
            data = request.get_json()

            note_schema = NoteSchema()
            note = note_schema.load(data)
            note.user_id = current_user

            db.session.add(note)
            db.session.commit()

            return note_schema.dump(note), 201
        except Exception as e:
            return {'message': 'An error occurred while processing your request'}, 500

    @jwt_required()  # Protect this route with JWT
    def get(self, note_id):
        current_user = get_jwt_identity()
        note = Note.query.get_or_404(note_id)

        if note.user_id != current_user:
            return '', 403  # Forbidden

        note_schema = NoteSchema()
        return note_schema.dump(note), 200

    @jwt_required()  # Protect this route with JWT
    def get(self):
        try:
            current_user = get_jwt_identity()
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            sort_by = request.args.get('sort_by', 'date')
            order = request.args.get('order', 'desc')
            tag = request.args.get('tag')

            query = Note.query.filter_by(user_id=current_user)

            if tag:
                query = query.filter(Note.tags.ilike(f"%{tag}%"))

            if sort_by == 'date':
                query = query.order_by(Note.date.desc() if order == 'desc' else Note.date)
            elif sort_by == 'title':
                query = query.order_by(Note.title.desc() if order == 'desc' else Note.title)

            notes = query.paginate(page, per_page, error_out=False)
            note_schema = NoteSchema(many=True)
            return {
                'notes': note_schema.dump(notes.items),
                'page': notes.page,
                'per_page': notes.per_page,
                'total_pages': notes.pages,
                'total_notes': notes.total
            }, 200
        except Exception as e:
            return {'message': 'An error occurred while processing your request'}, 500

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
note_bp.add_url_rule('/create', view_func=NoteResource.as_view('create_note'))
