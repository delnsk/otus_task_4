import re


def format_response(agent_output: str) -> str:
    """Format agent output into Status / Action / Data / Errors contract."""
    text = agent_output.strip()

    if _has_contract(text):
        return text

    return _wrap_as_contract(text)


def _has_contract(text: str) -> bool:
    return bool(
        re.search(r"^Status:\s*(success|error)", text, re.MULTILINE | re.IGNORECASE)
        and re.search(r"^Action:", text, re.MULTILINE)
    )


def _wrap_as_contract(text: str) -> str:
    lower = text.lower()
    is_error = any(
        word in lower
        for word in ("error", "ошибка", "failed", "не удалось", "not found", "не найден")
    )
    status = "error" if is_error else "success"
    return (
        f"Status: {status}\n"
        f"Action: Agent response\n"
        f"Data: {text}\n"
        f"Errors: {'None' if not is_error else text}"
    )
