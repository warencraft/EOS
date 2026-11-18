"""Identita pre nové funkcie EOS za súkromným Tailscale Serve."""

import os

from fastapi import Request
from urllib.parse import urlsplit


def authorized_user(request: Request, setting: str) -> str | None:
    origin = os.getenv("EOS_SERVE_ORIGIN", "").rstrip("/")
    public = urlsplit(origin)
    if public.scheme != "https" or not public.hostname or not public.hostname.endswith(".ts.net"):
        return None
    if request.headers.get("host", "").lower() != public.netloc.lower():
        return None
    if request.method == "POST" and request.headers.get("origin") != origin:
        return None
    if not request.client or request.client.host not in {"127.0.0.1", "::1"}:
        return None
    login = request.headers.get("tailscale-user-login", "").casefold()
    allowed = os.getenv(setting, "").casefold().split(",")
    return login if login and login in {email.strip() for email in allowed} else None
