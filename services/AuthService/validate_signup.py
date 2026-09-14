from flask import jsonify

from model.user import User


def validate_sign_up_input(username: str | None, email: str | None, password: str | None):
    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400

    if not isinstance(username, str) or not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"error": "Username, email, and password must be strings"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    return None