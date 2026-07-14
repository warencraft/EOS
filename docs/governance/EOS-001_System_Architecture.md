# EOS-001 - Architektúra systému EOS

**Project:** EOS - Engineering Operating System  
**Document ID:** EOS-001  
**Version:** 0.1  
**Revision:** 1  
**Status:** Draft  
**Author:** Chief Engineering Knowledge Architect + Codex  
**Last update:** 2026-07-13  
**Document basis:** Internal governance decision  

---

## 1. Účel

Tento dokument definuje základnú architektúru systému EOS vo fáze 0.1. Cieľom je určiť hranice systému, zodpovednosti modulov, povolené závislosti a pravidlá toku informácií.

Dokument rešpektuje manifest `EOS-000` a neobsahuje konkrétne strojárske hodnoty.

## 2. Hranice systému

EOS je interný znalostný a rozhodovací systém pre strojársku prax, výrobnú technológiu a prípravu cenových ponúk.

EOS vo fáze 0.1 zahŕňa:

- riadenú dokumentáciu,
- prázdne dátové kontrakty,
- pravidlá identifikácie a verziovania,
- pravidlá pre budúce databázy,
- pravidlá pre budúce kalkulátory,
- šablóny dokumentov a rozhodnutí.

EOS vo fáze 0.1 nezahŕňa:

- používateľské rozhranie,
- databázový server,
- reálne materiálové alebo technologické hodnoty,
- kalkulačnú logiku,
- automatické odhady času alebo ceny,
- integráciu s ERP, PDM alebo PLM systémom.

## 3. Hlavné moduly

### 3.1 `docs/`

Riadená projektová a technická dokumentácia. Obsahuje governance dokumenty, metodiky, štandardy a budúci manuál.

Zodpovednosť:

- popisovať pravidlá,
- dokumentovať rozhodnutia,
- oddeľovať fakty, odporúčania a otvorené otázky,
- odkazovať na autoritatívne dátové záznamy.

### 3.2 `data/`

Budúce úložisko znalostných záznamov vo formáte kompatibilnom s JSON.

Zodpovednosť:

- niesť znalosti,
- ukladať entity s ID, revíziou a väzbami na zdroje,
- umožniť neskoršiu migráciu do SQLite alebo PostgreSQL.

### 3.3 `schemas/`

Kontrakty dátových entít.

Zodpovednosť:

- definovať povinné a nepovinné polia,
- validovať štruktúru dát,
- oddeliť dátový model od implementácie.

### 3.4 `calculators/`

Budúci priestor pre výpočtový kód.

Zodpovednosť:

- počítať nad vstupnými dátami,
- nepoužívať hardcoded strojárske hodnoty,
- byť testovateľný a modulárny.

Vo fáze 0.1 sa sem nepridáva žiadna kalkulačná logika.

### 3.5 `templates/`

Šablóny dokumentov, formulárov a záznamov.

Zodpovednosť:

- zabezpečiť jednotnú štruktúru výstupov,
- podporiť spätnú dohľadateľnosť,
- nepôsobiť ako zdroj technických hodnôt.

### 3.6 `scripts/`

Pomocné skripty pre validáciu, exporty a údržbu.

Vo fáze 0.1 sa nepridávajú skripty bez jasnej potreby.

### 3.7 `tests/`

Budúce testy dátových kontraktov, kalkulátorov a pravidiel.

### 3.8 `exports/`

Výstupy generované zo systému. Exporty nie sú autoritatívnym zdrojom znalostí.

### 3.9 `assets/`

Podporné súbory, obrázky, diagramy a statické materiály.

### 3.10 `adr/`

Architektonické rozhodnutia. Každá významná zmena architektúry musí mať ADR.

## 4. Povolené závislosti

Povolený smer závislostí:

1. `docs/` môže odkazovať na `data/`, `schemas/`, `adr/` a `templates/`.
2. `schemas/` definuje tvar záznamov pre `data/`.
3. `data/` musí rešpektovať `schemas/`.
4. `calculators/` môžu čítať validované dáta z `data/`.
5. `tests/` môžu overovať `schemas/`, `data/`, `calculators/` a `scripts/`.
6. `exports/` môžu vzniknúť z `docs/`, `data/` a `templates/`.

Zakázané závislosti:

- `data/` nesmie závisieť od kalkulačného kódu,
- `schemas/` nesmú obsahovať konkrétne strojárske hodnoty,
- `calculators/` nesmú byť autoritatívnym zdrojom znalostí,
- `exports/` nesmú byť primárnym miestom úprav.

## 5. Tok informácií

Základný tok informácií:

1. Podklad alebo skúsenosť sa zaznamená ako zdroj.
2. Znalosť sa uloží do príslušnej entity v `data/`.
3. Štruktúra entity sa overí podľa `schemas/`.
4. Dokumentácia v `docs/` na záznam odkazuje.
5. Budúci kalkulátor použije validované dáta ako vstup.
6. Výsledok sa môže exportovať do `exports/`.

## 6. Dokumentácia, databáza a kalkulačný kód

Dokumentácia vysvetľuje pravidlá, kontext a rozhodnutia.

Databáza nesie znalosti, zdroje, hodnoty, väzby a revízie.

Kalkulačný kód počíta nad dátami, ale nevlastní technické znalosti.

Princíp:

**Kód počíta. Databáza nesie znalosti. Dokumentácia vysvetľuje.**

## 7. Migrácia JSON na databázový systém

Počiatočné dátové záznamy musia byť kompatibilné s JSON.

Každá entita má mať:

- stabilné `id`,
- `schemaVersion`,
- `recordVersion`,
- `revision`,
- `status`,
- `sourceLinks`,
- časové metadáta,
- jasné väzby na iné entity cez ID.

Tým sa zachová možnosť neskoršej migrácie do SQLite alebo PostgreSQL bez zmeny významu dát.

## 8. Bezpečnostné a validačné hranice

EOS nesmie automaticky považovať vstupné údaje za pravdivé.

Validačné hranice:

- kontrola povinných polí,
- kontrola formátu ID,
- kontrola väzieb na zdroje a zdrojovej klasifikácie technických tvrdení,
- kontrola stavu záznamu,
- kontrola jednotiek a textových polí,
- oddelenie interných štandardov EOS od externých normatívnych referencií,
- oddelenie noriem od odporúčaní.

Bezpečnostné hranice:

- bez overenia sa nesmú publikovať technické hodnoty ako záväzné,
- automatické výstupy musia byť označené ako návrh, kým nie sú schválené,
- historická zákazka nesmie nahrádzať normu.

## 9. Mimo rozsahu fázy 0.1

Mimo rozsahu sú:

- výpočty,
- používateľské rozhranie,
- import výkresov,
- optické alebo AI čítanie výkresovej dokumentácie,
- cenotvorba,
- databázový server,
- napojenie na externé systémy,
- konkrétne materiálové, strojové alebo technologické hodnoty.

## 10. Súvisiace dokumenty

- `EOS-000_Development_Manifesto.md`
- `EOS-002_Documentation_Standard.md`
- `EOS-003_Identification_and_Versioning.md`
- `EOS-004_Core_Data_Model.md`
- `ADR-0002_Use_JSON_compatible_schemas_as_initial_data_contract.md`
- `ADR-0003_Separate_engineering_knowledge_from_calculation_code.md`
- `ADR-0005_Separate_internal_EOS_standards_from_external_normative_references.md`
- `ADR-0006_Treat_source_references_as_first_class_entities.md`
- `ADR-0007_Separate_schema_version_from_record_version_and_revision.md`

## 11. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-07-13 | 0.1 | 0 | Chief Engineering Knowledge Architect + Codex | Initial draft |
| 2026-07-13 | 0.1 | 1 | Codex | Governance Alignment 0.1.1: zosúladenie dokumentu s `Document basis`, `sourceLinks`, `schemaVersion`, `recordVersion` a oddelením interných štandardov EOS od externých normatívnych referencií |
