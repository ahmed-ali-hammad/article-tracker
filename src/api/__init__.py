from flask import jsonify
from flask_openapi3 import Info, OpenAPI, Tag
from flask_sqlalchemy import SQLAlchemy
from src.api.controller import controller_bp
from src.api.explorer import explorer_bp
from src.config import Config
from src.db.main import check_db_connection

db = SQLAlchemy()


def create_app(config_class=Config):
    info = Info(title="Article Tracker", version="1.0.0")
    app = OpenAPI(__name__, info=info)

    app.config.from_object(config_class)

    db.init_app(app)
    app.register_api(controller_bp)
    app.register_api(explorer_bp)

    health_check_tag = Tag(
        name="Health",
        description="Endpoint for checking the health and status of the Flask application",
    )

    # a simple health check
    @app.get("/health", tags=[health_check_tag])
    async def health():
        db_connection_status = check_db_connection(db.session)

        if not db_connection_status:
            return jsonify("Oops, the API is down or not responding!"), 500
        return jsonify("Yay, the API is healthy"), 200

    return app
