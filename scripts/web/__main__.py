"""Spustenie: python -m scripts.web  (potom otvor http://127.0.0.1:8000)."""

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="EOS UI v0 – lokálna aplikácia nad intake/.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--intake", type=Path, default=None, help="priečinok intake (predvolene ./intake)")
    parser.add_argument("--allow-host", action="append", default=[],
                        help="ďalší povolený hostiteľ pre formuláre, napr. názov servera v Tailscale (ADR-0025)")
    args = parser.parse_args()

    import uvicorn

    from .app import ROOT, create_app

    app = create_app(ROOT, args.intake, allowed_hosts=set(args.allow_host))
    print(f"EOS beží na http://127.0.0.1:{args.port}  (Ctrl+C ukončí)")
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning", proxy_headers=False)


if __name__ == "__main__":
    main()
