from flask import Blueprint, jsonify

controller_bp = Blueprint("controller", __name__, url_prefix="/controller")


@controller_bp.route("/health", methods=["GET"])
def register():

    return jsonify("controller api is healthy"), 200
