from flask import Flask
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import os


def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('config.Config')

    # Enable CORS
    CORS(app)

    # Setup logging
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('UPI Fraud Detection API startup')

    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app