# ADR-0013 - Use a standards-compliant JSON Schema validator

**Status:** Accepted  
**Date:** 2026-07-14  

## Context

Fáza 0.2A zaviedla interný Python validátor nad štandardnou knižnicou. Tento validátor bol vhodný ako minimálna základná vrstva, ale nie je plnou implementáciou JSON Schema Draft 2020-12.

S rastom EOS by narastalo riziko, že vlastný subset validátor nebude pokrývať pravidlá, ktoré budú schémy potrebovať.

## Decision

EOS bude používať štandardne udržiavaný JSON Schema validátor:

- `jsonschema>=4.18.0`
- `jsonschema.validators.Draft202012Validator`

Interná EOS validačná vrstva zostáva zodpovedná za významové, referenčné a medzi-entitné pravidlá.

Závislosť je evidovaná v `pyproject.toml`.

Ak sa použije `referencing.Registry`, nejde o samostatnú priamu projektovú závislosť. Je to tranzitívna súčasť ekosystému knižnice `jsonschema`.

## Alternatives Considered

| Možnosť | Draft 2020-12 | Závislosti | Údržba | Výkon | Chybové hlásenia | Bezpečnosť | Udržateľnosť |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Vlastný EOS validátor | Čiastočná podpora | Žiadne externé | Interná zodpovednosť | Dostatočný pre malé fixtures | Jednoduché, projektové | Malá plocha závislostí | Rizikové pri rozšírení |
| Python `jsonschema` | Áno | Externý balík | Aktívne udržiavaný ekosystém | Dostatočný pre governance a dáta | Kvalitné a detailné | Vyžaduje správu závislosti | Dobrá |
| `fastjsonschema` | Čiastočne podľa verzie | Externý balík | Udržiavaný, výkonovo orientovaný | Veľmi dobrý | Menej ergonomické pre governance | Vyžaduje správu závislosti | Dobrá pre výkonové scenáre |
| Iný validátor | Závisí od voľby | Závisí od voľby | Neurčené | Neurčené | Neurčené | Neurčené | Vyžaduje samostatné posúdenie |

## Consequences

EOS získava štandardnú podporu JSON Schema Draft 2020-12 pre štrukturálnu validáciu.

Interný validátor zostáva ako tenká aplikačná vrstva pre významové pravidlá EOS, zatiaľ čo syntaktickú validáciu preberá štandardný nástroj.

Ak runtime nemá nainštalované závislosti z `pyproject.toml`, integračné testy validácie sú blokované a nesmú byť vydávané za úspešné.

## Migration

Migračný postup:

1. Zaviesť `jsonschema>=4.18.0` v `pyproject.toml`.
2. Nahradiť vlastnú interpretáciu JSON Schema keywordov volaním `Draft202012Validator`.
3. Registrovať modulárne schémy cez štandardný registry/resolver mechanizmus knižnice.
4. Zachovať EOS aplikačné pravidlá mimo JSON Schema validátora.
5. Rozlíšiť chyby kategóriami `schema_validation`, `schema_definition`, `application_validation` a `reference_integrity`.
6. Zachovať existujúce fixtures a regresné testy.

## EOS Application Validation Remains

V aplikačnej validácii EOS zostáva:

- pravidlo `sourceLinks` podľa lifecycle stavu a významového kontextu,
- základná hierarchická konzistencia ID,
- budúca referenčná integrita medzi záznamami,
- kompatibilita `SourceLink` a `SourceReference`,
- pravidlá `schemaVersion` vs `documentVersion`.

## Risks

Pridanie externej závislosti vyžaduje správu verzií, bezpečnostnú kontrolu a dohodnutý spôsob inštalácie v runtime prostredí.

Bez nainštalovaných závislostí zostane validácia blokovaná. Tento stav musí byť hlásený jasne a nesmie sa považovať za úspešný validačný beh.

## Recommendation

Rozhodnutie je prijaté. Pred pokračovaním do širších dátových kontraktov sa odporúča overiť inštalačný postup v cieľovom runtime.

## Related Documents

- `docs/governance/EOS-006_Data_Validation_Standard.md`
- `docs/governance/EOS-007_Validation_Capability_Matrix.md`
- `ADR-0011_Use_Python_standard_library_validation_layer.md`

## Review Date

2026-08-15

