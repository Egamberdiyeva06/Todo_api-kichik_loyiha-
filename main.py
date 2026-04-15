from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from api import users_router, todos_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(todos_router)

@app.get("/")
def home():
    return {"message": "API ishlamoqda. /docs ga kiring."}