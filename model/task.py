from sqlalchemy.orm import relationship

from database.base import db


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    position = db.Column(db.Integer, nullable=False, default=1000, server_default='1000')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dashboard_id = db.Column(db.Integer, db.ForeignKey('dashboards.id'), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'), nullable=False)

    user = relationship('User', back_populates='tasks')
    dashboard = relationship('Dashboard', back_populates='tasks')
    list = relationship('List', back_populates='tasks')

    def __init__(self, title:str, description:str, user_id:int, dashboard_id:int, list_id:int, position:int=1000):
        self.title = title
        self.description = description
        self.user_id = user_id
        self.dashboard_id = dashboard_id
        self.list_id = list_id
        self.position = position

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'user_id': self.user_id,
            'dashboard_id': self.dashboard_id,
            'list_id': self.list_id,
            'position': self.position
        }