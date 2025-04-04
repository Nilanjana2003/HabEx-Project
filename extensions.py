# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

# Configure login manager
login_manager.login_view = 'login' # The route name for the login page
login_manager.login_message_category = 'info' # Flash message category
login_manager.login_message = 'Please log in to access this page.'