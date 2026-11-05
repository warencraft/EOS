---
name: eos-schema-change
description: Postup pre novú entitu, katalóg alebo zmenu JSON schémy v EOS (napr. Machine). Použi pri každej úprave v schemas/ alebo pri implementácii fázy podľa CDR.
---

# Zmena alebo nová schéma v EOS

## 0. Smie sa to robiť?

- Fáza musí byť v hornej sekcii `BACKLOG.md` a používateľ ju musí explicitne zadať.
- Pre novú entitu musí existovať pre-design CDR so stavom `READY FOR IMPLEMENTATION`. Rozsah, povinné a voliteľné polia a validačná hranica sa berú **iba** z neho (napr. Machine: CDR-0021 §64.7 a §64.8).
- Čo CDR odkladá (deferred), sa neimplementuje. Ani „na skúšku“.

## 1. Schéma

- Súbor: `schemas/<oblasť>/<kebab-name>.schema.json` (oblasti: `common`, `knowledge-core`, `catalogs`, `entities`).
- Hlavička: `"$schema": "https://json-schema.org/draft/2020-12/schema"` a `"$id": "https://eos.local/schemas/<oblasť>/<názov>.schema.json"`.
- `"additionalProperties": false` (ADR-0010).
- Common metadata (`id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `createdAt/By`, `updatedAt/By`, `sourceLinks`, `changeSummary`, `notes`) cez `$ref` na `schemas/common/metadata.schema.json`. **Nekopíruj ich.** Vzor: `schemas/entities/material.schema.json`.
- Formát ID pridaj iba do `schemas/common/identifiers.schema.json` (ADR-0012). Prefix musí byť v tabuľke EOS-003.
- Každé pole má `description` po anglicky a opisuje aj to, čím pole **nie je**.
- Zaregistruj schému rovnako ako existujúce. Postup over v `scripts/validation/schema_loader.py`, `schemas/README.md` a `tests/validation_support.py`.

## 2. Validačné pravidlá

- Štrukturálne pravidlá patria do schémy. Významové a referenčné pravidlá patria do `scripts/validation/validator.py`, prípadne `catalog_context.py`.
- Znovu použi existujúce pravidlá (PropertyRecord, Classification, SourceLink). Nepíš paralelnú logiku.

## 3. Fixtúry a testy

Postupuj podľa skillu `eos-write-tests` a sekcie „Nová entita“ v `tests/README.md`:

- platné fixtúry `<family>-minimal-draft-valid.json` a `<family>-populated-source-links-valid.json` (+ iba tie, ktoré ukazujú odlišný tvar),
- tabuľka `tests/fixtures/invalid-cases/<family>.json` s blokom `deferred`,
- riadok v `ENTITY_PROFILES` v `tests/test_entity_profiles.py`,
- vlastný `tests/test_<entity>_validation.py` **iba** pre pravidlá nad rámec spoločného testu.

Potom spusti skill `eos-run-tests`.

## 4. Dokumentácia

Aktualizuj: `schemas/README.md`, `CHANGELOG.md`, hornú sekciu `ROADMAP.md`, `BACKLOG.md`, `docs/INDEX.md` a tabuľku súborov v `tests/README.md`. Stav fázy nastav na `IMPLEMENTED`, nie `COMPLETE`. COMPLETE prideľuje až samostatné closure review (CDR).

## 5. Na záver

Spusti skill `eos-governance-check`.
