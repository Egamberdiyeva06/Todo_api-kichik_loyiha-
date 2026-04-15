import security
import jwt

from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from models import Todo, User
from database import get_db
from schemas import TodoCreate, TodoOut, TodoUpdate, UserCreate, UserOut, Token


users_router = APIRouter(prefix='/api/users', tags=["Users"])
todos_router = APIRouter(prefix='/api/todos', tags=["Todos"])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token yaroqsiz yoki muddati tugagan",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.scalar(select(User).where(User.id == int(user_id)))
    if user is None:
        raise credentials_exception
    return user


@users_router.post("/", response_model=UserOut)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.scalar(select(User).where(User.username == user_in.username))
    if existing_user:
        raise HTTPException(status_code=400, detail="Bunday foydalanuvchi nomi band")

    user_dict = user_in.model_dump()
    hashed_password = security.get_password_hash(user_dict.pop("password"))
    
    new_user = User(**user_dict, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@users_router.post('/login', response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == form.username))
    if not user:
        raise HTTPException(status_code=400, detail="Bunday foydalanuvchi mavjud emas")

    if not security.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Usename yoki parol noto'g'ri")

    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}



@users_router.get("/", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User).options(selectinload(User.todos))).all()
    return users



@todos_router.post('/', response_model=TodoOut)
def create_todo(todo_in: TodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_todo = Todo(**todo_in.model_dump(), user_id=current_user.id)

    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return new_todo


@todos_router.get('/', response_model=List[TodoOut])
def get_todos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todos = db.scalars(select(Todo).where(Todo.user_id == current_user.id)).all()

    return todos


@todos_router.put("/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, todo_in: TodoUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = db.scalar(select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id))
    if not todo:
        raise HTTPException(status_code=404, detail="Vazifa topilmadi")

    for key, value in todo_in.model_dump().items():
        setattr(todo, key, value)

    db.commit()
    db.refresh(todo)

    return todo



@todos_router.delete("/{todo_id}")
def delete_todo(todo_id: int, db: Session=Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = db.scalar(select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id))
    if not todo:
        raise HTTPException(status_code=404, detail="Vazifa topilmadi!")

    db.delete(todo)
    db.commit()

    return {"message": f"{todo_id} - raqamli vazifa o'chirildi!"}