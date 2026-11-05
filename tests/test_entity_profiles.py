"""ADR-0017: shared entity contracts and legacy equivalence checkpoints."""
import re
import unittest

from jsonschema import Draft202012Validator

from scripts.validation import EosValidator
from tests.validation_support import BASE, FIXTURES, INDEX, INVALID, VALID, entity_fixture, load_json


COMMON = set("id schemaVersion recordVersion revision status createdAt createdBy updatedAt updatedBy sourceLinks changeSummary".split())
ENTITY_PROFILES = {
    "supplier": {
        "idFamily": "SUP", "required": COMMON | {"name"},
        "optional": {"description", "notes", "classifications"},
        "owned": {"classifications": "classification"}, "indexDef": "supplier",
        "collection": None,
        "deferredValue": "fictional-excluded-value",
    },
    "manufacturing-process": {
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
    base = entity_fixture(family)
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
        yield "deferred-" + field, {**base, field: profile["deferredValue"]}, [
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
                for field in COMMON - {"id"} | {"notes"}:
                    self.assertEqual(schema["properties"][field]["$ref"], BASE + "common/metadata.schema.json#/properties/" + field)
                for field, contract in profile["owned"].items():
                    self.assertEqual(schema["properties"][field]["items"]["$ref"], BASE + f"knowledge-core/{contract}.schema.json")
                self.assertEqual(index["$defs"][profile["indexDef"]]["$ref"], uri)
                collections = {key for key, prop in index["properties"].items()
                               if prop.get("items", {}).get("$ref") == "#/$defs/" + profile["indexDef"]}
                self.assertEqual(collections, {profile["collection"]} if profile["collection"] else set())
            for file in sorted(VALID.glob(f"{family}-*-valid.json")):
                with self.subTest(family=family, file=file.name):
                    result = self.validator.validate_json_file(file, uri)
                    self.assertTrue(result.ok, result.errors)

    def test_negative_cases(self):
        for family, profile in ENTITY_PROFILES.items():
            uri = BASE + f"entities/{family}.schema.json"
            table = load_json(FIXTURES / "invalid-cases" / (family + ".json"))
            seen = set()
            for name, record, expected in negative_cases(family, profile, table):
                with self.subTest(family=family, case=name):
                    self.assertNotIn(name, seen)
                    seen.add(name)
                    result = self.validator.validate(record, uri)
                    self.assertCountEqual([(e.errorCode, e.path) for e in result.errors], expected)

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

    def test_supplier_pilot_equivalence(self):
        # Retain this independent comparison until the pilot is reviewed.
        family = "supplier"
        table = load_json(FIXTURES / "invalid-cases/supplier.json")
        generated = {name: record for name, record, _ in negative_cases(family, ENTITY_PROFILES[family], table)}
        generated["empty-object"] = {}
        generated["sourceLinks-malformed"] = {**entity_fixture(family), "sourceLinks": [{}]}
        legacy = sorted(INVALID.glob("supplier-*-invalid.json"))
        self.assertTrue(legacy)
        for file in legacy:
            name = file.name[len("supplier-"):-len("-invalid.json")]
            with self.subTest(case=name):
                self.assertEqual(generated[name], load_json(file))
        uri = BASE + "entities/supplier.schema.json"
        for name, expected in (
            ("empty-object", [("schema_validation.required", "$." + k) for k in ENTITY_PROFILES[family]["required"]]),
            ("sourceLinks-malformed", [("schema_validation.required", "$.sourceLinks[0]." + k)
             for k in ("sourceReferenceId", "sourceClass", "usageType", "verificationStatus")]
             + [("schema_validation.anyOf", "$.sourceLinks[0]")]),
        ):
            with self.subTest(case=name):
                result = self.validator.validate(generated[name], uri)
                self.assertCountEqual([(e.errorCode, e.path) for e in result.errors], expected)

    def test_manufacturing_process_legacy_equivalence(self):
        family = "manufacturing-process"
        uri = BASE + f"entities/{family}.schema.json"
        profile = ENTITY_PROFILES[family]
        table = load_json(FIXTURES / "invalid-cases" / (family + ".json"))
        generated = {name: (record, errors) for name, record, errors in negative_cases(family, profile, table)}
        generated["empty-object"] = {}, [("schema_validation.required", "$." + k) for k in profile["required"]]

        # Legacy names differ only for these generated cases. The table keeps original names.
        mapping = {row["name"]: row["name"] for row in table["cases"]}
        mapping.update(("deferred-" + k, "deferred-" + k) for k in table["deferred"])
        for field in ("id", "name", "description", "sourceLinks"):
            mapping["missing-" + field] = "missing-" + field
            mapping["null-" + field] = field + "-null"
        mapping.update({"array-root": "array", "empty-name": "name-empty", "empty-object": "empty-object"})
        files = {p.name[len(family)+1:-len("-invalid.json")]: p for p in INVALID.glob(f"{family}-*-invalid.json")}
        self.assertEqual(set(mapping), set(files))
        for old, target in mapping.items():
            with self.subTest(legacy=old, target=target):
                record, errors = generated[target]
                self.assertEqual(record, load_json(files[old]))
                root_id = record.get("id") if isinstance(record, dict) else None
                expected = [(code, path, root_id, None, "error") for code, path in errors]
                for result in (self.validator.validate_json_file(files[old], uri), self.validator.validate(record, uri)):
                    self.assertCountEqual([(e.errorCode, e.path, e.recordId, e.referencedId, e.severity)
                                           for e in result.errors], expected)
