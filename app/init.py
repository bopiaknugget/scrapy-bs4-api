# app/__init__.py
from flask import Flask
import crochet
crochet.setup()

def create_app():
    """Initialize the Flask application"""
    app = Flask(__name__)
    
    # Register blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)
    
    return app