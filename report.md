# Отчёт: LangChain Task Manager Agent

## Описание проекта

Минимальный AI-агент на LangChain, который принимает запросы на естественном языке и управляет задачами через Mock REST API.

**Компоненты:**
- `api/server.py` — FastAPI-сервер с in-memory хранилищем задач
- `agent/` — LangChain-агент с 6 HTTP-tools
- `main.py` — CLI-точка входа
- `prompts/system.md` — системный промпт с контрактом ответа

---

## LLM: OpenRouter

| Параметр | Значение |
|----------|----------|
| Провайдер | [OpenRouter](https://openrouter.ai/) |
| Модель по умолчанию | `openai/gpt-4o-mini` |
| Интерфейс | OpenAI-совместимый (`ChatOpenAI`) |

### Настройка

1. Получить API-ключ на https://openrouter.ai/
2. Скопировать шаблон: `cp .env.example .env`
3. Заполнить в `.env`:
   ```dotenv
   OPENROUTER_API_KEY=sk-or-v1-...
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   OPENROUTER_MODEL=openai/gpt-4o-mini
   API_BASE_URL=http://localhost:8000
   ```

---

## API: Mock FastAPI

**Файл:** `api/server.py`

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/tasks` | Создать задачу |
| GET | `/tasks` | Список задач (фильтр `?status=`) |
| GET | `/tasks/{id}` | Получить задачу |
| PATCH | `/tasks/{id}/status` | Обновить статус |
| DELETE | `/tasks/{id}` | Удалить задачу |
| GET | `/tasks/stats` | Статистика по статусам |

Статусы: `pending`, `in_progress`, `done`.

---

## Как запустить

### Вариант 1: Локально

**Терминал 1 — API:**
```bash
pip install -r requirements.txt
uvicorn api.server:app --port 8000 --reload
```

**Терминал 2 — Агент:**
```bash
cp .env.example .env   # заполнить OPENROUTER_API_KEY
python main.py "создай задачу 'Написать тесты'"
```

### Вариант 2: Docker Compose

```bash
cp .env.example .env   # заполнить OPENROUTER_API_KEY
docker compose build
docker compose up api -d
docker compose run --rm -e QUERY="покажи все задачи" agent
docker compose down
```

PowerShell (Windows):

```powershell
docker compose run --rm -e QUERY="покажи все задачи" agent
```

> В Docker агент использует `API_BASE_URL=http://api:8000` (DNS-имя сервиса).

---

## Инструменты агента

**Объявление tools:** `agent/tools.py`

| Tool | Строки | HTTP-вызов |
|------|--------|-----------|
| `create_task` | L22–L27 | `POST /tasks` |
| `get_task` | L30–L35 | `GET /tasks/{id}` |
| `update_task_status` | L38–L43 | `PATCH /tasks/{id}/status` |
| `delete_task` | L46–L51 | `DELETE /tasks/{id}` |
| `list_tasks` | L54–L60 | `GET /tasks` |
| `get_statistics` | L63–L68 | `GET /tasks/stats` |

**Debug-вывод:** каждый tool печатает `print(f"[DEBUG {name}] response: {result}")` — см. `agent/tools.py`.

**Сборка агента:** `agent/agent.py` — `create_agent()` (LangChain 1.x) + `ChatOpenAI` через OpenRouter.

**Контракт ответа:** `prompts/system.md` + форматирование в `agent/response.py`.

---

## Тестовые запросы

Подробные результаты: [`tests/test_queries.md`](tests/test_queries.md)

| # | Запрос | Ожидаемый tool | Результат |
|---|--------|---------------|-----------|
| 1 | `создай задачу 'Купить молоко'` | `create_task` | ✅ ID=1, status=pending |
| 2 | `покажи все мои задачи` | `list_tasks` | ✅ 1 задача в списке |
| 3 | `отметь задачу 1 как выполненную` | `update_task_status` | ✅ status=done |
| 4 | `удали задачу с id 1` | `delete_task` | ✅ deleted=true |
| 5 | `сколько у меня задач и какой у них статус?` | `get_statistics` | ✅ total=0 |

### Результат прогона (2026-06-23)

Все 5 E2E-тестов пройдены. Агент корректно выбирает tool, debug-вывод `[DEBUG ...]` подтверждает HTTP-вызовы, ответы соответствуют контракту `Status / Action / Data / Errors`.

Пример (запрос 1):
```
Status: success
Action: Created a new task
Data: {"id":1,"title":"Купить молоко","description":"","status":"pending","created_at":"2026-06-23T12:20:24.791524+00:00"}
Errors: None
```

---

## Использованные промпты

| Промпт | Файл |
|--------|------|
| Системный prompt агента | [`prompts/system.md`](prompts/system.md) |
| Журнал промптов разработки | [`docs/prompts.md`](docs/prompts.md) |

---

## Структура репозитория

```
api/server.py          — Mock FastAPI
agent/tools.py         — 6 LangChain tools
agent/agent.py         — сборка агента
agent/response.py      — контракт ответа
prompts/system.md      — системный prompt
main.py                — CLI
Dockerfile             — единый образ
docker-compose.yml     — api + agent
tests/test_queries.md  — тестовые запросы
docs/architecture.md   — архитектура
report.md              — этот файл
```
