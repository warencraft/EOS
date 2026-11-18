"""Gmail cez IMAP s heslom aplikácie (ADR-0025). Iba štandardná knižnica.

Vie: overiť prihlásenie, nájsť vlákna podľa Gmail vyhľadávania, prečítať vlákno a uložiť
koncept odpovede do Konceptov. E-maily neodosiela.

Prihlasovacie údaje sú v ~/.config/eos/gmail.json (práva 0600) alebo v súbore z premennej
EOS_GMAIL_CONFIG, nikdy v repozitári ani v intake/.
"""

from __future__ import annotations

import email
import email.policy
import html
import imaplib
import json
import os
import re
import socket
import time
from email.message import EmailMessage
from email.utils import formatdate, make_msgid, parseaddr, parsedate_to_datetime
from pathlib import Path

HOST = "imap.gmail.com"
PORT = 993
TIMEOUT_S = 30
DEFAULT_QUERY = 'in:inbox newer_than:30d (dopyt OR "cenova ponuka" OR "cenovu ponuku" OR RFQ OR Anfrage)'
_FETCH_RE = re.compile(rb"X-GM-THRID (\d+)|X-GM-MSGID (\d+)|UID (\d+)")
_LIST_RE = re.compile(rb'^\((?P<flags>[^)]*)\) (?:"[^"]*"|NIL) (?P<name>"(?:[^"\\]|\\.)*"|\S+)$')


class GmailError(RuntimeError):
    """Zrozumiteľná chyba pre používateľa (bez hesla v texte)."""


def config_path() -> Path:
    return Path(os.environ.get("EOS_GMAIL_CONFIG") or Path.home() / ".config" / "eos" / "gmail.json")


def load_config(path: Path | None = None) -> dict | None:
    p = path or config_path()
    try:
        c = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return c if c.get("email") and c.get("appPassword") else None


def save_config(address: str, app_password: str, path: Path | None = None) -> Path:
    p = path or config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(p.parent, 0o700)
    except OSError:
        pass
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({"email": address, "appPassword": app_password}, f)
    os.chmod(p, 0o600)
    return p


def delete_config(path: Path | None = None) -> None:
    p = path or config_path()
    if p.exists():
        p.unlink()


def clean_password(pw: str) -> str:
    """Google zobrazuje heslo aplikácie po štvoriciach s medzerami."""
    return re.sub(r"\s+", "", pw or "")


def _quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _header(msg, name: str) -> str:
    v = msg.get(name)
    return str(v).strip() if v is not None else ""


def _text_body(msg) -> str:
    part = msg.get_body(preferencelist=("plain", "html"))
    if part is None:
        return ""
    try:
        text = part.get_content()
    except (LookupError, KeyError):
        text = part.get_payload(decode=True).decode("utf-8", "replace") if part.get_payload(decode=True) else ""
    if part.get_content_type() == "text/html":
        text = re.sub(r"(?is)<(script|style).*?</\1>", " ", text)
        text = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>", "\n", text)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n\s*\n+", "\n\n", text)).strip()


def _iso(date_header: str) -> str:
    try:
        return parsedate_to_datetime(date_header).isoformat()
    except (TypeError, ValueError, IndexError):
        return ""


class Gmail:
    def __init__(self, address: str, app_password: str, imap_factory=None):
        self.address = address
        self.app_password = clean_password(app_password)
        self._factory = imap_factory or (lambda: imaplib.IMAP4_SSL(HOST, PORT, timeout=TIMEOUT_S))

    @classmethod
    def from_config(cls, path: Path | None = None, imap_factory=None) -> "Gmail | None":
        c = load_config(path)
        return cls(c["email"], c["appPassword"], imap_factory) if c else None

    # -- spojenie -----------------------------------------------------------
    def _open(self):
        try:
            m = self._factory()
        except (OSError, socket.timeout) as e:
            raise GmailError(f"Gmail nie je dostupný ({type(e).__name__}). Skontroluj pripojenie servera.") from None
        try:
            m.login(self.address, self.app_password)
        except imaplib.IMAP4.error:
            self._close(m)
            raise GmailError("Prihlásenie do Gmailu zlyhalo. Skontroluj e-mail a heslo aplikácie a či je v Gmaile zapnutý IMAP.") from None
        return m

    @staticmethod
    def _close(m) -> None:
        try:
            m.logout()
        except Exception:
            pass

    def _call(self, fn):
        m = self._open()
        try:
            return fn(m)
        except imaplib.IMAP4.error as e:
            raise GmailError(f"Gmail odmietol požiadavku: {e}") from None
        except (OSError, socket.timeout) as e:
            raise GmailError(f"Spojenie s Gmailom sa prerušilo ({type(e).__name__}).") from None
        finally:
            self._close(m)

    def test(self) -> None:
        self._call(lambda m: None)

    @staticmethod
    def _folder(m, flag: str) -> str:
        typ, data = m.list()
        for line in data or []:
            if not isinstance(line, bytes):
                continue
            g = _LIST_RE.match(line)
            if g and flag.encode() in g.group("flags"):
                name = g.group("name").decode()
                return name if name.startswith('"') else _quote(name)
        raise GmailError(f"V Gmaile chýba priečinok {flag}. Zapni IMAP a zobrazenie priečinkov v nastaveniach Gmailu.")

    @staticmethod
    def _fetched(data):
        """Z odpovede FETCH vráti dvojice (metadáta, telo)."""
        out = []
        for item in data or []:
            if isinstance(item, tuple) and len(item) >= 2:
                meta = {}
                for g in _FETCH_RE.finditer(item[0]):
                    if g.group(1): meta["thrid"] = g.group(1).decode()
                    if g.group(2): meta["msgid"] = g.group(2).decode()
                    if g.group(3): meta["uid"] = g.group(3).decode()
                out.append((meta, item[1]))
        return out

    # -- čítanie ------------------------------------------------------------
    def search(self, query: str = DEFAULT_QUERY, limit: int = 20) -> list[dict]:
        """Vlákna podľa Gmail vyhľadávania (X-GM-RAW), najnovšie prvé."""
        def run(m):
            m.select(self._folder(m, "\\All"), readonly=True)
            m.literal = query.encode("utf-8")
            typ, data = m.uid("SEARCH", "CHARSET", "UTF-8", "X-GM-RAW")
            uids = (data[0] or b"").split() if data else []
            if not uids:
                return []
            uids = uids[-200:]
            typ, data = m.uid("FETCH", b",".join(uids).decode(),
                              "(X-GM-THRID X-GM-MSGID BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE MESSAGE-ID)])")
            threads: dict[str, dict] = {}
            for meta, raw in self._fetched(data):
                msg = email.message_from_bytes(raw, policy=email.policy.default)
                t = threads.setdefault(meta.get("thrid", meta.get("uid", "")), {"threadId": meta.get("thrid", ""), "count": 0})
                t["count"] += 1
                if "subject" not in t:  # prvá (najstaršia) správa vlákna = dopyt
                    t.update(subject=_header(msg, "Subject") or "(bez predmetu)", sender=_header(msg, "From"))
                t["date"] = _iso(_header(msg, "Date")) or t.get("date", "")
            return sorted(threads.values(), key=lambda t: t.get("date", ""), reverse=True)[:limit]
        return self._call(run)

    def thread(self, thread_id: str) -> list[dict]:
        if not re.fullmatch(r"\d{1,25}", thread_id or ""):
            raise GmailError("Neplatné vlákno.")
        def run(m):
            m.select(self._folder(m, "\\All"), readonly=True)
            typ, data = m.uid("SEARCH", "X-GM-THRID", thread_id)
            uids = (data[0] or b"").split() if data else []
            if not uids:
                return []
            typ, data = m.uid("FETCH", b",".join(uids[-30:]).decode(), "(X-GM-MSGID BODY.PEEK[])")
            out = []
            for meta, raw in self._fetched(data):
                msg = email.message_from_bytes(raw, policy=email.policy.default)
                out.append({
                    "uid": meta.get("uid", ""), "messageId": _header(msg, "Message-ID"), "references": _header(msg, "References"),
                    "from": _header(msg, "From"), "to": _header(msg, "To"), "date": _iso(_header(msg, "Date")),
                    "subject": _header(msg, "Subject"), "text": _text_body(msg)[:20000],
                    "attachments": [p.get_filename() for p in msg.iter_attachments() if p.get_filename()],
                })
            return sorted(out, key=lambda x: x["date"])
        return self._call(run)

    # -- koncept ------------------------------------------------------------
    def build_draft(self, to: str, subject: str, body: str, in_reply_to: str = "", references: str = "") -> EmailMessage:
        to_addr = parseaddr(to or "")[1]
        if not to_addr or "@" not in to_addr:
            raise GmailError("Chýba platný e-mail príjemcu.")
        msg = EmailMessage()
        msg["From"] = self.address
        msg["To"] = to_addr
        msg["Subject"] = subject or "Cenová ponuka"
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain=self.address.split("@")[-1] or None)
        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
            msg["References"] = (references + " " + in_reply_to).strip() if references else in_reply_to
        msg.set_content(body)
        return msg

    def create_draft(self, to: str, subject: str, body: str, in_reply_to: str = "", references: str = "") -> None:
        msg = self.build_draft(to, subject, body, in_reply_to, references)
        def run(m):
            typ, data = m.append(self._folder(m, "\\Drafts"), "\\Draft", imaplib.Time2Internaldate(time.time()), msg.as_bytes())
            if typ != "OK":
                raise GmailError("Gmail koncept neuložil.")
        self._call(run)
