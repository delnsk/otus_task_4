# Task Manager Agent

LangChain-агент для управления задачами через естественный язык. Принимает запрос пользователя, выбирает нужный HTTP-tool и возвращает структурированный ответ.

Подробный отчёт: [`report.md`](report.md)

---

## Требования

- Python 3.11+
- Ключ [OpenRouter](https://openrouter.ai/)
- (Опционально) Docker Desktop — для запуска через Compose

---

## Настройка

### 1. Установить зависимости

```bash
pip install -r requirements.txt
```

### 2. Настроить переменные окружения

```bash
cp .env.example .env
```

Заполните `.env`:

```dotenv
OPENROUTER_API_KEY=sk-or-v1-...          # ключ с https://openrouter.ai/keys
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4o-mini
API_BASE_URL=http://localhost:8000
```

> `.env` не коммитится. Ключ должен начинаться с `sk-or-`.

---

## Запуск

### Локально (два терминала)

**Терминал 1 — Mock API (FastAPI):**

```bash
uvicorn api.server:app --port 8000 --reload
```

**Терминал 2 — Агент:**

```bash
python main.py "создай задачу 'Написать тесты'"
python main.py "покажи все мои задачи"
python main.py "сколько у меня задач и какой у них статус?"
```

### Docker Compose

```bash
docker compose build
docker compose up api -d
docker compose run --rm -e QUERY="покажи все задачи" agent
docker compose down
```

**PowerShell (Windows):** синтаксис `QUERY=... command` не работает — используйте `-e` или `$env:`:

```powershell
docker compose run --rm -e QUERY="покажи все задачи" agent
# или
$env:QUERY = "покажи все задачи"; docker compose run --rm agent
```

> В Docker агент автоматически использует `API_BASE_URL=http://api:8000`.

---

## API (Mock FastAPI)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/tasks` | Создать задачу |
| GET | `/tasks` | Список задач |
| GET | `/tasks/{id}` | Получить задачу |
| PATCH | `/tasks/{id}/status` | Обновить статус |
| DELETE | `/tasks/{id}` | Удалить задачу |
| GET | `/tasks/stats` | Статистика |

Статусы: `pending`, `in_progress`, `done`.

---

## Инструменты агента

6 LangChain tools в [`agent/tools.py`](agent/tools.py): `create_task`, `get_task`, `update_task_status`, `delete_task`, `list_tasks`, `get_statistics`.

Каждый tool делает HTTP-запрос к Mock API и пишет debug-вывод в консоль: `[DEBUG <tool_name>] response: {...}`.

---

## Контракт ответа

```
Status: success | error
Action: <описание выполненного действия>
Data: <JSON-результат API>
Errors: <сообщение об ошибке или None>
```

Описание: [`prompts/system.md`](prompts/system.md), форматирование: [`agent/response.py`](agent/response.py).

---

## Тестовые запросы

5 проверочных запросов с результатами: [`tests/test_queries.md`](tests/test_queries.md)

---

## Структура проекта

```
api/server.py          — Mock FastAPI
agent/tools.py         — 6 LangChain tools
agent/agent.py         — сборка агента (OpenRouter)
agent/response.py      — контракт ответа
prompts/system.md      — системный prompt
main.py                — CLI
Dockerfile             — единый образ
docker-compose.yml     — api + agent
tests/test_queries.md  — тестовые запросы
docs/architecture.md   — архитектура
report.md              — отчёт
```

---

## Troubleshooting

### `WinError 10013` / порт 8000 занят

Порт уже используется — часто одновременно **Docker** (`docker compose up api`) и **локальный uvicorn**.

**Вариант A — только локально:**
```powershell
docker compose down
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
uvicorn api.server:app --port 8000 --reload
```

**Вариант B — только Docker:**
```powershell
# не запускайте uvicorn локально
docker compose up api -d
docker compose run --rm -e QUERY="покажи все задачи" agent
```

**Вариант C — другой порт локально:**
```powershell
uvicorn api.server:app --port 8001 --reload
$env:API_BASE_URL = "http://localhost:8001"; python main.py "покажи все задачи"
```
