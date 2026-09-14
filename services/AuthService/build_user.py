from model.user import User


def build_new_user(username: str, email: str, password: str) -> User:
    return User(username=username, email=email, password=password)