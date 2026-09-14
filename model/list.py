from sqlalchemy.orm import relationship

from database.base import db


class List(db.Model):
    __tablename__ = 'lists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=True)
    position = db.Column(db.Integer, nullable=False, default=1000, server_default='1000')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dashboard_id = db.Column(db.Integer, db.ForeignKey('dashboards.id'), nullable=False)

    user = relationship('User', back_populates='lists')
    dashboard = relationship('Dashboard', back_populates='lists')
    tasks = relationship('Task', back_populates='list', cascade='all, delete-orphan', order_by='Task.position')

    def __init__(self, name:str, description:str|None, user_id:int, dashboard_id:int, position:int=1000):
        self.name = name
        self.description = description
        self.user_id = user_id
        self.dashboard_id = dashboard_id
        self.position = position

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'dashboard_id': self.dashboard_id,
            'position': self.position,
            'tasks': [task.to_dict() for task in self.tasks]
        }

    def lightweight_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'dashboard_id': self.dashboard_id,
            'position': self.position
        }