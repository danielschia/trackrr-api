from app import app as flask_app
from model.dashboard import Dashboard


async def list_dashboards(user_id: int) -> list[dict]:
    """Lista todos os dashboards de um usuário."""
    with flask_app.app_context():
        dashboards = Dashboard.query.filter_by(user_id=user_id).all()
        return [d.lightweight_dict() for d in dashboards]