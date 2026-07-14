# ADR-0009 - Use JSON Schema Draft 2020-12

**Status:** Approved  
**Date:** 2026-07-13  

## Context

EOS potrebuje dátové kontrakty, ktoré budú čitateľné, modulárne a pripravené na budúcu migráciu do databázového systému.

## Decision

JSON schémy EOS budú používať JSON Schema Draft 2020-12.

## Alternatives Considered

- Starší draft JSON Schema: dostatočný pre jednoduché prípady, ale menej vhodný pre dlhodobé rozširovanie.
- Vlastný formát kontraktov: zbytočné riziko a slabšia interoperabilita.

## Consequences

Schémy budú používať explicitné `$schema`, `$id` a `$ref`.

Budúce nástroje môžu využiť štandardný ekosystém JSON Schema.

## Risks

Lokálne validačné nástroje musia vedieť pracovať s vybraným draftom alebo podporovať potrebnú podmnožinu pravidiel.

## Related Documents

- `docs/governance/EOS-006_Data_Validation_Standard.md`

## Review Date

2026-10-01

