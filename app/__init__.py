"""
This module defines the Flask application factory function, which sets up the Flask app with
the necessary configurations and registers the main and validation blueprints.

Modules:
    routes: Contains the main and validation blueprints.
    flask: Provides the Flask class for creating the Flask app.

Functions:
    create_app(): Creates and configures the Flask application.
"""

from flask import Flask

from .routes import main_bp, validation_bp


def create_app():
    """
    Creates and configures the Flask application.

    This function initializes the Flask app with template and static folders,
    loads configurations from the config object, and registers the main and
    validation blueprints.

    Returns:
        Flask: The configured Flask application instance.
    """

    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )
    app.config.from_object('config.Config')

    with app.app_context():
        app.register_blueprint(main_bp)
        app.register_blueprint(validation_bp)

    return app
