import security
import jwt
import asyncio

from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, APIRouter, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from email_service import send_welcome_email
from models import Todo, User
from database import get_db
from schemas import TodoCreate, TodoOut, TodoUpdate, UserCreate, UserOut, Token


users_router = APIRouter(prefix='/api/users', tags=["Users"])
todos_router = APIRouter(prefix='/api/todos', tags=["Todos"])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
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

    user = await db.scalar(select(User).where(User.id == int(user_id)))
    if user is None:
        raise credentials_exception
    
    return user


@users_router.post("/", response_model=UserOut)
async def create_user(bg_tasks: BackgroundTasks, user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await db.scalar(select(User).where(User.username == user_in.username))
    if existing_user:
        raise HTTPException(status_code=400, detail="Bunday foydalanuvchi nomi band")

    user_dict = user_in.model_dump()
    hashed_password = security.get_password_hash(user_dict.pop("password"))
    
    new_user = User(**user_dict, hashed_password=hashed_password)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    bg_tasks.add_task(send_welcome_email, f"{new_user.username}@gmail.com")

    return new_user


@users_router.post('/login', response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form.username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="Bunday foydalanuvchi mavjud emas")

    if not security.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Usename yoki parol noto'g'ri")

    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}



@users_router.get("/", response_model=List[UserOut])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).options(selectinload(User.todos)))
    users = result.scalars().all()
    return users



@todos_router.post('/', response_model=TodoOut)
async def create_todo(todo_in: TodoCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_todo = Todo(**todo_in.model_dump(), user_id=current_user.id)

    db.add(new_todo)
    await db.commit()
    await db.refresh(new_todo)

    return new_todo


@todos_router.get('/', response_model=List[TodoOut])
async def get_todos(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Todo).where(Todo.user_id == current_user.id))
    return result.scalars().all()


@todos_router.put("/{todo_id}", response_model=TodoOut)
async def update_todo(todo_id: int, todo_in: TodoUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = await db.scalar(select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id))
    if not todo:
        raise HTTPException(status_code=404, detail="Vazifa topilmadi")

    for key, value in todo_in.model_dump().items():
        setattr(todo, key, value)

    await db.commit()
    await db.refresh(todo)

    return todo



@todos_router.delete("/{todo_id}")
async def delete_todo(todo_id: int, db: AsyncSession=Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = await db.scalar(select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id))
    if not todo:
        raise HTTPException(status_code=404, detail="Vazifa topilmadi!")

    await db.delete(todo)
    await db.commit()

    return {"message": f"{todo_id} - raqamli vazifa o'chirildi!"}