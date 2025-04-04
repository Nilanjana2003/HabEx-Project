# models.py
from extensions import db,login_manager
from flask_login import UserMixin # Import UserMixin for Flask-Login
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt # For password hashing

# Define the user_loader function required by Flask-Login
# It loads a user object from the database based on the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relationships: Define one-to-many relationships with Expense and Habit
    expenses = db.relationship('Expense', backref='owner', lazy=True, cascade="all, delete-orphan")
    habits = db.relationship('Habit', backref='owner', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        # Use bcrypt for strong hashing
        pwhash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.password_hash = pwhash.decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def __repr__(self):
        return f'<User {self.username}>'

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today) # Use date.today for default
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    # Foreign Key to link Expense to a User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Expense {self.id}: {self.category} - {self.amount}>'

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today) # Use date.today for default
    habit_name = db.Column(db.String(150), nullable=False)
    # Status: True for completed, False for not completed/logged
    status = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.String(200), nullable=True) # Added optional description based on form
    # Foreign Key to link Habit to a User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Habit {self.id}: {self.habit_name} on {self.date}>'

