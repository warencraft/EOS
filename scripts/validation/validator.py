from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .schema_loader import SchemaRegistry


INSTALL_INSTRUCTIONS = (
    "Missing dependency 'jsonschema'. Create a virtual environment and install the project: "
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


class MissingValidationDependencyError(RuntimeError):
    pass


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"JSON value {value} is not allowed; use finite JSON numbers only")


def _load_jsonschema() -> tuple[Any, Any, Any, Any]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker, SchemaError
        from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on runtime
        raise MissingValidationDependencyError(INSTALL_INSTRUCTIONS) from exc
    return Draft202012Validator, FormatChecker, SchemaError, JsonSchemaValidationError


@dataclass
class ValidationError:
    errorCode: str
    category: str
    message: str
    instancePath: str = "$"
    schemaPath: str = ""
    recordId: str | None = None
    severity: str = "error"

    @property
    def path(self) -> str:
        return self.instancePath


@dataclass
class ValidationResult:
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def add(
        self,
        *,
        errorCode: str,
        category: str,
        message: str,
        instancePath: str = "$",
        schemaPath: str = "",
        recordId: str | None = None,
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
                severity=severity,
            )
        )


class EosValidator:
    def __init__(self, registry: SchemaRegistry | None = None) -> None:
        self.registry = registry or SchemaRegistry()
        self.registry.load_all()
        self.Draft202012Validator, self.FormatChecker, self.SchemaError, self.JsonSchemaValidationError = _load_jsonschema()
        self.referencing_registry = self.registry.as_referencing_registry()
        self.format_checker = self._build_format_checker()

    def validate_json_file(
        self,
        instance_path: Path,
        schema_id: str,
        *,
        has_verifiable_claims: bool = False,
    ) -> ValidationResult:
        result = ValidationResult()
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
        return self.validate(instance, schema_id, has_verifiable_claims=has_verifiable_claims)

    def validate(
        self,
        instance: Any,
        schema_id: str,
        *,
        has_verifiable_claims: bool = False,
    ) -> ValidationResult:
        result = ValidationResult()
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

        self._validate_application_rules(instance, result, has_verifiable_claims=has_verifiable_claims)
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
        has_verifiable_claims: bool,
    ) -> None:
        if not isinstance(instance, dict):
            return
        self._validate_finite_numbers(instance, result)
        self._validate_source_links_rule(instance, result, has_verifiable_claims=has_verifiable_claims)
        self._validate_source_link_ids(instance, result)
        self._validate_hierarchical_ids(instance, result)
        self._validate_document_record_versions(instance, result)

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

    def _validate_source_links_rule(
        self,
        instance: dict[str, Any],
        result: ValidationResult,
        *,
        has_verifiable_claims: bool,
    ) -> None:
        status = instance.get("status")
        source_links = instance.get("sourceLinks")
        if status in {"Review", "Approved"} and has_verifiable_claims and not source_links:
            result.add(
                errorCode="application_validation.source_links_required",
                category="application_validation",
                message="Review or Approved records with verifiable claims require sourceLinks",
                instancePath="$.sourceLinks",
                recordId=self._record_id(instance),
            )

    def _validate_source_link_ids(self, instance: Any, result: ValidationResult, path: str = "$") -> None:
        if isinstance(instance, dict):
            if "sourceReferenceId" in instance:
                value = instance["sourceReferenceId"]
                if not isinstance(value, str) or not re.fullmatch(r"SRC-[0-9]{6}", value):
                    result.add(
                        errorCode="reference_integrity.invalid_source_reference_id",
                        category="reference_integrity",
                        message="sourceReferenceId must be a SRC-xxxxxx identifier",
                        instancePath=f"{path}.sourceReferenceId",
                        recordId=self._record_id(instance),
                    )
            for key, value in instance.items():
                self._validate_source_link_ids(value, result, f"{path}.{key}")
        elif isinstance(instance, list):
            for index, value in enumerate(instance):
                self._validate_source_link_ids(value, result, f"{path}[{index}]")

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
