from flask import Blueprint
from flask_restx import Api

from .tasks import tasks_ns
from .auth import auth_ns

authorizations = {
    "Bearer": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}

api_bp = Blueprint("api", __name__, url_prefix="/api/v1/")
api = Api(
    api_bp,
    version="1.0",
    title="ToDo",
    authorizations=authorizations,
    security="Bearer"
)

api.add_namespace(tasks_ns)
api.add_namespace(auth_ns)
