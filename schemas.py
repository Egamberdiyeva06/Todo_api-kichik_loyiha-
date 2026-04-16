from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    username: str = Field(min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(min_length=4, max_length=100)

class UserOut(UserBase):
    id: int
    todos: List["TodoOut"] = []

    model_config = ConfigDict(from_attributes=True)


class TodoBase(BaseModel):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(None, max_length=200)
    priority: Optional[str] = 'medium'
    deadline: Optional[str] = None

class TodoCreate(TodoBase):
    pass

class TodoUpdate(TodoBase):
    is_completed: bool = False

class TodoOut(TodoBase):
    id: int
    is_completed: bool
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


UserOut.model_rebuild()