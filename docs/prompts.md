# Журнал промптов

---

# Промпт 01

## Параметры

| Параметр | Значение |
| ----- | ----- |
| **Agent** | Cursor IDE |
| **Plugins, rules, skills, MCPs** | log-agent-prompts rule |
| **Context** | `docs/source_task.md` |
| **Mode** | agent |
| **Model** | auto |

## Текст промпта

```
Проанализируй задание @docs/source_task.md , уточни если есть вопросы, предложи выбрать "тему" и инструменты для агента (5 штук минимум), после чего создай пошаговый план реализации и запиши его в файл docs/plan.md
```

## Результат

```
Проанализировано задание на создание LangChain-агента. Пользователю предложены варианты темы, типа API и LLM-провайдера через AskQuestion.
Выбрано: тема — Task Manager, API — Mock FastAPI внутри репо, LLM — OpenRouter.
Определены 6 инструментов агента: create_task, get_task, update_task_status, delete_task, list_tasks, get_statistics.
Создан файл docs/plan.md с пошаговым планом реализации (9 шагов), структурой проекта и проверочным чеклистом.
Создан файл docs/prompts.md (этот журнал).
```

---

# Промпт 02

## Параметры

| Параметр | Значение |
| ----- | ----- |
| **Agent** | Cursor IDE |
| **Plugins, rules, skills, MCPs** | log-agent-prompts rule, architecture-reference rule, create-rule skill |
| **Context** | `docs/plan.md`, `docs/source_task.md`, `README.md` |
| **Mode** | agent |
| **Model** | auto |

## Текст промпта

```
как опытный тимлид проанализируй @docs/plan.md (возможно @docs/source_task.md) и создай для проекта файл с описанием архитектуры (возможно правило что бы cursor агент всегда в него смотрел), должен обязательно содержать mirmade диаграмму свзи нод langchain. так же добавь обязательно требования по деплою - создание докер контейнера и поднятие по docker compose up. Актуализируй если потребуется план
```

## Результат

```
Создан docs/architecture.md: обзор системы, Mermaid-диаграмма потока выполнения LangChain AgentExecutor (7 нод),
описание всех компонентов (api, agent/tools, agent/agent, prompts, response.py, main.py), таблица ADR.
Раздел деплоя: Dockerfile (единый образ), docker-compose.yml (сервисы api + agent, healthcheck, bridge-сеть),
команды запуска локально и через Docker.
Создано правило .cursor/rules/architecture-reference.mdc (alwaysApply: true) — агент читает architecture.md перед изменениями.
Обновлён docs/plan.md: новая структура файлов (Dockerfile, docker-compose.yml, docs/architecture.md),
добавлены шаги 10 (Dockerfile) и 11 (docker-compose.yml), расширен чеклист разделом «Деплой».
```

---

# Промпт 03

## Параметры

| Параметр | Значение |
| ----- | ----- |
| **Agent** | Cursor IDE |
| **Plugins, rules, skills, MCPs** | log-agent-prompts rule, architecture-reference rule |
| **Context** | `docs/plan.md`, `docs/architecture.md` |
| **Mode** | agent |
| **Model** | auto |

## Текст промпта

```
шаг за шагом выполни @docs/plan.md , если нужна ручная проверка или какие то дополнительные вопросы - сообщи
```

## Результат

```
Реализованы шаги 1–11 плана: .gitignore, requirements.txt, .env.example, api/server.py (6 эндпоинтов),
prompts/system.md, agent/tools.py (6 tools с httpx + debug print), agent/agent.py (LangChain 1.x create_agent),
agent/response.py, main.py, Dockerfile, docker-compose.yml, report.md, tests/test_queries.md, README.md.
API и tools проверены локально. E2E-тесты агента и Docker требуют ручной проверки: OPENROUTER_API_KEY в .env и запущенный Docker Desktop.
```

---

# Промпт 04

## Параметры

| Параметр | Значение |
| ----- | ----- |
| **Agent** | Cursor IDE |
| **Plugins, rules, skills, MCPs** | log-agent-prompts rule, architecture-reference rule |
| **Context** | `.env`, `README.md`, `report.md`, `tests/test_queries.md` |
| **Mode** | agent |
| **Model** | auto |

## Текст промпта

```
заполнил env,- прогони тесты и обнови необходимую документацию. так же дополни @README.md описанием необходимым для настройки и запуска агента (можно продублировать из @report.md )
```

## Результат

```
Попытка E2E-теста #1: OpenRouter вернул 401 User not found — ключ из .env не принят сервисом.
Обновлены README.md (полная инструкция по настройке и запуску), tests/test_queries.md (статус прогона и шаблон),
report.md (результат попытки). Остальные 4 теста не запускались до исправления ключа.
```

---

# Промпт 05

## Параметры

| Параметр | Значение |
| ----- | ----- |
| **Agent** | Cursor IDE |
| **Plugins, rules, skills, MCPs** | log-agent-prompts rule |
| **Context** | terminal output (PowerShell docker compose) |
| **Mode** | agent |
| **Model** | auto |

## Текст промпта

```
@c:\Users\admin\.cursor\projects\c-git-otus-otus-task-4\terminals\4.txt:341-348
```

## Результат

```
Объяснена ошибка: синтаксис QUERY="..." command — bash, в PowerShell не работает.
Исправление: docker compose run --rm -e QUERY="покажи все задачи" agent
Обновлены README.md и report.md с PowerShell-вариантами.
```

---

# Промпт 06

## Параметры

| Параметр | Значение |
| ----- | ----- |
| **Agent** | Cursor IDE |
| **Plugins, rules, skills, MCPs** | log-agent-prompts rule |
| **Context** | terminal output (docker compose agent 401) |
| **Mode** | agent |
| **Model** | auto |

## Текст промпта

```
@c:\Users\admin\.cursor\projects\c-git-otus-otus-task-4\terminals\4.txt:350-361
```

## Результат

```
Docker Compose работает корректно (API healthy, агент стартует). Ошибка 401 User not found — OpenRouter отклоняет OPENROUTER_API_KEY.
Улучшены сообщения об ошибке в main.py, нормализация ключа в agent.py, убран obsolete version из docker-compose.yml.
```

---

# Промпт 07

## Параметры

| Параметр | Значение |
| ----- | ----- |
| **Agent** | Cursor IDE |
| **Plugins, rules, skills, MCPs** | log-agent-prompts rule |
| **Context** | `.env`, `tests/test_queries.md`, `report.md` |
| **Mode** | agent |
| **Model** | auto |

## Текст промпта

```
поправил OPENROUTER_API_KEY, прогони тесты и поправь необходимую документацию
```

## Результат

```
Все 5 E2E-тестов пройдены успешно (create_task, list_tasks, update_task_status, delete_task, get_statistics).
Обновлены tests/test_queries.md (реальные ответы и trace) и report.md (итоги прогона).
```

---

# Промпт 08

## Параметры

| Параметр | Значение |
| ----- | ----- |
| **Agent** | Cursor IDE |
| **Plugins, rules, skills, MCPs** | log-agent-prompts rule |
| **Context** | terminal output (WinError 10013 port 8000) |
| **Mode** | agent |
| **Model** | auto |

## Текст промпта

```
@c:\Users\admin\.cursor\projects\c-git-otus-otus-task-4\terminals\4.txt:7-10
```

## Результат

```
Диагностика: порт 8000 занят python.exe (локальный uvicorn) и Docker api-контейнером.
WinError 10013 — попытка запустить второй uvicorn на занятом порту.
Решение: docker compose down ИЛИ не запускать uvicorn локально, ИЛИ другой порт.
Добавлен раздел Troubleshooting в README.md.
```

---

# Промпт 09

## Параметры

| Параметр | Значение |
| ----- | ----- |
| **Agent** | Cursor IDE |
| **Plugins, rules, skills, MCPs** | log-agent-prompts rule, architecture-reference rule |
| **Context** | @docs/source_task.md, @report.md |
| **Mode** | agent |
| **Model** | auto |

## Текст промпта

```
проверь удовлетворяет ли текущее решение и @report.md  начальным требованиям @docs/source_task.md
```

## Результат

```
Проведён аудит соответствия: решение и report.md в целом удовлетворяют требованиям source_task.md
(8/8 шагов и 7/7 критериев оценки). Зафиксированы мелкие замечания: нет ссылки на PR/ветку,
нет отдельного файла пользовательских шаблонов промптов, расхождение architecture.md с create_agent API,
номера строк в report.md сдвинуты на 1.
```
