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


def _reindex_task_positions(task_list):
    def sort_key(t):
        # None becomes 9999 to sort to end, otherwise use actual position
        position = t.position if t.position is not None else 9999
        task_id = t.id if t.id is not None else 0
        return (position, task_id)
    
    sorted_tasks = sorted(task_list, key=sort_key)
    
    for new_position, task in enumerate(sorted_tasks, start=1):
        task.position = new_position


def _reorder_task(task, new_list_id: int, new_position: int):
    current_list_id = task.list_id
    current_dashboard_id = task.dashboard_id

    if new_list_id != current_list_id:
        old_list_tasks = Task.query.filter_by(user_id=task.user_id, dashboard_id=current_dashboard_id, list_id=current_list_id).order_by(Task.position.asc(), Task.id.asc()).all()
        new_list_tasks = Task.query.filter_by(user_id=task.user_id, dashboard_id=current_dashboard_id, list_id=new_list_id).order_by(Task.position.asc(), Task.id.asc()).all()

        old_list_tasks = [item for item in old_list_tasks if item.id != task.id]
        new_list_tasks = [item for item in new_list_tasks if item.id != task.id]

        target_index = max(1, min(new_position, len(new_list_tasks) + 1))
        new_list_tasks.insert(target_index - 1, task)
        task.list_id = new_list_id

        _reindex_task_positions(old_list_tasks)
        _reindex_task_positions(new_list_tasks)
        return

    tasks_in_list = Task.query.filter_by(user_id=task.user_id, dashboard_id=current_dashboard_id, list_id=current_list_id).order_by(Task.position.asc(), Task.id.asc()).all()
    tasks_in_list = [item for item in tasks_in_list if item.id != task.id]
    target_index = max(1, min(new_position, len(tasks_in_list) + 1))
    tasks_in_list.insert(target_index - 1, task)
    _reindex_task_positions(tasks_in_list)


class CreateTaskBody(BaseModel):
    title: str = Field(min_length=1, description="The title of the task")
    description: str | None = Field(default=None, description="The description of the task")
    list_id: int = Field(description="The ID of the list to which the task belongs")
    dashboard_id: int = Field(description="The ID of the dashboard to which the task belongs")
    position: int = Field(default=1000, description="The position of the task in the list (optional)")


class UpdateTaskBody(BaseModel):
    title: str | None = Field(default=None, min_length=1, description="The title of the task")
    description: str | None = Field(default=None, description="The description of the task")
    list_id: int | None = Field(default=None, description="The ID of the list to which the task belongs")
    position: int = Field(default=1000, description="The position of the task in the list (optional)")


class ReorderTaskBody(BaseModel):
    task_id: int = Field(description="The task ID to move")
    list_id: int = Field(description="The destination list ID")
    position: int = Field(default=1, ge=1, description="The new 1-based position within the list")


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

    if position is not None and position < 1:
        return jsonify({"error": "Position must be a positive integer"}), 400

    tasks_in_list = Task.query.filter_by(user_id=current_user_id, dashboard_id=dashboard.id, list_id=list_obj.id).order_by(Task.position.asc(), Task.id.asc()).all()
    target_position = max(1, min(position if position is not None else len(tasks_in_list) + 1, len(tasks_in_list) + 1))

    new_task = Task(
        title=title,
        description=description,
        user_id=current_user_id,
        dashboard_id=dashboard.id,
        list_id=list_obj.id,
        position=target_position,
    )
    tasks_in_list.append(new_task)
    _reindex_task_positions(tasks_in_list)

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

@tasks_api_bp.post("/tasks/reorder", tags=[tasks_tag], responses={"400": ErrorResponse, "200": TaskPath})
@jwt_required()
def reorder_tasks(body: ReorderTaskBody):
    current_user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=body.task_id, user_id=current_user_id).first()
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    list_obj = List.query.filter_by(id=body.list_id, user_id=current_user_id, dashboard_id=task.dashboard_id).first()
    if list_obj is None:
        return jsonify({"error": "List not found"}), 404

    _reorder_task(task, list_obj.id, body.position)
    db.session.commit()

    return jsonify(task.to_dict()), 200


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
        target_list_id = list_obj.id
        target_position = position if position is not None else task.position
        _reorder_task(task, target_list_id, int(target_position))

    elif position is not None:
        _reorder_task(task, task.list_id, int(position))

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