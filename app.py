import os
from pathlib import Path

from dotenv import load_dotenv
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_openapi3.models.info import Info
from flask_openapi3.openapi import OpenAPI

from database.base import db
from model.user import User
from routes.auth import auth_api_bp
from routes.dashboards import dashboards_api_bp
from routes.lists import lists_api_bp
from routes.tasks import tasks_api_bp

load_dotenv(Path(__file__).resolve().parent / ".env")

info = Info(
    title="Trackr API",
    version="1.0.0",
    description="API for the Trackr application",
)
app = OpenAPI(__name__, info=info)

# Get allowed origins from environment variable. It must include the local static web app port.
allowed_origins = os.getenv(
    "CORS_ORIGINS"
)
CORS(
    app,
    resources={r"/*": {"origins": allowed_origins}},
    supports_credentials=True,
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///trackrr.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-me")
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

db.init_app(app)
JWTManager(app)

app.register_api(auth_api_bp)
app.register_api(dashboards_api_bp)
app.register_api(lists_api_bp)
app.register_api(tasks_api_bp)

with app.app_context():
    db.create_all()


@app.cli.command("db_create")
def db_create():
    db.create_all()
    print("Database created")


@app.cli.command("db_drop")
def db_drop():
    db.drop_all()
    print("Database dropped")


@app.cli.command("db_seed")
def db_seed():
    test_user = User(username="Stephen Hawking", email="admin@admin.com", password="admin")
    db.session.add(test_user)
    db.session.commit()
    print("Database seeded")