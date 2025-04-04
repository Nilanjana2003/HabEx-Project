# config.py
import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# Base directory of the application
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key for session management, CSRF protection, etc.
    # IMPORTANT: Keep this secret! Use environment variable in production.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-should-really-change-this-key'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'database', 'habex.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False