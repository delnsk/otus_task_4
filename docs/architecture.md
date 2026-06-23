# Архитектура: LangChain Task Manager Agent

> **Обязательно читать перед любыми изменениями в коде.**  
> Если решение меняет структуру компонентов — обнови этот файл.

---

## 1. Обзор системы

Система состоит из двух независимых сервисов, запускаемых через Docker Compose:

| Сервис | Технология | Назначение |
|--------|-----------|-----------|
| `api` | FastAPI + uvicorn | Mock REST API для хранения задач (in-memory) |
| `agent` | LangChain + OpenRouter | NLP-агент, вызывающий API по запросу пользователя |

Взаимодействие: пользователь отправляет запрос на естественном языке → агент интерпретирует его → вызывает нужный HTTP-эндпоинт через LangChain tool → возвращает структурированный ответ.

---

## 2. Диаграмма нод LangChain (поток выполнения)

```mermaid
flowchart TD
    User(["👤 Пользователь"])
    User -->|"python main.py 'запрос'"| CLI

    subgraph CLI_LAYER ["Точка входа"]
        CLI["main.py\nload_dotenv · sys.argv\nформатирует вывод"]
    end

    CLI -->|input: str| AE

    subgraph AGENT ["🤖 LangChain AgentExecutor (LCEL)"]
        AE["AgentExecutor\nverbose=True\nhandle_parsing_errors=True"]
        AE -->|{"input", "agent_scratchpad"}| PT
        PT["ChatPromptTemplate\n① SystemMessage ← prompts/system.md\n② HumanMessage {input}\n③ MessagesPlaceholder agent_scratchpad"]
        PT -->|formatted messages| LLM
        LLM["ChatOpenAI\nbase_url: OpenRouter\nmodel: gpt-4o-mini"]
        LLM -->|AIMessage| DEC{tool_calls\nв ответе?}
        DEC -->|"нет → finish"| FA["Финальный\nответ"]
        DEC -->|"да → вызов tool"| TE["ToolExecutor\n(intermediate step)"]
        TE -->|ToolMessage result| AE
    end

    subgraph TOOLS ["🔧 agent/tools.py — LangChain Tools"]
        TE --> T1["create_task\n@tool"]
        TE --> T2["get_task\n@tool"]
        TE --> T3["update_task_status\n@tool"]
        TE --> T4["delete_task\n@tool"]
        TE --> T5["list_tasks\n@tool"]
        TE --> T6["get_statistics\n@tool"]
    end

    subgraph API_SERVER ["🌐 api/server.py — FastAPI :8000"]
        T1 -->|"POST /tasks"| STORE
        T2 -->|"GET /tasks/{id}"| STORE
        T3 -->|"PATCH /tasks/{id}/status"| STORE
        T4 -->|"DELETE /tasks/{id}"| STORE
        T5 -->|"GET /tasks"| STORE
        T6 -->|"GET /tasks/stats"| STORE
        STORE[("💾 In-Memory Dict\ntasks: dict[int, Task]")]
    end

    FA --> RF["agent/response.py\nformat_response()"]
    RF -->|"Status / Action / Data / Errors"| User
```

---

## 3. Компоненты

### 3.1 `api/server.py` — Mock FastAPI сервер

- **Запускается** независимо от агента: `uvicorn api.server:app --port 8000`
- **Хранилище:** in-memory `dict[int, Task]`, сбрасывается при перезапуске
- **Модель данных:**

```python
class Task(BaseModel):
    id: int
    title: str
    description: str = ""
    status: Literal["pending", "in_progress", "done"] = "pending"
    created_at: str  # ISO-8601
```

- **Эндпоинты:**

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/tasks` | Создать задачу |
| GET | `/tasks` | Список всех задач (фильтр `?status=`) |
| GET | `/tasks/{id}` | Получить задачу по ID |
| PATCH | `/tasks/{id}/status` | Обновить статус |
| DELETE | `/tasks/{id}` | Удалить задачу |
| GET | `/tasks/stats` | Статистика по статусам |

### 3.2 `agent/tools.py` — LangChain Tools

- Каждый tool декорирован `@tool` (или `StructuredTool.from_function`)
- Внутри: `httpx.post/get/patch/delete` к `API_BASE_URL` из `.env`
- **Обязательный debug-вывод:** `print(f"[DEBUG {tool_name}] {result}")`
- Возвращает `json.dumps(result, ensure_ascii=False)`

### 3.3 `agent/agent.py` — Сборка агента

```
ChatOpenAI (OpenRouter)
    ↓ bind_tools([6 tools])
ChatPromptTemplate (system.md + human + scratchpad)
    ↓ pipe (|)
create_tool_calling_agent
    ↓
AgentExecutor
```

### 3.4 `prompts/system.md` — Системный промпт

Содержит:
- Роль: Task Manager API Operator
- Доступные операции (список tool-ов)
- Правило: **всегда использовать tool**, не придумывать данные
- Контракт ответа (см. ниже)

### 3.5 `agent/response.py` — Форматирование вывода

Контракт ответа агента (строгий формат):

```
Status: success | error
Action: <описание выполненного действия>
Data: <JSON-результат API или пустая строка>
Errors: <сообщение об ошибке или None>
```

### 3.6 `main.py` — CLI Entry Point

```bash
python main.py "создай задачу 'Написать тесты'"
```

Порядок работы: загрузить `.env` → распарсить аргумент → вызвать `AgentExecutor.invoke` → вывести `format_response(output)`.

---

## 4. Структура файлов

```
otus_task_4/
├── api/
│   └── server.py              # FastAPI mock сервер
├── agent/
│   ├── tools.py               # 6 LangChain tools с HTTP-вызовами
│   ├── agent.py               # Сборка AgentExecutor
│   └── response.py            # Форматирование контракта ответа
├── prompts/
│   └── system.md              # Системный промпт агента
├── tests/
│   └── test_queries.md        # 5 тестовых запросов + результаты
├── docs/
│   ├── architecture.md        # ← этот файл
│   ├── plan.md
│   ├── source_task.md
│   └── prompts.md
├── docker/
│   └── (зарезервировано для кастомных образов)
├── main.py                    # CLI-точка входа
├── Dockerfile                 # Единый образ для обоих сервисов
├── docker-compose.yml         # Оркестрация: api + agent
├── requirements.txt
├── .env.example               # Шаблон переменных окружения
├── .env                       # НЕ коммитится
├── .gitignore
└── report.md
```

---

## 5. Деплой: Docker & Docker Compose

### 5.1 Принцип контейнеризации

Используется **один Dockerfile** для обоих сервисов — образ содержит весь код проекта. Разные сервисы различаются только командой запуска (`command` в docker-compose).

```
┌─────────────────────────────────────┐
│         Docker Compose              │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │  api         │  │  agent      │ │
│  │  :8000       │  │  (one-shot) │ │
│  │  FastAPI     │  │  LangChain  │ │
│  └──────┬───────┘  └──────┬──────┘ │
│         │    tasknet       │        │
│         └────────┬─────────┘        │
└──────────────────┼──────────────────┘
                   │
             bridge network
```

### 5.2 `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: запуск API-сервера
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.3 `docker-compose.yml`

```yaml
version: "3.9"

services:
  api:
    build: .
    command: uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    networks:
      - tasknet
    healthcheck:
      test: ["CMD", "python", "-c", "import httpx; httpx.get('http://localhost:8000/tasks')"]
      interval: 5s
      timeout: 3s
      retries: 5

  agent:
    build: .
    command: python main.py "${QUERY:-покажи все задачи}"
    environment:
      - API_BASE_URL=http://api:8000
    env_file:
      - .env
    depends_on:
      api:
        condition: service_healthy
    networks:
      - tasknet

networks:
  tasknet:
    driver: bridge
```

> **Важно:** в сервисе `agent` переменная `API_BASE_URL` перекрывает значение из `.env`, чтобы использовался hostname `api` (имя Docker-сервиса), а не `localhost`.

### 5.4 Команды запуска

```bash
# 1. Скопировать шаблон переменных окружения
cp .env.example .env
# Вставить OPENROUTER_API_KEY в .env

# 2. Собрать образы
docker compose build

# 3. Запустить только API-сервер (в фоне)
docker compose up api -d

# 4. Запустить агента с конкретным запросом
QUERY="создай задачу 'Написать тесты'" docker compose run --rm agent

# 5. Или запустить сразу оба сервиса (API + один запрос агента)
docker compose up

# 6. Остановить всё
docker compose down
```

### 5.5 Локальный запуск без Docker

```bash
# Терминал 1: запустить API
uvicorn api.server:app --port 8000 --reload

# Терминал 2: запустить агента
python main.py "покажи все задачи"
```

---

## 6. Переменные окружения

| Переменная | Пример | Описание |
|-----------|--------|----------|
| `OPENROUTER_API_KEY` | `sk-or-...` | Ключ OpenRouter (обязательно) |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | Базовый URL OpenRouter |
| `OPENROUTER_MODEL` | `openai/gpt-4o-mini` | Модель (любая поддерживаемая OpenRouter) |
| `API_BASE_URL` | `http://localhost:8000` | URL FastAPI-сервера (в Docker: `http://api:8000`) |

---

## 7. Принятые архитектурные решения (ADR)

| Решение | Обоснование |
|---------|-------------|
| Единый `Dockerfile` для api и agent | Код общий, различается только команда запуска |
| In-memory хранилище в FastAPI | Достаточно для учебного проекта, исключает зависимость от БД |
| OpenRouter как LLM-провайдер | OpenAI-совместимый интерфейс, поддерживает tool calling, без привязки к конкретному вендору |
| `create_tool_calling_agent` вместо ReAct | Tool calling надёжнее для структурированных вызовов API |
| `httpx` вместо `requests` | Современный async-ready клиент, совместим с FastAPI-экосистемой |
| Контракт ответа через `response.py` | Изолирует форматирование от логики агента, упрощает тестирование |
