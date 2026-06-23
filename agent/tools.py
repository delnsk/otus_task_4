import json
import os

import httpx
from langchain_core.tools import tool

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def _request(method: str, path: str, **kwargs) -> dict:
    url = f"{API_BASE_URL}{path}"
    with httpx.Client(timeout=10.0) as client:
        response = client.request(method, url, **kwargs)
        if response.status_code >= 400:
            return {"error": True, "status_code": response.status_code, "detail": response.text}
        if response.status_code == 204 or not response.content:
            return {}
        return response.json()


@tool
def create_task(title: str, description: str = "") -> str:
    """Создать новую задачу с заданным названием и описанием."""
    result = _request("POST", "/tasks", json={"title": title, "description": description})
    print(f"[DEBUG create_task] response: {result}")
    return json.dumps(result, ensure_ascii=False)


@tool
def get_task(task_id: int) -> str:
    """Получить задачу по ID."""
    result = _request("GET", f"/tasks/{task_id}")
    print(f"[DEBUG get_task] response: {result}")
    return json.dumps(result, ensure_ascii=False)


@tool
def update_task_status(task_id: int, status: str) -> str:
    """Обновить статус задачи. Допустимые значения: pending, in_progress, done."""
    result = _request("PATCH", f"/tasks/{task_id}/status", json={"status": status})
    print(f"[DEBUG update_task_status] response: {result}")
    return json.dumps(result, ensure_ascii=False)


@tool
def delete_task(task_id: int) -> str:
    """Удалить задачу по ID."""
    result = _request("DELETE", f"/tasks/{task_id}")
    print(f"[DEBUG delete_task] response: {result}")
    return json.dumps(result, ensure_ascii=False)


@tool
def list_tasks(status: str = "") -> str:
    """Получить список всех задач. Опционально фильтр по статусу: pending, in_progress, done."""
    params = {"status": status} if status else None
    result = _request("GET", "/tasks", params=params)
    print(f"[DEBUG list_tasks] response: {result}")
    return json.dumps(result, ensure_ascii=False)


@tool
def get_statistics() -> str:
    """Получить статистику задач: общее количество и количество по каждому статусу."""
    result = _request("GET", "/tasks/stats")
    print(f"[DEBUG get_statistics] response: {result}")
    return json.dumps(result, ensure_ascii=False)


ALL_TOOLS = [
    create_task,
    get_task,
    update_task_status,
    delete_task,
    list_tasks,
    get_statistics,
]
