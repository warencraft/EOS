# ADR-0011 - Use Python standard library validation layer

**Status:** Approved  
**Date:** 2026-07-13  

## Context

Fáza 0.2A potrebuje minimálnu aplikačnú validačnú vrstvu. V dostupnom runtime nie sú prítomné balíky `jsonschema` ani `pytest` a projekt nemá zavádzať nové závislosti bez jasného dôvodu.

## Decision

Počiatočná validačná vrstva bude napísaná v Pythone nad štandardnou knižnicou.

Bude podporovať iba podmnožinu JSON Schema potrebnú pre kontrakty fázy 0.2A a samostatné aplikačné pravidlá EOS.

## Alternatives Considered

- Pridať externý balík `jsonschema`: technicky vhodné, ale zavádza novú závislosť.
- Odložiť aplikačnú validáciu: oslabilo by to cieľ fázy 0.2A.
- Implementovať validáciu v inom jazyku: zbytočné, keď Python je preferovaný projektový jazyk.

## Consequences

Validácia je spustiteľná bez inštalácie externých balíkov.

Neskôr je možné interný validátor nahradiť alebo doplniť štandardnou knižnicou `jsonschema`, ak bude závislosť schválená.

## Risks

Interný validátor nie je plná implementácia JSON Schema Draft 2020-12. Tento limit je prijateľný, pretože fáza 0.2A potrebuje iba základnú vrstvu.

## Related Documents

- `docs/governance/EOS-006_Data_Validation_Standard.md`
- `scripts/validation/`

## Review Date

2026-10-01

