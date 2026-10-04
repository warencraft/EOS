from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping


class CatalogKind(str, Enum):
    UNIT = "unit"
    CONDITION_TYPE = "condition_type"
    PROPERTY = "property"
    CLASSIFICATION = "classification"


CATALOG_PREFIXES: dict[CatalogKind, str] = {
    CatalogKind.UNIT: "UNT-",
    CatalogKind.CONDITION_TYPE: "CND-",
    CatalogKind.PROPERTY: "PRP-",
    CatalogKind.CLASSIFICATION: "CLS-",
}


class CatalogRegistryError(ValueError):
    def __init__(self, message: str, *, error_code: str, entry_id: str | None = None) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.entry_id = entry_id


class DuplicateCatalogIdError(CatalogRegistryError):
    def __init__(self, entry_id: str) -> None:
        super().__init__(
            f"Duplicate catalog identifier: {entry_id}",
            error_code="reference_integrity.duplicate_catalog_id",
            entry_id=entry_id,
        )


@dataclass(frozen=True)
class CatalogRecord:
    kind: CatalogKind
    entry: Mapping[str, Any]

    @property
    def id(self) -> str:
        return self.entry["id"]


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


@dataclass(frozen=True, init=False)
class CatalogRegistry:
    """Immutable snapshot of already contract-validated catalog entries."""

    _records: Mapping[str, CatalogRecord]
    unit_entries: Mapping[str, Mapping[str, Any]]
    condition_type_entries: Mapping[str, Mapping[str, Any]]
    property_entries: Mapping[str, Mapping[str, Any]]
    classification_entries: Mapping[str, Mapping[str, Any]]

    def __init__(
        self,
        *,
        unit_entries: Iterable[Mapping[str, Any]] = (),
        condition_type_entries: Iterable[Mapping[str, Any]] = (),
        property_entries: Iterable[Mapping[str, Any]] = (),
        classification_entries: Iterable[Mapping[str, Any]] = (),
    ) -> None:
        records: dict[str, CatalogRecord] = {}
        typed: dict[CatalogKind, dict[str, Mapping[str, Any]]] = {
            kind: {} for kind in CatalogKind
        }
        inputs = {
            CatalogKind.UNIT: unit_entries,
            CatalogKind.CONDITION_TYPE: condition_type_entries,
            CatalogKind.PROPERTY: property_entries,
            CatalogKind.CLASSIFICATION: classification_entries,
        }

        for kind, entries in inputs.items():
            expected_prefix = CATALOG_PREFIXES[kind]
            for entry in entries:
                entry_id = entry.get("id")
                if not isinstance(entry_id, str) or not entry_id.startswith(expected_prefix):
                    raise CatalogRegistryError(
                        f"Catalog entry for {kind.value} must use an {expected_prefix} identifier",
                        error_code="reference_integrity.catalog_entry_type_mismatch",
                        entry_id=entry_id if isinstance(entry_id, str) else None,
                    )
                if entry_id in records:
                    raise DuplicateCatalogIdError(entry_id)
                frozen_entry = _freeze(entry)
                record = CatalogRecord(kind=kind, entry=frozen_entry)
                records[entry_id] = record
                typed[kind][entry_id] = frozen_entry

        object.__setattr__(self, "_records", MappingProxyType(records))
        object.__setattr__(self, "unit_entries", MappingProxyType(typed[CatalogKind.UNIT]))
        object.__setattr__(
            self,
            "condition_type_entries",
            MappingProxyType(typed[CatalogKind.CONDITION_TYPE]),
        )
        object.__setattr__(self, "property_entries", MappingProxyType(typed[CatalogKind.PROPERTY]))
        object.__setattr__(
            self,
            "classification_entries",
            MappingProxyType(typed[CatalogKind.CLASSIFICATION]),
        )

    def resolve(self, entry_id: str) -> CatalogRecord | None:
        return self._records.get(entry_id)

    def __len__(self) -> int:
        return len(self._records)


class CatalogLifecyclePolicy(str, Enum):
    DEFAULT = "default"
    AUTHORING = "authoring"

    def allows(self, status: str) -> bool:
        if self is CatalogLifecyclePolicy.AUTHORING:
            return status in {"Draft", "Review", "Approved", "Deprecated"}
        return status in {"Approved", "Deprecated"}


@dataclass(frozen=True)
class ValidationContext:
    catalogs: CatalogRegistry
    lifecycle_policy: CatalogLifecyclePolicy = CatalogLifecyclePolicy.DEFAULT

