# CHANGELOG

Všetky významné zmeny projektu EOS sa zaznamenávajú v tomto súbore.

## 0.2A.2 - 2026-07-14

Status: Draft

### Added

- Minimalistický `pyproject.toml` s riadenou závislosťou `jsonschema>=4.18.0`.
- Jednotný validačný chybový model s kategóriami `json_syntax`, `schema_definition`, `schema_validation`, `application_validation` a `reference_integrity`.
- Testy pripravené pre `allOf`, `oneOf`, `if/then/else`, `uniqueItems`, `maximum`, format checkery a cross-file `$ref`.

### Changed

- ADR-0013 zmenené zo `Proposed` na `Accepted`.
- Štrukturálna JSON Schema validácia migrovaná na `jsonschema.validators.Draft202012Validator`.
- Interná validačná vrstva ponechaná pre EOS aplikačné pravidlá.
- EOS-006 a EOS-007 aktualizované po integrácii štandardného validátora.
- Dokumentácia doplnená o postup vytvorenia virtuálneho prostredia, inštalácie projektu a spustenia `unittest`.
- `pyproject.toml` doplnený o explicitné package discovery pre `scripts*`, aby editable inštalácia nezahŕňala dokumentačné a dátové priečinky ako Python packages.
- Regresne opravené mapovanie `required` chýb na konkrétne pole a explicitné format checkery pre `date`, `date-time` a `uri`.

### Not Added

- Nebol pridaný `pytest`.
- Nebola začatá fáza 0.2B.
- Neboli pridané nové technické entity ani strojárske dáta.

## 0.2A.1 - 2026-07-14

Status: Draft

### Added

- `EOS-007_Validation_Capability_Matrix.md`.
- `ADR-0013_Use_a_standards_compliant_JSON_Schema_validator.md` so statusom `Proposed`.
- Auditné testy pre lokálne `$ref`, nepodporované schema keywordy, viac chýb a presné cesty k poliam.

### Changed

- Validačná vrstva teraz fail-closed hlási nepodporované alebo neznáme JSON Schema kľúčové slová.
- Dokumentácia validácie jasne uvádza, že aktuálny validátor nie je plná implementácia JSON Schema Draft 2020-12.

### Not Added

- Nebola pridaná externá validačná závislosť.
- Nebola začatá fáza 0.2B.

## 0.2A.0 - 2026-07-13

Status: Draft

### Added

- Modulárne JSON Schema kontrakty pre spoločné metadáta, identifikátory, `SourceLink`, `SourceReference`, `NormReference` a `DocumentRecord`.
- Centrálny schema index `schemas/index.schema.json`.
- Kompatibilitný vstup `schemas/core_entities.schema.json`.
- Minimálna Python validačná vrstva v `scripts/validation/`.
- Netechnické testovacie fixtures a `unittest` testy.
- Governance dokument `EOS-006_Data_Validation_Standard.md`.
- ADR-0009 až ADR-0012.

### Not Added

- Neboli pridané materiálové, technologické, strojové, nástrojové, dodávateľské ani zákazkové entity.
- Neboli pridané kalkulačky, UI, databázový server ani konkrétne strojárske dáta.

## 0.1.1 - 2026-07-13

Status: Completed / Approved

### Changed

- Normalizovaný `EOS-000` do slovenčiny s plnou diakritikou bez zmeny významu.
- Zvýšená revízia governance dokumentov `EOS-001` až `EOS-005` na `Revision 1` a doplnená `Change History`.
- Oddelený governance pôvod dokumentu od technickej zdrojovej klasifikácie `N`, `L`, `P`, `V`.
- Rozlíšené interné technické štandardy `STD-xxx` a externé normatívne referencie `NRM-xxxx`.
- Potvrdený `SourceReference` ako samostatná autoritatívna entita.
- Zavedený koncept `SourceLink` pre väzbu technického tvrdenia na zdroj.
- Spresnené spoločné metadáta entít: `schemaVersion`, `recordVersion`, `revision`, `sourceLinks` a `changeSummary`.
- Spresnené pravidlo, že `sourceLinks` môže byť prázdne v stave `Draft`, ale pri `Review` alebo `Approved` musí pokrývať overiteľné technické, výrobné, dodávateľské alebo obchodné tvrdenia.
- Spresnené oddelenie verzie riadeného dokumentu od verzie registračného záznamu `DocumentRecord`.
- Doplnené hierarchické ID pre entity vlastnené zákazkou.

### Added

- `ADR-0005` až `ADR-0008`.

### Not Added

- Neboli pridané detailné technické schémy jednotlivých entít.
- Neboli pridané kalkulačky, UI, databázový server ani konkrétne strojárske dáta.

## 0.1.0 - 2026-07-13

### Added

- Založená základná štruktúra repozitára.
- Pridaný manifest `EOS-000`.
- Pridané governance dokumenty `EOS-001` až `EOS-005`.
- Pridané prvé architektonické rozhodnutia `ADR-0001` až `ADR-0004`.
- Pridané pravidlá práce v `AGENTS.md`.

### Not Added

- Neboli pridané kalkulačky.
- Nebolo pridané používateľské rozhranie.
- Neboli pridané konkrétne strojárske hodnoty.
