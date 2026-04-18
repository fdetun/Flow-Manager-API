from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Flow Manager",
    description="Run a sequence of tasks with conditions that decide what happens next.",
    version="1.0.0",
)

app.include_router(router)
