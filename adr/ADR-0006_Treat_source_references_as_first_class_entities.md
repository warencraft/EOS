# ADR-0006 - Treat source references as first-class entities

**Status:** Approved  
**Date:** 2026-07-13  

## Context

EOS potrebuje dohľadateľnosť technických tvrdení. Ak by boli zdroje uložené iba ako voľný text pri jednotlivých záznamoch, rovnaký zdroj by sa duplikoval a nebolo by jasné, ktoré tvrdenie podporuje.

## Decision

`SourceReference` bude samostatná autoritatívna entita s ID `SRC-xxxxxx`.

Konkrétne použitie zdroja pri tvrdení alebo poli bude vyjadrené cez `SourceLink`.

## Alternatives Considered

- Ukladať zdroj priamo v každom zázname: jednoduché, ale duplicitné.
- Ukladať zdroje iba v dokumentácii: čitateľné, ale ťažko validovateľné.
- Riešiť zdroje až pri databázovej migrácii: odkladalo by to kľúčový governance problém.

## Consequences

Zdroje budú opakovane použiteľné, dohľadateľné a oddelené od interpretácie.

`SourceLink` umožní uviesť podporované tvrdenie, typ použitia zdroja, lokalizáciu a stav overenia.

## Risks

Model je prísnejší a vyžaduje disciplínu pri zadávaní zdrojov. Je to zámerné, pretože presnosť má v EOS prednosť pred množstvom.

## Related Documents

- `docs/governance/EOS-002_Documentation_Standard.md`
- `docs/governance/EOS-004_Core_Data_Model.md`

## Review Date

2026-10-01

