from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from jsonschema import Draft202012Validator

from scripts.validation import (
    CatalogKind,
    CatalogLifecyclePolicy,
    CatalogRecord,
    CatalogRegistry,
    EosValidator,
    ValidationContext,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://eos.local/schemas/"
PROCESS = BASE + "entities/manufacturing-process.schema.json"
INDEX = BASE + "index.schema.json"
VALID = ROOT / "tests/fixtures/valid/entities"
INVALID = ROOT / "tests/fixtures/invalid/entities"


def fixture(name: str = "minimal-draft") -> dict:
    return json.loads((VALID / f"manufacturing-process-{name}-valid.json").read_text(encoding="utf-8"))


class ManufacturingProcessValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = EosValidator()
        cls.schema = cls.validator.registry.by_id[PROCESS]
        data = json.loads(
            (ROOT / "tests/fixtures/catalog-context/fictional-catalog-context.json").read_text(encoding="utf-8")
        )
        cls.entries = data["classificationEntries"]
        cls.context = ValidationContext(CatalogRegistry(classification_entries=cls.entries))

    def assert_valid(self, record: dict) -> None:
        result = self.validator.validate(record, PROCESS)
        self.assertTrue(result.ok, [(e.category, e.path, e.message) for e in result.errors])

    def test_schema_definition_and_closed_shape(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        self.assertTrue(self.validator.validate_schema_definition(PROCESS).ok)
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(self.schema["type"], "object")
        self.assertIs(self.schema["additionalProperties"], False)

    def test_valid_fixtures(self) -> None:
        files = sorted(VALID.glob("manufacturing-process-*-valid.json"))
        self.assertEqual(len(files), 11)
        for file in files:
            with self.subTest(file=file.name):
                result = self.validator.validate_json_file(file, PROCESS)
                self.assertTrue(result.ok, result.errors)

    def test_invalid_fixtures(self) -> None:
        files = sorted(INVALID.glob("manufacturing-process-*-invalid.json"))
        self.assertEqual(len(files), 148)
        for file in files:
            with self.subTest(file=file.name):
                result = self.validator.validate_json_file(file, PROCESS)
                self.assertFalse(result.ok, file.name)
                self.assertTrue(any(e.category == "schema_validation" for e in result.errors))
                self.assertFalse(any(e.category == "schema_definition" for e in result.errors))

    def test_tec_reuses_exact_central_definition(self) -> None:
        ref = BASE + "common/identifiers.schema.json#/$defs/TEC"
        self.assertEqual(self.schema["properties"]["id"]["$ref"], ref)
        self.assertNotIn("pattern", self.schema["properties"]["id"])
        self.assertEqual(self.validator.registry.get(ref)["pattern"], "^TEC-[0-9]{4}$")
        for value in ("TEC-0001", "TEC-9001", "TEC-9999"):
            self.assert_valid({**fixture(), "id": value})

    def test_common_metadata_refs_and_required_fields(self) -> None:
        metadata = self.validator.registry.by_id[BASE + "common/metadata.schema.json"]
        self.assertEqual(set(self.schema["required"]), set(metadata["required"]) | {"name", "description"})
        for field in (set(metadata["required"]) - {"id"}) | {"notes"}:
            with self.subTest(field=field):
                ref = BASE + "common/metadata.schema.json#/properties/" + field
                self.assertEqual(self.schema["properties"][field]["$ref"], ref)
                self.assertEqual(self.validator.registry.get(ref), metadata["properties"][field])
        self.assertEqual(set(self.schema["properties"]) - set(self.schema["required"]),
                         {"classifications", "notes"})

    def test_minimum_needs_no_optional_or_deferred_fields(self) -> None:
        record = fixture()
        self.assertEqual(set(record), set(self.schema["required"]))
        for field in ("notes", "classifications", "properties", "parameters",
                      "materialIds", "machineIds", "supplierIds", "qualificationStatus",
                      "capabilities", "setupTime", "cost"):
            self.assertNotIn(field, record)
        self.assert_valid(record)

    def test_name_is_label_without_uniqueness_or_normalization(self) -> None:
        record = fixture()
        before = copy.deepcopy(record)
        self.assert_valid(record)
        self.assert_valid({**record, "id": "TEC-9002"})
        self.assertEqual(record, before)
        self.assert_valid({**record, "name": "  Fiktívny názov  "})

    def test_description_and_common_notes_semantics(self) -> None:
        self.assert_valid(fixture("description"))
        self.assert_valid(fixture("notes"))
        self.assert_valid({**fixture(), "notes": ""})
        self.assertFalse(self.validator.validate({**fixture(), "description": ""}, PROCESS).ok)

    def test_source_links_reuses_source_link_contract(self) -> None:
        ref = self.schema["properties"]["sourceLinks"]["$ref"]
        self.assertEqual(self.validator.registry.get(ref)["items"]["$ref"], BASE + "common/source-link.schema.json")
        self.assert_valid(fixture("populated-source-links"))

    def test_source_links_required_with_exact_path(self) -> None:
        record = fixture()
        del record["sourceLinks"]
        result = self.validator.validate(record, PROCESS)
        self.assertIn(("schema_validation.required", "$.sourceLinks"),
                      [(e.errorCode, e.path) for e in result.errors])

    def test_review_approved_require_root_provenance(self) -> None:
        self.assert_valid(fixture())
        for status in ("Review", "Approved"):
            with self.subTest(status=status):
                result = self.validator.validate({**fixture(), "status": status}, PROCESS)
                self.assertEqual([(e.category, e.errorCode, e.path) for e in result.errors],
                                 [("application_validation", "application_validation.source_links_required", "$.sourceLinks")])
                self.assert_valid({**fixture("populated-source-links"), "status": status})

    def test_assignment_sources_do_not_replace_root_sources(self) -> None:
        record = fixture("multiple-classifications")
        record["status"] = "Approved"
        self.assertTrue(record["classifications"][1]["sourceLinks"])
        result = self.validator.validate(record, PROCESS)
        self.assertIn("$.sourceLinks", [e.path for e in result.errors])

    def test_lifecycle_uses_record_status_not_business_status(self) -> None:
        for status in ("Draft", "Review", "Approved", "Deprecated", "Archived"):
            self.assert_valid({**fixture("populated-source-links"), "status": status})
        for status in ("Qualified", "ApprovedForProduction", "Accepted"):
            self.assertFalse(self.validator.validate({**fixture(), "status": status}, PROCESS).ok)

    def test_multiple_classifications_and_assignment_ref(self) -> None:
        self.assertEqual(self.schema["properties"]["classifications"]["items"]["$ref"],
                         BASE + "knowledge-core/classification.schema.json")
        for name in ("empty-classifications", "one-classification", "multiple-classifications"):
            self.assert_valid(fixture(name))
        self.assertEqual(len(fixture("multiple-classifications")["classifications"]), 2)

    def test_every_deferred_fixture_fails_as_unknown_field(self) -> None:
        for file in sorted(INVALID.glob("manufacturing-process-deferred-*-invalid.json")):
            field = file.name.removeprefix("manufacturing-process-deferred-").removesuffix("-invalid.json")
            with self.subTest(field=field):
                record = json.loads(file.read_text(encoding="utf-8"))
                result = self.validator.validate(record, PROCESS)
                self.assertEqual([(e.errorCode, e.path) for e in result.errors],
                                 [("schema_validation.additionalProperties", f"$.{field}")])
                del record[field]
                self.assert_valid(record)

    def test_observation_accepts_tec_subject_without_ownership(self) -> None:
        files = sorted((ROOT / "tests/fixtures/valid/knowledge-core").glob("observation-*-valid.json"))
        self.assertTrue(files)
        record = json.loads(files[0].read_text(encoding="utf-8"))
        record["subjectId"] = "TEC-9001"
        self.assertTrue(self.validator.validate(record, BASE + "knowledge-core/observation.schema.json").ok)
        for field in ("observations", "observationIds", "properties"):
            self.assertNotIn(field, self.schema["properties"])

    def test_index_definition_resolves_without_entity_collection(self) -> None:
        index = self.validator.registry.by_id[INDEX]
        self.assertEqual(index["$defs"]["manufacturingProcess"]["$ref"], PROCESS)
        self.assertNotIn("manufacturingProcesses", index["properties"])
        validator = Draft202012Validator(
            {"$ref": INDEX + "#/$defs/manufacturingProcess"},
            registry=self.validator.referencing_registry,
            format_checker=self.validator.format_checker,
        )
        self.assertFalse(list(validator.iter_errors(fixture())))
        self.assertTrue(list(validator.iter_errors({**fixture(), "id": "MAT-9001"})))

    def test_contract_only_needs_no_catalog_registry(self) -> None:
        for record in (fixture(), fixture("empty-classifications"), fixture("one-classification")):
            self.assert_valid(record)
        result = self.validator.validate_with_context(fixture(), PROCESS, ValidationContext(CatalogRegistry()))
        self.assertTrue(result.ok)

    def test_context_requires_explicit_context_consistently(self) -> None:
        result = self.validator.validate_with_context(fixture(), PROCESS, None)
        self.assertEqual([e.errorCode for e in result.errors], ["catalog_validation.context_required"])

    def test_context_valid_cls_and_multiple_assignments(self) -> None:
        record = fixture("one-classification")
        record["classifications"] *= 2
        before = copy.deepcopy(record)
        result = self.validator.validate_with_context(record, PROCESS, self.context)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(record, before)

    def test_context_missing_cls_keeps_nested_path_and_root_id(self) -> None:
        record = fixture("one-classification")
        record["classifications"].append({"classificationId": "CLS-999999"})
        result = self.validator.validate_with_context(record, PROCESS, self.context)
        self.assertEqual([(e.category, e.path, e.recordId, e.referencedId) for e in result.errors],
                         [("reference_integrity", "$.classifications[1].classificationId", "TEC-9001", "CLS-999999")])

    def test_context_cls_type_check_is_reused(self) -> None:
        wrong = CatalogRecord(CatalogKind.UNIT, {"id": "CLS-980001", "status": "Approved"})
        with patch.object(CatalogRegistry, "resolve", return_value=wrong):
            result = self.validator.validate_with_context(fixture("one-classification"), PROCESS, self.context)
        self.assertEqual([(e.errorCode, e.path) for e in result.errors],
                         [("reference_integrity.reference_type_mismatch", "$.classifications[0].classificationId")])

    def test_context_cls_lifecycle_default_and_authoring(self) -> None:
        for status in ("Draft", "Review", "Approved", "Deprecated", "Archived"):
            entry = {**copy.deepcopy(self.entries[0]), "status": status}
            self.assertTrue(self.validator.validate(
                entry, BASE + "catalogs/classification-catalog-entry.schema.json"
            ).ok)
            catalogs = CatalogRegistry(classification_entries=[entry])
            for policy in (CatalogLifecyclePolicy.DEFAULT, CatalogLifecyclePolicy.AUTHORING):
                with self.subTest(status=status, policy=policy):
                    record = {**fixture(), "classifications": [{"classificationId": entry["id"]}]}
                    result = self.validator.validate_with_context(record, PROCESS, ValidationContext(catalogs, policy))
                    expected_ok = policy.allows(status)
                    self.assertEqual(result.ok, expected_ok)
                    expected = []
                    if not expected_ok or status == "Deprecated":
                        code = "catalog_validation.deprecated_reference" if status == "Deprecated" else "catalog_validation.catalog_status_not_allowed"
                        severity = "warning" if status == "Deprecated" else "error"
                        expected = [("catalog_validation", code, "$.classifications[0].classificationId",
                                     record["id"], entry["id"], severity)]
                    self.assertEqual(
                        [(e.category, e.errorCode, e.path, e.recordId, e.referencedId, e.severity) for e in result.errors],
                        expected,
                    )
                    self.assertEqual(len(result.warnings), 1 if status == "Deprecated" else 0)

    def test_process_root_source_rule_runs_once_with_explicit_flag(self) -> None:
        for status in ("Draft", "Review", "Approved"):
            for populated in (False, True):
                record = {**fixture("populated-source-links" if populated else "minimal-draft"), "status": status}
                for kwargs in ({}, {"has_verifiable_claims": False}, {"has_verifiable_claims": True}):
                    with self.subTest(status=status, populated=populated, kwargs=kwargs):
                        result = self.validator.validate(record, PROCESS, **kwargs)
                        expected = [] if populated or status == "Draft" else [
                            ("application_validation", "application_validation.source_links_required", "$.sourceLinks", record["id"])
                        ]
                        self.assertEqual([(e.category, e.errorCode, e.path, e.recordId) for e in result.errors], expected)
                        self.assertEqual(result.ok, not expected)

    def test_nested_schema_errors_preserve_exact_paths(self) -> None:
        record = fixture("one-classification")
        record["classifications"][0]["sourceLinks"] = [{"sourceReferenceId": "TEC-9001"}]
        result = self.validator.validate_with_context(record, PROCESS, self.context)
        self.assertIn(("schema_validation.pattern", "$.classifications[0].sourceLinks[0].sourceReferenceId"),
                      [(e.errorCode, e.path) for e in result.errors])
        self.assertNotIn("catalog_validation", result.executedLayers)


    def test_invalid_fixture_expected_reason_and_path(self) -> None:
        expected = {
            "empty-object": ["required","$.id"],
            "array-root": ["type","$"],
            "missing-id": ["required","$.id"],
            "null-id": ["type","$.id"],
            "missing-name": ["required","$.name"],
            "null-name": ["type","$.name"],
            "missing-description": ["required","$.description"],
            "null-description": ["type","$.description"],
            "missing-sourceLinks": ["required","$.sourceLinks"],
            "null-sourceLinks": ["type","$.sourceLinks"],
            "malformed-tec": ["pattern","$.id"],
            "wrong-prefix": ["pattern","$.id"],
            "lowercase-tec": ["pattern","$.id"],
            "wrong-tec-padding": ["pattern","$.id"],
            "empty-name": ["minLength","$.name"],
            "name-wrong-type": ["type","$.name"],
            "empty-description": ["minLength","$.description"],
            "description-wrong-type": ["type","$.description"],
            "sourceLinks-wrong-type": ["type","$.sourceLinks"],
            "notes-wrong-type": ["type","$.notes"],
            "classifications-wrong-type": ["type","$.classifications"],
            "malformed-source-link": ["pattern","$.sourceLinks[0].sourceReferenceId"],
            "invalid-classification": ["pattern","$.classifications[0].classificationId"],
            "deferred-unknownField": ["additionalProperties","$.unknownField"],
            "deferred-properties": ["additionalProperties","$.properties"],
            "deferred-conditions": ["additionalProperties","$.conditions"],
            "deferred-observations": ["additionalProperties","$.observations"],
            "deferred-observationIds": ["additionalProperties","$.observationIds"],
            "deferred-parameters": ["additionalProperties","$.parameters"],
            "deferred-parameterDefinitions": ["additionalProperties","$.parameterDefinitions"],
            "deferred-parameterValues": ["additionalProperties","$.parameterValues"],
            "deferred-settings": ["additionalProperties","$.settings"],
            "deferred-recipe": ["additionalProperties","$.recipe"],
            "deferred-processParameters": ["additionalProperties","$.processParameters"],
            "deferred-materialIds": ["additionalProperties","$.materialIds"],
            "deferred-supportedMaterialIds": ["additionalProperties","$.supportedMaterialIds"],
            "deferred-materials": ["additionalProperties","$.materials"],
            "deferred-stockMaterialIds": ["additionalProperties","$.stockMaterialIds"],
            "deferred-stockForms": ["additionalProperties","$.stockForms"],
            "deferred-inputStock": ["additionalProperties","$.inputStock"],
            "deferred-machineIds": ["additionalProperties","$.machineIds"],
            "deferred-machines": ["additionalProperties","$.machines"],
            "deferred-machineTypes": ["additionalProperties","$.machineTypes"],
            "deferred-requiredMachines": ["additionalProperties","$.requiredMachines"],
            "deferred-cuttingToolIds": ["additionalProperties","$.cuttingToolIds"],
            "deferred-toolIds": ["additionalProperties","$.toolIds"],
            "deferred-tools": ["additionalProperties","$.tools"],
            "deferred-recommendedTools": ["additionalProperties","$.recommendedTools"],
            "deferred-supplierIds": ["additionalProperties","$.supplierIds"],
            "deferred-suppliers": ["additionalProperties","$.suppliers"],
            "deferred-serviceProviders": ["additionalProperties","$.serviceProviders"],
            "deferred-capabilities": ["additionalProperties","$.capabilities"],
            "deferred-capability": ["additionalProperties","$.capability"],
            "deferred-capabilityLimits": ["additionalProperties","$.capabilityLimits"],
            "deferred-supportedMaterials": ["additionalProperties","$.supportedMaterials"],
            "deferred-maxDiameter": ["additionalProperties","$.maxDiameter"],
            "deferred-maxLength": ["additionalProperties","$.maxLength"],
            "deferred-minTolerance": ["additionalProperties","$.minTolerance"],
            "deferred-achievableTolerance": ["additionalProperties","$.achievableTolerance"],
            "deferred-achievableRoughness": ["additionalProperties","$.achievableRoughness"],
            "deferred-capacity": ["additionalProperties","$.capacity"],
            "deferred-inputs": ["additionalProperties","$.inputs"],
            "deferred-outputs": ["additionalProperties","$.outputs"],
            "deferred-inputTypes": ["additionalProperties","$.inputTypes"],
            "deferred-outputTypes": ["additionalProperties","$.outputTypes"],
            "deferred-inputState": ["additionalProperties","$.inputState"],
            "deferred-outputState": ["additionalProperties","$.outputState"],
            "deferred-effects": ["additionalProperties","$.effects"],
            "deferred-transformedProperties": ["additionalProperties","$.transformedProperties"],
            "deferred-materialConditionIn": ["additionalProperties","$.materialConditionIn"],
            "deferred-materialConditionOut": ["additionalProperties","$.materialConditionOut"],
            "deferred-tolerance": ["additionalProperties","$.tolerance"],
            "deferred-roughness": ["additionalProperties","$.roughness"],
            "deferred-Ra": ["additionalProperties","$.Ra"],
            "deferred-qualityGrade": ["additionalProperties","$.qualityGrade"],
            "deferred-accuracy": ["additionalProperties","$.accuracy"],
            "deferred-surfaceFinish": ["additionalProperties","$.surfaceFinish"],
            "deferred-cuttingSpeed": ["additionalProperties","$.cuttingSpeed"],
            "deferred-feedRate": ["additionalProperties","$.feedRate"],
            "deferred-spindleSpeed": ["additionalProperties","$.spindleSpeed"],
            "deferred-depthOfCut": ["additionalProperties","$.depthOfCut"],
            "deferred-weldingCurrent": ["additionalProperties","$.weldingCurrent"],
            "deferred-weldingVoltage": ["additionalProperties","$.weldingVoltage"],
            "deferred-treatmentTemperature": ["additionalProperties","$.treatmentTemperature"],
            "deferred-treatmentTime": ["additionalProperties","$.treatmentTime"],
            "deferred-standards": ["additionalProperties","$.standards"],
            "deferred-normIds": ["additionalProperties","$.normIds"],
            "deferred-standardIds": ["additionalProperties","$.standardIds"],
            "deferred-documentIds": ["additionalProperties","$.documentIds"],
            "deferred-instructions": ["additionalProperties","$.instructions"],
            "deferred-workInstructions": ["additionalProperties","$.workInstructions"],
            "deferred-wpsIds": ["additionalProperties","$.wpsIds"],
            "deferred-qualified": ["additionalProperties","$.qualified"],
            "deferred-qualificationStatus": ["additionalProperties","$.qualificationStatus"],
            "deferred-validationStatus": ["additionalProperties","$.validationStatus"],
            "deferred-approvedProcess": ["additionalProperties","$.approvedProcess"],
            "deferred-specialProcessApproval": ["additionalProperties","$.specialProcessApproval"],
            "deferred-approvedForProduction": ["additionalProperties","$.approvedForProduction"],
            "deferred-validatedProcess": ["additionalProperties","$.validatedProcess"],
            "deferred-setupTime": ["additionalProperties","$.setupTime"],
            "deferred-cycleTime": ["additionalProperties","$.cycleTime"],
            "deferred-timePerPart": ["additionalProperties","$.timePerPart"],
            "deferred-processingTime": ["additionalProperties","$.processingTime"],
            "deferred-hourlyRate": ["additionalProperties","$.hourlyRate"],
            "deferred-cost": ["additionalProperties","$.cost"],
            "deferred-costPerHour": ["additionalProperties","$.costPerHour"],
            "deferred-costPerKg": ["additionalProperties","$.costPerKg"],
            "deferred-processCost": ["additionalProperties","$.processCost"],
            "deferred-setupCost": ["additionalProperties","$.setupCost"],
            "deferred-price": ["additionalProperties","$.price"],
            "deferred-currency": ["additionalProperties","$.currency"],
            "deferred-coolant": ["additionalProperties","$.coolant"],
            "deferred-gas": ["additionalProperties","$.gas"],
            "deferred-abrasive": ["additionalProperties","$.abrasive"],
            "deferred-consumables": ["additionalProperties","$.consumables"],
            "deferred-energy": ["additionalProperties","$.energy"],
            "deferred-electricity": ["additionalProperties","$.electricity"],
            "deferred-atmosphere": ["additionalProperties","$.atmosphere"],
            "deferred-operatorQualification": ["additionalProperties","$.operatorQualification"],
            "deferred-personnelRequirements": ["additionalProperties","$.personnelRequirements"],
            "deferred-welderQualification": ["additionalProperties","$.welderQualification"],
            "deferred-inspectorQualification": ["additionalProperties","$.inspectorQualification"],
            "deferred-parentProcessId": ["additionalProperties","$.parentProcessId"],
            "deferred-parentIds": ["additionalProperties","$.parentIds"],
            "deferred-children": ["additionalProperties","$.children"],
            "deferred-hierarchyPath": ["additionalProperties","$.hierarchyPath"],
            "deferred-level": ["additionalProperties","$.level"],
            "deferred-aliases": ["additionalProperties","$.aliases"],
            "deferred-synonyms": ["additionalProperties","$.synonyms"],
            "deferred-alternativeNames": ["additionalProperties","$.alternativeNames"],
            "deferred-externalCode": ["additionalProperties","$.externalCode"],
            "deferred-erpCode": ["additionalProperties","$.erpCode"],
            "deferred-camCode": ["additionalProperties","$.camCode"],
            "deferred-processCode": ["additionalProperties","$.processCode"],
            "deferred-externalIdentifiers": ["additionalProperties","$.externalIdentifiers"],
            "deferred-equivalentTo": ["additionalProperties","$.equivalentTo"],
            "deferred-alternativeTo": ["additionalProperties","$.alternativeTo"],
            "deferred-broaderThan": ["additionalProperties","$.broaderThan"],
            "deferred-narrowerThan": ["additionalProperties","$.narrowerThan"],
            "deferred-substituteProcessIds": ["additionalProperties","$.substituteProcessIds"],
            "deferred-replaces": ["additionalProperties","$.replaces"],
            "deferred-replacedBy": ["additionalProperties","$.replacedBy"],
            "deferred-measurementQuality": ["additionalProperties","$.measurementQuality"],
            "deferred-verificationStatus": ["additionalProperties","$.verificationStatus"],
            "deferred-processType": ["additionalProperties","$.processType"],
            "deferred-processFamily": ["additionalProperties","$.processFamily"],
            "deferred-shortName": ["additionalProperties","$.shortName"],
            "deferred-designation": ["additionalProperties","$.designation"],
        }
        for name, (keyword, path) in expected.items():
            with self.subTest(name=name):
                result = self.validator.validate_json_file(
                    INVALID / f"manufacturing-process-{name}-invalid.json", PROCESS
                )
                self.assertIn(("schema_validation." + keyword, path),
                              [(e.errorCode, e.path) for e in result.errors])
                if name not in {"empty-object", "array-root"}:
                    self.assertEqual(len(result.errors), 1, result.errors)

    def test_required_description_and_inspection_label(self) -> None:
        self.assert_valid(fixture("description"))
        record = fixture()
        del record["description"]
        result = self.validator.validate(record, PROCESS)
        self.assertEqual([(e.errorCode, e.path) for e in result.errors],
                         [("schema_validation.required", "$.description")])


if __name__ == "__main__":
    unittest.main()
