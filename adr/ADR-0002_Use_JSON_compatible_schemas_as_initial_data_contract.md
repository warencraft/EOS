# ADR-0002 - Use JSON-compatible schemas as the initial data contract

**Status:** Approved  
**Date:** 2026-07-13  

## Context

EOS potrebuje dátové kontrakty ešte pred vznikom databázového servera. Počiatočné dáta musia byť čitateľné, verzovateľné a migrovateľné.

## Decision

Počiatočné dátové kontrakty budú JSON-kompatibilné. Schémy budú uložené v `schemas/` a budú definovať štruktúru entít bez konkrétnych strojárskych hodnôt.

## Alternatives Considered

- SQLite od začiatku: technicky vhodné, ale v tejto fáze by predčasne zaviedlo databázovú vrstvu.
- PostgreSQL od začiatku: príliš ťažké pre fázu 0.1.
- Voľné Markdown tabuľky: ľahko čitateľné, ale slabé ako dátový kontrakt.

## Consequences

Dáta bude možné verzovať a validovať jednoduchými nástrojmi.

Neskoršia migrácia do SQLite alebo PostgreSQL zostane možná, ak budú ID a väzby stabilné.

## Risks

JSON súbory môžu byť pri veľkom objeme dát neergonomické. Toto riziko je prijateľné, pretože fáza 0.1 nerieši produkčnú databázu.

## Related Documents

- `docs/governance/EOS-001_System_Architecture.md`
- `docs/governance/EOS-004_Core_Data_Model.md`

## Review Date

2026-10-01

