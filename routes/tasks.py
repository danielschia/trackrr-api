from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag
from pydantic import BaseModel, Field

from database.base import db
from model.dashboard import Dashboard
from model.list import List
from model.task import Task

tasks_api_bp = APIBlueprint("tasks_api", __name__)
tasks_tag = Tag(name="Tasks", description="Operations related to tasks")

class CreateTaskBody(BaseModel):
    title: str = Field(min_length=1, description="The title of the task")
    description: str | None = Field(default=None, description="The description of the task")
    list_id: int = Field(description="The ID of the list to which the task belongs")
    dashboard_id: int = Field(description="The ID of the dashboard to which the task belongs")
    position: int | None = Field(default=None, description="The position of the task in the list (optional)")


class UpdateTaskBody(BaseModel):
    title: str | None = Field(default=None, min_length=1, description="The title of the task")
    description: str | None = Field(default=None, description="The description of the task")
    list_id: int | None = Field(default=None, description="The ID of the list to which the task belongs")
    position: int | None = Field(default=None, description="The position of the task in the list (optional)")


class TaskPath(BaseModel):
    task_id: int = Field(description="The task ID")

class ErrorResponse(BaseModel):
    error: str = Field(description="Error message")


@tasks_api_bp.post("/tasks", tags=[tasks_tag], responses={"400": ErrorResponse, "201": CreateTaskBody})
@jwt_required()
def create_task(body: CreateTaskBody):
    current_user_id = int(get_jwt_identity())
    title_raw = body.title
    description_raw = body.description
    list_id = body.list_id
    dashboard_id = body.dashboard_id
    position = body.position

    title = title_raw.strip()
    if not title:
        return jsonify({"error": "Task title is required"}), 400

    if description_raw is None:
        description = ""
    elif not isinstance(description_raw, str):
        return jsonify({"error": "Description must be a string"}), 400
    else:
        description = description_raw

    if not dashboard_id:
        return jsonify({"error": "Dashboard id is required"}), 400

    if not list_id:
        return jsonify({"error": "List id is required"}), 400

    dashboard = Dashboard.query.filter_by(id=dashboard_id, user_id=current_user_id).first()
    if dashboard is None:
        return jsonify({"error": "Dashboard not found"}), 404

    list_obj = List.query.filter_by(id=list_id, user_id=current_user_id, dashboard_id=dashboard.id).first()
    if list_obj is None:
        return jsonify({"error": "List not found"}), 404

    new_task = Task(
        title=title,
        description=description,
        user_id=current_user_id,
        dashboard_id=dashboard.id,
        list_id=list_obj.id,
        position=position if position is not None else 1000
    )
    db.session.add(new_task)
    db.session.commit()

    return jsonify(new_task.to_dict()), 201

@tasks_api_bp.delete("/tasks/<int:task_id>", tags=[tasks_tag], responses={"404": ErrorResponse, "200": None})
@jwt_required()
def delete_task(path: TaskPath):
    task_id = path.task_id

    current_user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted successfully"}), 200

@tasks_api_bp.put("/tasks/<int:task_id>", tags=[tasks_tag], responses={"404": ErrorResponse, "200": CreateTaskBody})
@jwt_required()
def update_task(path: TaskPath, body: UpdateTaskBody):
    task_id = path.task_id
    current_user_id = int(get_jwt_identity())
    list_id = body.list_id
    title = body.title
    description = body.description
    position = body.position

    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    if list_id is not None:
        list_obj = List.query.filter_by(id=list_id, user_id=current_user_id, dashboard_id=task.dashboard_id).first()
        if list_obj is None:
            return jsonify({"error": "List not found"}), 404
        if list_obj.dashboard_id != task.dashboard_id:
            return jsonify({"error": "List does not belong to the same dashboard as the task"}), 400
        task.list_id = list_obj.id

    if position is not None:
        task.position = position

    if title is not None:
        title = title.strip()
        if title == "":
            return jsonify({"error": "Task title is required"}), 400
        task.title = title
    

    if description is not None:
        description = description.strip()
        if description == "":
            return jsonify({"error": "Task description cannot be empty"}), 400
        task.description = description

    db.session.commit()

    return jsonify(task.to_dict()), 200