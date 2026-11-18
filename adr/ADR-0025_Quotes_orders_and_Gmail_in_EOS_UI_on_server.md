# ADR-0025 - Ponuky, objednávky a Gmail v EOS UI na serveri

**Status:** Accepted  
**Date:** 2026-11-18  
**Decided by:** Software Architect (IT strana projektu). Pripojenie Gmailu robí jeho vlastník sám zadaním hesla aplikácie.  
**Supersedes:** ADR-0023 (prototyp EOS Zákazky na claude.ai)  

## Context

Prototyp EOS Zákazky (ADR-0023) bežal na claude.ai mimo repozitára, bez testov a mimo pravidiel ADR-0019. Lokálne UI (ADR-0021, ADR-0022) vedelo iba zákazky a kalkuláciu a bežalo na jednom počítači. Cieľ: jedno UI v EOS pre ponuky, objednávky, sklad, dodávateľov a knowledge base, dostupné pre oboch bratov, s dopytmi z Marcovho Gmailu.

Software Architect rozhodol 2026-11-18: Gmail cez heslo aplikácie (IMAP), prístup súkromne cez Tailscale, údaje z prototypu preniesť na server.

## Decision

1. **Jedno UI.** Do `scripts/web/` pribudnú stránky Ponuky, Objednávky, Sklad, Dodávatelia, Knowledge a Gmail (`scripts/web/prevadzka_ui.py`). Prototyp na claude.ai sa po prenose údajov nepoužíva.
2. **Úložisko.** Prevádzkové záznamy sú JSON súbory v `intake/_eos/prevadzka/<druh>/<id>.json`, mimo gitu, rovnako ako kalkulácie podľa ADR-0021. Formát `scripts/prevadzka/prevadzka.schema.json` je nástrojový, nie kontrakt EOS; zápis ho validuje. Nie je to zdroj pravdy pre znalosti EOS. Knowledge base je pracovný kontext s klasifikáciou N/L/P/V. Entity Job a ďalšie ich neskôr nahradia.
3. **Gmail cez IMAP** (`scripts/gmail/`, iba štandardná knižnica `imaplib` a `email`). Prihlásenie e-mailom a heslom aplikácie Google. Stránka Gmail heslo najprv overí a až potom uloží do `~/.config/eos/gmail.json` (práva 0600) alebo do súboru z `EOS_GMAIL_CONFIG`. Nikdy nie do repozitára ani do `intake/`. EOS vie hľadať vlákna (Gmail vyhľadávanie), čítať vlákno a uložiť koncept odpovede s `In-Reply-To`. **Neodosiela** e-maily.
4. **Bez AI na e-mailoch.** Obsah e-mailov sa neposiela do žiadnej AI; ceny do ponuky zadáva človek. Hľadanie cien (ADR-0024) dostáva iba materiál a domény dodávateľov.
5. **Server a prístup.** UI beží na serveri pod samostatným používateľom ako služba systemd na `127.0.0.1`. Do súkromnej siete Tailscale ho sprístupní `tailscale serve` s HTTPS. Verejný port sa neotvára. Ochrana formulárov (ADR-0022 bod 7) povolí okrem localhostu iba hostiteľov z `--allow-host` alebo `EOS_ALLOWED_HOSTS`.
6. **Prenos z prototypu** jednorazovo príkazom `python -m scripts.prevadzka import export.json`.

## Alternatives Considered

| Možnosť | Posúdenie |
| --- | --- |
| Gmail cez Google OAuth a Gmail API | Bez hesla na serveri, ale nové závislosti, projekt v Google Cloud a pri @gmail.com účte v testovacom režime obnova prihlásenia každých 7 dní. |
| Konektor Gmail z claude.ai | Funguje iba v stránkach a chatoch claude.ai, nie vo vlastnej aplikácii na serveri. |
| SQLite pre prevádzkové údaje | Etapa B. JSON súbory stačia pre dvoch ľudí a zodpovedajú ADR-0021; prechod na SQLite je samostatné rozhodnutie. |
| Verejná doména s prihlásením | Treba doménu, prihlasovanie a ochranu proti útokom z internetu. Tailscale to rieši bez kódu. |

## Consequences

- Marco a Robino majú jedno UI, ktoré otvoria v prehliadači cez Tailscale z počítača aj mobilu.
- Koncepty ponúk vznikajú v Marcovom Gmaile ako odpovede vo vlákne dopytu.
- Údaje sú na jednom serveri. Zálohu `intake/` treba riešiť (návod `docs/manual/SERVER.md`).
- TECH_STACK sa nemení: žiadna nová závislosť, FastAPI a HTMX sú už v `.[ui]`.

## Risks

- **Heslo aplikácie na serveri.** Kto má prístup k používateľovi `eos` na serveri, vidí Marcov Gmail. Opatrenie: samostatný používateľ, súbor 0600, odpojenie v UI heslo zmaže, heslo sa dá kedykoľvek zrušiť v Google účte.
- **Prístup do UI má každý v Tailnete.** UI nemá vlastné prihlásenie. Opatrenie: do Tailnetu iba bratia; zariadenia spravuje admin Tailscale.
- **Súbežné úpravy.** Dvaja ľudia môžu naraz upraviť ten istý záznam a vyhrá posledný. Pri dvoch ľuďoch prijateľné; zamykanie príde s etapou B.
- **Citlivé údaje zákazníkov na serveri.** Otázka 8 z `docs/handoff/2026-11-04_otazky.md` je čiastočne zodpovedaná: údaje sú na vlastnom serveri a nejdú do AI. Ak niečo z nich nesmie byť ani na serveri, rozhodne Marco.

## Related Documents

- `adr/ADR-0019_Keep_real_job_intake_outside_git.md`, `adr/ADR-0021_Local_UI_v0_and_working_calculation.md`, `adr/ADR-0022_Job_entry_in_UI_and_status_board.md`
- `adr/ADR-0023_Web_app_for_quotes_orders_and_stock.md` (nahradené), `adr/ADR-0024_Supplier_price_search_with_Claude_API.md`
- `docs/manual/SERVER.md`, `docs/manual/UI.md`
- `scripts/prevadzka/`, `scripts/gmail/`, `scripts/web/prevadzka_ui.py`, `tests/test_prevadzka.py`

## Review Date

Pri návrhu entity Job, pri prechode do etapy B alebo 2027-02-28, podľa toho, čo nastane skôr.
