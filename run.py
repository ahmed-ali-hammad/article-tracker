"""
Entry point for running the Flask application.

This script uses Click to provide a command-line interface for running the Flask application,
"""

import click
from src.api import create_app

app = create_app()


@click.command()
@click.option(
    "--host", default=app.config.get("FLASK_RUN_HOST"), help="Host to run the app on"
)
@click.option(
    "--port", default=app.config.get("FLASK_RUN_PORT"), help="Port to run the app on"
)
@click.option(
    "--debug", is_flag=app.config.get("DEBUG"), help="Run the app in debug mode"
)
def run_api(host, port, debug):
    """
    Runs the Flask app with the specified configurations.

    Args:
        host (str): The host address to run the app on.
        port (int): The port to run the app on.
        debug (bool): Whether to run the app in debug mode.
    """
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_api()
