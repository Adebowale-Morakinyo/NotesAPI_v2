from flask.views import MethodView
from flask_smorest import Blueprint, abort

from app.models import Tag
from app.schamas import TagSchema

tag_blp = Blueprint("Tags", "tags", description="Operations on tags")


@tag_blp.route("/tag/<int:tag_id>")
class TagResource(MethodView):
    @tag_blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = Tag.query.get_or_404(tag_id)
        return tag

# more views for creating, updating, and deleting tags will be added lol, still testing
