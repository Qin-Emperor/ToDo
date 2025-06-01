import pytz
from celery import Celery, Task
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

from config import Config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
jwt = JWTManager()
cors = CORS()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config.from_mapping(
        CELERY=dict(
            broker_url=app.config["CELERY_BROKER_URL"],
            result_backend=app.config["CELERY_RESULT_BACKEND"],
            task_ignore_result=True,
        ),
    )
    app.jinja_env.filters['utc_time_filter'] = utc_time_filter

    celery_init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    login_manager.init_app(app)

    from .main import main
    app.register_blueprint(main)

    from .auth import auth
    app.register_blueprint(auth)

    from .apis import api_bp
    app.register_blueprint(api_bp)

    return app


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def utc_time_filter(time, user_timezone):
    local_tz = pytz.timezone(user_timezone)
    local_time = time.astimezone(local_tz)
    return local_time.strftime("%Y-%m-%d %H:%M")
