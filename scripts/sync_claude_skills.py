"""Copy EOS skills from .agents/skills/ to .claude/skills/ so Claude Code finds them.

Usage:
    python scripts/sync_claude_skills.py           # update the copy
    python scripts/sync_claude_skills.py --check   # exit 1 if the copy is out of date

.agents/skills/ is the source (shared by Codex and Claude). .claude/skills/ is a
generated copy, because Claude Code only discovers skills there and a symlink does
not work reliably on Windows. Never edit the copy by hand. Standard library only.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(".agents/skills")
TARGET = Path(".claude/skills")
README = "README.md"
README_TEXT = """# Kópia skillov pre Claude Code

Tento priečinok je **generovaný**. Neupravuj ho ručne.

Zdroj skillov je `.agents/skills/` (spoločný pre Codex aj Claude). Claude Code hľadá skilly iba tu,
preto sa kopírujú. Po zmene skillu v `.agents/skills/` spusti:

```bash
python scripts/sync_claude_skills.py
```

Test `tests/test_claude_skills.py` zlyhá, keď sa kópia rozíde so zdrojom.
"""


def _text(path: Path) -> bytes:
    """File content with Windows line endings normalized, so a checkout with autocrlf matches."""
    return path.read_bytes().replace(b"\r\n", b"\n")


def expected(root: Path) -> dict[str, bytes]:
    """Relative path in the target -> content it must have."""
    files = {README: README_TEXT.encode("utf-8")}
    source = root / SOURCE
    for path in sorted(source.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            files[path.relative_to(source).as_posix()] = _text(path)
    return files


def differences(root: Path = ROOT) -> list[str]:
    """Human-readable list of files that are missing, different or extra in the copy."""
    target = root / TARGET
    want = expected(root)
    have = {p.relative_to(target).as_posix(): p for p in target.rglob("*") if p.is_file()} if target.exists() else {}
    problems = [f"chýba: {name}" for name in sorted(want) if name not in have]
    problems += [f"líši sa: {name}" for name in sorted(want) if name in have and _text(have[name]) != want[name]]
    problems += [f"navyše: {name}" for name in sorted(have) if name not in want]
    return problems


def sync(root: Path = ROOT) -> None:
    target = root / TARGET
    if target.exists():
        shutil.rmtree(target)
    for name, content in expected(root).items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="iba over, nič nemeň")
    args = parser.parse_args(argv)
    if args.check:
        problems = differences()
        for problem in problems:
            print(problem)
        if problems:
            print("Kópia v .claude/skills/ nie je aktuálna. Spusti: python scripts/sync_claude_skills.py")
            return 1
        print("OK")
        return 0
    sync()
    print(f"Skilly skopírované do {TARGET.as_posix()}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
