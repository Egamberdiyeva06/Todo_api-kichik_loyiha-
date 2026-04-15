from pydantic import BaseModel, Field
from typing import List


class UserBase(BaseModel):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)


class UserCreate(UserBase):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=100)


class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(UserBase):
    id: int
    todos: List["TodoOut"] = Field(default_factory=list)

    class Config:
        from_attributes = True



class TodoBase(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=200)  
    user_id: int


    
class TodoCreate(TodoBase):
    pass  

class TodoUpdate(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=200)
    is_completed: bool = Field(default=False)


class TodoOut(TodoBase):
    id: int = Field(ge=1)
    is_completed: bool = Field(default=False)
    
    class Config:
        from_attributes = True