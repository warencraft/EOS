"""Súkromné rozhovory v EOS cez firemné Claude API."""

import hashlib
import json
import os
import tempfile
from contextlib import aclosing, contextmanager
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import Form, HTTPException, Request
from fastapi.responses import RedirectResponse, StreamingResponse

from scripts.ai import chat_client
from scripts.ai.context import Turn, prepare_context

from .tailnet_identity import authorized_user

MAX_TURNS = 60
# Allow an 8 000-character prompt even if each Unicode character takes four bytes.
MAX_CONTEXT_BYTES = 32_000


def save(path: Path, record: dict):
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as file:
        try:
            json.dump(record, file, ensure_ascii=False)
            file.flush()
            os.replace(file.name, path)
        finally:
            Path(file.name).unlink(missing_ok=True)


def register(app, templates, root: Path, board, tools=None):
    """`tools`: scripts.ai.nastroje.Nastroje (čítanie EOS cez bránu, ADR-0027) alebo None."""
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

    @contextmanager
    def prepare(request, session, prompt):
        folder = user_folder(request)
        key, model = chat_client.settings()
        if not key or not model:
            raise HTTPException(503, "Claude API ešte nie je nastavené.")
        prompt = prompt.strip()
        if not 1 <= len(prompt) <= 8000:
            raise HTTPException(422, "Napíš správu s najviac 8 000 znakmi.")
        try:
            prompt.encode("utf-8")
        except UnicodeEncodeError:
            raise HTTPException(422, "Správa obsahuje neplatný text.") from None
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
            history = record["messages"]
            turns = [
                Turn(index // 2 + 1, history[index]["content"], history[index + 1]["content"])
                for index in range(0, len(history), 2)
            ]
            context = prepare_context(
                prompt, turns, can_use_source=lambda _source: False, max_bytes=MAX_CONTEXT_BYTES,
            )
            model_messages = [{"role": message.role, "content": message.content}
                              for message in context.messages]
            def finish(answer, supplier, sources=()):
                record["messages"] = history + [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": answer},
                ]
                if supplier:
                    record.setdefault("suppliers", {})[str(len(history) + 1)] = supplier
                if sources:
                    record.setdefault("sources", {})[str(len(history) + 1)] = list(sources)[:20]
                save(path, record)
                return f"/chat?session={path.stem}"

            yield key, model, model_messages, finish
        finally:
            lock.rmdir()

    @app.post("/chat")
    def chat_send(request: Request, session: str = Form(""), prompt: str = Form(...)):
        with prepare(request, session, prompt) as (key, model, messages, finish):
            try:
                answer, supplier, sources = chat_client.reply(key, model, messages, tools)
            except ImportError:
                raise HTTPException(503, "Chýba voliteľná závislosť EOS pre Claude API.") from None
            except chat_client.ChatError:
                return RedirectResponse("/chat?error=api" + (f"&session={UUID(session).hex}" if session else ""), 303)
            return RedirectResponse(finish(answer, supplier, sources), 303)

    @app.post("/chat/stream")
    async def chat_stream(request: Request, session: str = Form(""), prompt: str = Form(...)):
        user_folder(request)

        def event(kind, text):
            return json.dumps({"type": kind, "text": text}, ensure_ascii=False) + "\n"

        async def generate():
            try:
                with prepare(request, session, prompt) as (key, model, messages, finish):
                    async with aclosing(chat_client.stream_reply(key, model, messages, tools)) as stream:
                        async for update in stream:
                            if isinstance(update, str):
                                yield event("delta", update)
                            else:
                                location = finish(*update)
                    yield event("done", location)
            except HTTPException as exc:
                yield event("error", exc.detail)
            except (ImportError, OSError, chat_client.ChatError):
                yield event("error", "Claude nevrátil odpoveď. Správu môžeš skúsiť znova.")

        return StreamingResponse(generate(), media_type="application/x-ndjson",
                                 headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})

    def supplier_proposal(request: Request, session: str, turn: str) -> dict:
        _, record = load(user_folder(request), session)
        proposal = record.get("suppliers", {}).get(turn)
        if proposal is None:
            raise HTTPException(404, "Návrh dodávateľa sa nenašiel.")
        return {**proposal, "status": "verify"}

    return supplier_proposal
