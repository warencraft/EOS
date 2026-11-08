---
name: eos-schema-change
description: Postup pre novú entitu, katalóg alebo zmenu JSON schémy v EOS (vzor Machine, EngineeringItem). Použi pri každej úprave v schemas/ alebo pri implementácii fázy podľa CDR.
---

# Zmena alebo nová schéma v EOS

Vzorové implementácie: Machine (CDR-0021 → CDR-0023, PR #8) a EngineeringItem (CDR-0026 §19 → CDR-0027, PR #12). Pri pochybnosti sa pozri, ktoré súbory menil ich commit (`git show --stat 23e41dc`, `git show --stat c579660`).

## 0. Smie sa to robiť?

- Fázu musí používateľ explicitne zadať; je v hornej sekcii `BACKLOG.md`.
- Pre novú entitu musí existovať prijatý pre-design CDR so **zmrazeným zoznamom polí** (napr. CDR-0021 §64.7–64.8, CDR-0026 §19). Rozsah, povinné a voliteľné polia, vlastníctvo a validačná hranica sa berú **iba** z neho.
- Čo CDR odkladá, sa neimplementuje. Ani „na skúšku“. Odložené polia idú do zoznamu `deferred` v tabuľke neplatných prípadov.
- Doménové otázky (čo ID identifikuje, kedy vzniká nové) rozhoduje Chief Engineering Knowledge Architect. Ak CDR odpoveď nemá, zastav sa a opýtaj sa.

## 1. Identifikátor

- Formát ID patrí iba do `schemas/common/identifiers.schema.json` (ADR-0012), napr. `EIT` = `^EIT-[0-9]{4}$`.
- Prefix musí byť v tabuľke `docs/governance/EOS-003_Identification_and_Versioning.md`. Implementáciou kontraktu sa jeho stav mení z `Candidate` na `Active`; iné kandidátske prefixy (napr. `ERL`) ostávajú `Candidate`.
- Nemeň existujúce množiny povolených subjektov (napr. Observation `subjectId`), ak to CDR výslovne nevyžaduje.

## 2. Schéma

- Súbor `schemas/entities/<kebab-name>.schema.json`; hlavička `"$schema": "https://json-schema.org/draft/2020-12/schema"`, `"$id": "https://eos.local/schemas/entities/<kebab-name>.schema.json"`.
- Uzavretý koreň `"additionalProperties": false` (ADR-0010).
- Povinné common metadata (`id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `createdAt`, `createdBy`, `updatedAt`, `updatedBy`, `sourceLinks`, `changeSummary`) cez `$ref` na `schemas/common/metadata.schema.json`; `id` cez `$ref` na centrálny identifikátor. `notes` iba ak ho CDR povoľuje. **Nekopíruj ich.** Vzor: `schemas/entities/machine.schema.json`.
- Vnorené kontrakty cez `$ref`: `knowledge-core/classification.schema.json`, `knowledge-core/property-record.schema.json`.
- Každé pole má `description` po anglicky a opisuje aj to, čím pole **nie je**.
- Objaviteľnosť: `$defs.<camelName>` v `schemas/index.schema.json`. Novú koreňovú kolekciu iba ak ju CDR určuje.

## 3. Validátor

- Štruktúrne pravidlá patria do schémy; významové a referenčné do `scripts/validation/validator.py`, kontext katalógov do `catalog_context.py`.
- Nová entita sa iba **registruje** do existujúcich ciest: konštanta `<NAME>_SCHEMA_ID`, mapa vnorených kontraktov (properties, classifications), množina pre koreňové `sourceLinks` a množiny pre katalógovú kontrolu. Hľadaj existujúce výskyty `MACHINE_SCHEMA_ID` a `ENGINEERING_ITEM_SCHEMA_ID`.
- Nepíš paralelnú logiku pre PropertyRecord, Classification ani SourceLink. Nová diagnostika iba ak ju CDR vyžaduje.

## 4. Fixtúry a testy

Postupuj podľa skillu `eos-write-tests`:

- dve platné fixtúry `tests/fixtures/valid/entities/<family>-minimal-draft-valid.json` a `<family>-populated-source-links-valid.json`,
- tabuľka `tests/fixtures/invalid-cases/<family>.json` (`cases` s presným `expect`, `deferred` so zoznamom odložených polí),
- riadok v `ENTITY_PROFILES` v `tests/test_entity_profiles.py`,
- `tests/test_<entity>_validation.py`, ktorý dedí `OwnedClassificationChecks` alebo `OwnedClaimChecks` z `tests/owned_claim_checks.py` a pridáva iba pravidlá špecifické pre entitu,
- skúšky citlivosti v pamäti a celá sada (`eos-run-tests`).

## 5. Dokumentácia

Aktualizuj:

- `schemas/README.md` a pri zmene validátora `scripts/README.md`,
- `docs/governance/EOS-003_Identification_and_Versioning.md` pri novom prefixe,
- sekciu v `tests/README.md` (tabuľka `Súbor | Overenie`, počet testov),
- `CHANGELOG.md`, hornú sekciu `ROADMAP.md` a `BACKLOG.md`, `docs/INDEX.md`.

## 6. Uzavretie

- Implementácia sama nie je `COMPLETE`. Stav `COMPLETE` určuje integračné uzatváracie CDR s ďalším voľným číslom (vzor CDR-0023, CDR-0027): rozsah a identita, posúdenie kontraktu, presná diagnostika kľúčových scenárov, skúšky citlivosti, počet testov, schém a `$ref` a governance body.
- Uzatváracie CDR môže byť v tom istom pull requeste. Rozlišuj „COMPLETE lokálne, čaká na publikovanie“ od stavu po zlúčení do `main`.

## 7. Na záver

Spusti skill `eos-governance-check`.
