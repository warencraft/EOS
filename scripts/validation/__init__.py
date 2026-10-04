"""EOS validation helpers for Phase 0.2A."""

from .catalog_context import (
    CatalogKind,
    CatalogLifecyclePolicy,
    CatalogRecord,
    CatalogRegistry,
    CatalogRegistryError,
    DuplicateCatalogIdError,
    ValidationContext,
)

from .validator import (
    INSTALL_INSTRUCTIONS,
    EosValidator,
    MissingValidationDependencyError,
    ValidationError,
    ValidationResult,
)

__all__ = [
    "CatalogKind",
    "CatalogLifecyclePolicy",
    "CatalogRecord",
    "CatalogRegistry",
    "CatalogRegistryError",
    "DuplicateCatalogIdError",
    "INSTALL_INSTRUCTIONS",
    "EosValidator",
    "MissingValidationDependencyError",
    "ValidationContext",
    "ValidationError",
    "ValidationResult",
]
