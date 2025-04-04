from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from src.api.controller import controller_bp
from src.api.explorer import explorer_bp
from src.config import Config
from src.db.main import check_db_connection

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(config_class)

    db.init_app(app)

    app.register_blueprint(controller_bp)
    app.register_blueprint(explorer_bp)

    # a simple health check
    @app.route("/health")
    def health():
        db_connection_status = check_db_connection(db.session)

        if not db_connection_status:
            return jsonify("Oops, the API is down or not responding!"), 500
        return jsonify("Yay, the API is healthy"), 200

    return app
