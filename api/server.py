from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="Task Manager Mock API")

TaskStatus = Literal["pending", "in_progress", "done"]

_tasks: dict[int, dict] = {}
_next_id: int = 1


class Task(BaseModel):
    id: int
    title: str
    description: str = ""
    status: TaskStatus = "pending"
    created_at: str


class TaskCreate(BaseModel):
    title: str
    description: str = ""


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskStats(BaseModel):
    total: int
    pending: int
    in_progress: int
    done: int


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(body: TaskCreate) -> Task:
    global _next_id
    task = Task(
        id=_next_id,
        title=body.title,
        description=body.description,
        status="pending",
        created_at=_now_iso(),
    )
    _tasks[_next_id] = task.model_dump()
    _next_id += 1
    return task


@app.get("/tasks/stats", response_model=TaskStats)
def get_statistics() -> TaskStats:
    tasks = list(_tasks.values())
    return TaskStats(
        total=len(tasks),
        pending=sum(1 for t in tasks if t["status"] == "pending"),
        in_progress=sum(1 for t in tasks if t["status"] == "in_progress"),
        done=sum(1 for t in tasks if t["status"] == "done"),
    )


@app.get("/tasks", response_model=list[Task])
def list_tasks(
    status: TaskStatus | None = Query(default=None, description="Filter by status"),
) -> list[Task]:
    tasks = [Task(**t) for t in _tasks.values()]
    if status is not None:
        tasks = [t for t in tasks if t.status == status]
    return tasks


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return Task(**_tasks[task_id])


@app.patch("/tasks/{task_id}/status", response_model=Task)
def update_task_status(task_id: int, body: TaskStatusUpdate) -> Task:
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    _tasks[task_id]["status"] = body.status
    return Task(**_tasks[task_id])


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int) -> dict:
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    deleted = Task(**_tasks.pop(task_id))
    return {"deleted": True, "task": deleted.model_dump()}
