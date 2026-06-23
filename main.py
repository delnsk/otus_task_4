import sys

import httpx
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from agent.agent import create_agent_executor
from agent.response import format_response


def _check_api_available() -> None:
    import os

    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    try:
        with httpx.Client(timeout=5.0) as client:
            client.get(f"{base_url}/tasks")
    except httpx.ConnectError as exc:
        raise RuntimeError(
            f"API server is not reachable at {base_url}. "
            "Start it with: uvicorn api.server:app --port 8000"
        ) from exc


def main() -> None:
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: python main.py \"<your query>\"")
        sys.exit(1)

    user_query = sys.argv[1]

    try:
        _check_api_available()
        agent = create_agent_executor()
        result = agent.invoke({"messages": [HumanMessage(content=user_query)]})
        output = result["messages"][-1].content
        print(format_response(output))
    except ValueError as exc:
        print(f"Configuration error: {exc}")
        sys.exit(1)
    except RuntimeError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    except Exception as exc:
        err = str(exc)
        if "401" in err or "User not found" in err:
            print(
                "OpenRouter authentication failed (401 User not found).\n"
                "Check OPENROUTER_API_KEY in .env:\n"
                "  1. Key from https://openrouter.ai/keys (starts with sk-or-)\n"
                "  2. No quotes or extra spaces around the key\n"
                "  3. Account has credits and access to the model"
            )
            sys.exit(1)
        print(f"Unexpected error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
