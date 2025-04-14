from flask import Flask
from config import Config
from extensions import db, migrate, jwt

from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.post_routes import post_bp
from routes.collection_routes import collection_bp
from flask_cors import CORS


def create_app():
    app = Flask(__name__, static_url_path='', static_folder='uploads')
    app.config.from_object(Config)
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from models import User, Post, Album, Comment, Like

    # Register API routes
    from routes import api_blueprint
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(post_bp, url_prefix="/api/posts")
    app.register_blueprint(collection_bp, url_prefix="/api/collections")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
