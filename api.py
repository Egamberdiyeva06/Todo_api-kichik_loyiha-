
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from schemas import TodoCreate, TodoOut, TodoUpdate
from database import Base, get_db, engine
from models import Todo


Base.metadata.create_all(bind=engine)
api_router = APIRouter(prefix='/api/todo')


@api_router.post('/', response_model=TodoOut)
def create_todo(todo_in: TodoCreate, db = Depends(get_db)):
    todo = Todo(**todo_in.model_dump())

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return todo


@api_router.get('/', response_model=List[TodoOut])
def get_todos(db = Depends(get_db)):
    stmt = select(Todo)
    todos = db.scalars(stmt).all()

    return todos


@api_router.get("/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int, db = Depends(get_db)):
    stmt = select(Todo).where(Todo.id == todo_id)
    todo = db.scalar(stmt)
    if not todo:
        raise HTTPException(status_code=404, detail="Topilmadi")
    return todo



@api_router.put("/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, todo_in: TodoUpdate, db=Depends(get_db)):
    stmt = select(Todo).where(Todo.id == todo_id)
    todo: TodoOut = db.scalar(stmt)

    if not todo:
        raise HTTPException(status_code=404, detail= f"{todo_id} - raqamli vazifa topilmadi!")

    todo.name = todo_in.name
    todo.description = todo_in.description
    todo.is_completed = todo_in.is_completed

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return todo

@api_router.delete("/{todo_id}")
def delete_ticket(todo_id: int, db=Depends(get_db)):
    todo = db.get(Todo, todo_id)

    if not todo:
        raise HTTPException(status_code=404, detail=f"{todo_id} - raqamli vazifa topilmadi!")

    db.delete(todo)
    db.commit()

    return {"message": f"{todo_id} - raqamli vazifa o'chirildi!"}