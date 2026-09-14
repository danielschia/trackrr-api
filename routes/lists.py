from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag
from pydantic import BaseModel, Field

from database.base import db
from model.dashboard import Dashboard
from model.list import List

lists_api_bp = APIBlueprint("lists_api", __name__)

class CreateListBody(BaseModel):
    name: str = Field(min_length=1, description="The name of the list")
    description: str | None = Field(default=None, description="The description of the list")
    dashboard_id: int = Field(description="The ID of the dashboard to which the list belongs")


class UpdateListBody(BaseModel):
    name: str = Field(min_length=1, description="The name of the list")
    description: str | None = Field(default=None, description="The description of the list")


class ListResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    user_id: int
    dashboard_id: int
    position: int | None = None

class ListsResponse(BaseModel):
    lists: list[ListResponse] = Field(description="List of lists")


class ListsQuery(BaseModel):
    dashboard_id: int = Field(description="The dashboard ID used to filter lists")


class ListPath(BaseModel):
    list_id: int = Field(description="The list ID")

class ErrorResponse(BaseModel):
    error: str = Field(description="Error message")

@lists_api_bp.post("/lists", tags=[Tag(name="Lists", description="Operations related to lists")], responses={400: ErrorResponse, 201: CreateListBody})
@jwt_required()
def create_list(body: CreateListBody):
    current_user_id = int(get_jwt_identity())
    name = body.name.strip()
    description = body.description or ""
    dashboard_id = body.dashboard_id

    if not name:
        return jsonify({"error": "List name is required"}), 400

    if not isinstance(name, str):
        return jsonify({"error": "List name must be a string"}), 400

    if description is not None and not isinstance(description, str):
        return jsonify({"error": "Description must be a string"}), 400

    if not dashboard_id:
        return jsonify({"error": "Dashboard id is required"}), 400

    dashboard = Dashboard.query.filter_by(id=dashboard_id, user_id=current_user_id).first()
    if dashboard is None:
        return jsonify({"error": "Dashboard not found"}), 404

    new_list = List(
        name=name,
        description=description,
        user_id=current_user_id,
        dashboard_id=dashboard.id,
    )
    db.session.add(new_list)
    db.session.commit()

    return jsonify(new_list.to_dict()), 201

@lists_api_bp.delete("/lists/<int:list_id>", tags=[Tag(name="Lists", description="Operations related to lists")], responses={404: ErrorResponse, 200: None})
@jwt_required()
def delete_list(path: ListPath):
    current_user_id = int(get_jwt_identity())
    list_to_delete = List.query.filter_by(id=path.list_id, user_id=current_user_id).first()

    if list_to_delete is None:
        return jsonify({"error": "List not found"}), 404

    db.session.delete(list_to_delete)
    db.session.commit()

    return jsonify({"message": "List deleted successfully"}), 200

@lists_api_bp.put("/lists/<int:list_id>", tags=[Tag(name="Lists", description="Operations related to lists")], responses={404: ErrorResponse, 200: CreateListBody})
@jwt_required()
def update_list(path: ListPath, body: UpdateListBody):
    current_user_id = int(get_jwt_identity())
    name = body.name.strip()
    description = body.description or ""

    list_to_update = List.query.filter_by(id=path.list_id, user_id=current_user_id).first()

    if list_to_update is None:
        return jsonify({"error": "List not found"}), 404

    if not name:
        return jsonify({"error": "List name is required"}), 400

    if not isinstance(name, str):
        return jsonify({"error": "List name must be a string"}), 400

    if description is not None and not isinstance(description, str):
        return jsonify({"error": "Description must be a string"}), 400

    list_to_update.name = name
    list_to_update.description = description
    db.session.commit()

    return jsonify(list_to_update.to_dict()), 200

@lists_api_bp.get("/lists", tags=[Tag(name="Lists", description="Operations related to lists")], responses={404: ErrorResponse, 200: ListsResponse})
@jwt_required()
def list_lists(query: ListsQuery):
    current_user_id = int(get_jwt_identity())
    lists = List.query.filter_by(user_id=current_user_id, dashboard_id=query.dashboard_id).all()

    if not lists:
        return jsonify({"error": "No lists found for this dashboard"}), 404

    return jsonify({"lists": [list_obj.lightweight_dict() for list_obj in lists]}), 200

@lists_api_bp.get("/lists/<int:list_id>", tags=[Tag(name="Lists", description="Operations related to lists")], responses={404: ErrorResponse, 200: ListResponse})
@jwt_required()
def list_detail(path: ListPath):
    current_user_id = int(get_jwt_identity())
    list_obj = List.query.filter_by(id=path.list_id, user_id=current_user_id).first()

    if list_obj is None:
        return jsonify({"error": "List not found"}), 404

    return jsonify(list_obj.to_dict()), 200