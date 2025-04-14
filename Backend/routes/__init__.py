# routes/__init__.py

from flask import Blueprint

api_blueprint = Blueprint("api", __name__)

# Import each routes file here to register their routes
from . import auth_routes
from . import user_routes
from . import post_routes
from . import collection_routes
