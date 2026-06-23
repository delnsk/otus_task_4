import os
from pathlib import Path

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from agent.tools import ALL_TOOLS

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_system_prompt() -> str:
    path = PROJECT_ROOT / "prompts" / "system.md"
    return path.read_text(encoding="utf-8")


def _normalize_api_key(key: str) -> str:
    return key.strip().strip('"').strip("'")


def create_agent_executor():
    raw_key = os.getenv("OPENROUTER_API_KEY")
    if not raw_key:
        raise ValueError("OPENROUTER_API_KEY is not set. Copy .env.example to .env and add your key.")

    api_key = _normalize_api_key(raw_key)
    if not api_key.startswith("sk-or-"):
        raise ValueError(
            "OPENROUTER_API_KEY must start with 'sk-or-'. "
            "Get a key at https://openrouter.ai/keys"
        )

    llm = ChatOpenAI(
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=api_key,
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        temperature=0,
        default_headers={
            "HTTP-Referer": "https://github.com/otus-task-4",
            "X-Title": "Task Manager Agent",
        },
    )

    return create_agent(
        model=llm,
        tools=ALL_TOOLS,
        system_prompt=_load_system_prompt(),
        debug=True,
    )
