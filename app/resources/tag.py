from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required

from app.models import Tag, Note
from app.schemas import TagSchema, NoteTagSchema, TagAutocompleteSchema, TagAutocompleteResponseSchema

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
            tag.save_to_db()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")

        return tag


@tag_blp.route("/tag/<int:tag_id>/note/<int:note_id>")
class LinkTagsToNote(MethodView):
    @jwt_required(fresh=True)
    @tag_blp.response(201, TagSchema)
    def post(self, tag_id, note_id):
        tag = Tag.query.get_or_404(tag_id)
        note = Note.query.get_or_404(note_id)

        if tag in note.tags:
            abort(400, message="Tag is already linked to this note.")

        note.tags.append(tag)

        try:
            tag.save_to_db()
        except SQLAlchemyError:
            abort(500, message="An error occurred while linking the tag to the note.")

        return tag

    @jwt_required(fresh=True)
    @tag_blp.response(200, NoteTagSchema)
    def delete(self, tag_id, note_id):
        tag = Tag.query.get_or_404(tag_id)
        note = Note.query.get_or_404(note_id)

        if tag not in note.tags:
            abort(400, message="Tag is not linked to this note.")

        note.tags.remove(tag)

        try:
            note.save_to_db()
        except SQLAlchemyError:
            abort(500, message="An error occurred while removing the tag from the note.")

        return {"message": "Tag removed from note", "tag": tag, "note": note}


@tag_blp.route("/autocomplete")
class TagAutocompleteResource(MethodView):
    @tag_blp.arguments(TagAutocompleteSchema, location="query")
    @tag_blp.response(200, TagAutocompleteResponseSchema)
    def get(self, tag_data):
        query = tag_data["query"]
        tags = Tag.query.filter(Tag.name.ilike(f"%{query}%")).limit(10).all()
        tag_names = [tag.name for tag in tags]
        return {"tags": tag_names}
