"""Príjem podkladov reálnej zákazky do lokálneho priečinka intake/ (ADR-0019).

Súbory zákazky (výkresy, modely, dopyt, ponuka, objednávka, výroba, merania) zostávajú
iba lokálne; git ich ignoruje. Do gitu patrí iba tento nástroj a šablóna.

Spustenie z koreňa repozitára:

    python scripts/job_intake.py new JOB-2026-0001 --title "Hriadeľ pre zákazníka A" --by Marco
    python scripts/job_intake.py scan intake/JOB-2026-0001
    python scripts/job_intake.py check                # všetky zákazky v intake/

`scan` doplní nové súbory do manifest.json (kontrolný súčet, veľkosť, kategória podľa
podpriečinka) a ohlási zmenené a chýbajúce. `check` overí manifest a súbory; návratový
kód 1 = chyba.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INTAKE = ROOT / "intake"
MANIFEST = "manifest.json"
SCHEMA = Path(__file__).with_name("job_intake_manifest.schema.json")

# Podpriečinok zákazky → kategória v manifeste.
FOLDERS = {
    "vykresy": "drawing",
    "modely": "model",
    "dopyt": "inquiry",
    "ponuka": "quote",
    "objednavka": "order",
    "vyroba": "production",
    "merania": "measurement",
    "korespondencia": "correspondence",
    "ine": "other",
}
IGNORED_NAMES = {MANIFEST, ".DS_Store", "Thumbs.db", "desktop.ini"}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def job_files(job_dir: Path) -> dict[str, Path]:
    """Všetky podklady zákazky okrem manifestu a systémových súborov, kľúč = relatívna cesta."""
    found = {}
    for path in sorted(job_dir.rglob("*")):
        if not path.is_file() or path.name in IGNORED_NAMES or path.name.startswith("~$"):
            continue
        rel = path.relative_to(job_dir)
        if any(part.startswith(".") for part in rel.parts):
            continue
        found[rel.as_posix()] = path
    return found


def category_for(rel: str) -> str:
    return FOLDERS.get(rel.split("/", 1)[0], "other") if "/" in rel else "other"


def load_manifest(job_dir: Path) -> dict:
    return json.loads((job_dir / MANIFEST).read_text(encoding="utf-8"))


def save_manifest(job_dir: Path, manifest: dict) -> None:
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    (job_dir / MANIFEST).write_text(text, encoding="utf-8")


def schema_errors(manifest: object) -> list[str]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"manifest {'/'.join(str(p) for p in error.absolute_path) or '$'}: {error.message}"
        for error in sorted(validator.iter_errors(manifest), key=lambda e: list(e.absolute_path))
    ]


def cmd_new(job_ref: str, title: str, by: str, intake: Path = INTAKE) -> Path:
    job_dir = intake / job_ref
    if job_dir.exists():
        raise SystemExit(f"{job_dir} už existuje")
    manifest = {
        "manifestVersion": "0.1.0",
        "jobRef": job_ref,
        "title": title,
        "confidentiality": "confidential",
        "aiProcessingAllowed": False,
        "createdAt": now(),
        "createdBy": by,
        "updatedAt": now(),
        "files": [],
    }
    errors = schema_errors(manifest)
    if errors:
        raise SystemExit("\n".join(errors))
    for folder in FOLDERS:
        (job_dir / folder).mkdir(parents=True)
    save_manifest(job_dir, manifest)
    return job_dir


def cmd_scan(job_dir: Path) -> dict[str, list[str]]:
    manifest = load_manifest(job_dir)
    files = job_files(job_dir)
    listed = {entry["path"]: entry for entry in manifest["files"]}
    report: dict[str, list[str]] = {"added": [], "changed": [], "missing": []}
    for rel, path in files.items():
        digest, size = sha256(path), path.stat().st_size
        entry = listed.get(rel)
        if entry is None:
            manifest["files"].append({
                "path": rel, "category": category_for(rel),
                "sha256": digest, "bytes": size, "sourceClass": None,
            })
            report["added"].append(rel)
        elif entry["sha256"] != digest or entry["bytes"] != size:
            entry["sha256"], entry["bytes"] = digest, size
            report["changed"].append(rel)
    report["missing"] = sorted(set(listed) - set(files))
    manifest["files"].sort(key=lambda entry: entry["path"])
    if report["added"] or report["changed"]:
        manifest["updatedAt"] = now()
        save_manifest(job_dir, manifest)
    return report


def tracked_intake_files(root: Path = ROOT) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--", "intake"], cwd=root, capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    return [line for line in result.stdout.splitlines() if line and line != "intake/README.md"]


def cmd_check(job_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not (job_dir / MANIFEST).is_file():
        return [f"{job_dir.name}: chýba {MANIFEST}"], warnings
    try:
        manifest = load_manifest(job_dir)
    except json.JSONDecodeError as exc:
        return [f"{job_dir.name}: neplatný JSON v {MANIFEST}: {exc}"], warnings
    errors += [f"{job_dir.name}: {message}" for message in schema_errors(manifest)]
    if errors:
        return errors, warnings
    if manifest["jobRef"] != job_dir.name:
        errors.append(f"{job_dir.name}: jobRef {manifest['jobRef']} nezodpovedá názvu priečinka")
    files = job_files(job_dir)
    seen: set[str] = set()
    for entry in manifest["files"]:
        rel = entry["path"]
        if rel in seen:
            errors.append(f"{job_dir.name}: duplicitný záznam {rel}")
            continue
        seen.add(rel)
        path = files.get(rel)
        if path is None:
            errors.append(f"{job_dir.name}: chýba súbor {rel}")
        elif sha256(path) != entry["sha256"] or path.stat().st_size != entry["bytes"]:
            errors.append(f"{job_dir.name}: súbor {rel} sa zmenil (spusti scan)")
        if entry["sourceClass"] is None:
            warnings.append(f"{job_dir.name}: {rel} nemá sourceClass (N/L/P/V)")
    for rel in sorted(set(files) - seen):
        errors.append(f"{job_dir.name}: súbor {rel} nie je v manifeste (spusti scan)")
    return errors, warnings


def job_dirs(paths: list[str]) -> list[Path]:
    if paths:
        return [Path(p).resolve() for p in paths]
    return sorted(p for p in INTAKE.glob("JOB-*") if p.is_dir())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Príjem podkladov reálnej zákazky (ADR-0019).")
    sub = parser.add_subparsers(dest="command", required=True)
    new = sub.add_parser("new", help="vytvorí priečinok zákazky a prázdny manifest")
    new.add_argument("job_ref", help="napr. JOB-2026-0001")
    new.add_argument("--title", required=True)
    new.add_argument("--by", required=True, help="kto zákazku zakladá")
    scan = sub.add_parser("scan", help="doplní nové a zmenené súbory do manifestu")
    scan.add_argument("job_dir")
    check = sub.add_parser("check", help="overí manifesty a súbory")
    check.add_argument("job_dirs", nargs="*")
    args = parser.parse_args(argv)

    if args.command == "new":
        job_dir = cmd_new(args.job_ref, args.title, args.by)
        print(f"Vytvorené: {job_dir.relative_to(ROOT)} (podpriečinky: {', '.join(FOLDERS)})")
        return 0
    if args.command == "scan":
        report = cmd_scan(Path(args.job_dir).resolve())
        labels = (("added", "pridané"), ("changed", "zmenené"), ("missing", "chýbajú"))
        for key, label in labels:
            print(f"{label}: {len(report[key])}")
            for rel in report[key]:
                print(f"  - {rel}")
        return 1 if report["missing"] else 0

    errors: list[str] = []
    warnings: list[str] = []
    dirs = job_dirs(args.job_dirs)
    for job_dir in dirs:
        job_errors, job_warnings = cmd_check(job_dir)
        errors += job_errors
        warnings += job_warnings
    errors += [f"súbor zákazky je v gite (nesmie byť): {rel}" for rel in tracked_intake_files()]
    print(f"Zákazky: {len(dirs)}, chyby: {len(errors)}, upozornenia: {len(warnings)}")
    for message in errors:
        print(f"  CHYBA {message}")
    for message in warnings:
        print(f"  upozornenie {message}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
