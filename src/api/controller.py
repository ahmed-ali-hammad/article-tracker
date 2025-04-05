from flask import jsonify
from flask_openapi3 import APIBlueprint, Tag

controller_bp = APIBlueprint("controller", __name__, url_prefix="/controller")
controller_tag = Tag(name="Controller", description=" ")


@controller_bp.get("/health", tags=[controller_tag])
async def register():
    return jsonify("controller api is healthy"), 200
