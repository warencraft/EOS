"""Stránky Ponuky, Objednávky, Sklad, Dodávatelia, Knowledge base a Gmail (ADR-0025).

Dáta: scripts.prevadzka (JSON v intake/_eos/prevadzka/, mimo gitu). Gmail: scripts.gmail (IMAP,
heslo aplikácie). Žiadne AI: obsah e-mailov sa nikam neposiela.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
from email.utils import parseaddr
from urllib.parse import urlsplit

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from scripts import gmail as G
from scripts import prevadzka as P

from .tailnet_identity import authorized_user

QUOTE_LINES = {"items": [("name", "Položka", "text"), ("qty", "Množstvo", "num"), ("unit", "Jedn.", "short"),
                         ("unitPrice", "Cena/jedn. €", "num"), ("note", "Poznámka", "text")]}
ORDER_LINES = {
    "items": [("name", "Výrobok / diel", "text"), ("qty", "Množstvo", "num"), ("unit", "Jedn.", "short")],
    "materials": [("name", "Materiál / diel", "text"), ("qty", "Množstvo", "num"), ("unit", "Jedn.", "short"),
                  ("status", "Stav", "material_status"), ("supplierId", "Dodávateľ", "supplier"), ("note", "Poznámka", "text")],
    "operations": [("part", "Diel", "text"), ("process", "Proces", "text"), ("machine", "Stroj", "text"),
                   ("minPerPiece", "min/ks", "num"), ("pieces", "ks", "num"), ("done", "Hotové", "check")],
}
LINE_TITLES = {"items": "Položky", "materials": "Materiál a nákup", "operations": "Operácie a stroje"}

RECORDS = {
    "sklad": {"title": "Sklad", "one": "Skladová položka", "prefix": "s", "sort": ("category", "name"),
              "intro": "Polotovary a nakupované diely. Položky pod minimom sú označené.",
              "fields": [("name", "Názov", "text", True), ("category", "Kategória", "text", False), ("qty", "Množstvo", "num", False),
                         ("unit", "Jednotka", "short", False), ("location", "Miesto", "text", False), ("minQty", "Minimum", "num", False),
                         ("note", "Poznámka", "area", False)],
              "cols": ["name", "category", "qty", "unit", "location", "minQty", "note"]},
    "dodavatelia": {"title": "Dodávatelia", "one": "Dodávateľ", "prefix": "d", "sort": ("category", "name"),
                    "intro": "Kde hľadať materiál a nakupované diely. Web s doménou umožní hľadanie cien (ADR-0024).",
                    "fields": [("name", "Názov", "text", True), ("category", "Kategória", "text", True),
                               ("status", "Stav", "supplier_status", True), ("supplies", "Čo dodáva", "text", False),
                               ("location", "Kde", "text", False), ("web", "Web", "text", False),
                               ("searchUrl", "Vyhľadávanie na ich webe ({q} = hľadaný výraz)", "text", False),
                               ("email", "E-mail na dopyty", "text", False), ("note", "Poznámka", "area", False)],
                    "cols": ["name", "category", "supplies", "location", "status"]},
    "kb": {"title": "Knowledge base", "one": "Záznam knowledge base", "prefix": "k", "sort": ("category", "title"),
           "intro": "Sadzby, pravidlá nacenenia, stroje, materiály, firemné údaje. Hodnoty zapisuj so zdrojom N/L/P/V. Nie je to zdroj pravdy EOS (ADR-0025).",
           "fields": [("title", "Názov", "text", True), ("category", "Kategória", "kb_category", True),
                      ("source", "Zdroj (N/L/P/V)", "source", False), ("content", "Obsah", "area", True)],
           "cols": ["title", "category", "source", "content"]},
}
COL_LABELS = {"name": "Názov", "category": "Kategória", "qty": "Množstvo", "unit": "Jedn.", "location": "Miesto", "minQty": "Minimum",
              "note": "Poznámka", "supplies": "Čo dodáva", "status": "Stav", "title": "Názov", "source": "Zdroj", "content": "Obsah"}


def norm(s) -> str:
    return unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()


def num(v):
    s = str(v if v is not None else "").replace(" ", "").replace(" ", "").replace(",", ".")
    if not s:
        return None
    try:
        n = float(s)
    except ValueError:
        raise ValueError(f"„{v}“ nie je číslo")
    if n < 0 or n != n:
        raise ValueError(f"„{v}“ nie je kladné číslo")
    return n


def eur(v) -> str:
    return "–" if v is None else f"{v:,.2f}".replace(",", " ").replace(".", ",") + " €"


def quote_total(q: dict) -> float:
    return sum((i.get("qty") or 0) * (i.get("unitPrice") or 0) for i in q.get("items", []))


def domain_of(web: str) -> str:
    try:
        host = urlsplit(web if "://" in (web or "") else "https://" + (web or "")).hostname or ""
    except ValueError:
        return ""
    host = host.lower()
    host = host[4:] if host.startswith("www.") else host
    return host if re.fullmatch(r"([a-z0-9]([a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}", host) else ""


def read_lines(form, key: str, cols, skip: int | None = None) -> list[dict]:
    """Riadky tabuľky z formulára: <key>-<i>-<pole>. Prázdne riadky a riadok `skip` sa vynechajú."""
    idx = sorted({int(m.group(1)) for k in form.keys() if (m := re.fullmatch(rf"{key}-(\d+)-\w+", k))} - {skip})
    out = []
    for i in idx:
        row = {}
        for name, label, kind in cols:
            raw = form.get(f"{key}-{i}-{name}")
            if kind == "check":
                row[name] = raw is not None
            elif kind == "num":
                try:
                    row[name] = num(raw)
                except ValueError as e:
                    raise ValueError(f"{LINE_TITLES.get(key, key)}, riadok {i + 1}, {label}: {e}")
            else:
                row[name] = str(raw or "").strip()
        keep = [c[0] for c in cols if c[0] in ("name", "part", "process", "machine")]
        if any(row.get(k) for k in keep):
            out.append(row)
    return out


def _skip(akcia: str, key: str) -> int | None:
    m = re.fullmatch(rf"odobrat-{key}-(\d+)", akcia or "")
    return int(m.group(1)) if m else None


def quote_body(q: dict) -> str:
    if q.get("emailBody"):
        return q["emailBody"]
    lines = []
    for n, i in enumerate(q.get("items", []), 1):
        qty = "" if i.get("qty") is None else f"{i['qty']:g}".replace(".", ",")
        price = f" × {eur(i['unitPrice'])} = {eur((i.get('qty') or 0) * i['unitPrice'])}" if i.get("unitPrice") is not None else " – cena bude doplnená"
        lines.append(f"{n}. {i['name']} – {qty} {i.get('unit') or ''}{price}".replace("  ", " ") + (f"\n   {i['note']}" if i.get("note") else ""))
    parts = [f"Dobrý deň,\n\nďakujeme za Váš dopyt. Posielame cenovú ponuku{(' ' + q['number']) if q.get('number') else ''}"
             f"{(' – ' + q['subject']) if q.get('subject') else ''}:\n", *lines, f"\nSpolu bez DPH: {eur(quote_total(q))}"]
    if q.get("dueDate"):
        parts.append(f"Termín dodania: {q['dueDate']}")
    if q.get("notes"):
        parts.append("\n" + q["notes"])
    parts.append("\nS pozdravom\n")
    return "\n".join(parts)


def register(app: FastAPI, sablony, store: P.Prevadzka, gmail_provider, gmail_saver, supplier_proposal) -> None:
    """gmail_provider(request) vráti Gmail alebo None; gmail_saver(email, heslo | None) uloží alebo zmaže údaje."""
    sablony.env.filters["eur2"] = eur
    sablony.env.globals.update(QUOTE_STATUS=P.QUOTE_STATUS, ORDER_STATUS=P.ORDER_STATUS, MATERIAL_STATUS=P.MATERIAL_STATUS,
                               SUPPLIER_STATUS=P.SUPPLIER_STATUS, KB_CATEGORIES=P.KB_CATEGORIES, COL_LABELS=COL_LABELS)

    def get_or_404(kind, id_):
        try:
            return store.get(kind, id_)
        except KeyError:
            raise HTTPException(404, "Záznam neexistuje.") from None

    def suppliers():
        return sorted(store.list("dodavatelia"), key=lambda s: norm(s.get("name")))

    # --- Gmail -------------------------------------------------------------------------
    @app.get("/gmail", response_class=HTMLResponse)
    def gmail_page(request: Request, ok: str = ""):
        g = gmail_provider(request)
        return sablony.TemplateResponse(request, "gmail.html", {"active": "ponuky", "pripojeny": g.address if g else None,
                                                                "ok": ok, "chyba": None})

    @app.post("/gmail")
    def gmail_connect(request: Request, email: str = Form(""), heslo: str = Form(""), akcia: str = Form("pripojit")):
        if "EOS_GMAIL_USERS" in os.environ and not authorized_user(request, "EOS_GMAIL_USERS"):
            raise HTTPException(403, "Nemáš povolenie pripojiť Gmail.")
        if akcia == "odpojit":
            gmail_saver(request, None, None)
            return RedirectResponse("/gmail?ok=odpojeny", status_code=303)
        addr = parseaddr(email)[1].strip()
        chyba = None
        if "@" not in addr or not G.clean_password(heslo):
            chyba = "Vyplň e-mail a heslo aplikácie."
        else:
            try:
                G.Gmail(addr, heslo, getattr(app.state, "imap_factory", None)).test()
            except G.GmailError as e:
                chyba = str(e)
        if chyba:
            return sablony.TemplateResponse(request, "gmail.html", {"active": "ponuky", "pripojeny": None, "ok": "",
                                                                    "chyba": chyba, "email": addr}, status_code=422)
        gmail_saver(request, addr, G.clean_password(heslo))
        return RedirectResponse("/gmail?ok=pripojeny", status_code=303)

    # --- Ponuky ------------------------------------------------------------------------
    @app.get("/ponuky", response_class=HTMLResponse)
    def ponuky(request: Request, q: str = "", hladat: int = 0):
        g = gmail_provider(request)
        vlakna, chyba = None, None
        if g and hladat:
            try:
                vlakna = g.search(q or G.DEFAULT_QUERY)
            except G.GmailError as e:
                chyba = str(e)
        zoznam = sorted(store.list("ponuky"), key=lambda x: x.get("updatedAt", ""), reverse=True)
        podla_vlakna = {x["gmail"]["threadId"]: x["id"] for x in zoznam
                        if g and x.get("gmail", {}).get("threadId") and mailbox_matches(g, x)}
        return sablony.TemplateResponse(request, "ponuky.html", {
            "active": "ponuky", "ponuky": zoznam, "spolu": {x["id"]: quote_total(x) for x in zoznam}, "gmail": g.address if g else None,
            "q": q or G.DEFAULT_QUERY, "vlakna": vlakna, "chyba": chyba, "podla_vlakna": podla_vlakna})

    def mailbox_matches(gmail, quote):
        metadata = quote.get("gmail", {})
        if not metadata.get("threadId") or "EOS_GMAIL_USERS" not in os.environ:
            return True
        return metadata.get("mailbox", "").casefold() == gmail.address.casefold()

    def next_number() -> str:
        ns = [int(m.group(0)) for x in store.list("ponuky") if (m := re.search(r"\d+", x.get("number", "")))]
        return f"CP {max(ns) + 1}" if ns else ""

    @app.post("/ponuky/nova")
    def ponuka_nova():
        q = store.save("ponuky", {"id": P.new_id("cp"), "number": next_number(), "status": "draft", "items": []})
        return RedirectResponse(f"/ponuka/{q['id']}", status_code=303)

    @app.post("/ponuky/z-gmailu")
    def ponuka_z_gmailu(request: Request, vlakno: str = Form(...)):
        g = gmail_provider(request)
        if not g:
            return RedirectResponse("/gmail", status_code=303)
        existing = next((x for x in store.list("ponuky") if x.get("gmail", {}).get("threadId") == vlakno
                         and mailbox_matches(g, x)), None)
        if existing:
            return RedirectResponse(f"/ponuka/{existing['id']}", status_code=303)
        try:
            msgs = g.thread(vlakno)
        except G.GmailError as e:
            raise HTTPException(502, str(e)) from None
        if not msgs:
            raise HTTPException(404, "Vlákno je prázdne alebo neexistuje.")
        first, last = msgs[0], msgs[-1]
        name, addr = parseaddr(first["from"])
        q = store.save("ponuky", {
            "id": P.new_id("cp"), "number": next_number(), "customer": name or addr, "email": addr,
            "subject": first["subject"][:300], "status": "draft", "items": [],
            "gmail": {"threadId": vlakno, "mailbox": g.address, "messageId": last["messageId"][:300], "from": first["from"][:300],
                      "subject": last["subject"][:300]}})
        return RedirectResponse(f"/ponuka/{q['id']}", status_code=303)

    def email_subject(quote):
        original = quote.get("gmail", {}).get("subject")
        subject = original or quote.get("subject") or f"Cenová ponuka {quote.get('number', '')}".strip()
        if quote.get("gmail", {}).get("messageId") and not subject.lower().startswith("re:"):
            return "Re: " + subject
        return subject

    def send_allowed(request):
        return authorized_user(request, "EOS_MAIL_SENDERS")

    def send_snapshot(request, id_):
        sender = send_allowed(request)
        if not sender:
            raise HTTPException(403, "Nemáš povolenie odosielať ponuky.")
        quote = get_or_404("ponuky", id_)
        attempts = store.root / "mail-attempts"
        marker = attempts / f"{id_}.json"
        if marker.exists() or quote["status"] not in {"draft", "gmail_draft"}:
            raise HTTPException(409, "Ponuku nemožno odoslať. Pri predošlom pokuse skontroluj Odoslané v Gmaile.")
        gmail = gmail_provider(request)
        if not gmail:
            raise HTTPException(422, "Gmail nie je pripojený.")
        if not mailbox_matches(gmail, quote):
            raise HTTPException(403, "Pôvodný dopyt patrí do inej schránky.")
        try:
            message = gmail.build_draft(quote.get("email", ""), email_subject(quote), quote_body(quote),
                                        in_reply_to=quote.get("gmail", {}).get("messageId", ""))
        except (G.GmailError, ValueError):
            raise HTTPException(422, "Skontroluj adresu príjemcu a predmet.") from None
        snapshot = json.dumps([sender, quote, str(message["From"]), str(message["To"]),
                               str(message["Subject"]), message.get_content()], sort_keys=True)
        return gmail, message, marker, hashlib.sha256(snapshot.encode()).hexdigest()

    @app.get("/ponuka/{id_}/odoslat", response_class=HTMLResponse)
    def preview_send(request: Request, id_: str):
        _, message, _, fingerprint = send_snapshot(request, id_)
        return sablony.TemplateResponse(request, "odoslat_ponuku.html", {
            "id": id_, "message": message, "fingerprint": fingerprint,
        }, headers={"Cache-Control": "no-store"})

    @app.post("/ponuka/{id_}/odoslat")
    def send_quote(request: Request, id_: str, fingerprint: str = Form(...)):
        gmail, message, marker, current = send_snapshot(request, id_)
        if fingerprint != current:
            raise HTTPException(409, "Ponuka alebo schránka sa zmenila. Otvor nový náhľad.")

        def record_attempt():
            # Po prihlásení do SMTP ešte raz over zhodu s potvrdeným náhľadom.
            _, _, _, latest = send_snapshot(request, id_)
            if fingerprint != latest:
                raise HTTPException(409, "Ponuka sa zmenila. Otvor nový náhľad.")
            marker.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            try:
                with marker.open("x", encoding="utf-8") as file:
                    json.dump({"messageId": str(message["Message-ID"]), "at": P.now(),
                               "sender": send_allowed(request)}, file)
            except FileExistsError:
                raise HTTPException(409, "Odoslanie tejto ponuky už bolo spustené.") from None

        try:
            gmail.send_quote(message, record_attempt)
        except G.GmailRejected:
            marker.unlink(missing_ok=True)
            raise HTTPException(502, "Gmail správu odmietol. Ponuka nebola odoslaná.") from None
        except G.GmailError as error:
            raise HTTPException(502, str(error)) from None

        quote = get_or_404("ponuky", id_)
        if quote["status"] in {"draft", "gmail_draft"}:
            store.save("ponuky", {**quote, "status": "sent"})
        return RedirectResponse(f"/ponuka/{id_}?ok=odoslane", status_code=303)

    def render_quote(request: Request, q: dict, chyba: str | None = None, ok: str = "", status_code: int = 200):
        g = gmail_provider(request)
        vlakno, gm_chyba = None, None
        thr = q.get("gmail", {}).get("threadId")
        if thr and g and not mailbox_matches(g, q):
            gm_chyba = "Pôvodný dopyt nie je priradený k tvojej schránke."
        elif thr and g:
            try:
                vlakno = g.thread(thr)
            except G.GmailError as e:
                gm_chyba = str(e)
        return sablony.TemplateResponse(request, "ponuka.html", {
            "active": "ponuky", "q": q, "lines": QUOTE_LINES, "titles": LINE_TITLES, "spolu": quote_total(q), "vlakno": vlakno,
            "gm_chyba": gm_chyba, "gmail": g.address if g else None,
            "can_send": bool(send_allowed(request)), "chyba": chyba, "ok": ok, "telo": quote_body(q)},
            status_code=status_code)

    @app.get("/ponuka/{id_}", response_class=HTMLResponse)
    def ponuka(request: Request, id_: str, ok: str = ""):
        return render_quote(request, get_or_404("ponuky", id_), ok=ok)

    @app.post("/ponuka/{id_}")
    async def ponuka_uloz(request: Request, id_: str):
        q = get_or_404("ponuky", id_)
        form = await request.form()
        akcia = form.get("akcia", "ulozit")
        if akcia == "zmazat":
            store.delete("ponuky", id_)
            return RedirectResponse("/ponuky", status_code=303)
        new = dict(q)
        try:
            for k in ("number", "customer", "email", "subject", "dueDate", "notes"):
                new[k] = str(form.get(k, q.get(k, "")) or "").strip()
            if "emailBody" in form:
                new["emailBody"] = str(form["emailBody"]).strip()
                if len(new["emailBody"]) > 100000:
                    raise ValueError("Text e-mailu je príliš dlhý.")
            if new["dueDate"] and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", new["dueDate"]):
                raise ValueError("Termín zadaj ako dátum.")
            if form.get("status") in P.QUOTE_STATUS:
                new["status"] = form["status"]
            new["items"] = read_lines(form, "items", QUOTE_LINES["items"], skip=_skip(akcia, "items"))
        except (ValueError, IndexError) as e:
            return render_quote(request, {**q, **{k: v for k, v in new.items() if k != "items"}}, chyba=str(e), status_code=422)
        if akcia == "nahlad-odoslania" and not send_allowed(request):
            raise HTTPException(403, "Nemáš povolenie odosielať ponuky.")
        if akcia == "koncept":
            g = gmail_provider(request)
            if not g:
                return render_quote(request, new, chyba="Gmail nie je pripojený.", status_code=422)
            if not mailbox_matches(g, new):
                return render_quote(request, new, chyba="Pôvodný dopyt patrí do inej schránky.", status_code=403)
            try:
                gm = new.get("gmail", {})
                subj = email_subject(new)
                g.create_draft(new.get("email", ""), subj, quote_body(new), in_reply_to=gm.get("messageId", ""))
            except G.GmailError as e:
                return render_quote(request, new, chyba=str(e), status_code=422)
            new["status"] = "gmail_draft"
            new["gmail"] = {**new.get("gmail", {}), "draftSavedAt": P.now()}
        try:
            saved = store.save("ponuky", new)
        except P.RecordError as e:
            return render_quote(request, new, chyba=f"Ponuka sa neuložila: {e}", status_code=422)
        if akcia == "nahlad-odoslania":
            return RedirectResponse(f"/ponuka/{id_}/odoslat", status_code=303)
        if akcia == "pridat-items":
            return render_quote(request, {**saved, "items": saved["items"] + [{"name": "", "qty": None, "unit": "ks", "unitPrice": None, "note": ""}]})
        if akcia == "objednavka":
            o = store.save("objednavky", {
                "id": P.new_id("obj"), "number": re.sub(r"^CP\s*", "OBJ ", saved.get("number", "")) if saved.get("number") else "",
                "quoteId": saved["id"], "customer": saved.get("customer", ""), "dueDate": saved.get("dueDate", ""), "status": "accepted",
                "items": [{"name": i["name"], "qty": i.get("qty"), "unit": i.get("unit", "")} for i in saved["items"]],
                "materials": [], "operations": [], "notes": saved.get("notes", "")})
            store.save("ponuky", {**saved, "status": "accepted", "orderId": o["id"]})
            return RedirectResponse(f"/objednavka/{o['id']}", status_code=303)
        msg = "koncept" if akcia == "koncept" else "ulozene"
        return RedirectResponse(f"/ponuka/{id_}?ok={msg}", status_code=303)

    # --- Objednávky --------------------------------------------------------------------
    @app.get("/objednavky", response_class=HTMLResponse)
    def objednavky(request: Request):
        zoznam = sorted(store.list("objednavky"), key=lambda o: o.get("dueDate") or "9999")
        return sablony.TemplateResponse(request, "objednavky.html", {"active": "objednavky", "objednavky": zoznam})

    @app.post("/objednavky/nova")
    def objednavka_nova():
        o = store.save("objednavky", {"id": P.new_id("obj"), "status": "accepted", "items": [], "materials": [], "operations": []})
        return RedirectResponse(f"/objednavka/{o['id']}", status_code=303)

    def render_order(request, o, chyba=None, ok="", status_code=200):
        mins = sum((x.get("minPerPiece") or 0) * (x.get("pieces") or 0) for x in o.get("operations", []))
        return sablony.TemplateResponse(request, "objednavka.html", {
            "active": "objednavky", "o": o, "lines": ORDER_LINES, "titles": LINE_TITLES, "dodavatelia": suppliers(),
            "hodiny": mins / 60 if mins else None, "chyba": chyba, "ok": ok}, status_code=status_code)

    @app.get("/objednavka/{id_}", response_class=HTMLResponse)
    def objednavka(request: Request, id_: str, ok: str = ""):
        return render_order(request, get_or_404("objednavky", id_), ok=ok)

    def check_stock(o: dict) -> int:
        stock = store.list("sklad")
        hit = 0
        for m in o["materials"]:
            if not m["name"] or m["status"] in ("ordered", "received"):
                continue
            n = norm(m["name"])
            s = next((x for x in stock if norm(x.get("name")) and (norm(x["name"]) in n or n in norm(x["name"]))), None)
            have = (s or {}).get("qty") or 0
            if s and have > 0 and (m.get("qty") is None or have >= m["qty"]):
                m["status"], hit = "in_stock", hit + 1
                m["note"] = f"sklad: {s['name']}, {have:g} {s.get('unit', '')}{', ' + s['location'] if s.get('location') else ''}".strip()
            else:
                m["status"] = "to_order"
                if s:
                    m["note"] = f"na sklade iba {have:g} {s.get('unit', '')} ({s['name']})"
        return hit

    def price_input(o: dict) -> dict:
        items = [{"id": f"P{n}", "text": m["name"][:300], **({"quantity": m["qty"]} if m.get("qty") else {}),
                  **({"unit": m["unit"][:20]} if m.get("unit") and m.get("qty") else {})}
                 for n, m in enumerate([m for m in o["materials"] if m["status"] == "to_order"][:30], 1)]
        sups = [{"id": P.slug(s["id"])[:60], "name": s["name"][:120], "domain": domain_of(s.get("web", ""))}
                for s in suppliers() if s.get("status") != "not_used" and domain_of(s.get("web", ""))][:20]
        return {"formatVersion": "0.1.0", "items": items, "suppliers": sups}

    @app.post("/objednavka/{id_}")
    async def objednavka_uloz(request: Request, id_: str):
        o = get_or_404("objednavky", id_)
        form = await request.form()
        akcia = form.get("akcia", "ulozit")
        if akcia == "zmazat":
            store.delete("objednavky", id_)
            return RedirectResponse("/objednavky", status_code=303)
        new = dict(o)
        try:
            for k in ("number", "customer", "dueDate", "notes"):
                new[k] = str(form.get(k, o.get(k, "")) or "").strip()
            if new["dueDate"] and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", new["dueDate"]):
                raise ValueError("Termín zadaj ako dátum.")
            if form.get("status") in P.ORDER_STATUS:
                new["status"] = form["status"]
            for key, cols in ORDER_LINES.items():
                new[key] = read_lines(form, key, cols, skip=_skip(akcia, key))
                for row in new[key]:
                    if key == "materials" and row.get("status") not in P.MATERIAL_STATUS:
                        row["status"] = "verify"
        except (ValueError, IndexError) as e:
            return render_order(request, o, chyba=str(e), status_code=422)
        ok = "ulozene"
        if akcia == "sklad":
            ok = f"sklad-{check_stock(new)}"
        try:
            clean = store.save("objednavky", new)
        except P.RecordError as e:
            return render_order(request, new, chyba=f"Objednávka sa neuložila: {e}", status_code=422)
        for key in ORDER_LINES:
            if akcia == f"pridat-{key}":
                blank = {c[0]: (False if c[2] == "check" else None if c[2] == "num" else "verify" if c[0] == "status" else "")
                         for c in ORDER_LINES[key]}
                return render_order(request, {**clean, key: clean[key] + [blank]})
        if akcia == "ceny":
            data = price_input(clean)
            if not data["items"] or not data["suppliers"]:
                return render_order(request, clean, chyba="Na hľadanie cien treba materiál so stavom Objednať a dodávateľa s webom.", status_code=422)
            return Response(json.dumps(data, ensure_ascii=False, indent=2), media_type="application/json",
                            headers={"Content-Disposition": f'attachment; filename="ceny-{id_}.json"'})
        return RedirectResponse(f"/objednavka/{id_}?ok={ok}", status_code=303)

    # --- Sklad, dodávatelia, KB --------------------------------------------------------
    def list_page(kind):
        def page(request: Request, f: str = ""):
            d = RECORDS[kind]
            rows = store.list(kind)
            if f:
                rows = [r for r in rows if norm(f) in norm(" ".join(str(r.get(c, "")) for c in d["cols"]))]
            rows.sort(key=lambda r: tuple(norm(r.get(k)) for k in d["sort"]))
            return sablony.TemplateResponse(request, "zoznam.html", {"active": kind, "kind": kind, "d": d, "rows": rows, "f": f})
        return page

    def edit_page(kind):
        def page(request: Request, id_: str):
            rec = {} if id_ == "novy" else get_or_404(kind, id_)
            session = request.query_params.get("chat", "")
            draft = kind == "dodavatelia" and id_ == "novy" and bool(session)
            if draft:
                rec = supplier_proposal(request, session, request.query_params.get("turn", ""))
            return sablony.TemplateResponse(request, "zaznam.html", {
                "active": kind, "kind": kind, "d": RECORDS[kind], "r": rec, "chyba": None, "chat_draft": draft,
            })
        return page

    def save_page(kind):
        async def page(request: Request, id_: str):
            d = RECORDS[kind]
            form = await request.form()
            if form.get("akcia") == "zmazat" and id_ != "novy":
                store.delete(kind, id_)
                return RedirectResponse(f"/{kind}", status_code=303)
            rec = {} if id_ == "novy" else get_or_404(kind, id_)
            new = dict(rec)
            try:
                for name, label, typ, req in d["fields"]:
                    raw = str(form.get(name, "") or "").strip()
                    if req and not raw:
                        raise ValueError(f"Vyplň: {label}.")
                    if typ == "num":
                        new[name] = num(raw)
                    elif typ == "source":
                        new[name] = raw if raw in ("N", "L", "P", "V") else None
                    else:
                        new[name] = raw
                if kind == "dodavatelia" and new.get("searchUrl") and "{q}" not in new["searchUrl"]:
                    raise ValueError("Odkaz na vyhľadávanie musí obsahovať {q}.")
                if id_ == "novy":
                    base = P.slug(new.get("name") or new.get("title") or "", d["prefix"])
                    new["id"] = base if kind == "dodavatelia" and not any(r["id"] == base for r in store.list(kind)) else P.new_id(d["prefix"])
                store.save(kind, new)
            except (ValueError, P.RecordError) as e:
                return sablony.TemplateResponse(request, "zaznam.html", {"active": kind, "kind": kind, "d": d, "r": new, "chyba": str(e)},
                                                status_code=422)
            return RedirectResponse(f"/{kind}", status_code=303)
        return page

    for kind in RECORDS:
        app.add_api_route(f"/{kind}", list_page(kind), methods=["GET"], response_class=HTMLResponse)
        app.add_api_route(f"/{kind}/{{id_}}", edit_page(kind), methods=["GET"], response_class=HTMLResponse)
        app.add_api_route(f"/{kind}/{{id_}}", save_page(kind), methods=["POST"])
