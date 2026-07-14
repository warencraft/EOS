# ADR-0005 - Separate internal EOS standards from external normative references

**Status:** Approved  
**Date:** 2026-07-13  

## Context

Prefix `STD` bol pôvodne použitý pre normy a štandardy všeobecne. To miešalo interné pravidlá EOS s externými normami, štandardmi a záväznými technickými predpismi.

## Decision

EOS bude používať:

- `STD-xxx` pre interný technický štandard alebo pravidlo EOS,
- `NRM-xxxx` pre externú normu, štandard alebo záväzný technický predpis.

Entita pre externú normatívnu referenciu sa bude volať `NormReference`.

## Alternatives Considered

- Ponechať `STD` pre všetko: jednoduché, ale nejasné.
- Použiť iba textové citácie noriem: čitateľné, ale slabé pre väzby a validáciu.
- Použiť `ExternalStandardReference`: presné, ale dlhšie ako potrebné pre bežné dátové polia.

## Consequences

Interné pravidlá EOS a externé normatívne zdroje budú jasne oddelené.

Dokumentácia aj dátový model budú lepšie rešpektovať pravidlo, že normy a odporúčania sa nesmú miešať.

## Risks

Existujúce odkazy na `STD` treba skontrolovať pri každej ďalšej fáze, aby bolo jasné, či ide o interný štandard alebo externú normu.

## Related Documents

- `docs/governance/EOS-003_Identification_and_Versioning.md`
- `docs/governance/EOS-004_Core_Data_Model.md`

## Review Date

2026-10-01

