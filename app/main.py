from datetime import datetime, timezone

import pytz
from celery.result import AsyncResult
from flask import Blueprint, flash, render_template, redirect, url_for, request
from flask_login import current_user, login_required
from sqlalchemy import select

from app.tasks import update_task_status
from . import db
from .forms import AddTaskForm, UpdateTaskForm
from .models import Task, TaskStatus

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def index():
    form = AddTaskForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Спочатку треба увійти в акаунт!", category="error")
            return redirect(url_for("auth.login"))
        local_tz = pytz.timezone(current_user.timezone)
        local_deadline = local_tz.localize(form.deadline.data)
        utc_deadline = local_deadline.astimezone(pytz.utc)
        new_task = Task(
            content=form.content.data,
            user_id=current_user.id,
            deadline=utc_deadline
        )
        db.session.add(new_task)
        db.session.commit()
        result = update_task_status.apply_async((new_task.id,), eta=utc_deadline)
        new_task.celery_id = result.id
        db.session.commit()
        return redirect(url_for("main.index"))
    tasks = []
    if current_user.is_authenticated:
        tasks = db.session.scalars(
            select(Task)
            .where(Task.user_id == current_user.id)
            .order_by(Task.created_at.desc())
        ).all()
    return render_template("main/index.html", user=current_user, form=form, tasks=tasks)


@main.route("/search")
@login_required
def search():
    query = request.args.get("query")
    if query:
        tasks = db.session.scalars(
            select(Task)
            .where(Task.user_id == current_user.id)
            .where(Task.content.ilike(f"%{query}%"))
            .order_by(Task.created_at.desc())
        ).all()
    else:
        tasks = db.session.scalars(
            select(Task)
            .where(Task.user_id == current_user.id)
            .order_by(Task.created_at.desc())
        ).all()
    return render_template("main/search.html", tasks=tasks)


@main.route("/update_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def update_task(task_id):
    task = db.session.scalars(select(Task).where(Task.id == task_id)).first()
    local_timezone = pytz.timezone(current_user.timezone)
    task.deadline = task.deadline.astimezone(local_timezone)
    update_task_form = UpdateTaskForm(obj=task)
    if update_task_form.validate_on_submit():
        update_task_form.populate_obj(task)
        task.deadline = local_timezone.localize(task.deadline).astimezone(pytz.utc)
        if task.deadline > datetime.now(timezone.utc):
            task.status = TaskStatus.IN_PROGRESS
        db.session.commit()
        update_task_status.apply_async((task.id,), eta=task.deadline)
        return redirect(url_for('main.index'))
    return render_template("main/update_task.html", user=current_user, task=task, update_task_form=update_task_form)


@main.route("/delete_task/<int:task_id>")
@login_required
def delete_task(task_id):
    task = db.session.scalars(select(Task).where(Task.id == task_id, Task.user_id == current_user.id)).first()
    if task is None:
        return redirect(url_for("main.index"))
    result = AsyncResult(task.celery_id)
    result.revoke(terminate=True)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("main.index"))


@main.route("/complete_task/<int:task_id>")
@login_required
def complete_task(task_id):
    task = db.session.scalars(select(Task).where(Task.id == task_id, Task.user_id == current_user.id)).first()
    if task is None:
        return redirect(url_for("main.index"))
    result = AsyncResult(task.celery_id)
    result.revoke(terminate=True)
    task.status = TaskStatus.COMPLETED
    db.session.commit()
    return redirect(url_for("main.index"))
