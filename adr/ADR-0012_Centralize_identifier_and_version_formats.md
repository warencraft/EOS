# ADR-0012 - Centralize identifier and version formats

**Status:** Approved  
**Date:** 2026-07-13  

## Context

EOS používa viacero stabilných ID formátov a odlišuje `schemaVersion`, `recordVersion` a dokumentové verzie. Ak by sa tieto formáty duplikovali v každej schéme, vzniklo by riziko nekonzistentných pravidiel.

## Decision

Formáty identifikátorov a základné formáty verzií budú definované centrálne v spoločných schémach a opakovane používané cez `$ref` alebo jednotné regex pravidlá.

## Alternatives Considered

- Duplikovať regex v každej schéme: jednoduché na začiatku, rizikové pri zmene.
- Kontrolovať ID iba aplikačne: slabšie pre kontrakt a dokumentáciu dát.

## Consequences

Schémy budú konzistentnejšie a ľahšie rozšíriteľné.

Zmena ID pravidla bude mať jedno autoritatívne miesto.

## Risks

Schémy sú viac previazané cez `$ref`. Tento kompromis je prijateľný, pretože modularita je cieľ fázy 0.2A.

## Related Documents

- `schemas/common/identifiers.schema.json`
- `docs/governance/EOS-003_Identification_and_Versioning.md`

## Review Date

2026-10-01

