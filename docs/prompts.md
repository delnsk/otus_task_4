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
