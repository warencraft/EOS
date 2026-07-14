# ADR-0010 - Use closed schema contracts by default

**Status:** Approved  
**Date:** 2026-07-13  

## Context

EOS má byť presný a dohľadateľný systém. Voľné neznáme polia v dátových záznamoch by časom vytvorili paralelný neformálny dátový model.

## Decision

Riadené JSON schémy EOS budú používať `additionalProperties: false`, ak neexistuje výslovný dôvod pre výnimku.

## Alternatives Considered

- Povoliť neznáme polia: pružné, ale rizikové pre dlhodobú kvalitu dát.
- Povoliť neznáme polia iba v `notes`: postačuje pre voľný text, nie pre štruktúrované údaje.

## Consequences

Neznáme polia budú odmietnuté.

Každé nové pole musí byť vedome pridané do schémy.

## Risks

Vývoj prototypov môže byť pomalší. Toto riziko je prijateľné, pretože presnosť a kontrola majú v EOS prednosť.

## Related Documents

- `docs/governance/EOS-006_Data_Validation_Standard.md`

## Review Date

2026-10-01

