"""Súkromné rozhovory v EOS cez firemné Claude API."""

import hashlib
import json
import os
import tempfile
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from scripts.ai import chat_client

from .tailnet_identity import authorized_user

MAX_TURNS = 60


def save(path: Path, record: dict):
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as file:
        try:
            json.dump(record, file, ensure_ascii=False)
            file.flush()
            os.replace(file.name, path)
        finally:
            Path(file.name).unlink(missing_ok=True)


def register(app, templates, root: Path, board):
    templates.env.globals["eos_chat_available"] = lambda request: bool(
        authorized_user(request, "EOS_CHAT_USERS")
    )

    def user_folder(request):
        identity = authorized_user(request, "EOS_CHAT_USERS")
        if not identity:
            raise HTTPException(403, "Chat je dostupný iba povoleným používateľom.")
        return root / hashlib.sha256(identity.encode()).hexdigest()

    def load(folder, chat_id):
        try:
            path = folder / f"{UUID(chat_id).hex}.json"
            return path, json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, FileNotFoundError):
            raise HTTPException(404, "Rozhovor sa nenašiel.") from None

    @app.get("/chat")
    def chat(request: Request, session: str = "", error: str = "", submitted: bool = False, new: bool = False):
        folder = user_folder(request)
        chats = sorted(folder.glob("*.json"), key=lambda entry: entry.stat().st_mtime, reverse=True)
        sessions = [(entry.stem, json.loads(entry.read_text(encoding="utf-8"))["title"]) for entry in chats]
        if not session and not new and not error and sessions:
            session = sessions[0][0]
        current = load(folder, session)[1] if session else None
        return templates.TemplateResponse(request, "claude_chat.html", {
            "sessions": sessions, "session": session, "current": current,
            "ready": all(chat_client.settings()), "error": error == "api", "submitted": submitted,
        }, headers={"Cache-Control": "no-store", "X-Frame-Options": "SAMEORIGIN"})

    @app.post("/chat/navrh")
    def submit_feedback(request: Request, topic: str = Form(...), text: str = Form(...),
                        session: str = Form("")):
        folder = user_folder(request)
        if session:
            load(folder, session)
        try:
            board.pridaj(autor="marco", pre="robino", typ="feedback",
                         tema=topic.strip(), text=text.strip())
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from None
        return RedirectResponse("/chat?" + (f"session={UUID(session).hex}&" if session else "") + "submitted=1", 303)

    @app.post("/chat")
    def chat_send(request: Request, session: str = Form(""), prompt: str = Form(...)):
        folder = user_folder(request)
        key, model = chat_client.settings()
        if not key or not model:
            raise HTTPException(503, "Claude API ešte nie je nastavené.")
        prompt = prompt.strip()
        if not 1 <= len(prompt) <= 8000:
            raise HTTPException(422, "Napíš správu s najviac 8 000 znakmi.")
        folder.mkdir(parents=True, mode=0o700, exist_ok=True)
        path, record = load(folder, session) if session else (
            folder / f"{uuid4().hex}.json", {"title": prompt[:65], "messages": []}
        )
        lock = folder / ".request"
        try:
            lock.mkdir(mode=0o700)
        except FileExistsError:
            raise HTTPException(409, "Predošlá správa sa ešte spracúva.") from None
        try:
            if session:
                path, record = load(folder, session)
            if len(record["messages"]) >= MAX_TURNS:
                raise HTTPException(422, "Tento rozhovor dosiahol limit. Začni nový.")
            messages = record["messages"] + [{"role": "user", "content": prompt}]
            try:
                answer, supplier = chat_client.reply(key, model, messages)
            except ImportError:
                raise HTTPException(503, "Chýba voliteľná závislosť EOS pre Claude API.") from None
            except chat_client.ChatError:
                return RedirectResponse("/chat?error=api" + (f"&session={path.stem}" if session else ""), 303)
            record["messages"] = messages + [{"role": "assistant", "content": answer}]
            if supplier:
                record.setdefault("suppliers", {})[str(len(messages))] = supplier
            save(path, record)
        finally:
            lock.rmdir()
        return RedirectResponse(f"/chat?session={path.stem}", 303)

    def supplier_proposal(request: Request, session: str, turn: str) -> dict:
        _, record = load(user_folder(request), session)
        proposal = record.get("suppliers", {}).get(turn)
        if proposal is None:
            raise HTTPException(404, "Návrh dodávateľa sa nenašiel.")
        return {**proposal, "status": "verify"}

    return supplier_proposal
