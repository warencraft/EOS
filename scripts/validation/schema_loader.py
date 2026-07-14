from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "schemas"


class SchemaRegistry:
    def __init__(self, schema_root: Path | None = None) -> None:
        self.schema_root = schema_root or SCHEMA_ROOT
        self.by_id: dict[str, dict[str, Any]] = {}
        self.by_path: dict[Path, dict[str, Any]] = {}

    def load_all(self) -> None:
        for path in self.schema_root.rglob("*.schema.json"):
            self.load_path(path)

    def load_path(self, path: Path) -> dict[str, Any]:
        resolved = path.resolve()
        if resolved in self.by_path:
            return self.by_path[resolved]
        with resolved.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
        self.by_path[resolved] = schema
        schema_id = schema.get("$id")
        if isinstance(schema_id, str):
            self.by_id[schema_id] = schema
        return schema

    def get(self, ref: str) -> Any:
        base, _, fragment = ref.partition("#")
        if base:
            if base not in self.by_id:
                raise KeyError(f"Unknown schema id: {base}")
            target: Any = self.by_id[base]
        else:
            raise KeyError(f"Local refs require an active schema: {ref}")
        if not fragment:
            return target
        for part in fragment.lstrip("/").split("/"):
            part = part.replace("~1", "/").replace("~0", "~")
            target = target[part]
        return target

    def validate_schema_syntax(self) -> list[str]:
        errors: list[str] = []
        for path in self.schema_root.rglob("*.schema.json"):
            try:
                self.load_path(path)
            except Exception as exc:  # pragma: no cover - defensive report
                errors.append(f"{path}: {exc}")
        return errors

    def as_referencing_registry(self) -> Any:
        from referencing import Registry, Resource
        from referencing.jsonschema import DRAFT202012

        resources = []
        for schema_id, schema in self.by_id.items():
            resources.append((schema_id, Resource.from_contents(schema, default_specification=DRAFT202012)))
        return Registry().with_resources(resources)
