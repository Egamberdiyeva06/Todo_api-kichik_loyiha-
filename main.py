import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api import users_router, todos_router

app = FastAPI(title="Todo App API")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    start_time = time.time()
    response = await call_next(request)
    end_time = time.time()
    print(f"Response: {end_time - start_time} seconds")
    response.headers["X-Process-Time"] = str(end_time - start_time)
    return response


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