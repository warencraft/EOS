from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from .catalog_context import CatalogKind, ValidationContext
from .schema_loader import SchemaRegistry


INSTALL_INSTRUCTIONS = (
    "Create a virtual environment and install the project: "
    "python -m venv .venv; .venv\\Scripts\\python -m pip install -e ."
)

ALLOWED_SCHEMA_KEYWORDS = {
    "$schema",
    "$id",
    "$anchor",
    "$dynamicAnchor",
    "$ref",
    "$dynamicRef",
    "$defs",
    "$vocabulary",
    "$comment",
    "title",
    "description",
    "default",
    "examples",
    "deprecated",
    "readOnly",
    "writeOnly",
    "type",
    "enum",
    "const",
    "multipleOf",
    "maximum",
    "exclusiveMaximum",
    "minimum",
    "exclusiveMinimum",
    "maxLength",
    "minLength",
    "pattern",
    "format",
    "prefixItems",
    "items",
    "contains",
    "maxItems",
    "minItems",
    "uniqueItems",
    "maxContains",
    "minContains",
    "properties",
    "patternProperties",
    "additionalProperties",
    "unevaluatedProperties",
    "required",
    "propertyNames",
    "dependentRequired",
    "dependentSchemas",
    "allOf",
    "anyOf",
    "oneOf",
    "not",
    "if",
    "then",
    "else",
}

QUANTITY_SCHEMA_ID = "https://eos.local/schemas/knowledge-core/quantity.schema.json"
VALUE_RANGE_SCHEMA_ID = "https://eos.local/schemas/knowledge-core/value-range.schema.json"
MEASUREMENT_QUALITY_SCHEMA_ID = "https://eos.local/schemas/knowledge-core/measurement-quality.schema.json"
CONDITION_SCHEMA_ID = "https://eos.local/schemas/knowledge-core/condition.schema.json"
CLASSIFICATION_SCHEMA_ID = "https://eos.local/schemas/knowledge-core/classification.schema.json"
PROPERTY_RECORD_SCHEMA_ID = "https://eos.local/schemas/knowledge-core/property-record.schema.json"
OBSERVATION_SCHEMA_ID = "https://eos.local/schemas/knowledge-core/observation.schema.json"
UNIT_CATALOG_ENTRY_SCHEMA_ID = "https://eos.local/schemas/catalogs/unit-catalog-entry.schema.json"
CONDITION_TYPE_CATALOG_ENTRY_SCHEMA_ID = "https://eos.local/schemas/catalogs/condition-type-catalog-entry.schema.json"
PROPERTY_CATALOG_ENTRY_SCHEMA_ID = "https://eos.local/schemas/catalogs/property-catalog-entry.schema.json"
CLASSIFICATION_CATALOG_ENTRY_SCHEMA_ID = "https://eos.local/schemas/catalogs/classification-catalog-entry.schema.json"
MATERIAL_SCHEMA_ID = "https://eos.local/schemas/entities/material.schema.json"
SUPPLIER_SCHEMA_ID = "https://eos.local/schemas/entities/supplier.schema.json"
INDEX_SCHEMA_ID = "https://eos.local/schemas/index.schema.json"

EMBEDDED_CONTRACT_FIELDS: dict[str, dict[str, tuple[str, bool]]] = {
    MEASUREMENT_QUALITY_SCHEMA_ID: {
        "uncertainty": (QUANTITY_SCHEMA_ID, False),
        "resolution": (QUANTITY_SCHEMA_ID, False),
    },
    CONDITION_SCHEMA_ID: {
        "quantity": (QUANTITY_SCHEMA_ID, False),
        "valueRange": (VALUE_RANGE_SCHEMA_ID, False),
    },
    PROPERTY_RECORD_SCHEMA_ID: {
        "quantity": (QUANTITY_SCHEMA_ID, False),
        "valueRange": (VALUE_RANGE_SCHEMA_ID, False),
        "measurementQuality": (MEASUREMENT_QUALITY_SCHEMA_ID, False),
        "conditions": (CONDITION_SCHEMA_ID, True),
    },
    OBSERVATION_SCHEMA_ID: {
        "quantity": (QUANTITY_SCHEMA_ID, False),
        "valueRange": (VALUE_RANGE_SCHEMA_ID, False),
        "measurementQuality": (MEASUREMENT_QUALITY_SCHEMA_ID, False),
        "conditions": (CONDITION_SCHEMA_ID, True),
    },
    SUPPLIER_SCHEMA_ID: {
        "classifications": (CLASSIFICATION_SCHEMA_ID, True),
    },
    MATERIAL_SCHEMA_ID: {
        "properties": (PROPERTY_RECORD_SCHEMA_ID, True),
        "classifications": (CLASSIFICATION_SCHEMA_ID, True),
    },
    INDEX_SCHEMA_ID: {
        "propertyRecords": (PROPERTY_RECORD_SCHEMA_ID, True),
        "observations": (OBSERVATION_SCHEMA_ID, True),
        "unitCatalogEntries": (UNIT_CATALOG_ENTRY_SCHEMA_ID, True),
        "conditionTypeCatalogEntries": (CONDITION_TYPE_CATALOG_ENTRY_SCHEMA_ID, True),
        "propertyCatalogEntries": (PROPERTY_CATALOG_ENTRY_SCHEMA_ID, True),
        "classificationCatalogEntries": (CLASSIFICATION_CATALOG_ENTRY_SCHEMA_ID, True),
        "materials": (MATERIAL_SCHEMA_ID, True),
    },
}


class MissingValidationDependencyError(RuntimeError):
    pass


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"JSON value {value} is not allowed; use finite JSON numbers only")


def _load_jsonschema() -> tuple[Any, Any, Any, Any]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker, SchemaError
        from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on runtime
        dependency = (exc.name or "jsonschema").split(".", 1)[0]
        raise MissingValidationDependencyError(
            f"Missing required validation dependency '{dependency}'. {INSTALL_INSTRUCTIONS}"
        ) from exc
    return Draft202012Validator, FormatChecker, SchemaError, JsonSchemaValidationError


@dataclass
class ValidationError:
    errorCode: str
    category: str
    message: str
    instancePath: str = "$"
    schemaPath: str = ""
    recordId: str | None = None
    referencedId: str | None = None
    severity: str = "error"

    @property
    def path(self) -> str:
        return self.instancePath


@dataclass
class ValidationResult:
    errors: list[ValidationError] = field(default_factory=list)
    executedLayers: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not any(error.severity == "error" for error in self.errors)

    @property
    def warnings(self) -> list[ValidationError]:
        return [error for error in self.errors if error.severity == "warning"]

    def add(
        self,
        *,
        errorCode: str,
        category: str,
        message: str,
        instancePath: str = "$",
        schemaPath: str = "",
        recordId: str | None = None,
        referencedId: str | None = None,
        severity: str = "error",
    ) -> None:
        self.errors.append(
            ValidationError(
                errorCode=errorCode,
                category=category,
                message=message,
                instancePath=instancePath,
                schemaPath=schemaPath,
                recordId=recordId,
                referencedId=referencedId,
                severity=severity,
            )
        )


class EosValidator:
    def __init__(self, registry: SchemaRegistry | None = None) -> None:
        self.registry = registry or SchemaRegistry()
        self.registry.load_all()
        self.Draft202012Validator, self.FormatChecker, self.SchemaError, self.JsonSchemaValidationError = _load_jsonschema()
        try:
            self.referencing_registry = self.registry.as_referencing_registry()
        except ModuleNotFoundError as exc:  # pragma: no cover - depends on runtime
            dependency = (exc.name or "referencing").split(".", 1)[0]
            raise MissingValidationDependencyError(
                f"Missing required validation dependency '{dependency}'. {INSTALL_INSTRUCTIONS}"
            ) from exc
        self.format_checker = self._build_format_checker()

    def validate_json_file(
        self,
        instance_path: Path,
        schema_id: str,
        *,
        has_verifiable_claims: bool = False,
    ) -> ValidationResult:
        result = ValidationResult(executedLayers=("json_syntax",))
        try:
            with instance_path.open("r", encoding="utf-8") as handle:
                instance = json.load(handle, parse_constant=_reject_json_constant)
        except (json.JSONDecodeError, ValueError) as exc:
            result.add(
                errorCode="json_syntax.invalid_json",
                category="json_syntax",
                message=str(exc),
                instancePath="$",
            )
            return result
        validated = self.validate(instance, schema_id, has_verifiable_claims=has_verifiable_claims)
        validated.executedLayers = ("json_syntax",) + validated.executedLayers
        return validated

    def validate(
        self,
        instance: Any,
        schema_id: str,
        *,
        has_verifiable_claims: bool = False,
    ) -> ValidationResult:
        result = ValidationResult(executedLayers=("schema_validation", "application_validation"))
        schema = self.registry.by_id.get(schema_id)
        if schema is None:
            result.add(
                errorCode="schema_definition.unknown_schema",
                category="schema_definition",
                message=f"Unknown schema id: {schema_id}",
                schemaPath=schema_id,
                recordId=self._record_id(instance),
            )
            return result

        schema_result = self.validate_schema_definition(schema_id)
        if not schema_result.ok:
            return schema_result

        try:
            validator = self.Draft202012Validator(
                schema,
                registry=self.referencing_registry,
                format_checker=self.format_checker,
            )
            for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.path)):
                instance_path = self._validation_error_instance_path(error)
                result.add(
                    errorCode=f"schema_validation.{error.validator}",
                    category="schema_validation",
                    message=error.message,
                    instancePath=instance_path,
                    schemaPath=self._json_path(error.schema_path),
                    recordId=self._record_id(instance),
                )
        except Exception as exc:
            result.add(
                errorCode="schema_definition.reference_error",
                category="schema_definition",
                message=str(exc),
                schemaPath=schema_id,
                recordId=self._record_id(instance),
            )
            return result

        self._validate_application_rules(
            instance,
            result,
            schema_id=schema_id,
            has_verifiable_claims=has_verifiable_claims,
        )
        return result

    def validate_json_file_with_context(
        self,
        instance_path: Path,
        schema_id: str,
        context: ValidationContext | None,
        *,
        has_verifiable_claims: bool = False,
    ) -> ValidationResult:
        result = ValidationResult(executedLayers=("json_syntax",))
        try:
            with instance_path.open("r", encoding="utf-8") as handle:
                instance = json.load(handle, parse_constant=_reject_json_constant)
        except (json.JSONDecodeError, ValueError) as exc:
            result.add(
                errorCode="json_syntax.invalid_json",
                category="json_syntax",
                message=str(exc),
                instancePath="$",
            )
            return result
        validated = self.validate_with_context(
            instance,
            schema_id,
            context,
            has_verifiable_claims=has_verifiable_claims,
        )
        validated.executedLayers = ("json_syntax",) + validated.executedLayers
        return validated

    def validate_with_context(
        self,
        instance: Any,
        schema_id: str,
        context: ValidationContext | None,
        *,
        has_verifiable_claims: bool = False,
    ) -> ValidationResult:
        if context is None:
            result = ValidationResult()
            result.add(
                errorCode="catalog_validation.context_required",
                category="catalog_validation",
                message="Catalog-aware validation requires an explicit ValidationContext.",
                instancePath="$",
                recordId=self._record_id(instance),
            )
            return result

        result = self.validate(
            instance,
            schema_id,
            has_verifiable_claims=has_verifiable_claims,
        )
        if any(
            error.severity == "error"
            and error.category in {"json_syntax", "schema_definition", "schema_validation"}
            for error in result.errors
        ):
            return result

        result.executedLayers += ("reference_integrity", "catalog_validation")
        self._validate_catalog_contract(
            instance,
            result,
            schema_id=schema_id,
            context=context,
            path="$",
            record_id=self._record_id(instance),
        )
        return result

    def validate_schema_syntax(self) -> ValidationResult:
        result = ValidationResult()
        for error in self.registry.validate_schema_syntax():
            result.add(
                errorCode="schema_definition.invalid_json",
                category="schema_definition",
                message=error,
            )
        for schema_id in sorted(self.registry.by_id):
            schema_result = self.validate_schema_definition(schema_id)
            result.errors.extend(schema_result.errors)
        return result

    def validate_schema_definition(self, schema_id: str) -> ValidationResult:
        result = ValidationResult()
        schema = self.registry.by_id.get(schema_id)
        if schema is None:
            result.add(
                errorCode="schema_definition.unknown_schema",
                category="schema_definition",
                message=f"Unknown schema id: {schema_id}",
                schemaPath=schema_id,
            )
            return result
        self._check_unknown_schema_keywords(schema, schema_id, result)
        if not result.ok:
            return result
        try:
            self.Draft202012Validator.check_schema(schema)
        except self.SchemaError as exc:
            result.add(
                errorCode="schema_definition.invalid_schema",
                category="schema_definition",
                message=exc.message,
                schemaPath=self._json_path(exc.schema_path),
            )
        return result

    def _build_format_checker(self) -> Any:
        checker = self.FormatChecker()

        @checker.checks("date-time", raises=ValueError)
        def is_datetime(value: Any) -> bool:
            if not isinstance(value, str):
                return True
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return True

        @checker.checks("date", raises=ValueError)
        def is_date(value: Any) -> bool:
            if not isinstance(value, str):
                return True
            date.fromisoformat(value)
            return True

        @checker.checks("uri")
        def is_uri(value: Any) -> bool:
            if not isinstance(value, str):
                return True
            parsed = urlparse(value)
            return bool(parsed.scheme and not any(char.isspace() for char in value))

        return checker

    def _check_unknown_schema_keywords(self, schema: Any, path: str, result: ValidationResult) -> None:
        if isinstance(schema, bool):
            return
        if isinstance(schema, dict):
            for key, value in schema.items():
                if key not in ALLOWED_SCHEMA_KEYWORDS:
                    result.add(
                        errorCode="schema_definition.unknown_keyword",
                        category="schema_definition",
                        message=f"unknown schema keyword: {key}",
                        schemaPath=f"{path}.{key}",
                    )
                if key in {"properties", "$defs", "patternProperties", "dependentSchemas"} and isinstance(value, dict):
                    for child_key, child_schema in value.items():
                        self._check_unknown_schema_keywords(child_schema, f"{path}.{key}.{child_key}", result)
                elif key in {"items", "additionalProperties", "propertyNames", "contains", "not", "if", "then", "else", "unevaluatedProperties"}:
                    self._check_unknown_schema_keywords(value, f"{path}.{key}", result)
                elif key in {"allOf", "anyOf", "oneOf", "prefixItems"} and isinstance(value, list):
                    for index, child_schema in enumerate(value):
                        self._check_unknown_schema_keywords(child_schema, f"{path}.{key}[{index}]", result)
        elif isinstance(schema, list):
            for index, value in enumerate(schema):
                self._check_unknown_schema_keywords(value, f"{path}[{index}]", result)

    def _validate_application_rules(
        self,
        instance: Any,
        result: ValidationResult,
        *,
        schema_id: str,
        has_verifiable_claims: bool,
    ) -> None:
        if not isinstance(instance, dict):
            return
        self._validate_finite_numbers(instance, result)
        self._validate_contract_rules(instance, result, schema_id=schema_id)
        if schema_id != OBSERVATION_SCHEMA_ID:
            self._validate_source_links_rule(instance, result, has_verifiable_claims=has_verifiable_claims)
        self._validate_hierarchical_ids(instance, result)
        self._validate_document_record_versions(instance, result)

    def _validate_contract_rules(
        self,
        instance: Any,
        result: ValidationResult,
        *,
        schema_id: str,
        path: str = "$",
    ) -> None:
        if not isinstance(instance, dict):
            return

        if schema_id == VALUE_RANGE_SCHEMA_ID:
            self._validate_value_range_rules(instance, result, path=path)
        elif schema_id == MEASUREMENT_QUALITY_SCHEMA_ID:
            self._validate_measurement_quality_rules(instance, result, path=path)
        elif schema_id == OBSERVATION_SCHEMA_ID:
            self._validate_source_links_rule(
                instance,
                result,
                has_verifiable_claims=True,
                path=path,
            )
        elif schema_id == UNIT_CATALOG_ENTRY_SCHEMA_ID:
            self._validate_source_links_rule(
                instance,
                result,
                has_verifiable_claims=True,
                path=path,
            )
        elif schema_id == CONDITION_TYPE_CATALOG_ENTRY_SCHEMA_ID:
            self._validate_source_links_rule(
                instance,
                result,
                has_verifiable_claims=True,
                path=path,
            )
        elif schema_id == PROPERTY_CATALOG_ENTRY_SCHEMA_ID:
            self._validate_source_links_rule(
                instance,
                result,
                has_verifiable_claims=True,
                path=path,
            )
        elif schema_id == CLASSIFICATION_CATALOG_ENTRY_SCHEMA_ID:
            self._validate_source_links_rule(
                instance,
                result,
                has_verifiable_claims=True,
                path=path,
            )
        elif schema_id in {MATERIAL_SCHEMA_ID, SUPPLIER_SCHEMA_ID}:
            self._validate_source_links_rule(
                instance,
                result,
                has_verifiable_claims=True,
                path=path,
            )

        for field_name, (child_schema_id, is_array) in EMBEDDED_CONTRACT_FIELDS.get(schema_id, {}).items():
            child = instance.get(field_name)
            child_path = f"{path}.{field_name}"
            if is_array and isinstance(child, list):
                for index, value in enumerate(child):
                    self._validate_contract_rules(
                        value,
                        result,
                        schema_id=child_schema_id,
                        path=f"{child_path}[{index}]",
                    )
            elif not is_array:
                self._validate_contract_rules(child, result, schema_id=child_schema_id, path=child_path)

    def _validate_catalog_contract(
        self,
        instance: Any,
        result: ValidationResult,
        *,
        schema_id: str,
        context: ValidationContext,
        path: str,
        record_id: str | None,
    ) -> None:
        if not isinstance(instance, dict):
            return

        if schema_id == QUANTITY_SCHEMA_ID:
            self._validate_unit_reference(instance.get("unitId"), result, context, f"{path}.unitId", record_id)
        elif schema_id == VALUE_RANGE_SCHEMA_ID:
            self._validate_unit_reference(instance.get("unitId"), result, context, f"{path}.unitId", record_id)
        elif schema_id == MEASUREMENT_QUALITY_SCHEMA_ID:
            for field_name in ("uncertainty", "resolution"):
                child = instance.get(field_name)
                if isinstance(child, dict):
                    self._validate_catalog_contract(
                        child,
                        result,
                        schema_id=QUANTITY_SCHEMA_ID,
                        context=context,
                        path=f"{path}.{field_name}",
                        record_id=record_id,
                    )
        elif schema_id == CONDITION_SCHEMA_ID:
            self._validate_condition_catalog_rules(instance, result, context, path, record_id)
        elif schema_id in {PROPERTY_RECORD_SCHEMA_ID, OBSERVATION_SCHEMA_ID}:
            self._validate_property_consumer(instance, result, context, path, record_id)
        elif schema_id == CLASSIFICATION_SCHEMA_ID:
            self._resolve_catalog_reference(
                instance.get("classificationId"),
                CatalogKind.CLASSIFICATION,
                result,
                context,
                f"{path}.classificationId",
                record_id,
            )
        elif schema_id == SUPPLIER_SCHEMA_ID:
            for index, child in enumerate(instance.get("classifications", [])):
                self._validate_catalog_contract(
                    child,
                    result,
                    schema_id=CLASSIFICATION_SCHEMA_ID,
                    context=context,
                    path=f"{path}.classifications[{index}]",
                    record_id=record_id,
                )
        elif schema_id == MATERIAL_SCHEMA_ID:
            embedded_contracts = {
                "properties": PROPERTY_RECORD_SCHEMA_ID,
                "classifications": CLASSIFICATION_SCHEMA_ID,
            }
            for field_name, child_schema_id in embedded_contracts.items():
                children = instance.get(field_name)
                if not isinstance(children, list):
                    continue
                for index, child in enumerate(children):
                    self._validate_catalog_contract(
                        child,
                        result,
                        schema_id=child_schema_id,
                        context=context,
                        path=f"{path}.{field_name}[{index}]",
                        record_id=record_id,
                    )
        elif schema_id == INDEX_SCHEMA_ID:
            indexed_contracts = {
                "quantities": QUANTITY_SCHEMA_ID,
                "valueRanges": VALUE_RANGE_SCHEMA_ID,
                "measurementQualities": MEASUREMENT_QUALITY_SCHEMA_ID,
                "conditions": CONDITION_SCHEMA_ID,
                "classifications": CLASSIFICATION_SCHEMA_ID,
                "propertyRecords": PROPERTY_RECORD_SCHEMA_ID,
                "observations": OBSERVATION_SCHEMA_ID,
                "materials": MATERIAL_SCHEMA_ID,
            }
            for field_name, child_schema_id in indexed_contracts.items():
                children = instance.get(field_name)
                if not isinstance(children, list):
                    continue
                for index, child in enumerate(children):
                    self._validate_catalog_contract(
                        child,
                        result,
                        schema_id=child_schema_id,
                        context=context,
                        path=f"{path}.{field_name}[{index}]",
                        record_id=record_id,
                    )

    def _validate_property_consumer(
        self,
        instance: dict[str, Any],
        result: ValidationResult,
        context: ValidationContext,
        path: str,
        record_id: str | None,
    ) -> None:
        property_entry = self._resolve_catalog_reference(
            instance.get("propertyId"),
            CatalogKind.PROPERTY,
            result,
            context,
            f"{path}.propertyId",
            record_id,
        )

        value_type = instance.get("valueType")
        result_value = instance.get(value_type) if isinstance(value_type, str) else None
        unit_entry: Mapping[str, Any] | None = None
        unit_id: str | None = None
        unit_path: str | None = None
        if value_type in {"quantity", "valueRange"} and isinstance(result_value, dict):
            unit_id = result_value.get("unitId")
            unit_path = f"{path}.{value_type}.unitId"
            unit_entry = self._validate_unit_reference(
                unit_id,
                result,
                context,
                unit_path,
                record_id,
            )

        measurement_quality = instance.get("measurementQuality")
        if isinstance(measurement_quality, dict):
            self._validate_catalog_contract(
                measurement_quality,
                result,
                schema_id=MEASUREMENT_QUALITY_SCHEMA_ID,
                context=context,
                path=f"{path}.measurementQuality",
                record_id=record_id,
            )

        condition_results: list[tuple[int, dict[str, Any], Mapping[str, Any] | None]] = []
        conditions = instance.get("conditions")
        if isinstance(conditions, list):
            for index, condition in enumerate(conditions):
                if not isinstance(condition, dict):
                    continue
                condition_entry = self._validate_condition_catalog_rules(
                    condition,
                    result,
                    context,
                    f"{path}.conditions[{index}]",
                    record_id,
                )
                condition_results.append((index, condition, condition_entry))

        if property_entry is None:
            return

        allowed_value_types = property_entry.get("allowedValueTypes", ())
        if value_type not in allowed_value_types:
            self._add_catalog_error(
                result,
                error_code="catalog_validation.value_type_not_allowed",
                message=f"Property {property_entry['id']} does not allow value type {value_type!r}.",
                path=f"{path}.valueType",
                record_id=record_id,
                referenced_id=property_entry["id"],
            )

        if unit_entry is not None and unit_id not in property_entry.get("allowedUnitIds", ()):
            self._add_catalog_error(
                result,
                error_code="catalog_validation.unit_not_allowed",
                message=f"Property {property_entry['id']} does not allow unit {unit_id}.",
                path=unit_path or path,
                record_id=record_id,
                referenced_id=unit_id,
            )

        allowed_condition_ids = property_entry.get("allowedConditionTypeIds")
        for index, condition, condition_entry in condition_results:
            condition_id = condition.get("conditionTypeId")
            condition_path = f"{path}.conditions[{index}].conditionTypeId"
            if allowed_condition_ids is None:
                self._add_catalog_error(
                    result,
                    error_code="catalog_validation.condition_not_allowed",
                    message=f"Property {property_entry['id']} does not allow Conditions.",
                    path=condition_path,
                    record_id=record_id,
                    referenced_id=condition_id if isinstance(condition_id, str) else None,
                )
            elif condition_entry is not None and condition_id not in allowed_condition_ids:
                self._add_catalog_error(
                    result,
                    error_code="catalog_validation.condition_not_allowed",
                    message=f"Property {property_entry['id']} does not allow condition type {condition_id}.",
                    path=condition_path,
                    record_id=record_id,
                    referenced_id=condition_id if isinstance(condition_id, str) else None,
                )

    def _validate_condition_catalog_rules(
        self,
        instance: dict[str, Any],
        result: ValidationResult,
        context: ValidationContext,
        path: str,
        record_id: str | None,
    ) -> Mapping[str, Any] | None:
        condition_id = instance.get("conditionTypeId")
        condition_entry = self._resolve_catalog_reference(
            condition_id,
            CatalogKind.CONDITION_TYPE,
            result,
            context,
            f"{path}.conditionTypeId",
            record_id,
        )

        value_forms = ("quantity", "valueRange", "textValue", "booleanValue", "referenceId")
        value_form = next((field for field in value_forms if field in instance), None)
        if value_form == "quantity" and isinstance(instance.get("quantity"), dict):
            self._validate_catalog_contract(
                instance["quantity"],
                result,
                schema_id=QUANTITY_SCHEMA_ID,
                context=context,
                path=f"{path}.quantity",
                record_id=record_id,
            )
        elif value_form == "valueRange" and isinstance(instance.get("valueRange"), dict):
            self._validate_catalog_contract(
                instance["valueRange"],
                result,
                schema_id=VALUE_RANGE_SCHEMA_ID,
                context=context,
                path=f"{path}.valueRange",
                record_id=record_id,
            )

        if condition_entry is None or value_form is None:
            return condition_entry

        allowed_forms = condition_entry.get("allowedValueForms", ())
        if value_form not in allowed_forms:
            self._add_catalog_error(
                result,
                error_code="catalog_validation.condition_value_form_not_allowed",
                message=f"Condition type {condition_entry['id']} does not allow value form {value_form}.",
                path=path,
                record_id=record_id,
                referenced_id=condition_entry["id"],
            )
            return condition_entry

        if value_form == "referenceId":
            reference_id = instance.get("referenceId")
            allowed_prefixes = condition_entry.get("allowedReferencePrefixes", ())
            reference_prefix = self._reference_prefix(reference_id)
            if reference_prefix not in allowed_prefixes:
                self._add_catalog_error(
                    result,
                    error_code="catalog_validation.reference_prefix_not_allowed",
                    message=(
                        f"Condition type {condition_entry['id']} does not allow reference prefix "
                        f"{reference_prefix or '<unknown>'}."
                    ),
                    path=f"{path}.referenceId",
                    record_id=record_id,
                    referenced_id=reference_id if isinstance(reference_id, str) else None,
                )
        return condition_entry

    def _validate_unit_reference(
        self,
        unit_id: Any,
        result: ValidationResult,
        context: ValidationContext,
        path: str,
        record_id: str | None,
    ) -> Mapping[str, Any] | None:
        return self._resolve_catalog_reference(
            unit_id,
            CatalogKind.UNIT,
            result,
            context,
            path,
            record_id,
        )

    def _resolve_catalog_reference(
        self,
        reference_id: Any,
        expected_kind: CatalogKind,
        result: ValidationResult,
        context: ValidationContext,
        path: str,
        record_id: str | None,
    ) -> Mapping[str, Any] | None:
        if not isinstance(reference_id, str):
            return None
        record = context.catalogs.resolve(reference_id)
        if record is None:
            result.add(
                errorCode="reference_integrity.reference_not_found",
                category="reference_integrity",
                message=f"Catalog reference {reference_id} was not found.",
                instancePath=path,
                recordId=record_id,
                referencedId=reference_id,
            )
            return None
        if record.kind is not expected_kind:
            result.add(
                errorCode="reference_integrity.reference_type_mismatch",
                category="reference_integrity",
                message=(
                    f"Catalog reference {reference_id} resolved as {record.kind.value}, "
                    f"expected {expected_kind.value}."
                ),
                instancePath=path,
                recordId=record_id,
                referencedId=reference_id,
            )
            return None
        if not self._validate_catalog_lifecycle(record.entry, result, context, path, record_id):
            return None
        return record.entry

    def _validate_catalog_lifecycle(
        self,
        entry: Mapping[str, Any],
        result: ValidationResult,
        context: ValidationContext,
        path: str,
        record_id: str | None,
    ) -> bool:
        status = entry.get("status")
        entry_id = entry.get("id")
        if status == "Deprecated":
            replacement = entry.get("replacedBy")
            suffix = f" Suggested replacement: {replacement}." if replacement else ""
            result.add(
                errorCode="catalog_validation.deprecated_reference",
                category="catalog_validation",
                message=f"Catalog reference {entry_id} is Deprecated.{suffix}",
                instancePath=path,
                recordId=record_id,
                referencedId=entry_id if isinstance(entry_id, str) else None,
                severity="warning",
            )
            return True
        if isinstance(status, str) and context.lifecycle_policy.allows(status):
            return True
        result.add(
            errorCode="catalog_validation.catalog_status_not_allowed",
            category="catalog_validation",
            message=(
                f"Catalog reference {entry_id} has status {status!r}, which is not allowed by "
                f"the {context.lifecycle_policy.value} policy."
            ),
            instancePath=path,
            recordId=record_id,
            referencedId=entry_id if isinstance(entry_id, str) else None,
        )
        return False

    def _add_catalog_error(
        self,
        result: ValidationResult,
        *,
        error_code: str,
        message: str,
        path: str,
        record_id: str | None,
        referenced_id: str | None,
    ) -> None:
        result.add(
            errorCode=error_code,
            category="catalog_validation",
            message=message,
            instancePath=path,
            recordId=record_id,
            referencedId=referenced_id,
        )

    def _reference_prefix(self, reference_id: Any) -> str | None:
        if not isinstance(reference_id, str):
            return None
        if reference_id.startswith("JOB-"):
            if "-OP-" in reference_id and "-TM-" in reference_id:
                return "JOB_TIME_RECORD"
            if "-OP-" in reference_id:
                return "JOB_OPERATION"
            if "-RSK-" in reference_id:
                return "JOB_RISK"
            if "-QN-" in reference_id:
                return "JOB_QUOTATION_NOTE"
            return "JOB"
        return reference_id.split("-", 1)[0] if "-" in reference_id else None

    def _validate_finite_numbers(self, instance: Any, result: ValidationResult, path: str = "$") -> None:
        if isinstance(instance, float) and not math.isfinite(instance):
            result.add(
                errorCode="application_validation.non_finite_number",
                category="application_validation",
                message="Numeric values must be finite; NaN and Infinity are not allowed.",
                instancePath=path,
                recordId=self._record_id(instance),
            )
            return
        if isinstance(instance, dict):
            for key, value in instance.items():
                self._validate_finite_numbers(value, result, f"{path}.{key}")
        elif isinstance(instance, list):
            for index, value in enumerate(instance):
                self._validate_finite_numbers(value, result, f"{path}[{index}]")

    def _validate_value_range_rules(
        self,
        instance: dict[str, Any],
        result: ValidationResult,
        *,
        path: str,
    ) -> None:
        min_value = instance.get("minValue")
        max_value = instance.get("maxValue")
        if isinstance(min_value, (int, float)) and not isinstance(min_value, bool):
            if isinstance(max_value, (int, float)) and not isinstance(max_value, bool):
                if min_value > max_value:
                    result.add(
                        errorCode="application_validation.value_range_reversed_bounds",
                        category="application_validation",
                        message="ValueRange minValue must be less than or equal to maxValue.",
                        instancePath=f"{path}.minValue",
                        recordId=self._record_id(instance),
                    )

        if "lowerInclusive" in instance and "minValue" not in instance:
            result.add(
                errorCode="application_validation.value_range_lower_inclusive_without_min",
                category="application_validation",
                message="ValueRange lowerInclusive is meaningful only when minValue exists.",
                instancePath=f"{path}.lowerInclusive",
                recordId=self._record_id(instance),
            )

        if "upperInclusive" in instance and "maxValue" not in instance:
            result.add(
                errorCode="application_validation.value_range_upper_inclusive_without_max",
                category="application_validation",
                message="ValueRange upperInclusive is meaningful only when maxValue exists.",
                instancePath=f"{path}.upperInclusive",
                recordId=self._record_id(instance),
            )

    def _validate_measurement_quality_rules(
        self,
        instance: dict[str, Any],
        result: ValidationResult,
        *,
        path: str,
    ) -> None:
        uncertainty_value = self._quantity_value(instance.get("uncertainty"))
        if uncertainty_value is not None and uncertainty_value < 0:
            result.add(
                errorCode="application_validation.measurement_quality_negative_uncertainty",
                category="application_validation",
                message="MeasurementQuality uncertainty.value must be greater than or equal to zero.",
                instancePath=f"{path}.uncertainty.value",
                recordId=self._record_id(instance),
            )

        resolution_value = self._quantity_value(instance.get("resolution"))
        if resolution_value is not None and resolution_value <= 0:
            result.add(
                errorCode="application_validation.measurement_quality_nonpositive_resolution",
                category="application_validation",
                message="MeasurementQuality resolution.value must be greater than zero.",
                instancePath=f"{path}.resolution.value",
                recordId=self._record_id(instance),
            )

    def _quantity_value(self, candidate: Any) -> int | float | None:
        if not isinstance(candidate, dict):
            return None
        value = candidate.get("value")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        return value

    def _validate_source_links_rule(
        self,
        instance: dict[str, Any],
        result: ValidationResult,
        *,
        has_verifiable_claims: bool,
        path: str = "$",
    ) -> None:
        status = instance.get("status")
        source_links = instance.get("sourceLinks")
        if status in {"Review", "Approved"} and has_verifiable_claims and not source_links:
            result.add(
                errorCode="application_validation.source_links_required",
                category="application_validation",
                message="Review or Approved records with verifiable claims require sourceLinks",
                instancePath=f"{path}.sourceLinks",
                recordId=self._record_id(instance),
            )

    def _validate_hierarchical_ids(self, instance: dict[str, Any], result: ValidationResult) -> None:
        record_id = instance.get("id")
        job_id = instance.get("jobId")
        operation_id = instance.get("jobOperationId")
        if isinstance(record_id, str) and isinstance(job_id, str) and record_id.startswith("JOB-"):
            if not record_id.startswith(job_id):
                result.add(
                    errorCode="reference_integrity.job_owned_id_mismatch",
                    category="reference_integrity",
                    message="job-owned record id must start with jobId",
                    instancePath="$.id",
                    recordId=record_id,
                )
        if isinstance(record_id, str) and isinstance(operation_id, str):
            if not record_id.startswith(operation_id):
                result.add(
                    errorCode="reference_integrity.operation_owned_id_mismatch",
                    category="reference_integrity",
                    message="operation-owned record id must start with jobOperationId",
                    instancePath="$.id",
                    recordId=record_id,
                )

    def _validate_document_record_versions(self, instance: dict[str, Any], result: ValidationResult) -> None:
        if "documentVersion" not in instance:
            return
        schema_version = instance.get("schemaVersion")
        document_version = instance.get("documentVersion")
        record_id = self._record_id(instance)
        if isinstance(document_version, str) and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", document_version):
            result.add(
                errorCode="application_validation.document_version_format",
                category="application_validation",
                message="documentVersion must use document format x.y, not schema format x.y.z",
                instancePath="$.documentVersion",
                recordId=record_id,
            )
        if isinstance(schema_version, str) and re.fullmatch(r"[0-9]+\.[0-9]+", schema_version):
            result.add(
                errorCode="application_validation.schema_version_format",
                category="application_validation",
                message="schemaVersion must use schema format x.y.z, not document format x.y",
                instancePath="$.schemaVersion",
                recordId=record_id,
            )

    def _record_id(self, instance: Any) -> str | None:
        if isinstance(instance, dict) and isinstance(instance.get("id"), str):
            return instance["id"]
        return None

    def _json_path(self, path: Any) -> str:
        parts = list(path)
        if not parts:
            return "$"
        rendered = "$"
        for part in parts:
            if isinstance(part, int):
                rendered += f"[{part}]"
            else:
                rendered += f".{part}"
        return rendered

    def _validation_error_instance_path(self, error: Any) -> str:
        if error.validator == "required":
            match = re.search(r"'([^']+)' is a required property", error.message)
            if match:
                return f"{self._json_path(error.path)}.{match.group(1)}"
        if error.validator == "additionalProperties":
            match = re.search(r"\('([^']+)'.*(?:was|were) unexpected\)", error.message)
            if match:
                return f"{self._json_path(error.path)}.{match.group(1)}"
        return self._json_path(error.path)
