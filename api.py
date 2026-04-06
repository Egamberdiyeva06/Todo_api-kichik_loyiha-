from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from schemas import UserCreate, UserOut, TodoCreate, TodoOut, TodoUpdate
from database import Base, get_db, engine
from models import Todo, User


Base.metadata.create_all(bind=engine)
users_router = APIRouter(prefix='/api/users', tags=["Users"])
todos_router = APIRouter(prefix='/api/todos', tags=["Todos"])



@users_router.post("/", response_model=UserOut)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = User(**user_in.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@users_router.get("/", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).options(selectinload(User.todos)).all()
    return users



@users_router.get("/{id}", response_model=UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).options(selectinload(User.todos)).filter(User.id == id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User topilmadi")

    return user


@users_router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Bunday user mavjud emas.")
    
    user.first_name = user_in.first_name
    user.last_name = user_in.last_name
    db.commit()
    db.refresh(user)

    return user


@users_router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Bunday user mavjud emas.")
    
    db.delete(user)
    db.commit()

    return {"message": "User o'chirildi!"}



@todos_router.post('/', response_model=TodoOut)
def create_todo(todo_in: TodoCreate, db: Session = Depends(get_db)):
    user = db.get(User, todo_in.user_id)
    if not user: 
        raise HTTPException(status_code=400, detail=f'{todo_in.user_id} idili user mavjud emas.')
    

    todo = Todo(**todo_in.model_dump())

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return todo


@todos_router.get('/', response_model=list[TodoOut])
def get_todos(db: Session = Depends(get_db)):
    stmt = select(Todo)
    todos = db.scalars(stmt).all()

    return todos


@todos_router.get("/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Topilmadi")
    return todo



@todos_router.put("/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, todo_in: TodoUpdate, db: Session=Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail= f"{todo_id} - raqamli vazifa topilmadi!")

    todo.name = todo_in.name
    todo.description = todo_in.description
    todo.is_completed = todo_in.is_completed


    db.commit()
    db.refresh(todo)

    return todo


@todos_router.delete("/{todo_id}")
def delete_todo(todo_id: int, db=Depends(get_db)):
    todo = db.get(Todo, todo_id)

    if not todo:
        raise HTTPException(status_code=404, detail=f"{todo_id} - raqamli vazifa topilmadi!")

    db.delete(todo)
    db.commit()

    return {"message": f"{todo_id} - raqamli vazifa o'chirildi!"}