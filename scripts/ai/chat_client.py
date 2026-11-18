"""Volanie Claude Messages API pre rozhovor v EOS."""

import os
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


def reply(key: str, model: str, messages: list[dict]) -> tuple[str, dict | None]:
    import anthropic

    try:
        with anthropic.Anthropic(api_key=key, timeout=40, max_retries=0) as client:
            response = client.messages.create(
                model=model, max_tokens=1500, messages=messages,
                tools=[SUPPLIER_TOOL], tool_choice={"type": "auto", "disable_parallel_tool_use": True},
                system="Si asistent EOS. Odpovedaj po slovensky. Texty ponúk označ ako návrh.",
            )
    except anthropic.APIError:
        raise ChatError from None
    answer = "\n".join(block.text for block in response.content if block.type == "text").strip()
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
