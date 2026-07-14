# EOS-007 - Matica schopností validačnej vrstvy

**Project:** EOS - Engineering Operating System  
**Document ID:** EOS-007  
**Version:** 0.1  
**Revision:** 1  
**Status:** Draft  
**Author:** Chief Engineering Knowledge Architect + Codex  
**Last update:** 2026-07-14  
**Document basis:** Internal governance decision  

---

## 1. Účel

Tento dokument popisuje schopnosti validačnej vrstvy po integrácii štandardného validátora `jsonschema`.

Od fázy 0.2A.2 štrukturálnu JSON Schema validáciu vykonáva `jsonschema.validators.Draft202012Validator`.

Interná EOS vrstva zostáva určená na významové, referenčné a medzi-entitné pravidlá.

## 2. Základné rozhodnutie

Aktuálna architektúra validácie:

- JSON syntax: Python `json`.
- JSON Schema definície: `jsonschema` + `Draft202012Validator.check_schema`.
- JSON Schema validácia záznamu: `Draft202012Validator`.
- Formáty `date`, `date-time`, `uri`: `jsonschema.FormatChecker`.
- Modulárne `$ref`: štandardné registry/resolver API používané cez ekosystém `jsonschema`.
- EOS aplikačné pravidlá: interná vrstva `scripts/validation`.

Ak runtime nemá nainštalované `jsonschema`, integračná validácia je blokovaná a nesmie byť reportovaná ako úspešná.

## 3. Capability Matrix

| JSON Schema keyword | Stav | Poznámka |
| --- | --- | --- |
| `$schema` | delegated to jsonschema | Draft 2020-12. |
| `$id` | delegated to jsonschema | Používa sa aj pri registrácii modulárnych schém. |
| `$ref` | delegated to jsonschema | Podporované vrátane cross-file referencií cez registrované schémy. |
| `$defs` | delegated to jsonschema | Podporované pre lokálne aj zdieľané definície. |
| `type` | delegated to jsonschema | Plná podpora podľa Draft 2020-12. |
| `required` | delegated to jsonschema | Štrukturálna kontrola povinných polí. |
| `properties` | delegated to jsonschema | Štrukturálna validácia objektov. |
| `additionalProperties` | delegated to jsonschema | EOS používa predvolene `false` pre riadené kontrakty. |
| `enum` | delegated to jsonschema | Kontrola povolených hodnôt. |
| `const` | delegated to jsonschema | Kontrola konštantnej hodnoty. |
| `pattern` | delegated to jsonschema | Štandardná regex validácia. |
| `format` | delegated to jsonschema | Používa sa `FormatChecker` pre `date`, `date-time`, `uri`. |
| `minimum` | delegated to jsonschema | Štandardná numerická validácia. |
| `maximum` | delegated to jsonschema | Štandardná numerická validácia. |
| `minLength` | delegated to jsonschema | Štandardná textová validácia. |
| `minItems` | delegated to jsonschema | Štandardná validácia polí. |
| `uniqueItems` | delegated to jsonschema | Štandardná validácia jedinečnosti položiek. |
| `allOf` | delegated to jsonschema | Štandardná kompozícia schém. |
| `anyOf` | delegated to jsonschema | Štandardná kompozícia schém. |
| `oneOf` | delegated to jsonschema | Štandardná kompozícia schém. |
| `if / then / else` | delegated to jsonschema | Štandardná podmienená validácia. |

## 4. EOS aplikačná validácia

Tieto pravidlá zostávajú mimo JSON Schema validátora:

- `Draft` záznam môže mať prázdne `sourceLinks`.
- `Review` alebo `Approved` záznam s overiteľnými tvrdeniami musí mať `sourceLinks`.
- `SourceLink.sourceReferenceId` musí mať formát `SRC-xxxxxx`.
- Základná hierarchická konzistencia ID sa kontroluje pre budúce job-owned entity.
- `DocumentRecord` nesmie zamieňať `schemaVersion` a `documentVersion`.
- Budúca referenčná integrita medzi existujúcimi záznamami zostáva aplikačné pravidlo.

## 5. Známe obmedzenia

Aktuálna vrstva závisí od dostupnosti runtime závislosti `jsonschema`.

Ak závislosť nie je nainštalovaná:

- integračné testy JSON Schema validácie sú blokované,
- validácia záznamov sa nesmie reportovať ako úspešná,
- používateľ musí nainštalovať projekt podľa `pyproject.toml`.

EOS stále nekontroluje:

- pravdivosť technických tvrdení,
- existenciu reálnych zdrojových záznamov,
- platnosť externých noriem,
- obchodnú správnosť údajov,
- databázovú referenčnú integritu.

## 6. Súvisiace dokumenty

- `EOS-006_Data_Validation_Standard.md`
- `ADR-0013_Use_a_standards_compliant_JSON_Schema_validator.md`

## 7. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-07-14 | 0.1 | 0 | Codex | Initial draft for Phase 0.2A.1 |
| 2026-07-14 | 0.1 | 1 | Codex | Phase 0.2A.2: aktualizácia po integrácii `jsonschema` a presun JSON Schema schopností na štandardný validátor |

