from fastapi import FastAPI
from api import router as todo_router

app = FastAPI(title="Todo API")

app.include_router(todo_router)

@app.get("/")
def root():
    return {"message": "Todo API ga xush kelibsiz!"}