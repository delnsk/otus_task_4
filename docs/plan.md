# План реализации: LangChain-агент «Task Manager»

## Обзор

**Тема:** Управление задачами через естественный язык  
**API:** Mock-сервер на FastAPI (запускается внутри репозитория)  
**LLM:** OpenRouter (OpenAI-совместимый интерфейс, модель по выбору, например `openai/gpt-4o-mini`)  
**Фреймворк агента:** LangChain (LCEL + `create_tool_calling_agent`)

### Инструменты агента (6 штук)

| # | Tool | HTTP-метод | Эндпоинт |
|---|------|-----------|---------|
| 1 | `create_task` | POST | `/tasks` |
| 2 | `get_task` | GET | `/tasks/{id}` |
| 3 | `update_task_status` | PATCH | `/tasks/{id}/status` |
| 4 | `delete_task` | DELETE | `/tasks/{id}` |
| 5 | `list_tasks` | GET | `/tasks` |
| 6 | `get_statistics` | GET | `/tasks/stats` |

---

## Структура проекта

```
otus_task_4/
├── api/
│   └── server.py          # Mock FastAPI-сервер
├── agent/
│   ├── tools.py           # LangChain tools (6 инструментов)
│   ├── agent.py           # Сборка агента (LLM + tools + prompt)
│   └── response.py        # Форматирование контракта ответа
├── prompts/
│   └── system.md          # Системный prompt агента
├── docs/
│   ├── architecture.md    # Архитектура системы + Mermaid-диаграмма
│   ├── source_task.md
│   ├── plan.md            # Этот файл
│   └── prompts.md         # Журнал промптов (авто)
├── tests/
│   └── test_queries.md    # 5 тестовых запросов + ответы
├── main.py                # CLI-точка входа
├── Dockerfile             # Единый образ для api и agent
├── docker-compose.yml     # Оркестрация: сервисы api + agent
├── requirements.txt
├── .env.example
├── .env                   # НЕ коммитится
├── .gitignore
└── report.md
```

---

## Пошаговый план реализации

### Шаг 1. Инициализация проекта

1. Убедиться что `.gitignore` содержит `.env` и `__pycache__`.
2. Создать `requirements.txt`:
   ```
   langchain>=0.3
   langchain-openai>=0.2
   fastapi>=0.110
   uvicorn>=0.29
   httpx>=0.27
   python-dotenv>=1.0
   pydantic>=2.0
   ```
3. Создать `.env.example`:
   ```dotenv
   OPENROUTER_API_KEY=your_key_here
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   OPENROUTER_MODEL=openai/gpt-4o-mini
   API_BASE_URL=http://localhost:8000
   ```

---

### Шаг 2. Mock FastAPI-сервер (`api/server.py`)

Реализовать сервер с in-memory хранилищем (`dict`).

**Модель задачи:**
```python
class Task(BaseModel):
    id: int
    title: str
    description: str = ""
    status: str = "pending"   # pending | in_progress | done
    created_at: str
```

**Эндпоинты:**
- `POST /tasks` — создать задачу
- `GET /tasks` — список всех задач (опционально: фильтр по `status`)
- `GET /tasks/{id}` — получить задачу по ID
- `PATCH /tasks/{id}/status` — обновить статус (`{"status": "done"}`)
- `DELETE /tasks/{id}` — удалить задачу
- `GET /tasks/stats` — статистика (всего, по статусам)

Запуск: `uvicorn api.server:app --port 8000`

---

### Шаг 3. Системный промпт (`prompts/system.md`)

Написать системный prompt с:
- ролью агента (Task Manager API Operator);
- списком доступных операций;
- правилами: всегда использовать tool для операций, никогда не придумывать данные;
- контрактом ответа (формат вывода).

**Контракт ответа:**
```
Status: success | error
Action: <описание выполненного действия>
Data: <JSON-результат API>
Errors: <сообщение об ошибке, если есть>
```

---

### Шаг 4. LangChain Tools (`agent/tools.py`)

Для каждого инструмента:
1. Определить Pydantic-схему входных параметров.
2. Обернуть HTTP-запрос к FastAPI через `httpx`.
3. Добавить `print()`/логирование результата tool (для дебага).
4. Задекорировать через `@tool` или `StructuredTool.from_function`.

Пример структуры одного tool:
```python
@tool
def create_task(title: str, description: str = "") -> str:
    """Создать новую задачу с заданным названием и описанием."""
    response = httpx.post(f"{API_BASE_URL}/tasks", json={...})
    result = response.json()
    print(f"[DEBUG create_task] response: {result}")
    return json.dumps(result, ensure_ascii=False)
```

---

### Шаг 5. Сборка агента (`agent/agent.py`)

1. Инициализировать `ChatOpenAI` с `base_url=OPENROUTER_BASE_URL`, `api_key=OPENROUTER_API_KEY`, `model=OPENROUTER_MODEL`.
2. Загрузить системный prompt из `prompts/system.md`.
3. Создать `ChatPromptTemplate` с `SystemMessage` + `HumanMessage` + `MessagesPlaceholder("agent_scratchpad")`.
4. Собрать агента через `create_tool_calling_agent(llm, tools, prompt)`.
5. Обернуть в `AgentExecutor(agent, tools, verbose=True)`.

---

### Шаг 6. Форматирование ответа (`agent/response.py`)

Написать функцию `format_response(agent_output: str) -> str`, которая:
- парсит вывод агента;
- возвращает структуру `Status / Action / Data / Errors`.

Если агент уже возвращает контракт — просто проксирует. Если нет — оборачивает.

---

### Шаг 7. CLI-точка входа (`main.py`)

```python
python main.py "создай задачу 'Написать тесты' с описанием 'unit-тесты для модуля auth'"
```

Логика:
1. Загрузить `.env`.
2. Принять аргумент из `sys.argv[1]`.
3. Вызвать `AgentExecutor.invoke({"input": user_query})`.
4. Вывести отформатированный ответ.
5. Обработать ошибки (нет API-сервера, нет ключа и т.д.).

---

### Шаг 8. Тестирование (5 запросов)

Выполнить и зафиксировать в `tests/test_queries.md`:

| # | Запрос | Ожидаемый tool | Ожидаемый результат |
|---|--------|---------------|---------------------|
| 1 | `"создай задачу 'Купить молоко'"` | `create_task` | Задача создана, ID возвращён |
| 2 | `"покажи все мои задачи"` | `list_tasks` | Список задач |
| 3 | `"отметь задачу 1 как выполненную"` | `update_task_status` | Статус обновлён на `done` |
| 4 | `"удали задачу с id 1"` | `delete_task` | Задача удалена |
| 5 | `"сколько у меня задач и какой у них статус?"` | `get_statistics` | Статистика по статусам |

Минимум 3 из 5 должны реально вызывать tool (все 5 вызывают).

---

### Шаг 9. Отчёт (`report.md`)

Написать отчёт со структурой:
- Описание проекта
- LLM: OpenRouter, как настроить (ключ, модель)
- API: Mock FastAPI, поддерживаемые операции
- Как запустить — **два варианта**: локально и через Docker Compose
- 5 тестовых запросов с реальным выводом
- Раздел «Использованные промпты»
- Ссылки на файлы: где объявлен tool, где debug-вывод

---

### Шаг 10. Dockerfile

Создать единый `Dockerfile` в корне репозитория:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Дефолтная команда — API-сервер (переопределяется в docker-compose)
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

Проверить: `docker build -t taskmanager .`

---

### Шаг 11. `docker-compose.yml`

Создать `docker-compose.yml` с двумя сервисами:

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

**Ключевой момент:** `agent` переопределяет `API_BASE_URL=http://api:8000` — используется DNS-имя Docker-сервиса, а не `localhost`.

Проверить:
```bash
cp .env.example .env          # заполнить OPENROUTER_API_KEY
docker compose build
docker compose up api -d      # поднять только API
docker compose logs api       # убедиться что сервер стартовал
QUERY="покажи все задачи" docker compose run --rm agent
docker compose down
```

---

## Порядок разработки (рекомендуемая последовательность)

```
Шаг 1   →  requirements.txt, .env.example, .gitignore
Шаг 2   →  api/server.py  (проверить curl/браузер)
Шаг 3   →  prompts/system.md
Шаг 4   →  agent/tools.py  (проверить каждый tool изолированно)
Шаг 5   →  agent/agent.py
Шаг 6   →  agent/response.py
Шаг 7   →  main.py  (e2e локальный запуск)
Шаг 8   →  tests/test_queries.md  (5 тестов)
Шаг 9   →  report.md
Шаг 10  →  Dockerfile
Шаг 11  →  docker-compose.yml  (e2e запуск в контейнерах)
```

---

## Проверочный чеклист

### Функциональность
- [ ] Агент запускается локально по инструкции из `report.md`
- [ ] Реализован минимум один API-tool с реальным HTTP-вызовом
- [ ] Debug-вывод tool в консоль (`print()`)
- [ ] Агент корректно выбирает нужный tool по запросу
- [ ] Ответ агента соответствует контракту (`Status/Action/Data/Errors`)
- [ ] Зафиксированы 5 тестовых запросов с результатами
- [ ] Все промпты оформлены в Markdown
- [ ] `.env` не закоммичен, есть `.env.example`

### Деплой (Docker)
- [ ] `Dockerfile` собирается без ошибок (`docker build`)
- [ ] `docker compose up api -d` поднимает FastAPI-сервер на порту 8000
- [ ] `docker compose run --rm agent` выполняет запрос агента
- [ ] Агент внутри контейнера достигает API по `http://api:8000`
- [ ] `docker compose down` корректно останавливает всё
