from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
import logging
from flask import request
import secrets

from db import db
from app.models import Note, Tag
from app.schemas import (
    NoteSchema,
    NoteListResponseSchema,
    NoteListSchema,
    NoteListQuerySchema,
    NoteUpdateSchema,
    ShareViaEmailSchema
)
from app.email import send_email

note_blp = Blueprint("Notes", "notes", description="Operations on notes")


@note_blp.route("/note/<int:note_id>")
class NoteResource(MethodView):
    @jwt_required()
    @note_blp.response(200, NoteSchema)
    def get(self, note_id):
        current_user = get_jwt_identity()
        note = Note.query.get_or_404(note_id)

        if note.user_id != current_user:
            abort(403, message="You are not authorized to access this note.")

        return note

    @jwt_required()
    def delete(self, note_id):
        current_user = get_jwt_identity()
        note = Note.query.get_or_404(note_id)

        # Check if the note belongs to the current user
        if note.user_id != current_user:
            abort(403, message="You are not authorized to delete this note.")

        note.delete_from_db()
        return {"message": "Note deleted."}

    @jwt_required(fresh=True)
    @note_blp.arguments(NoteUpdateSchema)
    @note_blp.response(200, NoteSchema)
    def put(self, note_data, note_id):
        note = Note.query.get(note_id)
        current_user = get_jwt_identity()
        note = Note.query.get_or_404(note_id)

        # Check if the note belongs to the current user
        if note.user_id != current_user:
            abort(403, message="You are not authorized to update this note.")

        if note:
            note.title = note_data["title"]
            note.content = note_data["content"]
        else:
            note = Note(id=note_id, **note_data)

        note.save_to_db()

        return note


@note_blp.route("/note")
class NoteList(MethodView):
    @jwt_required(fresh=True)
    @note_blp.arguments(NoteSchema)
    @note_blp.response(201, NoteSchema)
    def post(self, note_data):
        current_user = get_jwt_identity()
        note = Note(**note_data)

        # Check if the note belongs to the current user
        if note.user_id != current_user:
            abort(403, message="You are not authorized to create note.")

        # Check if a note with the same title already exists for the current user
        existing_note = Note.query.filter_by(user_id=current_user, title=note_data["title"]).first()
        if existing_note:
            abort(400, message="A note with the same title already exists.")

        note = Note(**note_data)
        note.user_id = current_user

        try:
            note.save_to_db()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the note.")

        return note

    @jwt_required()
    @note_blp.arguments(NoteListQuerySchema, location="query", validate=False)
    @note_blp.response(200, NoteListResponseSchema)
    def get(self, query_params):
        current_user = get_jwt_identity()

        # Convert empty string values to None
        page = query_params.get("page", None)
        per_page = query_params.get("per_page", None)
        sort_by = query_params.get("sort_by", "date")
        order = query_params.get("order", "desc")
        tag = query_params.get("tag")

        # Handle defaults if values are None
        if page is None:
            page = 1
        if per_page is None:
            per_page = 10

        logging.debug(f"Page: {page}, Per Page: {per_page}, Tag: {tag}")

        # Build the query based on the query parameters and user identity
        query = Note.query.filter_by(user_id=current_user)

        if tag:
            query = query.join(Note.tags).filter(func.lower(Tag.name) == tag.lower())

        logging.debug(f"Query: {query}")

        if sort_by == "date":
            query = query.order_by(Note.date.desc() if order == "desc" else Note.date)
        elif sort_by == "title":
            query = query.order_by(Note.title.desc() if order == "desc" else Note.title)

        notes = query.options(db.joinedload(Note.tags)).paginate(page=page, per_page=per_page, error_out=False)

        logging.debug(f"Notes Items: {notes.items}")

        serialized_notes = NoteListSchema(many=True).dump(notes.items)

        return {
            "notes": serialized_notes,
            "page": notes.page,
            "per_page": notes.per_page,
            "total_pages": notes.pages,
            "total_notes": notes.total,
        }, 200


@note_blp.route("/note/<int:note_id>/favorite")
class FavoriteNoteResource(MethodView):
    @jwt_required()
    @note_blp.response(200, NoteSchema)
    def post(self, note_id):
        current_user = get_jwt_identity()
        note = Note.query.get_or_404(note_id)

        if note.user_id != current_user:
            abort(403, message="You are not authorized to mark this note as a favorite.")

        note.is_favorite = True
        note.save_to_db()

        return note


@note_blp.route("/favorites")
class FavoriteNotesList(MethodView):
    @jwt_required()
    @note_blp.response(200, NoteSchema(many=True))
    def get(self):
        current_user = get_jwt_identity()
        favorite_notes = Note.query.filter_by(user_id=current_user, is_favorite=True).all()
        return favorite_notes


@note_blp.route("/note/<int:note_id>/shareable-link")
class ShareableLinkResource(MethodView):
    @jwt_required()
    @note_blp.response(200, NoteSchema)
    def post(self, note_id):
        current_user = get_jwt_identity()
        note = Note.query.get_or_404(note_id)

        if note.user_id != current_user:
            abort(403, message="You are not authorized to generate a shareable link for this note.")

        shareable_link = secrets.token_urlsafe(20)
        note.shareable_link = shareable_link
        note.save_to_db()

        return note


@note_blp.route("/note/<int:note_id>/share-via-email")
class ShareViaEmailResource(MethodView):
    @jwt_required()
    @note_blp.arguments(ShareViaEmailSchema)
    @note_blp.response(200, description="Note shared successfully.")
    def post(self, note_data, note_id):
        current_user = get_jwt_identity()
        note = Note.query.get_or_404(note_id)

        if note.user_id != current_user:
            abort(403, message="You are not authorized to share this note.")

        recipient_email = note_data["email"]
        # Send an email to the recipient with the shareable link
        send_email(recipient_email, "Note Sharing", f"Here's the shareable link: {note.shareable_link}")

        return {"message": "Note shared successfully."}


@note_blp.route("/note/search")
class SearchNotes(MethodView):
    @jwt_required()
    @note_blp.response(200, NoteSchema(many=True))
    def get(self):
        current_user = get_jwt_identity()
        search_query = request.args.get("query")

        if not search_query:
            abort(400, message="Missing search query.")

        notes = Note.query.filter_by(user_id=current_user).filter(
            db.or_(
                Note.title.ilike(f"%{search_query}%"),
                Note.content.ilike(f"%{search_query}%"),
                Note.tags.any(Tag.name.ilike(f"%{search_query}%"))
            )
        ).all()

        return notes
