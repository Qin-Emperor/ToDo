# ToDo

ToDo is a web application for task management built with Flask. It supports user registration and login, task creation and management, asynchronous notifications via Celery, and a REST API with JWT authentication.

## Features

- User registration and login
- Create, update, and delete tasks
- Asynchronous email notifications (Celery + Redis)
- REST API with JWT authentication
- Database migrations (Flask-Migrate)
- Form validation (WTForms)
- Modular structure with Blueprints and API namespaces

## Technologies

- Python 3.x
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Login
- Flask-Mail
- Flask-JWT-Extended
- Flask-CORS
- Flask-RESTx
- Celery
- Redis
- WTForms

## Quick Start

1. **Clone the repository:**
   ```
   git clone https://github.com/Qin-Emperor/ToDo.git
   cd ToDo
   ```

2. **Create and activate a virtual environment:**
   ```
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Create a `.env` file based on `.env.example` and fill in your values:**
   ```
   cp .env.example .env
   # or copy and edit manually
   ```

5. **Initialize the database:**
   ```
   flask db upgrade
   ```

6. **Start Redis (if not already running):**
   ```
   redis-server
   ```

7. **Start the Celery worker:**
   ```
   celery -A make_celery worker --loglevel=info -P solo
   ```

8. **Run the Flask application:**
   ```
   flask run
   ```

## Project Structure

```
ToDo/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── forms.py
│   ├── main.py
│   ├── auth.py
│   ├── tasks.py
│   ├── apis/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── tasks.py
│   ├── static/
│   └── templates/
│       ├── base.html
│       ├── main/
│       │   ├── index.html
│       │   ├── search.html
│       │   └── update_task.html
│       └── auth/
│           ├── login.html
│           └── register.html
├── migrations/
├── .env.example
├── .gitignore
├── config.py
├── make_celery.py
├── requirements.txt
└── README.md
```

## Notes

- Add your real values to the `.env` file (secret keys, mail credentials, etc.).
- Do not commit your `.env` file to a public repository.
- On Windows, use the `-P solo` pool option for Celery.

## License

This project is for portfolio and educational purposes.