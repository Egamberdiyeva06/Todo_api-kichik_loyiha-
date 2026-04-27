from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime
from typing import List
from sqlalchemy.sql import func
from datetime import datetime


from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(length=50), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(length=50))
    last_name: Mapped[str] = mapped_column(String(length=50))
    hashed_password: Mapped[str] = mapped_column(String(length=200))


    todos: Mapped[List['Todo']] = relationship(back_populates='user', cascade='all, delete-orphan',
                                               lazy="selectin")
    

class Todo(Base):
    __tablename__ = 'todos'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index= True)
    name: Mapped[str] = mapped_column(String(length=100))
    description: Mapped[str] = mapped_column(String(length=200), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    priority: Mapped[str] = mapped_column(String(20), default="medium")
    deadline: Mapped[str] = mapped_column(String(50), nullable=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates='todos', lazy="selectin")
