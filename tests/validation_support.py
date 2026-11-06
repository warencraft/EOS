"""Shared paths and fresh JSON inputs for EOS entity tests."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://eos.local/schemas/"
INDEX = BASE + "index.schema.json"
FIXTURES = ROOT / "tests/fixtures"
VALID = FIXTURES / "valid/entities"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def entity_fixture(family, name="minimal-draft"):
    if (family, name) == ("material", "legacy-draft"):
        return {**entity_fixture("material"), "name": "Example Material", "changeSummary": "Fictional fixture."}
    return load_json(VALID / f"{family}-{name}-valid.json")
