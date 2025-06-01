from datetime import datetime

import pytz
from celery import shared_task
from flask import current_app
from flask_mail import Message
from sqlalchemy import select

from app import mail
from app.models import Task, TaskStatus
from . import db


@shared_task
def update_task_status(task_id):
    task = db.session.scalar(select(Task).where(Task.id == task_id))
    if task and task.deadline < datetime.now(pytz.UTC) and task.status != TaskStatus.COMPLETED:
        task.status = TaskStatus.OVERDUE
        db.session.commit()
        send_mail_async.delay(
            recipient=task.author.email,
            subject="Завдання прострочено",
            body=f"Ваше завдання \"{task.content}\" прострочено."
        )


@shared_task
def send_mail_async(recipient, subject, body):
    app = current_app._get_current_object()
    msg = Message(
        subject=subject,
        recipients=[recipient],
        sender=app.config["MAIL_USERNAME"]
    )
    msg.body = body
    with app.app_context():
        mail.send(msg)
