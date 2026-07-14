# EOS-006 - Štandard validácie dát

**Project:** EOS - Engineering Operating System  
**Document ID:** EOS-006  
**Version:** 0.1  
**Revision:** 2  
**Status:** Draft  
**Author:** Chief Engineering Knowledge Architect + Codex  
**Last update:** 2026-07-14  
**Document basis:** Internal governance decision  

---

## 1. Účel

Tento dokument definuje základné pravidlá validácie dát vo fáze 0.2A. Cieľom je oddeliť syntaktickú validáciu dátového kontraktu od významovej validácie inžinierskeho obsahu.

## 2. Syntaktická validácia

Syntaktická validácia kontroluje, či JSON záznam zodpovedá schéme.

JSON Schema validátor `jsonschema.validators.Draft202012Validator` kontroluje najmä:

- existenciu povinných polí,
- dátové typy,
- formát identifikátorov,
- povolené enum hodnoty,
- základný formát dátumov,
- prítomnosť neznámych polí podľa `additionalProperties`,
- základný tvar `sourceLinks`.

Od fázy 0.2A.2 vykonáva štandardnú JSON Schema validáciu knižnica `jsonschema`.

Ak závislosť `jsonschema` nie je v runtime nainštalovaná, integračná validácia je blokovaná a nesmie byť reportovaná ako úspešná.

## 3. Významová validácia

Významová validácia kontroluje pravidlá, ktoré samotná JSON Schema nevie spoľahlivo posúdiť bez znalosti významu obsahu.

Aplikačná validačná vrstva kontroluje najmä:

- či `Review` alebo `Approved` záznam s overiteľným tvrdením obsahuje `sourceLinks`,
- či `SourceLink.sourceReferenceId` používa formát `SRC-xxxxxx`,
- základnú hierarchickú konzistenciu ID,
- zámenu `schemaVersion` a `documentVersion` pri `DocumentRecord`.

## 4. Čo sa zatiaľ nekontroluje

Vo fáze 0.2A sa zatiaľ nekontroluje:

- pravdivosť technických tvrdení,
- existencia reálnych zdrojových záznamov,
- platnosť externých noriem,
- úplnosť materiálových alebo technologických údajov,
- obchodná správnosť údajov,
- databázová referenčná integrita.

## 5. Hlásenie chýb

Validačná vrstva má hlásiť:

- cestu k chybnému poľu,
- stručný popis chyby,
- typ chyby, ak bude neskôr zavedený.

Vo fáze 0.2A sa používa jednoduchý zoznam chýb s cestou a textom.

## 6. Fail-fast verzus zber všetkých chýb

Pre dátové kontrakty EOS je preferovaný zber všetkých nájdených chýb v jednom behu validácie.

Fail-fast prístup sa môže použiť iba pri technickej chybe, ktorá znemožňuje pokračovanie, napríklad nečitateľný JSON súbor.

## 7. Pravidlá testovania schém

Každá základná schéma má mať minimálne:

- pozitívny test platného záznamu,
- negatívny test neplatného ID,
- negatívny test neplatného statusu alebo enum hodnoty,
- negatívny test chýbajúceho povinného poľa,
- negatívny test neznámeho poľa.

Testovacie fixtures nesmú obsahovať reálne strojárske hodnoty, výrobné časy, ceny, rezné podmienky ani normové tabuľky.

## 8. Súvisiace dokumenty

- `EOS-000_Development_Manifesto.md`
- `EOS-001_System_Architecture.md`
- `EOS-004_Core_Data_Model.md`
- `ADR-0009_Use_JSON_Schema_Draft_2020_12.md`
- `ADR-0010_Use_closed_schema_contracts_by_default.md`
- `ADR-0011_Use_Python_standard_library_validation_layer.md`
- `ADR-0012_Centralize_identifier_and_version_formats.md`
- `EOS-007_Validation_Capability_Matrix.md`
- `ADR-0013_Use_a_standards_compliant_JSON_Schema_validator.md`

## 9. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-07-13 | 0.1 | 0 | Chief Engineering Knowledge Architect + Codex | Initial draft for Phase 0.2A |
| 2026-07-14 | 0.1 | 1 | Codex | Phase 0.2A.1: spresnenie, že aktuálny validátor je subset Draft 2020-12 a nepodporované kľúčové slová používajú fail-closed správanie |
| 2026-07-14 | 0.1 | 2 | Codex | Phase 0.2A.2: integrácia štandardného validátora `jsonschema` pre Draft 2020-12 |
