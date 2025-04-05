from flask import jsonify
from flask_openapi3 import APIBlueprint, Tag

explorer_bp = APIBlueprint("explorer", __name__, url_prefix="/explorer")
explorer_tag = Tag(name="Explorer", description=" ")


@explorer_bp.get("/health", tags=[explorer_tag])
async def register():
    return jsonify("explore api is healthy"), 200
