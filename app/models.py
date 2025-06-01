from datetime import datetime, timezone
from enum import Enum

from flask_login import UserMixin
from sqlalchemy import DateTime, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    email: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)

    tasks: Mapped["Task"] = relationship(
        back_populates="author",
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.name}>"


class TaskStatus(Enum):
    IN_PROGRESS = "в процесі"
    COMPLETED = "готово"
    OVERDUE = "прострочено"


class Task(db.Model):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(String(140))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc)
    )
    deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc)
    )
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus),
        default=TaskStatus.IN_PROGRESS
    )
    celery_id: Mapped[str] = mapped_column(String(50), nullable=True)

    author: Mapped[User] = relationship(back_populates="tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "deadline": self.deadline.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status.value,
            "celery_id": self.celery_id,
        }

    def __repr__(self):
        return f"<Task {self.content} (Status: {self.status})>"
