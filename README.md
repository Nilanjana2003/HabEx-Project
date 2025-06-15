# HabEx: Expense & Habit Tracker 🎯
A web application which uses HTML,CSS,JS and Python Data Analytics tools to track and analyze a user's habits and expenses, ultimately leading to informed decisions and a balanced life.

HabEx is a full-stack web application designed to help users track their personal expenses and daily habits.The goal is a simple yet functional web app with a clean UI, full CRUD (Create, Read, Update, Delete) operations, and insightful analytics powered by Python.

This project was built as a personal portfolio piece to demonstrate skills in backend development with Flask, database management with SQLite, and data visualization with Pandas and Matplotlib.


## ✨ Features

* **Full CRUD for Expenses & Habits:** Users can add, view, edit, and delete both expense records and habit logs through dedicated pages.
* **Expense Analysis:** The application can generate and display a pie chart that shows the breakdown of expenses by category, providing a clear visual of spending patterns.
* **Habit Consistency Analysis:** Users can generate a bar chart that tracks the consistency of completed habits over time, helping to visualize their progress.
* **Central Dashboard:** A home page offers an overview and quick links to all major features of the application.
* **Persistent Storage:** All data is stored in a lightweight SQLite database, ensuring information is saved between sessions.

## 🛠️ Tech Stack

* **Backend:** Flask
* **Database:** SQLite with the Flask-SQLAlchemy ORM.
* **Data Analytics:** Pandas and Matplotlib libraries for data processing and visualization.
* **Frontend:** HTML, CSS, and Jinja2 for templating.


## 🗄️ Database Schema

The application uses two tables to store data:

1.  **`expenses` table:**
    * `id` (Integer, Primary Key)
    * `date` (Date)
    * `category` (String)
    * `amount` (Float)
    * `description` (String, nullable)
2.  **`habits` table:**
    * `id` (Integer, Primary Key)
    * `date` (Date)
    * `habit_name` (String)
    * `status` (Boolean)

## 🚀 Setup and Installation

To run this project locally, follow these steps:

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/Nilanjana2003/HabEx-Project.git
    cd HabEx-Project
    ```

2.  **Create and activate a virtual environment:**
    * **Windows:**
        ```sh
        python -m venv venv
        .\venv\Scripts\activate
        ```
    * **macOS / Linux:**
        ```sh
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install the required packages from `requirements.txt`:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```sh
    python app.py
    ```
    The application will start, and the database file (`habex.db`) will be automatically created in the `database` directory.

5.  Open your browser and navigate to `http://127.0.0.1:5000`.
