from __future__ import annotations

import argparse
from pathlib import Path

from .validator import EosValidator, MissingValidationDependencyError


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate EOS JSON records.")
    parser.add_argument("record", type=Path)
    parser.add_argument("schema_id")
    parser.add_argument("--has-verifiable-claims", action="store_true")
    args = parser.parse_args()

    try:
        validator = EosValidator()
    except MissingValidationDependencyError as exc:
        print(str(exc))
        return 2
    result = validator.validate_json_file(
        args.record,
        args.schema_id,
        has_verifiable_claims=args.has_verifiable_claims,
    )
    if result.ok:
        print("OK")
        return 0
    for error in result.errors:
        print(f"{error.path}: {error.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
