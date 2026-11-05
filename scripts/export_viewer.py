"""Generate a read-only HTML overview of the EOS repository.

Usage:
    python scripts/export_viewer.py [--root .] [--out exports/viewer/index.html]

Standard library only. The output is an export (EOS-001 §3.8): it is not an
authoritative source of knowledge and must never be edited by hand.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
from pathlib import Path

AREAS = [
    ("common", "Spoločné stavebné prvky", "ID, metadáta, stav a odkazy na zdroje, ktoré používa každý záznam."),
    ("knowledge-core", "Jadro znalostí", "Ako sa zapisuje jedna technická vlastnosť: hodnota, rozsah, podmienky, kvalita merania, pozorovanie."),
    ("catalogs", "Katalógy", "Riadené zoznamy pojmov: jednotky, typy podmienok, vlastnosti a klasifikácie."),
    ("entities", "Entity", "Skutočné veci zo sveta výroby. Každá má stabilné ID a vlastní svoje vlastnosti."),
    ("root", "Dokumenty a zdroje", "Záznamy o dokumentoch, normách a zdrojoch, z ktorých znalosti pochádzajú."),
]

STEP_KINDS = [
    ("close.", "oprava", "corr"),
    ("-close", "uzavretie", "close"),
    ("-prep", "príprava", "prep"),
]

GLOSSARY = [
    ("Schéma", "Pravidlá pre tvar jedného typu záznamu: aké polia musí mať, aké môže mať a v akom formáte."),
    ("Entita", "Samostatná vec s vlastným ID, napríklad materiál MAT-0001 alebo dodávateľ SUP-0001."),
    ("Katalóg", "Riadený zoznam pojmov, na ktoré sa záznamy odkazujú, napríklad jednotky alebo názvy vlastností."),
    ("ADR", "Architecture Decision Record. Zapísané architektonické rozhodnutie a jeho dôvody."),
    ("RFC", "Request for Comments. Väčší návrh, ktorý sa posudzuje pred prijatím."),
    ("CDR", "Contract Design Review. Posudok dátového kontraktu pred implementáciou (pre-design) a po nej (closure)."),
    ("Fixtúra", "Vzorový záznam pre testy. V EOS sú všetky fiktívne, bez reálnych hodnôt."),
    ("N / L / P / V", "Klasifikácia zdroja tvrdenia: norma, literatúra, prax, overené výrobou."),
]


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def inline_md(text: str) -> str:
    out = esc(text)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    return out


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def md_tables_after(text: str, heading: str) -> list[dict[str, str]]:
    """Return rows of the first Markdown table under a heading that starts with `heading`."""
    lines = text.splitlines()
    rows: list[dict[str, str]] = []
    inside = False
    header: list[str] | None = None
    for line in lines:
        if line.startswith("## "):
            if inside and header:
                break
            inside = line[3:].startswith(heading)
            continue
        if not inside or not line.startswith("|"):
            if inside and header and rows:
                break
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = cells
        elif set("".join(cells)) <= set("-: "):
            continue
        else:
            rows.append(dict(zip(header, cells)))
    return rows


def top_section(text: str) -> tuple[str, str]:
    """First `## ` heading and its first paragraph."""
    match = re.search(r"^## (.+)$", text, re.M)
    if not match:
        return "", ""
    rest = text[match.end():].strip().split("\n\n")
    return match.group(1).strip(), rest[0].strip() if rest else ""


# ---------- schemas ----------

def ref_target(ref: str) -> tuple[str, str]:
    """Return (schema file stem, fragment tail) for an $ref."""
    url, _, frag = ref.partition("#")
    stem = url.rsplit("/", 1)[-1].replace(".schema.json", "")
    tail = frag.rsplit("/", 1)[-1] if frag else ""
    return stem, tail


TRANSLATIONS: dict = {}
BASIC_TYPES = {"string": "text", "number": "číslo", "integer": "celé číslo", "boolean": "áno/nie",
               "object": "objekt", "array": "zoznam"}


def load_translations(path: Path | None) -> dict:
    if path is None or not path.is_file():
        return {}
    try:
        data = json.loads(read(path))
    except json.JSONDecodeError:
        return {}
    return {k: v for k, v in data.items() if not k.startswith("_") and isinstance(v, dict)}


def label(stem: str) -> str:
    """Human label for a schema stem (translated title when available)."""
    return TRANSLATIONS.get(stem, {}).get("title", stem)


def describe_type(spec: dict) -> str:
    if "$ref" in spec:
        stem, tail = ref_target(spec["$ref"])
        if stem == "identifiers":
            return f"ID {tail}"
        if not stem:
            return tail
        return label(stem) if not tail or stem == "metadata" else f"{label(stem)} ({tail})"
    if spec.get("type") == "array":
        return f"zoznam {describe_type(spec.get('items', {}))}"
    if "enum" in spec:
        return " | ".join(str(v) for v in spec["enum"][:6])
    if "const" in spec:
        return f"= {spec['const']}"
    for key in ("oneOf", "anyOf"):
        if key in spec:
            return " alebo ".join(describe_type(s) for s in spec[key][:3])
    t = spec.get("type", "object")
    if isinstance(t, list):
        return " | ".join(BASIC_TYPES.get(x, str(x)) for x in t)
    return BASIC_TYPES.get(t, str(t))


def collect_refs(node: object, found: set[str]) -> None:
    if isinstance(node, dict):
        if isinstance(node.get("$ref"), str) and not node["$ref"].startswith("#"):
            found.add(ref_target(node["$ref"])[0])
        for value in node.values():
            collect_refs(value, found)
    elif isinstance(node, list):
        for value in node:
            collect_refs(value, found)


def load_schemas(root: Path) -> list[dict]:
    schemas = []
    for path in sorted((root / "schemas").rglob("*.schema.json")):
        try:
            data = json.loads(read(path))
        except json.JSONDecodeError:
            continue
        area = path.parent.name if path.parent.name != "schemas" else "root"
        stem = path.name.replace(".schema.json", "")
        required = set(data.get("required", []))
        fields, common = [], []
        for name, spec in (data.get("properties") or {}).items():
            spec = spec if isinstance(spec, dict) else {}
            is_meta = ref_target(spec.get("$ref", ""))[0] == "metadata"
            tr = TRANSLATIONS.get(stem, {})
            item = {
                "name": name,
                "type": describe_type(spec),
                "required": name in required,
                "desc": tr.get("fields", {}).get(name) or spec.get("description", ""),
            }
            (common if is_meta else fields).append(item)
        refs: set[str] = set()
        collect_refs(data, refs)
        refs.discard(stem)
        schemas.append({
            "stem": stem,
            "area": area,
            "path": path.relative_to(root).as_posix(),
            "title": TRANSLATIONS.get(stem, {}).get("title") or data.get("title", stem).replace("EOS ", ""),
            "orig": data.get("title", stem).replace("EOS ", ""),
            "desc": TRANSLATIONS.get(stem, {}).get("desc") or data.get("description", ""),
            "fields": fields,
            "common": common,
            "defs": sorted((data.get("$defs") or {}).keys()),
            "refs": sorted(refs),
        })
    used_by: dict[str, list[str]] = {}
    for s in schemas:
        for r in s["refs"]:
            used_by.setdefault(r, []).append(s["stem"])
    for s in schemas:
        s["used_by"] = sorted(used_by.get(s["stem"], []))
    return schemas


# ---------- history ----------

def phase_of(version: str) -> str:
    m = re.match(r"(\d+\.\d+[A-Z]?(?:\.\d+)?)", version)
    if not m:
        return version
    v = m.group(1)
    # 0.2B.1.3 -> 0.2B.1, 0.2C.2 -> 0.2C, 0.2A.1 -> 0.2A, 0.1.1 -> 0.1
    parts = v.split(".")
    if len(parts) >= 3 and parts[1][-1:].isalpha() and parts[1].startswith("2B"):
        return ".".join(parts[:3])
    return ".".join(parts[:2])


def load_history(root: Path) -> list[dict]:
    text = read(root / "CHANGELOG.md")
    entries = []
    for m in re.finditer(r"^## (.+?) - (\d{4}-\d{2}-\d{2})\s*$", text, re.M):
        version, date = m.group(1).strip(), m.group(2)
        body = text[m.end(): m.end() + 600]
        status = re.search(r"^Status:\s*(.+)$", body, re.M)
        kind, kind_cls = "implementácia", "impl"
        for marker, label, cls in STEP_KINDS:
            if marker in version:
                kind, kind_cls = label, cls
                break
        if not re.match(r"\d", version):
            kind, kind_cls = "údržba", "maint"
        entries.append({
            "version": version,
            "date": date,
            "status": status.group(1).strip() if status else "",
            "kind": kind,
            "cls": kind_cls,
            "phase": phase_of(version) if re.match(r"\d", version) else "údržba",
        })
    return list(reversed(entries))


PHASE_NAMES = {
    "0.1": "Základy a pravidlá",
    "0.2A": "Prvé dátové kontrakty a validátor",
    "0.2B.0": "Príprava znalostnej vrstvy",
    "0.2B.1": "Jadro znalostí",
    "0.2B.2": "Katalógy",
    "0.2C": "Entity",
    "údržba": "Údržba",
}


# ---------- render ----------

def render_schema(s: dict) -> str:
    rows = "".join(
        f'<li><div class="fl"><code class="f-name{" req" if f["required"] else ""}">{esc(f["name"])}</code>'
        f'<span class="f-type">{esc(f["type"])}</span></div>'
        + (f'<p class="f-desc">{esc(f["desc"])}</p>' if f["desc"] else "") + "</li>"
        for f in s["fields"]
    )
    common = ""
    if s["common"]:
        names = ", ".join(c["name"] for c in s["common"])
        common = (f'<p class="common"><span class="tag">+ {len(s["common"])} spoločných metadát</span> '
                  f'<span class="muted small">{esc(names)}</span></p>')
    table = f'<ul class="fields">{rows}</ul>' if rows else ""
    defs = ""
    if s["defs"] and not s["fields"]:
        defs = '<p class="chips">' + "".join(f'<span class="chip">{esc(d)}</span>' for d in s["defs"][:40]) + "</p>"
    links = ""
    if s["refs"]:
        links += '<p class="rel"><span class="lbl">Používa</span>' + "".join(
            f'<a class="chip" href="#s-{esc(r)}">{esc(label(r))}</a>' for r in s["refs"]) + "</p>"
    if s["used_by"]:
        links += '<p class="rel"><span class="lbl">Používajú ho</span>' + "".join(
            f'<a class="chip" href="#s-{esc(r)}">{esc(label(r))}</a>' for r in s["used_by"]) + "</p>"
    n_req = sum(1 for f in s["fields"] if f["required"])
    meta = f'{len(s["fields"])} polí' + (f', {n_req} povinných' if n_req else "") if s["fields"] else (
        f'{len(s["defs"])} definícií' if s["defs"] else "")
    search = " ".join([s["stem"], s["title"], s["orig"], s["desc"]] + [f["name"] for f in s["fields"]]).lower()
    return (
        f'<details class="schema" id="s-{esc(s["stem"])}" data-search="{esc(search)}">'
        f'<summary><span class="s-title">{esc(s["title"])}'
        + (f' <span class="s-orig">{esc(s["orig"])}</span>' if s["orig"] != s["title"] else "")
        + '</span>'
        f'<span class="s-meta">{esc(meta)}</span></summary>'
        f'<div class="s-body"><p class="s-desc">{esc(s["desc"])}</p>{common}{table}{defs}{links}'
        f'<p class="path"><code>{esc(s["path"])}</code></p></div></details>'
    )


def render(root: Path) -> str:
    schemas = load_schemas(root)
    history = load_history(root)
    index = read(root / "docs" / "INDEX.md")
    adrs = md_tables_after(index, "ADR")
    cdrs = md_tables_after(index, "Kontraktové")
    rfcs = md_tables_after(index, "RFC")
    roadmap_head, roadmap_body = top_section(read(root / "ROADMAP.md"))
    backlog_head, backlog_body = top_section(read(root / "BACKLOG.md"))
    tests = re.search(r"(\d+) testov", read(root / "tests" / "README.md"))
    tests_n = tests.group(1) if tests else "?"
    entities = [s for s in schemas if s["area"] == "entities"]
    first = history[0]["date"] if history else ""
    last = history[-1]["date"] if history else ""
    days = ""
    if first and last:
        days = (dt.date.fromisoformat(last) - dt.date.fromisoformat(first)).days
    next_entity = re.search(r"Phase [\d.A-Z]+ - (\w+) Entity", backlog_head)
    generated = dt.date.today().isoformat()

    # --- title block
    title_block = f"""
<header class="sheet-head">
  <div class="tb-name"><span class="eyebrow">Engineering Operating System</span><h1>EOS</h1>
    <p class="lede">Interný inžiniersky znalostný systém pre strojársku prax, výrobnú technológiu a prípravu cenových ponúk.</p>
    <p class="motto">Kód počíta. Databáza nesie znalosti. Dokumentácia vysvetľuje.</p></div>
  <dl class="tb-grid">
    <div><dt>Aktuálny míľnik</dt><dd>{inline_md(roadmap_head.replace("Míľnik ", ""))}</dd></div>
    <div><dt>Ďalší krok</dt><dd>{inline_md(backlog_head.replace("Nasledujúce: ", ""))}</dd></div>
    <div><dt>Schémy</dt><dd class="num">{len(schemas)}</dd></div>
    <div><dt>Entity</dt><dd class="num">{len(entities)}</dd></div>
    <div><dt>Testy</dt><dd class="num">{esc(tests_n)}</dd></div>
    <div><dt>Rozhodnutia ADR</dt><dd class="num">{len(adrs)}</dd></div>
    <div><dt>Vývoj</dt><dd>{esc(first)} → {esc(last)}{f" · {days} dní" if days != "" else ""}</dd></div>
    <div><dt>Reálne dáta</dt><dd>zatiaľ žiadne (fáza architektúry)</dd></div>
  </dl>
</header>"""

    # --- layers
    cols = []
    for key, name, desc in AREAS:
        items = [s for s in schemas if s["area"] == key]
        if not items:
            continue
        cards = "".join(render_schema(s) for s in items)
        if key == "entities" and next_entity:
            cards += (f'<div class="schema ghost"><span class="s-title">{esc(label(next_entity.group(1).lower()))}</span>'
                      f'<span class="s-meta">navrhnutá, čaká na implementáciu</span></div>')
        cols.append(f'<section class="layer layer-{esc(key)}"><h3>{esc(name)}</h3>'
                    f'<p class="muted small">{esc(desc)}</p><div class="cards">{cards}</div></section>')
    layers = "".join(cols)

    # --- history
    phases: dict[str, list[dict]] = {}
    for e in history:
        phases.setdefault(e["phase"], []).append(e)
    hist_html = ""
    for ph, items in phases.items():
        steps = "".join(
            f'<li class="step {e["cls"]}" title="{esc(e["status"])}"><span class="v">{esc(e["version"])}</span>'
            f'<span class="k">{esc(e["kind"])}</span><span class="d">{esc(e["date"][5:].replace("-", "."))}</span></li>'
            for e in items)
        hist_html += (f'<div class="phase"><div class="ph-head"><span class="ph-id">{esc(ph)}</span>'
                      f'<span class="ph-name">{esc(PHASE_NAMES.get(ph, ""))}</span></div><ol class="steps">{steps}</ol></div>')

    def table(rows: list[dict[str, str]], cols: list[str]) -> str:
        if not rows:
            return '<p class="muted">Nenašiel sa index v docs/INDEX.md.</p>'
        head = "".join(f"<th>{esc(c)}</th>" for c in cols)
        body = "".join("<tr>" + "".join(f"<td>{inline_md(r.get(c, ''))}</td>" for c in cols) + "</tr>" for r in rows)
        return f'<div class="tbl"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'

    glossary = "".join(f"<div><dt>{esc(t)}</dt><dd>{esc(d)}</dd></div>" for t, d in GLOSSARY)

    return TEMPLATE.format(
        title_block=title_block,
        roadmap_body=inline_md(roadmap_body),
        backlog_body=inline_md(backlog_body),
        layers=layers,
        history=hist_html,
        adr=table(adrs, ["ID", "Stav", "Rozhodnutie"]),
        cdr=table(cdrs, ["ID", "Téma", "Typ / fáza", "KB", "Výsledok"]),
        rfc=table(rfcs, ["ID", "Stav", "KB", "Obsah"]),
        glossary=glossary,
        generated=esc(generated),
        n_hist=len(history),
    )


TEMPLATE = """<title>EOS Prehľad projektu</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: technický výkres — rohové razítko hore, potom vrstvy schém v stĺpcoch, časová os, registre. */
:root {{
  --paper: #f3f5f6; --sheet: #fbfcfc; --ink: #17222b; --ink-2: #4b5a66; --line: #c9d2d8; --line-2: #e1e7ea;
  --accent: #d0560f; --accent-soft: #fbe6d8; --blue: #24557a; --blue-soft: #e1ebf3; --ok: #2f7a4a; --warn: #9a6a00;
  --display: "Barlow Condensed", "Arial Narrow", Arial, sans-serif;
  --body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --paper: #11171c; --sheet: #172028; --ink: #e4eaee; --ink-2: #9fb0bc; --line: #33424e; --line-2: #24303a;
  --accent: #f07a35; --accent-soft: #3a2416; --blue: #8fbbe0; --blue-soft: #1d2d3b; --ok: #6cc28c; --warn: #e0b04a; color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --paper: #11171c; --sheet: #172028; --ink: #e4eaee; --ink-2: #9fb0bc; --line: #33424e; --line-2: #24303a;
  --accent: #f07a35; --accent-soft: #3a2416; --blue: #8fbbe0; --blue-soft: #1d2d3b; --ok: #6cc28c; --warn: #e0b04a; color-scheme: dark; }}
* {{ box-sizing: border-box; }}
body {{ background: var(--paper); color: var(--ink); font: 15px/1.55 var(--body); margin: 0;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 24px 48px; }}
.wrap {{ max-width: 1240px; margin: 0 auto; display: grid; grid-template-columns: minmax(0, 1fr); gap: 40px; }}
h1, h2, h3 {{ font-family: var(--display); font-weight: 600; letter-spacing: .01em; text-wrap: balance; margin: 0; }}
h2 {{ font-size: 1.9rem; }} h3 {{ font-size: 1.3rem; }}
code {{ font-family: var(--mono); font-size: .86em; background: var(--line-2); padding: 0 .3em; border-radius: 3px; }}
a {{ color: var(--blue); }}
.muted {{ color: var(--ink-2); }} .small {{ font-size: .86rem; }}
.eyebrow, dt, .lbl, th {{ font-family: var(--display); text-transform: uppercase; letter-spacing: .08em; font-size: .8rem; color: var(--ink-2); font-weight: 600; }}
.sheet-head {{ background: var(--sheet); border: 2px solid var(--ink); display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr); }}
.tb-name {{ padding: 22px 24px; border-right: 2px solid var(--ink); display: grid; gap: 8px; align-content: start; }}
.tb-name h1 {{ font-size: 4.2rem; line-height: .9; font-weight: 700; }}
.lede {{ margin: 0; max-width: 46ch; }}
.motto {{ margin: 6px 0 0; font-family: var(--mono); font-size: .82rem; color: var(--accent); }}
.tb-grid {{ margin: 0; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); }}
.tb-grid > div {{ padding: 10px 14px; border-left: 1px solid var(--line); border-bottom: 1px solid var(--line); min-width: 0; }}
.tb-grid > div:nth-child(4n+1) {{ border-left: 0; }}
.tb-grid > div:nth-child(1), .tb-grid > div:nth-child(2) {{ grid-column: span 2; }}
.tb-grid > div:nth-child(3) {{ border-left: 0; }}
.tb-grid > div:nth-child(7) {{ border-left: 0; grid-column: span 2; }}
.tb-grid > div:nth-child(8) {{ grid-column: span 2; border-bottom: 0; }}
.tb-grid > div:nth-child(7) {{ border-bottom: 0; }}
dd {{ margin: 2px 0 0; overflow-wrap: anywhere; }}
dd.num {{ font-family: var(--display); font-size: 2.2rem; line-height: 1; font-weight: 600; font-variant-numeric: tabular-nums; }}
.now {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
.note {{ background: var(--sheet); border: 1px solid var(--line); padding: 16px 18px; min-width: 0; }}
.note.next {{ border-left: 4px solid var(--accent); }}
.note p {{ margin: 6px 0 0; max-width: 75ch; }}
.sec-head {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: end; gap: 12px; margin-bottom: 14px; border-bottom: 2px solid var(--ink); padding-bottom: 8px; }}
.sec-head p {{ margin: 0; max-width: 70ch; }}
#q {{ font: inherit; padding: 7px 10px; border: 1px solid var(--line); background: var(--sheet); color: var(--ink); width: min(100%, 280px); }}
#q:focus-visible, summary:focus-visible, a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
.layers {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; align-items: start; }}
.layer-root {{ grid-column: 1 / -1; }}
.layer-root .cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 8px; align-items: start; }}
.layer {{ display: grid; gap: 6px; min-width: 0; }}
.layer h3 {{ display: flex; gap: 8px; align-items: baseline; }}
.layer p {{ margin: 0 0 6px; }}
.cards {{ display: grid; gap: 8px; }}
.schema {{ background: var(--sheet); border: 1px solid var(--line); min-width: 0; }}
.layer-entities .schema:not(.ghost) {{ border-color: var(--blue); }}
.schema summary {{ cursor: pointer; padding: 10px 12px; display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px; align-items: baseline; list-style: none; }}
.schema summary::-webkit-details-marker {{ display: none; }}
.schema summary::before {{ content: "+"; font-family: var(--mono); color: var(--accent); margin-right: 2px; }}
.schema[open] summary::before {{ content: "−"; }}
.schema[open] {{ grid-column: 1 / -1; }}
.s-orig {{ display: block; font-family: var(--mono); font-weight: 400; font-size: .72rem; color: var(--ink-2); }}
.s-title {{ font-weight: 600; flex: 1 1 0; min-width: 0; overflow-wrap: anywhere; }}
.s-meta {{ font-family: var(--mono); font-size: .74rem; color: var(--ink-2); }}
.ghost {{ border-style: dashed; padding: 10px 12px; display: flex; flex-wrap: wrap; gap: 6px; justify-content: space-between; color: var(--ink-2); }}
.ghost .s-meta {{ color: var(--accent); white-space: normal; }}
.s-body {{ padding: 0 12px 12px; display: grid; gap: 8px; }}
.s-body p {{ margin: 0; }}
.s-desc {{ color: var(--ink-2); font-size: .9rem; }}
.tbl {{ overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; font-size: .86rem; }}
th, td {{ text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--line-2); vertical-align: top; }}
th {{ border-bottom: 1px solid var(--line); }}
.fields {{ list-style: none; margin: 0; padding: 0; display: grid; }}
.fields li {{ border-top: 1px solid var(--line-2); padding: 6px 0; display: grid; gap: 2px; min-width: 0; }}
.fl {{ display: flex; flex-wrap: wrap; gap: 4px 10px; align-items: baseline; }}
.f-name {{ background: none; padding: 0; font-weight: 500; overflow-wrap: anywhere; }}
.f-name.req::after {{ content: " *"; color: var(--accent); }}
.f-type {{ font-family: var(--mono); color: var(--blue); font-size: .76rem; overflow-wrap: anywhere; }}
.f-desc {{ color: var(--ink-2); font-size: .84rem; }}
.chips, .rel {{ display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }}
.lbl {{ margin-right: 4px; }}
.chip, .tag {{ font-family: var(--mono); font-size: .74rem; padding: 1px 6px; border: 1px solid var(--line); background: var(--paper); text-decoration: none; color: var(--ink); }}
.tag {{ background: var(--blue-soft); border-color: transparent; color: var(--blue); }}
a.chip:hover {{ border-color: var(--accent); }}
.path {{ font-size: .78rem; color: var(--ink-2); }}
.cycle {{ display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin: 0 0 16px; font-size: .9rem; }}
.cycle .step {{ list-style: none; }}
.arrow {{ color: var(--ink-2); font-family: var(--mono); }}
.timeline {{ display: grid; gap: 10px; }}
.phase {{ display: grid; grid-template-columns: 210px minmax(0, 1fr); gap: 12px; align-items: start; border-top: 1px solid var(--line); padding-top: 10px; }}
.ph-head {{ display: grid; }}
.ph-id {{ font-family: var(--mono); font-weight: 500; }}
.ph-name {{ font-family: var(--display); font-size: 1.1rem; font-weight: 600; }}
.steps {{ margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 6px; }}
.step {{ list-style: none; display: grid; padding: 5px 9px; border: 1px solid var(--line); border-top-width: 3px; background: var(--sheet); min-width: 92px; }}
.step .v {{ font-family: var(--mono); font-size: .8rem; font-weight: 500; }}
.step .k {{ font-size: .74rem; color: var(--ink-2); }}
.step .d {{ font-family: var(--mono); font-size: .7rem; color: var(--ink-2); font-variant-numeric: tabular-nums; }}
.step.prep {{ border-top-color: var(--blue); }}
.step.impl {{ border-top-color: var(--ink); }}
.step.close {{ border-top-color: var(--ok); }}
.step.corr {{ border-top-color: var(--warn); }}
.step.maint {{ border-top-color: var(--line); }}
.registers {{ display: grid; grid-template-columns: minmax(0, 1fr); gap: 28px; }}
.glossary {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px 24px; margin: 0; }}
.glossary dd {{ color: var(--ink-2); font-size: .9rem; }}
footer {{ border-top: 2px solid var(--ink); padding-top: 10px; font-size: .82rem; color: var(--ink-2); display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px; }}
@media (max-width: 980px) {{
  .sheet-head {{ grid-template-columns: minmax(0, 1fr); }} .tb-name {{ border-right: 0; border-bottom: 2px solid var(--ink); }}
  .layers {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
}}
@media (max-width: 620px) {{
  .layers, .now {{ grid-template-columns: 1fr; }}
  .tb-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .tb-grid > div {{ grid-column: span 1 !important; border-left: 0 !important; border-bottom: 1px solid var(--line) !important; }}
  .tb-grid > div:nth-child(1), .tb-grid > div:nth-child(2), .tb-grid > div:nth-child(7), .tb-grid > div:nth-child(8) {{ grid-column: 1 / -1 !important; }}
  .tb-name h1 {{ font-size: 3.2rem; }}
  .phase {{ grid-template-columns: 1fr; }}
}}
@media (prefers-reduced-motion: no-preference) {{ .schema summary, a.chip {{ transition: border-color .15s; }} }}
</style>
<div class="wrap">
{title_block}

<section class="now" aria-label="Aktuálny stav">
  <div class="note"><span class="eyebrow">Kde sme</span><p>{roadmap_body}</p></div>
  <div class="note next"><span class="eyebrow">Čo nasleduje</span><p>{backlog_body}</p></div>
</section>

<section aria-labelledby="h-model">
  <div class="sec-head"><div><h2 id="h-model">Stavebnica znalostí</h2>
    <p class="muted">Každá karta je jedna schéma, teda pravidlá pre jeden typ záznamu. Čítaj zľava doprava: zo spoločných prvkov sa skladá jadro znalostí, na ne sa odkazujú katalógy a z toho všetkého sa skladajú entity. Povinné polia majú hviezdičku.</p></div>
    <input id="q" type="search" placeholder="Hľadaj pole alebo schému…" aria-label="Hľadaj pole alebo schému"></div>
  <div class="layers">{layers}</div>
</section>

<section aria-labelledby="h-hist">
  <div class="sec-head"><div><h2 id="h-hist">Ako projekt vznikal</h2>
    <p class="muted">{n_hist} zápisov z CHANGELOG. Každá časť prešla rovnakým cyklom:</p></div></div>
  <ul class="cycle"><li class="step prep"><span class="k">príprava</span><span class="v">pre-design CDR</span></li><span class="arrow">→</span>
    <li class="step impl"><span class="k">implementácia</span><span class="v">schéma + testy</span></li><span class="arrow">→</span>
    <li class="step close"><span class="k">uzavretie</span><span class="v">closure CDR</span></li><span class="arrow">→</span>
    <li class="step corr"><span class="k">oprava</span><span class="v">nálezy z uzavretia</span></li></ul>
  <div class="timeline">{history}</div>
</section>

<section class="registers" aria-labelledby="h-reg">
  <div class="sec-head"><div><h2 id="h-reg">Rozhodnutia a posudky</h2>
    <p class="muted">Prevzaté z <code>docs/INDEX.md</code>.</p></div></div>
  <div><h3>Architektonické rozhodnutia (ADR)</h3>{adr}</div>
  <div><h3>Posudky kontraktov (CDR)</h3>{cdr}</div>
  <div><h3>Návrhy architektúry (RFC)</h3>{rfc}</div>
</section>

<section aria-labelledby="h-gl">
  <div class="sec-head"><h2 id="h-gl">Slovníček</h2></div>
  <dl class="glossary">{glossary}</dl>
</section>

<footer><span>Vygenerované {generated} skriptom <code>export_viewer.py</code> z repozitára EOS.</span>
<span>Export iba na čítanie, nie autoritatívny zdroj (EOS-001 §3.8).</span></footer>
</div>
<script>
(function () {{
  var q = document.getElementById('q');
  var cards = Array.prototype.slice.call(document.querySelectorAll('.schema[data-search]'));
  q.addEventListener('input', function () {{
    var t = q.value.trim().toLowerCase();
    cards.forEach(function (c) {{ c.hidden = t !== '' && c.getAttribute('data-search').indexOf(t) === -1; }});
  }});
  function openHash() {{
    var el = location.hash && document.getElementById(location.hash.slice(1));
    if (el && el.tagName === 'DETAILS') {{ el.open = true; el.scrollIntoView({{block: 'start'}}); }}
  }}
  window.addEventListener('hashchange', openHash); openHash();
}})();
</script>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a read-only HTML overview of EOS.")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, default=Path("exports/viewer/index.html"))
    parser.add_argument("--fragment", action="store_true", help="omit the <html>/<head> wrapper")
    parser.add_argument("--translations", type=Path, default=Path(__file__).with_name("viewer_sk.json"),
                        help="JSON with Slovak schema labels; missing entries fall back to the schema text")
    args = parser.parse_args()
    TRANSLATIONS.update(load_translations(args.translations))
    page = render(args.root.resolve())
    if not args.fragment:
        page = ('<!doctype html>\n<html lang="sk">\n<head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head>\n<body>\n'
                + page + "\n</body>\n</html>\n")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page, encoding="utf-8")
    print(f"OK {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
