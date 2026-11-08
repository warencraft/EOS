"""ADR-0017: shared entity contract and diagnostic tests."""
import re
import unittest

from jsonschema import Draft202012Validator

from scripts.validation import EosValidator
from tests.validation_support import BASE, FIXTURES, INDEX, VALID, entity_fixture, load_json


COMMON = set("id schemaVersion recordVersion revision status createdAt createdBy updatedAt updatedBy sourceLinks changeSummary".split())
ENTITY_PROFILES = {
    "engineering-item": {
        "validCases": ["minimal-draft", "populated-source-links"],
        "idFamily": "EIT", "required": COMMON | {"name"},
        "optional": {"description", "classifications"},
        "owned": {"classifications": "classification"}, "indexDef": "engineeringItem",
        "collection": None, "deferredValue": "fictional",
    },
    "machine": {
        "validCases": ["minimal-draft", "populated-source-links"],
        "idFamily": "MAC", "required": COMMON | {"name"},
        "optional": {"description", "notes", "properties", "classifications"},
        "owned": {"properties": "property-record", "classifications": "classification"},
        "indexDef": "machine", "collection": None, "deferredValue": "fictional",
    },
    "material": {
        "validCases": (
            "conflicting-claims description empty-classifications empty-properties "
            "empty-source-links minimal-draft multiple-classifications multiple-properties notes "
            "one-classification one-property populated-source-links properties-classifications "
            "replaced-by replaces same-property-multiple"
        ).split(),
        "idFamily": "MAT", "required": COMMON | {"name"},
        "optional": {"description", "notes", "properties", "classifications", "replaces", "replacedBy"},
        "owned": {"properties": "property-record", "classifications": "classification"},
        "indexDef": "material", "collection": "materials", "caseBase": "legacy-draft",
        "deferredValue": [],
        "deferredValues": {
            "chemicalComposition": {}, "deliveryCondition": "Example state", "designation": "Example designation",
            "materialFamily": "Example family", "heatTreatment": "Example process", "materialCondition": "Example state",
            "supplierId": "SUP-9001", "materialType": "Example type", "verificationStatus": "Draft",
        },
    },
    "supplier": {
        "validCases": (
            "approved-with-source description empty-classifications empty-source-links full-profile "
            "minimal-draft multiple-classifications notes one-classification populated-source-links "
            "review-with-source without-classifications"
        ).split(),
        "idFamily": "SUP", "required": COMMON | {"name"},
        "optional": {"description", "notes", "classifications"},
        "owned": {"classifications": "classification"}, "indexDef": "supplier",
        "collection": None,
        "deferredValue": "fictional-excluded-value",
    },
    "manufacturing-process": {
        "validCases": (
            "approved description empty-classifications empty-source-links full-profile "
            "minimal-draft multiple-classifications notes one-classification populated-source-links "
            "review"
        ).split(),
        "idFamily": "TEC", "required": COMMON | {"name", "description"},
        "optional": {"classifications", "notes"},
        "owned": {"classifications": "classification"}, "indexDef": "manufacturingProcess",
        "collection": None, "deferredValue": "fictional",
    },
}


def mutate(record, op):
    """Apply one table operation to a fresh fixture, never create implicit parents."""
    verb, path, *value = op
    if not path.startswith("/") or re.search(r"~(?![01])", path):
        raise ValueError(f"Invalid JSON pointer: {path}")
    if (verb, len(value)) not in {("remove", 0), ("set", 1)}:
        raise ValueError(f"Invalid operation: {op}")
    parts = path[1:].split("/")
    node = record
    for i, token in enumerate(parts):
        key = token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, list):
            if not re.fullmatch("0|[1-9][0-9]*", key):
                raise ValueError(f"Invalid array index: {key}")
            key = int(key)
        if i < len(parts) - 1:
            node = node[key]
        elif verb == "remove":
            del node[key]
        else:
            node[key] = value[0]


def negative_cases(family, profile, table):
    base = entity_fixture(family, profile.get("caseBase", "minimal-draft"))
    for field in sorted(profile["required"]):
        path = "$." + field
        yield "missing-" + field, {k: v for k, v in base.items() if k != field}, [("schema_validation.required", path)]
        expected = [("schema_validation.type", path)]
        if field == "status":
            expected.append(("schema_validation.enum", path))
        yield field + "-null", {**base, field: None}, expected
    yield "name-empty", {**base, "name": ""}, [("schema_validation.minLength", "$.name")]
    yield "generic-wrong-family", {**base, "id": "XXX-9001"}, [("schema_validation.pattern", "$.id")]
    yield "generic-unknown", {**base, "unknownField": True}, [("schema_validation.additionalProperties", "$.unknownField")]
    yield "array", [], [("schema_validation.type", "$")]
    yield "empty-object", {}, [("schema_validation.required", "$." + k) for k in profile["required"]]
    if family in {"supplier", "material"}:
        yield "malformed-source-link", {**base, "sourceLinks": [{}]}, [
            ("schema_validation.required", "$.sourceLinks[0]." + k)
            for k in ("sourceReferenceId", "sourceClass", "usageType", "verificationStatus")
        ] + [("schema_validation.anyOf", "$.sourceLinks[0]")]
    if "properties" in profile["owned"]:
        yield "invalid-property-record", {**base, "properties": [{"propertyId": "PRP-980001"}]}, [
            ("schema_validation.required", "$.properties[0]." + k)
            for k in ("valueType", "verificationStatus", "sourceLinks")
        ] + [("schema_validation.oneOf", "$.properties[0]")]
    if set(table) != {"cases", "deferred"} or not table["cases"]:
        raise ValueError(f"Missing or unexpected case data: {family}")
    for row in table["cases"]:
        if len(row["ops"]) != 1:
            raise ValueError(f"Expected one isolated mutation: {row['name']}")
        if not re.fullmatch(r"[a-z0-9-]+", row["base"]):
            raise ValueError(f"Invalid fixture base: {row['base']}")
        record = entity_fixture(family, row["base"])
        mutate(record, row["ops"][0])
        yield row["name"], record, [(row["expect"]["errorCode"], row["expect"]["path"])]
    for field in table["deferred"]:
        if field in profile["required"] | profile["optional"]:
            raise ValueError(f"Deferred field is allowed: {field}")
        value = profile.get("deferredValues", {}).get(field, profile["deferredValue"])
        yield "deferred-" + field, {**base, field: value}, [
            ("schema_validation.additionalProperties", "$." + field)]


class EntityProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = EosValidator()

    def test_contract_and_fixtures(self):
        for family, profile in ENTITY_PROFILES.items():
            uri = BASE + f"entities/{family}.schema.json"
            schema = self.validator.registry.by_id[uri]
            index = self.validator.registry.by_id[INDEX]
            with self.subTest(family=family):
                Draft202012Validator.check_schema(schema)
                self.assertTrue(self.validator.validate_schema_definition(uri).ok)
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertEqual(schema["type"], "object")
                self.assertIs(schema["additionalProperties"], False)
                self.assertEqual(set(schema["required"]), profile["required"])
                self.assertEqual(set(schema["properties"]), profile["required"] | profile["optional"])
                self.assertEqual(set(entity_fixture(family)), profile["required"])
                self.assertTrue(entity_fixture(family, "populated-source-links")["sourceLinks"])
                self.assertEqual(schema["properties"]["id"]["$ref"], BASE + "common/identifiers.schema.json#/$defs/" + profile["idFamily"])
                for field in COMMON - {"id"} | ({"notes"} & profile["optional"]):
                    self.assertEqual(schema["properties"][field]["$ref"], BASE + "common/metadata.schema.json#/properties/" + field)
                for field, contract in profile["owned"].items():
                    self.assertEqual(schema["properties"][field]["items"]["$ref"], BASE + f"knowledge-core/{contract}.schema.json")
                self.assertEqual(index["$defs"][profile["indexDef"]]["$ref"], uri)
                collections = {key for key, prop in index["properties"].items()
                               if prop.get("items", {}).get("$ref") == "#/$defs/" + profile["indexDef"]}
                self.assertEqual(collections, {profile["collection"]} if profile["collection"] else set())
            files = sorted(VALID.glob(f"{family}-*-valid.json"))
            expected_names = {f"{family}-{case}-valid.json" for case in profile["validCases"]}
            self.assertLessEqual(expected_names, {p.name for p in files})
            for file in files:
                with self.subTest(family=family, file=file.name):
                    result = self.validator.validate_json_file(file, uri)
                    self.assertTrue(result.ok, result.errors)

    def test_negative_cases(self):
        for family, profile in ENTITY_PROFILES.items():
            uri = BASE + f"entities/{family}.schema.json"
            table = load_json(FIXTURES / "invalid-cases" / (family + ".json"))
            seen = set()
            self.assertTrue(self.validator.validate(entity_fixture(family, profile.get("caseBase", "minimal-draft")), uri).ok)
            for name, record, expected in negative_cases(family, profile, table):
                with self.subTest(family=family, case=name):
                    self.assertNotIn(name, seen)
                    seen.add(name)
                    result = self.validator.validate(record, uri)
                    root_id = record.get("id") if isinstance(record, dict) else None
                    self.assertFalse(result.ok)
                    self.assertCountEqual(
                        [(e.errorCode, e.path, e.recordId, e.referencedId, e.severity, e.category) for e in result.errors],
                        [(code, path, root_id, None, "error", "schema_validation") for code, path in expected],
                    )

    def test_root_provenance(self):
        for family in ENTITY_PROFILES:
            for status in ("Draft", "Review", "Approved"):
                for populated in (False, True):
                    base = entity_fixture(family, "populated-source-links" if populated else "minimal-draft")
                    for flags in ({}, {"has_verifiable_claims": False}, {"has_verifiable_claims": True}):
                        with self.subTest(family=family, status=status, populated=populated, flags=flags):
                            r = self.validator.validate({**base, "status": status}, BASE + f"entities/{family}.schema.json", **flags)
                            expected = [] if populated or status == "Draft" else [
                                ("application_validation", "application_validation.source_links_required", "$.sourceLinks", base["id"])]
                            self.assertEqual([(e.category, e.errorCode, e.path, e.recordId) for e in r.errors], expected)
