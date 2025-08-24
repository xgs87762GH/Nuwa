# Task Management API Module
from fastapi import FastAPI, APIRouter

router = APIRouter()


@router.get("/tasks", tags=["tasks"])
async def list_tasks():
    """
    List all tasks.
    """
    return {"tasks": []}
