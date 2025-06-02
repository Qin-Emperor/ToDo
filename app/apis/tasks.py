from celery.result import AsyncResult
from dateutil.parser import isoparse
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select

from app import db
from app.models import Task, TaskStatus
from app.tasks import update_task_status

tasks_ns = Namespace("tasks", description="Task operations")

task_model = tasks_ns.model("Task", {
    "content": fields.String(required=True, description="Task title"),
    "deadline": fields.DateTime(required=True, description="Task deadline"),
})


@tasks_ns.route("/")
class UserTaskList(Resource):
    @jwt_required()
    def get(self):
        """Get list of tasks for the current user"""
        user_id = get_jwt_identity()
        tasks = db.session.scalars(select(Task).where(Task.user_id == user_id)).all()
        return {"tasks": [task.to_dict() for task in tasks]}, 200

    @jwt_required()
    @tasks_ns.expect(task_model)
    def post(self):
        """Create a new task"""
        data = tasks_ns.payload
        user_id = get_jwt_identity()
        deadline = isoparse(data["deadline"])
        new_task = Task(
            content=data["content"],
            user_id=user_id,
            deadline=deadline
        )
        db.session.add(new_task)
        db.session.commit()
        result = update_task_status.apply_async((new_task.id,), eta=deadline)
        new_task.celery_id = result.id
        db.session.commit()
        return {"msg": "Task created", "task": new_task.to_dict()}, 201


@tasks_ns.route("/<int:task_id>")
class UserTask(Resource):
    @jwt_required()
    @tasks_ns.expect(task_model)
    def put(self, task_id):
        """Update a task by ID"""
        data = tasks_ns.payload
        task = db.session.scalar(select(Task).where(Task.id == task_id))
        task.content = data["content"]
        task.deadline = isoparse(data["deadline"])
        db.session.commit()
        result = update_task_status.apply_async((task.id,), eta=task.deadline)
        task.celery_id = result.id
        db.session.commit()
        return {"msg": "Task updated"}, 200

    @jwt_required()
    def delete(self, task_id):
        """Delete a task by ID"""
        task = db.session.scalar(select(Task).where(Task.id == task_id))
        if task.status != TaskStatus.COMPLETED:
            result = AsyncResult(task.celery_id)
            result.revoke(terminate=True)
        db.session.delete(task)
        db.session.commit()
        return {"msg": "Task deleted"}, 200


@tasks_ns.route("/complete/<int:task_id>")
class CompleteTask(Resource):
    @jwt_required()
    def post(self, task_id):
        """Mark a task as completed"""
        task = db.session.scalar(select(Task).where(Task.id == task_id))
        if task.status == TaskStatus.IN_PROGRESS or task.status == TaskStatus.OVERDUE:
            task.status = TaskStatus.COMPLETED
            AsyncResult(task.celery_id).revoke(terminate=True)
            db.session.commit()
            return {"msg": "Task marked as completed"}, 200
        return {"msg": "Task is already completed"}, 400