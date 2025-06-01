from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from sqlalchemy import select

from app import db
from app.models import User

auth_ns = Namespace("auth", description="Auth operations")

user_login_model = auth_ns.model("Login", {
    "email": fields.String(required=True, description="Email"),
    "password": fields.String(required=True, description="Password"),
})
user_register_model = auth_ns.model("Register", {
    "name": fields.String(required=True, description="Name"),
    "email": fields.String(required=True, description="Email"),
    "password": fields.String(required=True, description="Password"),
    "timezone": fields.String(required=False, description="Timezone", default="UTC"),
})


@auth_ns.route("/register")
class Register(Resource):
    @auth_ns.expect(user_register_model)
    def post(self):
        """User registration endpoint"""
        email = auth_ns.payload["email"]
        user = db.session.scalar(select(User).where(User.email == email))
        if user:
            return {"msg": "User already exists"}, 400
        new_user = User(
            name=auth_ns.payload["name"],
            email=email,
            timezone=auth_ns.payload.get("timezone", "UTC")
        )
        new_user.set_password(auth_ns.payload["password"])
        db.session.add(new_user)
        db.session.commit()
        return {"msg": "User created successfully"}, 201


@auth_ns.route("/login")
class Login(Resource):
    @auth_ns.expect(user_login_model)
    def post(self):
        """User login endpoint"""
        email = auth_ns.payload["email"]
        user = db.session.scalar(select(User).where(User.email == email))
        if user and user.check_password(auth_ns.payload["password"]):
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token}, 200
        return {"msg": "Invalid credentials"}, 401
