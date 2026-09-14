from flask import Response, jsonify, make_response
from flask_jwt_extended import create_access_token, set_access_cookies
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag
from pydantic import BaseModel, Field

from database.base import db
from model.user import User
from services.AuthService.build_user import build_new_user
from services.AuthService.validate_signup import validate_sign_up_input

auth_tag = Tag(name="Auth", description="Operations related to authentication")
auth_api_bp = APIBlueprint("auth_api", __name__)

class SignupBody(BaseModel):
    username: str = Field(min_length=1, description="The username of the new user")
    email: str = Field(min_length=1, description="The email of the new user")
    password: str = Field(min_length=1, description="The password of the new user")

class LoginBody(BaseModel):
    username: str = Field(min_length=1, description="The username of the user")
    password: str = Field(min_length=1, description="The password of the user")


class TokenResponse(BaseModel):
    access_token: str = Field(description="JWT access token")

class ErrorResponse(BaseModel):
    error: str = Field(description="Error message")


@auth_api_bp.post("/signup", tags=[auth_tag], responses={"400": ErrorResponse, "201": TokenResponse})
def api_signup(body: SignupBody):
    username = body.username
    email = body.email
    password = body.password

    validation_error = validate_sign_up_input(username, email, password)
    if validation_error:
        return validation_error

    new_user = build_new_user(username, email, password)
    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=str(new_user.id))
    response: Response = make_response(jsonify({"access_token": access_token}), 201)
    set_access_cookies(response, access_token)
    return response

@auth_api_bp.post("/login", tags=[auth_tag], responses={"400": ErrorResponse, "401": ErrorResponse, "200": TokenResponse})
def api_login(body: LoginBody):
    username = body.username
    password = body.password

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    response: Response = make_response(jsonify({"access_token": access_token}), 200)
    set_access_cookies(response, access_token)
    return response