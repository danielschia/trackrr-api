from app import app as flask_app
from model.dashboard import Dashboard
from model.list import List


async def list_lists(user_id:int, dashboard_id:int) -> list[dict]:
    """Lista todas as listas de um dashboard"""

    with flask_app.app_context():
        dashboard = Dashboard.query.filter_by(user_id=user_id, id=dashboard_id).first()
        if dashboard is None:
            raise ValueError("Dashboard não encontrado")

        lists = List.query.filter_by(
            user_id=user_id,
            dashboard_id=dashboard_id
        ).order_by(
            List.position.asc(),
            List.id.asc()
        ).all()
    
        return [l.lightweight_dict() for l in lists]