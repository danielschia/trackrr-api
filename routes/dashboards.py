from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag
from pydantic import BaseModel, Field
from sqlalchemy.orm import selectinload

from database.base import db
from model.dashboard import Dashboard
from model.list import List

dashboards_api_bp = APIBlueprint("dashboards_api", __name__)

class CreateDashboardBody(BaseModel):
    name: str = Field(min_length=1, description="The name of the dashboard")
    description: str | None = Field(default=None, description="The description of the dashboard")


class DashboardPath(BaseModel):
    dashboard_id: int = Field(description="The dashboard ID")


class DashboardResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    user_id: int


class DashboardsResponse(BaseModel):
    dashboards: list[DashboardResponse] = Field(description="List of dashboards")

class ErrorResponse(BaseModel):
    error: str = Field(description="Error message")


@dashboards_api_bp.get("/dashboards", tags=[Tag(name="Dashboards", description="Operations related to dashboards")], responses={"200": DashboardsResponse})
@jwt_required()
def list_dashboards():
    current_user_id = int(get_jwt_identity())
    dashboards = Dashboard.query.filter_by(user_id=current_user_id).all()
    
    return jsonify([dashboard.lightweight_dict() for dashboard in dashboards]), 200


@dashboards_api_bp.post("/dashboards", tags=[Tag(name="Dashboards", description="Operations related to dashboards")], responses={"400": ErrorResponse, "201": DashboardResponse})
@jwt_required()
def create_dashboard(body: CreateDashboardBody):
    current_user_id = int(get_jwt_identity())
    name = body.name
    description = body.description

    if not name:
        return jsonify({"error": "Dashboard name is required"}), 400

    if not isinstance(name, str):
        return jsonify({"error": "Dashboard name must be a string"}), 400

    if description is not None and not isinstance(description, str):
        return jsonify({"error": "Description must be a string"}), 400

    if description is None:
        description = ""

    new_dashboard = Dashboard(name=name, description=description, user_id=current_user_id)
    db.session.add(new_dashboard)
    db.session.commit()

    return jsonify(new_dashboard.to_dict()), 201


@dashboards_api_bp.get("/dashboards/<int:dashboard_id>", tags=[Tag(name="Dashboards", description="Operations related to dashboards")], responses={"404": ErrorResponse, "200": DashboardResponse})
@jwt_required()
def dashboard_detail(path: DashboardPath):
    current_user_id = int(get_jwt_identity())
    dashboard = Dashboard.query.options(selectinload(Dashboard.lists).selectinload(List.tasks)).filter_by(id=path.dashboard_id, user_id=current_user_id).first()
    if dashboard is None:
        return jsonify({"error": "Dashboard not found"}), 404

    return jsonify(dashboard.to_dict()), 200

@dashboards_api_bp.delete("/dashboards/<int:dashboard_id>", tags=[Tag(name="Dashboards", description="Operations related to dashboards")], responses={"404": ErrorResponse, "204": None})
@jwt_required()
def delete_dashboard(path: DashboardPath):
    current_user_id = int(get_jwt_identity())
    dashboard = Dashboard.query.filter_by(id=path.dashboard_id, user_id=current_user_id).first()
    if dashboard is None:
        return jsonify({"error": "Dashboard not found"}), 404

    db.session.delete(dashboard)
    db.session.commit()

    return "", 204
