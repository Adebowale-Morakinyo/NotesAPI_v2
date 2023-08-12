from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from app.models import Tag, Note
from app.schamas import TagSchema, NoteTagSchema

tag_blp = Blueprint("Tags", "tags", description="Operations on tags")


@tag_blp.route("/tag/<int:tag_id>")
class TagResource(MethodView):
    @tag_blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = Tag.query.get_or_404(tag_id)
        return tag


@tag_blp.route("/tag")
class TagList(MethodView):
    @tag_blp.response(200, TagSchema(many=True))
    def get(self):
        return Tag.query.all()

    @tag_blp.arguments(TagSchema)
    @tag_blp.response(201, TagSchema)
    def post(self, tag_data):
        tag = Tag(**tag_data)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")

        return tag


@tag_blp.route("/tag/<int:note_id>/note/<int:tag_id>")
class LinkTagsToNote(MethodView):
    @tag_blp.response(201, TagSchema)
    def post(self, tag_id, note_id):
        tag = Tag.query.get_or_404(tag_id)
        note = Note.query.get_or_404(note_id)

        note.tags.append(tag)

        try:
            db.session.add(note)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while linking the tag to the note.")

        return tag

    @tag_blp.response(200, NoteTagSchema)
    def delete(self, tag_id, note_id):
        tag = Tag.query.get_or_404(tag_id)
        note = Note.query.get_or_404(note_id)

        note.tags.remove(tag)

        try:
            db.session.add(note)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while removing the tag from the note.")

        return {"message": "Tag removed from note", "tag": tag, "note": note}
