# ADR-0008 - Use hierarchical identifiers for job-owned entities

**Status:** Approved  
**Date:** 2026-07-13  

## Context

Niektoré entity existujú primárne v kontexte konkrétnej zákazky, napríklad operácie, časové záznamy, riziká a poznámky do ponuky. Ich ID má byť stabilné a zároveň má ukazovať vlastníctvo zákazkou.

## Decision

Entity vlastnené zákazkou budú používať hierarchické ID:

- `JOB-yyyy-xxxx-OP-xxx`,
- `JOB-yyyy-xxxx-OP-xxx-TM-xxx`,
- `JOB-yyyy-xxxx-RSK-xxx`,
- `JOB-yyyy-xxxx-QN-xxx`.

## Alternatives Considered

- Samostatné globálne ID pre každú entitu: jednoduchšie na databázové indexovanie, ale menej čitateľné v súborovom systéme.
- Poradové čísla bez ID zákazky: krátke, ale nedohľadateľné mimo kontextu.
- Vnorené objekty bez vlastného ID: jednoduché pre malé dáta, nevhodné pre revízie a väzby.

## Consequences

Z ID bude jasné, ku ktorej zákazke alebo operácii záznam patrí.

Budúce odkazy medzi operáciami, časmi, rizikami a poznámkami budú stabilnejšie.

## Risks

ID sú dlhšie. Táto nevýhoda je prijateľná, pretože spätná dohľadateľnosť je pre EOS dôležitejšia než krátkosť identifikátora.

## Related Documents

- `docs/governance/EOS-003_Identification_and_Versioning.md`
- `docs/governance/EOS-004_Core_Data_Model.md`

## Review Date

2026-10-01

