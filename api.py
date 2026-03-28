from fastapi import APIRouter, HTTPException
from schemas import TodoCreate, Todo
from database import add_todo, get_all_todos, get_todo, update_todo, delete_todo

router = APIRouter(prefix="/todos", tags=["Todos"])

@router.get("/", response_model=list[Todo])
def read_todos():
    return get_all_todos()

@router.post("/", response_model=Todo)
def create_todo(todo: TodoCreate):
    return add_todo(todo.dict())

@router.get("/{todo_id}", response_model=Todo)
def read_todo(todo_id: int):
    todo = get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Vazifa topilmadi!")
    return todo

@router.put("/{todo_id}", response_model=Todo)
def update_todo_item(todo_id: int, todo: TodoCreate):
    updated = update_todo(todo_id, todo.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Vazifa topilmadi!")
    return updated

@router.delete("/{todo_id}")
def delete_todo_item(todo_id: int):
    delete_todo(todo_id)
    return {"detail": "Vazifa o'chirildi!"}