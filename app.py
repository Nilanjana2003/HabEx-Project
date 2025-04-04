# app.py
# app.py (near the top imports)

import matplotlib
matplotlib.use('Agg') # <--- MAKE SURE THIS LINE IS HERE and ABOVE the next line
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from config import Config
from extensions import db, login_manager
from models import User, Expense, Habit
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime, date
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# --- Application Factory ---
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Initialize Extensions ---
    db.init_app(app)
    login_manager.init_app(app)

    # --- Create Database Tables ---
    with app.app_context():
        db.create_all() # Creates tables if they don't exist

    # --- Routes ---

    # --- Authentication Routes ---
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        # This route now handles both login and registration based on form submit button name
        if request.method == 'POST':
            # Determine if it's login or registration
            action = request.form.get('action')

            if action == 'register':
                username = request.form.get('reg-username')
                password = request.form.get('reg-password')
                # Add more validation as needed (e.g., password complexity)
                if not username or not password:
                    flash('Username and password are required for registration.', 'error')
                    return redirect(url_for('index'))

                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    flash('Username already exists. Please choose a different one or login.', 'warning')
                    return redirect(url_for('index'))

                new_user = User(username=username)
                new_user.set_password(password) # Hash the password
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('index')) # Redirect to login after registration

            elif action == 'login':
                username = request.form.get('login-username')
                password = request.form.get('login-password')
                remember = True if request.form.get('remember-me') else False # Checkbox

                if not username or not password:
                    flash('Username and password are required for login.', 'error')
                    return redirect(url_for('index'))

                user = User.query.filter_by(username=username).first()

                # Check if user exists and password is correct
                if not user or not user.check_password(password):
                    flash('Invalid username or password.', 'error')
                    return redirect(url_for('index'))

                # Log the user in
                login_user(user, remember=remember)
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard')) # Redirect to dashboard after login

        # If GET request or failed POST, show the index page
        return render_template('index.html')

    @app.route('/logout')
    @login_required # Ensure user is logged in to logout
    def logout():
        logout_user()
        flash('You have been logged out.', 'success')
        return redirect(url_for('index'))

    # --- Core Application Routes ---
    @app.route('/dashboard')
    @login_required
    def dashboard():
        # You could fetch some summary data here later
        return render_template('dashboard.html', username=current_user.username)

    # --- Expense Routes ---
    @app.route('/add_expense', methods=['GET', 'POST'])
    @login_required
    def add_expense():
        if request.method == 'POST':
            expense_date_str = request.form.get('current-date')
            expense_name = request.form.get('expense-name') # We map this to description
            category = request.form.get('category')
            amount_str = request.form.get('amount')
            description_optional = request.form.get('description', '')

            if not all([expense_date_str, expense_name, category, amount_str]):
                 flash('Please fill in all required fields!', 'error')
                 return redirect(url_for('add_expense'))

            try:
                expense_date = datetime.strptime(expense_date_str, '%Y-%m-%d').date()
                amount_float = float(amount_str)
                if amount_float <= 0: raise ValueError("Amount must be positive.")

                full_description = expense_name
                if description_optional: full_description += f" - {description_optional}"

                new_expense = Expense(
                    date=expense_date, category=category, amount=amount_float,
                    description=full_description, owner=current_user # Link to current user
                )
                db.session.add(new_expense)
                db.session.commit()
                flash(f'Expense "{expense_name}" added successfully!', 'success')
                return redirect(url_for('add_expense'))

            except ValueError as ve:
                 db.session.rollback()
                 flash(f'Invalid input: {ve}', 'error')
            except Exception as e:
                 db.session.rollback()
                 flash(f'An error occurred: {e}', 'error')

            return redirect(url_for('add_expense')) # Redirect back on error too

        return render_template('add_expenses.html') # Show form on GET

    @app.route('/view_expenses')
    @login_required
    def view_expenses():
        user_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
        return render_template('view_expenses.html', expenses=user_expenses)

    @app.route('/delete_expense/<int:expense_id>', methods=['POST'])
    @login_required
    def delete_expense(expense_id):
        expense_to_delete = Expense.query.get_or_404(expense_id)
        if expense_to_delete.owner != current_user:
            flash('You do not have permission to delete this expense.', 'error')
            return redirect(url_for('view_expenses')) # Or abort(403)

        try:
            db.session.delete(expense_to_delete)
            db.session.commit()
            flash('Expense deleted successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting expense: {e}', 'error')

        return redirect(url_for('view_expenses'))


    # --- Habit Routes ---
    @app.route('/add_habit', methods=['GET', 'POST'])
    @login_required
    def add_habit():
        if request.method == 'POST':
            habit_date_str = request.form.get('current-date')
            habit_name = request.form.get('habit-name')
            description = request.form.get('habit-description') # Get description
            # Assuming 'status' indicates completion for the day added
            status = True # Or get from a checkbox if you add one: bool(request.form.get('status'))

            if not all([habit_date_str, habit_name]):
                 flash('Date and Habit Name are required!', 'error')
                 return redirect(url_for('add_habit'))

            try:
                 habit_date = datetime.strptime(habit_date_str, '%Y-%m-%d').date()

                 # Check if habit for this name and date already exists for the user
                 existing_habit = Habit.query.filter_by(
                     user_id=current_user.id,
                     habit_name=habit_name,
                     date=habit_date
                 ).first()

                 if existing_habit:
                     flash(f'Habit "{habit_name}" already logged for {habit_date_str}.', 'warning')
                 else:
                     new_habit = Habit(
                         date=habit_date, habit_name=habit_name, status=status,
                         description=description, owner=current_user # Link to user
                     )
                     db.session.add(new_habit)
                     db.session.commit()
                     flash(f'Habit "{habit_name}" logged successfully for {habit_date_str}!', 'success')

                 return redirect(url_for('add_habit')) # Redirect back to form

            except ValueError:
                 db.session.rollback()
                 flash('Invalid date format.', 'error')
            except Exception as e:
                 db.session.rollback()
                 flash(f'An error occurred: {e}', 'error')

            return redirect(url_for('add_habit'))

        return render_template('add_habits.html') # Show form on GET

    @app.route('/view_habits')
    @login_required
    def view_habits():
        # Fetch habits, maybe grouped by name or just listed by date
        user_habits = Habit.query.filter_by(user_id=current_user.id).order_by(Habit.date.desc(), Habit.habit_name).all()
        return render_template('view_habits.html', habits=user_habits)

    @app.route('/delete_habit/<int:habit_id>', methods=['POST'])
    @login_required
    def delete_habit(habit_id):
        habit_to_delete = Habit.query.get_or_404(habit_id)
        if habit_to_delete.owner != current_user:
            flash('You do not have permission to delete this habit log.', 'error')
            return redirect(url_for('view_habits')) # Or abort(403)

        try:
            db.session.delete(habit_to_delete)
            db.session.commit()
            flash('Habit log deleted successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting habit log: {e}', 'error')

        return redirect(url_for('view_habits'))


    # --- Analytics Routes ---
    def create_plot(fig):
        """Helper function to convert matplotlib figure to base64 image"""
        buf = io.BytesIO()
        canvas = FigureCanvas(fig)
        canvas.print_png(buf)
        plt.close(fig) # Close the figure to free memory
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    @app.route('/analyze_expenses')
    @login_required
    def analyze_expenses():
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
        if not expenses:
            flash('No expense data available for analysis.', 'info')
            return render_template('analyze_expenses.html', plot_cat=None, plot_trend=None)

        df = pd.DataFrame([(e.date, e.category, e.amount) for e in expenses], columns=['Date', 'Category', 'Amount'])
        df['Date'] = pd.to_datetime(df['Date'])

        # --- Category Plot (Pie Chart) ---
        category_summary = df.groupby('Category')['Amount'].sum()
        fig_cat, ax_cat = plt.subplots(figsize=(6, 4)) # Smaller figure size
        category_summary.plot(kind='pie', ax=ax_cat, autopct='%1.1f%%', startangle=90)
        ax_cat.set_ylabel('') # Remove y-label for pie chart
        ax_cat.set_title('Expense Breakdown by Category')
        plt.tight_layout()
        plot_cat_base64 = create_plot(fig_cat)


        # --- Monthly Trend Plot (Bar Chart) ---
        df['Month'] = df['Date'].dt.to_period('M')
        monthly_summary = df.groupby('Month')['Amount'].sum()
        monthly_summary.index = monthly_summary.index.strftime('%Y-%m') # Format index for display

        fig_trend, ax_trend = plt.subplots(figsize=(8, 4)) # Wider figure for trend
        monthly_summary.plot(kind='bar', ax=ax_trend)
        ax_trend.set_title('Monthly Spending Trend')
        ax_trend.set_xlabel('Month')
        ax_trend.set_ylabel('Total Amount (₹)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plot_trend_base64 = create_plot(fig_trend)

        return render_template('analyze_expenses.html', plot_cat=plot_cat_base64, plot_trend=plot_trend_base64)


    @app.route('/analyze_habits')
    @login_required
    def analyze_habits():
        # Get unique habit names for the dropdown
        unique_habits = db.session.query(Habit.habit_name).filter_by(user_id=current_user.id).distinct().all()
        habit_names = [h[0] for h in unique_habits]

        # Initially render the page with the habit list
        return render_template('analyze_habits.html', habit_names=habit_names)


    @app.route('/get_habit_analysis/<habit_name>')
    @login_required
    def get_habit_analysis(habit_name):
        # Fetch data for the specific habit
        habits = Habit.query.filter_by(user_id=current_user.id, habit_name=habit_name).order_by(Habit.date).all()

        if not habits:
            return jsonify({'error': 'No data found for this habit.'}), 404

        df = pd.DataFrame([(h.date, h.status) for h in habits], columns=['Date', 'Status'])
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')

        # --- Simple Consistency Calculation (Example) ---
        total_days = (df['Date'].max() - df['Date'].min()).days + 1
        completed_days = df['Status'].sum()
        consistency = (completed_days / total_days) * 100 if total_days > 0 else 0

        # --- Simple Streak Calculation (Example) ---
        current_streak = 0
        max_streak = 0
        df['Date_Diff'] = df['Date'].diff().dt.days
        streak = 0
        for index, row in df.iterrows():
            if row['Status']: # If completed
                if row['Date_Diff'] == 1 or pd.isna(row['Date_Diff']): # Continuous day or first day
                    streak += 1
                else: # Gap in days
                    streak = 1 # Reset streak
            else: # If not completed
                 streak = 0 # Reset streak
            max_streak = max(max_streak, streak)
            current_streak = streak # Update current streak based on last entry

        # You could create a plot (e.g., heatmap or calendar view) here as well
        # For now, just return data as JSON

        return jsonify({
            'habit_name': habit_name,
            'total_logs': len(df),
            'completed_logs': int(completed_days), # Convert numpy.int64
            'consistency_percent': round(consistency, 2),
            'current_streak': int(current_streak), # Convert numpy.int64
            'max_streak': int(max_streak) # Convert numpy.int64
        })


    return app

# --- Run the App ---
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) # Turn off debug mode in production