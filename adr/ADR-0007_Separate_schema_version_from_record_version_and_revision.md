# ADR-0007 - Separate schema version from record version and revision

**Status:** Approved  
**Date:** 2026-07-13  

## Context

Pôvodný dátový model používal všeobecné polia `version` a `revision`. Pri dátových entitách to nestačí, pretože zmena štruktúry záznamu a zmena významu konkrétneho záznamu sú rozdielne veci.

## Decision

Dátové entity budú používať:

- `schemaVersion` pre verziu dátového kontraktu,
- `recordVersion` pre významovú verziu konkrétneho záznamu,
- `revision` pre menšie opravy v rámci rovnakej významovej verzie.

## Alternatives Considered

- Použiť iba `version`: jednoduché, ale nejasné.
- Použiť iba `revision`: nevie rozlíšiť kontrakt a obsah.
- Riešiť verzie iba cez Git: nestačí pre budúce databázové záznamy.

## Consequences

Budúca migrácia JSON na SQLite alebo PostgreSQL bude čistejšia.

Bude jasné, či sa zmenila štruktúra dát, význam záznamu alebo iba formálna oprava.

## Risks

Používatelia musia rozumieť rozdielu medzi tromi verziovacími poľami. Vysvetlenie je súčasťou `EOS-004`.

## Related Documents

- `docs/governance/EOS-003_Identification_and_Versioning.md`
- `docs/governance/EOS-004_Core_Data_Model.md`

## Review Date

2026-10-01

