# Тестовые запросы агента

**Дата прогона:** 2026-06-23  
**Окружение:** Windows, Python 3.11, API на `http://localhost:8000`, модель `openai/gpt-4o-mini`

---

## Предварительная проверка tools (без LLM)

Все 6 инструментов успешно вызывают Mock API (`agent/tools.py` → `http://localhost:8000`):

| Tool | Результат |
|------|-----------|
| `create_task` | Задача создана, ID возвращён |
| `list_tasks` | Список задач |
| `update_task_status` | Статус обновлён |
| `get_statistics` | Статистика по статусам |
| `delete_task` | Задача удалена |

Debug-вывод подтверждён: `[DEBUG <tool_name>] response: {...}`

---

## E2E-тесты через агента (5 запросов)

**Команда:** `python main.py "<запрос>"`  
**Предусловие:** API запущен (`uvicorn api.server:app --port 8000`), `.env` заполнен.

| # | Запрос | Ожидаемый tool | Фактический tool | Статус |
|---|--------|---------------|-----------------|--------|
| 1 | `"создай задачу 'Купить молоко'"` | `create_task` | `create_task` | ✅ |
| 2 | `"покажи все мои задачи"` | `list_tasks` | `list_tasks` | ✅ |
| 3 | `"отметь задачу 1 как выполненную"` | `update_task_status` | `update_task_status` | ✅ |
| 4 | `"удали задачу с id 1"` | `delete_task` | `delete_task` | ✅ |
| 5 | `"сколько у меня задач и какой у них статус?"` | `get_statistics` | `get_statistics` | ✅ |

Все 5 запросов привели к реальному вызову tool (подтверждено debug-логом `[DEBUG ...]` и trace LangChain).

---

### Запрос 1 — `create_task`

**Trace (фрагмент):**
```
tool_calls=[{'name': 'create_task', 'args': {'title': 'Купить молоко'}, ...}]
[DEBUG create_task] response: {'id': 1, 'title': 'Купить молоко', ...}
```

**Ответ агента:**
```
Status: success
Action: Created a new task
Data: {"id":1,"title":"Купить молоко","description":"","status":"pending","created_at":"2026-06-23T12:20:24.791524+00:00"}
Errors: None
```

---

### Запрос 2 — `list_tasks`

**Ответ агента:**
```
Status: success
Action: Listed all tasks
Data: [{"id":1,"title":"Купить молоко","description":"","status":"pending","created_at":"2026-06-23T12:20:24.791524+00:00"}]
Errors: None
```

---

### Запрос 3 — `update_task_status`

**Ответ агента:**
```
Status: success
Action: Task 1 marked as done
Data: {"id":1,"title":"Купить молоко","description":"","status":"done","created_at":"2026-06-23T12:20:24.791524+00:00"}
Errors: None
```

---

### Запрос 4 — `delete_task`

**Ответ агента:**
```
Status: success
Action: Deleted task with ID 1
Data: {"deleted":true,"task":{"id":1,"title":"Купить молоко","description":"","status":"done","created_at":"2026-06-23T12:20:24.791524+00:00"}}
Errors: None
```

---

### Запрос 5 — `get_statistics`

**Ответ агента:**
```
Status: success
Action: Retrieved task statistics
Data: {"total":0,"pending":0,"in_progress":0,"done":0}
Errors: None
```

> После удаления задачи в тесте 4 статистика корректно показывает 0 задач.
