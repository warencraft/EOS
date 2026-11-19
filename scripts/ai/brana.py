"""Brána: čo smie ísť do Clauda v EOS chate (ADR-0027, plán Claude chatu §5.1).

Čisté funkcie bez siete a bez čítania súborov. Vrátia (áno/nie, dôvod po slovensky); dôvod
uvidí Claude aj človek. Kontrola beží pri každom volaní nástroja.

V tejto etape smú ísť iba znalosti a pracovné katalógy bez údajov zákazníkov. Ponuky,
objednávky, zákazky, kalkulácie a Gmail brána odmietne, kým Marco nerozhodne D1–D3
(docs/handoff/2026-11-18_claude-chat-plan.md §11).
"""

from __future__ import annotations

from pathlib import PurePosixPath

# Súbory repozitára EOS: znalosti, pravidlá a kód. Nie intake/, exports/, outputs/ ani skryté priečinky.
REPO_ROOT_FILES = {"README.md", "ROADMAP.md", "BACKLOG.md", "CHANGELOG.md", "TECH_STACK.md", "AGENTS.md",
                   "CLAUDE.md", "CONTRIBUTING.md", "pyproject.toml"}
REPO_FOLDERS = {"adr", "docs", "schemas", "scripts", "tests", "templates", "data", "calculators", "assets"}
REPO_TEXT_SUFFIXES = {".md", ".json", ".py", ".toml", ".txt", ".html", ".css", ".js", ".yml", ".yaml", ".csv"}
REPO_MAX_BYTES = 400_000

# Knowledge base: kategórie s údajmi zákazníkov a reálnych zákaziek čakajú na Marca (D1, D3).
KB_BLOCKED_CATEGORIES = {"Referenčné zákazky", "Zákazníci"}

# Prevádzkové záznamy, ktoré smú ísť do Clauda bez ďalšieho rozhodnutia.
OPEN_KINDS = {"dodavatelia", "sklad", "kb", "nastenka"}
WAITING_KINDS = {
    "ponuky": "Ponuky obsahujú zákazníkov a ceny. Do Clauda smú až po rozhodnutí Marca (D1, D3).",
    "objednavky": "Objednávky obsahujú zákazníkov. Do Clauda smú až po rozhodnutí Marca (D1, D3).",
    "zakazky": "Zákazky smú ísť do Clauda iba s aiProcessingAllowed: true (ADR-0019) a po rozhodnutí Marca (D1–D3).",
    "kalkulacie": "Kalkulácie patria k zákazkám; čakajú na rozhodnutie Marca (D1, D3).",
    "gmail": "E-maily zákazníkov do Clauda nejdú (ADR-0025 bod 4).",
}


def repo_file(rel: str, size: int | None = None) -> tuple[bool, str]:
    """Smie Claude čítať súbor repozitára EOS s relatívnou cestou `rel`?"""
    p = PurePosixPath(rel.replace("\\", "/"))
    if p.is_absolute() or not p.parts or any(part in ("..", "") for part in p.parts):
        return False, "Cesta musí byť relatívna k repozitáru EOS a bez „..“."
    if any(part.startswith(".") for part in p.parts):
        return False, "Skryté súbory a priečinky do Clauda nejdú."
    if p.parts[0] == "intake":
        return False, "intake/ obsahuje reálne zákazky; do Clauda nejde (ADR-0019)."
    if len(p.parts) == 1:
        if p.name not in REPO_ROOT_FILES:
            return False, "Tento súbor v koreni repozitára nie je medzi povolenými."
    elif p.parts[0] not in REPO_FOLDERS:
        return False, f"Priečinok {p.parts[0]}/ nie je medzi povolenými."
    if p.suffix.lower() not in REPO_TEXT_SUFFIXES:
        return False, "Povolené sú iba textové súbory."
    if size is not None and size > REPO_MAX_BYTES:
        return False, "Súbor je na Clauda príliš veľký."
    return True, ""


def record(kind: str, rec: dict | None = None) -> tuple[bool, str]:
    """Smie Claude čítať prevádzkový záznam druhu `kind` (scripts/prevadzka)?"""
    if kind in WAITING_KINDS:
        return False, WAITING_KINDS[kind]
    if kind not in OPEN_KINDS:
        return False, "Neznámy druh údajov."
    if kind == "kb" and rec is not None and rec.get("category") in KB_BLOCKED_CATEGORIES:
        return False, f"Kategória „{rec.get('category')}“ obsahuje údaje zákaziek; čaká na rozhodnutie Marca (D1, D3)."
    return True, ""
