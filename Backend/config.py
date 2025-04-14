import os
from dotenv import load_dotenv

load_dotenv()  # This will load variables from .env

class Config:
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'fallback-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = SECRET_KEY