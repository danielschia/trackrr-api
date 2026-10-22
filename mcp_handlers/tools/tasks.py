from app import app as flask_app
from database.base import db
from model.dashboard import Dashboard
from model.list import List
from model.task import Task
from services.reindex_tasks import _reindex_task_positions


async def list_tasks(user_id:int, list_id:int) -> list[dict]:
    """Lista todas as tasks de uma lista."""

    with flask_app.app_context():
        list_obj = List.query.filter_by(id=list_id, user_id=user_id).first()

        if list_obj is None:
            raise ValueError("Lista de tarefas não encontrada")

        tasks = Task.query.filter_by(
            user_id=user_id, 
            list_id=list_obj.id
        ).order_by(
            Task.position.asc(), 
            Task.id.asc()
        ).all()

        return [t.to_dict() for t in tasks]

async def create_task(
    user_id: int,
    title: str,
    description: str,
    list_id: int,
    dashboard_id: int
) -> dict:
    """Cria uma nova task em uma lista de um dashboard."""

    if not title:
        raise ValueError("Título da tarefa está vazio")

    with flask_app.app_context():
        dashboard = Dashboard.query.filter_by(id=dashboard_id, user_id=user_id).first()
        if dashboard is None:
            raise ValueError("Dashboard não encontrado")

        list_obj = List.query.filter_by(dashboard_id=dashboard_id, user_id=user_id, id=list_id).first()
        if list_obj is None:
            raise ValueError("Lista de tarefas não encontrada")

        tasks_in_list = Task.query.filter_by(
            user_id=user_id, 
            dashboard_id=dashboard.id, 
            list_id=list_obj.id
        ).order_by(
            Task.position.asc(), 
            Task.id.asc()
        ).all()

        target_position = len(tasks_in_list) + 1

        new_task = Task(
                user_id=user_id, 
                title=title, 
                dashboard_id=dashboard_id, 
                list_id=list_id, 
                description=description, 
                position=target_position
            )
        
        tasks_in_list.append(new_task)
        _reindex_task_positions(tasks_in_list)
        db.session.add(new_task)
        db.session.commit()
    
        return(new_task.to_dict())


