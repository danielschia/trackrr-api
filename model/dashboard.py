from sqlalchemy.orm import relationship

from database.base import db


class Dashboard(db.Model):
    __tablename__ = 'dashboards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = relationship('User', back_populates='dashboards')
    lists = relationship('List', back_populates='dashboard', cascade='all, delete-orphan', order_by='List.position' )
    tasks = relationship('Task', back_populates='dashboard', cascade='all, delete-orphan')

    def __init__(self, name:str, description:str, user_id:int):
        self.name = name
        self.description = description
        self.user_id = user_id

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'lists': [list.to_dict() for list in self.lists],
            'tasks': [task.to_dict() for task in self.tasks]
        }

    def lightweight_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id
        }