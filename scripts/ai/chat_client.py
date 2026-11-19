"""Volanie Claude Messages API pre rozhovor v EOS."""

import os
from collections.abc import AsyncIterator
from pathlib import Path
from urllib.parse import urlsplit


SUPPLIER_FIELDS = ("name", "category", "supplies", "location", "web", "email", "note")
SUPPLIER_TOOL = {
    "name": "propose_supplier",
    "description": "Priprav návrh nového dodávateľa, ak o to používateľ požiada. Použi iba známe údaje. Ak chýba názov alebo kategória, opýtaj sa. Návrh ešte nič neukladá.",
    "input_schema": {
        "type": "object",
        "properties": {field: {"type": "string", "maxLength": 2000} for field in SUPPLIER_FIELDS},
        "required": ["name", "category"],
        "additionalProperties": False,
    },
}


class ChatError(RuntimeError):
    """Claude nevrátil použiteľnú textovú odpoveď."""


def settings() -> tuple[str, str]:
    credential_dir = os.getenv("CREDENTIALS_DIRECTORY")
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if credential_dir and not key:
        try:
            key = (Path(credential_dir) / "anthropic_key").read_text().strip()
        except OSError:
            pass
    return key, os.getenv("EOS_CLAUDE_MODEL", "")


MAX_TOOL_STEPS = 8
SYSTEM_PROMPT = Path(__file__).with_name("system_prompt.md")


def system_prompt() -> str:
    try:
        return SYSTEM_PROMPT.read_text(encoding="utf-8").strip()
    except OSError:
        return "Si asistent EOS. Odpovedaj po slovensky. Texty ponúk označ ako návrh."


def request_params(model: str, messages: list[dict], tools=None, final: bool = False) -> dict:
    """`tools` je scripts.ai.nastroje.Nastroje alebo None. `final` vynúti textovú odpoveď bez nástrojov."""
    from . import nastroje
    return {
        "model": model, "max_tokens": 1500, "messages": messages,
        "tools": [SUPPLIER_TOOL] + (nastroje.TOOLS if tools is not None else []),
        "tool_choice": {"type": "none"} if final else {"type": "auto", "disable_parallel_tool_use": True},
        "system": system_prompt(),
    }


def _block(block) -> dict:
    if hasattr(block, "model_dump"):
        return block.model_dump(exclude_none=True)
    if block.type == "text":
        return {"type": "text", "text": block.text}
    return {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}


def _eos_uses(response, tools) -> list:
    from . import nastroje
    if tools is None:
        return []
    return [b for b in response.content if b.type == "tool_use" and b.name in nastroje.TOOL_NAMES]


def _run_tools(response, uses, tools, messages: list[dict], sources: list[str]) -> list[dict]:
    """Vykoná nástroje EOS a vráti nové správy: odpoveď Clauda a výsledky nástrojov."""
    results = []
    for use in uses:
        text, used = tools.run(use.name, use.input if isinstance(use.input, dict) else {})
        sources.extend(s for s in used if s not in sources)
        results.append({"type": "tool_result", "tool_use_id": use.id, "content": text})
    return messages + [{"role": "assistant", "content": [_block(b) for b in response.content]},
                       {"role": "user", "content": results}]


def _texts(response) -> list[str]:
    return [b.text for b in response.content if b.type == "text" and b.text.strip()]


def reply(key: str, model: str, messages: list[dict], tools=None) -> tuple[str, dict | None, list[str]]:
    import anthropic

    sources: list[str] = []
    earlier: list[str] = []
    try:
        with anthropic.Anthropic(api_key=key, timeout=40, max_retries=0) as client:
            for step in range(MAX_TOOL_STEPS + 1):
                response = client.messages.create(**request_params(model, messages, tools, final=step == MAX_TOOL_STEPS))
                uses = _eos_uses(response, tools) if step < MAX_TOOL_STEPS else []
                if not uses:
                    break
                earlier += _texts(response)
                messages = _run_tools(response, uses, tools, messages, sources)
    except anthropic.APIError:
        raise ChatError from None
    return (*parse_response(response, earlier), sources)


async def stream_reply(key: str, model: str, messages: list[dict], tools=None) -> AsyncIterator[str | tuple[str, dict | None, list[str]]]:
    import anthropic

    sources: list[str] = []
    earlier: list[str] = []
    try:
        async with anthropic.AsyncAnthropic(api_key=key, timeout=40, max_retries=0) as client:
            for step in range(MAX_TOOL_STEPS + 1):
                final = step == MAX_TOOL_STEPS
                async with client.messages.stream(**request_params(model, messages, tools, final=final)) as stream:
                    async for text in stream.text_stream:
                        yield text
                    response = await stream.get_final_message()
                uses = _eos_uses(response, tools) if not final else []
                if not uses:
                    break
                if _texts(response):
                    earlier += _texts(response)
                    yield "\n\n"
                messages = _run_tools(response, uses, tools, messages, sources)
    except anthropic.APIError:
        raise ChatError from None
    yield (*parse_response(response, earlier), sources)


def parse_response(response, earlier: list[str] = ()) -> tuple[str, dict | None]:
    answer = "\n\n".join([*earlier, "\n".join(block.text for block in response.content if block.type == "text").strip()]).strip()
    for block in response.content:
        if block.type == "tool_use" and block.name == SUPPLIER_TOOL["name"] and isinstance(block.input, dict):
            fields = {key: value.strip()[:2000] for key, value in block.input.items()
                      if key in SUPPLIER_FIELDS and isinstance(value, str)}
            if fields.get("web"):
                try:
                    website = urlsplit(fields["web"])
                    if website.scheme not in {"http", "https"} or not website.hostname:
                        fields.pop("web")
                except ValueError:
                    fields.pop("web")
            if fields.get("name") and fields.get("category"):
                return "Pripravil som návrh dodávateľa. Skontroluj údaje vo formulári.", fields
    if not answer:
        raise ChatError
    return answer, None
