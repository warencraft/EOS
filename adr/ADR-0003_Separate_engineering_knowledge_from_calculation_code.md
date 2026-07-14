# ADR-0003 - Separate engineering knowledge from calculation code

**Status:** Approved  
**Date:** 2026-07-13  

## Context

EOS bude časom obsahovať kalkulátory. Ak by technické hodnoty boli zapísané priamo v kóde, systém by stratil dohľadateľnosť, revízie a zdrojovú klasifikáciu.

## Decision

Inžinierske znalosti budú uložené v dátových záznamoch. Kalkulačný kód bude iba spracúvať validované vstupy.

Princíp:

**Kód počíta. Databáza nesie znalosti.**

## Alternatives Considered

- Ukladať hodnoty priamo v kóde: jednoduché krátkodobo, neudržateľné dlhodobo.
- Ukladať hodnoty v dokumentoch: čitateľné, ale ťažko validovateľné.
- Miešať dáta a výpočty: rýchle na prototyp, nevhodné pre profesionálny systém.

## Consequences

Kalkulátory budú testovateľné a dátové záznamy zostanú dohľadateľné.

Každá technická hodnota bude musieť mať zdroj, stav a kontext.

## Risks

Vývoj môže byť pomalší, pretože najprv treba navrhnúť dátový model. Riziko je prijateľné vzhľadom na dlhodobý cieľ EOS.

## Related Documents

- `docs/governance/EOS-000_Development_Manifesto.md`
- `docs/governance/EOS-001_System_Architecture.md`
- `docs/governance/EOS-004_Core_Data_Model.md`

## Review Date

2026-10-01

