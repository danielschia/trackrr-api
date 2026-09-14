from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from database.base import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    dashboards = relationship('Dashboard', back_populates='user')
    lists = relationship('List', back_populates='user')
    tasks = relationship('Task', back_populates='user')

    def __init__(self, username:str, email:str, password:str):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password:str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password:str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'dashboards': [dashboard.to_dict() for dashboard in self.dashboards],
            'lists': [list.to_dict() for list in self.lists],
            'tasks': [task.to_dict() for task in self.tasks]
        }
