from flask import Blueprint, jsonify

explorer_bp = Blueprint("explorer", __name__, url_prefix="/explorer")


@explorer_bp.route("/health", methods=["GET"])
def register():

    return jsonify("explore api is healthy"), 200
