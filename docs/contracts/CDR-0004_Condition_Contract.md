# CDR-0004 - Condition Contract

Project: EOS – Engineering Operating System

Contract Review ID: CDR-0004

Contract: Condition

Version: 0.1

Revision: 0

Status: Review

Document basis: Accepted EOS architecture

## 1. Purpose

Tento dokument definuje Knowledge Core Contract pre hodnotový objekt `Condition`.

`Condition` opisuje kontext, okolnosť, hranicu alebo stav, za ktorých má technické tvrdenie, vlastnosť, pozorovanie alebo schopnosť určený význam. Je to lokálny kvalifikátor významu, nie samostatné tvrdenie.

## 2. Scope

Rozsah kontraktu je minimálny a implementačný:

- zaviesť serializačný kontrakt pre `Condition`,
- potvrdiť `Condition` ako immutable value object,
- použiť centrálny identifikátor `CND-xxxxxx` pre budúci Condition Type Catalog význam,
- umožniť presne jednu hodnotovú formu podmienky,
- zachovať `Quantity` a `ValueRange` ako vnorené opakovane použiteľné kontrakty,
- odmietnuť entity metadata, lifecycle metadata, zdroje, verifikáciu a property alebo observation identitu.

## 3. Non-goals

Tento kontrakt nezavádza:

- Condition Type Catalog,
- pravidlá vyhodnocovania splnenia podmienky,
- porovnávač podmienok,
- dimenzionálnu kompatibilitu,
- jednotkové konverzie,
- výrobné alebo konštrukčné tolerancie,
- časovú platnosť,
- workflow stav,
- zdrojové dôkazy,
- samostatnú entitu `Condition`.

## 4. Terminology

`Condition` je immutable value object vlastnený rodičovským objektom.

`conditionTypeId` je odkaz na budúci Condition Type Catalog Entry. Nie je identitou konkrétnej vnorenej podmienky.

`evaluationMode` určuje, ako má rodičovský objekt s podmienkou významovo zaobchádzať. Nevykonáva samotné vyhodnotenie.

Hodnotová forma je jedno z polí `quantity`, `valueRange`, `textValue`, `booleanValue` alebo `referenceId`.

## 5. Dependencies

Kontrakt závisí od:

- `EOS-003_Identification_and_Versioning.md` pre prefix `CND-xxxxxx`,
- `RFC-0001_Engineering_Property_Model.md`,
- `RFC-0002_Engineering_Object_Taxonomy.md`,
- `RFC-0003_EOS_Engineering_Glossary.md`,
- `CDR-0001_Quantity_Contract.md`,
- `CDR-0002_ValueRange_Contract.md`,
- `schemas/common/identifiers.schema.json`,
- `schemas/knowledge-core/quantity.schema.json`,
- `schemas/knowledge-core/value-range.schema.json`.

Nezávisí od Unit Catalog ani Condition Type Catalog záznamov, pretože tieto katalógy ešte nie sú implementované.

## 6. Field model

| Field | Required | Type | Meaning |
| --- | --- | --- | --- |
| `conditionTypeId` | Yes | string | Budúci Condition Type Catalog význam vo formáte `CND-xxxxxx`. |
| `evaluationMode` | Yes | enum | Spôsob použitia podmienky rodičovským objektom. |
| `quantity` | Conditional | `Quantity` | Jedna skalárna hodnota s jednotkou. |
| `valueRange` | Conditional | `ValueRange` | Jeden interval s jednotkou. |
| `textValue` | Conditional | string | Krátka textová hodnota podmienky. |
| `booleanValue` | Conditional | boolean | Pravdivostná hodnota podmienky. |
| `referenceId` | Conditional | string | Odkaz na existujúci podporovaný EOS identifikátor. |
| `notes` | No | string | Doplnková lokálna poznámka. |

Presne jedna hodnotová forma musí byť prítomná. `notes` nie je hodnotová forma.

## 7. Value forms

`quantity` používa `Quantity` bez duplikovania jeho štruktúry.

`valueRange` používa `ValueRange` bez duplikovania jeho štruktúry.

`textValue` musí byť neprázdny string. Nesmie obchádzať budúce katalógy, niesť viacero podmienok ani zdrojové citácie.

`booleanValue` je JSON boolean.

`referenceId` je neprázdny odkaz na existujúce centrálne podporované EOS identifikátory. Kontrakt nezavádza univerzálny prefix a nekontroluje existenciu cieľového záznamu.

## 8. Invariants

| Invariant | Validation layer |
| --- | --- |
| `Condition` je objekt. | JSON Schema structural validation |
| Neznáme polia sú odmietnuté. | JSON Schema structural validation |
| `conditionTypeId` je povinné. | JSON Schema structural validation |
| `conditionTypeId` používa `CND-xxxxxx`. | JSON Schema structural validation |
| `evaluationMode` je povinné. | JSON Schema structural validation |
| `evaluationMode` je jedna zo schválených hodnôt. | JSON Schema structural validation |
| Presne jedna hodnotová forma je prítomná. | JSON Schema structural validation |
| `notes` samotné nestačí. | JSON Schema structural validation |
| `quantity` je validný `Quantity`. | JSON Schema structural validation |
| `valueRange` je validný `ValueRange`. | JSON Schema structural validation |
| `textValue` je neprázdny string. | JSON Schema structural validation |
| `referenceId` je podporovaný centrálny EOS identifikátor. | JSON Schema structural validation |
| Entity metadata nie sú povolené. | JSON Schema structural validation |
| Lifecycle metadata nie sú povolené. | JSON Schema structural validation |
| `sourceLinks` nie sú povolené. | JSON Schema structural validation |
| `verificationStatus` nie je povolený. | JSON Schema structural validation |
| `propertyId` a `observationId` nie sú povolené. | JSON Schema structural validation |
| `Condition` nevykonáva jednotkové konverzie. | Contract invariant |
| `Condition` sa sama nevyhodnocuje. | Contract invariant |
| Vyhodnotenie použiteľnosti je odložené. | Future application validation |

## 9. Structural validation

JSON Schema Draft 2020-12 kontroluje:

- typ objektu,
- povinné polia,
- `CND-xxxxxx` cez centrálny `$ref`,
- `evaluationMode` enum,
- presne jednu hodnotovú formu cez `oneOf`,
- vnorený `Quantity` a `ValueRange` cez `$ref`,
- neprázdne textové a referenčné hodnoty,
- `additionalProperties: false`.

## 10. Application validation

V tomto míľniku nie je potrebné nové aplikačné pravidlo pre `Condition`.

Odložené aplikačné kontroly:

- existencia `conditionTypeId` v budúcom Condition Type Catalog,
- kompatibilita hodnotovej formy s typom podmienky,
- dimenzionálna kompatibilita `quantity` alebo `valueRange`,
- vyhodnotenie, či je podmienka splnená,
- pravidlá dedenia a kombinácie podmienok v rodičovskom objekte,
- referenčná integrita `referenceId`.

## 11. Valid examples

Platné príklady sú fiktívne a netechnické:

```json
{
  "conditionTypeId": "CND-000001",
  "evaluationMode": "mandatory",
  "quantity": {
    "value": 1,
    "unitId": "UNT-000001"
  }
}
```

```json
{
  "conditionTypeId": "CND-000002",
  "evaluationMode": "descriptive",
  "textValue": "fictional context"
}
```

## 12. Invalid examples

Neplatné:

```json
{
  "conditionTypeId": "CND-000001",
  "evaluationMode": "mandatory",
  "quantity": {
    "value": 1,
    "unitId": "UNT-000001"
  },
  "textValue": "second value form"
}
```

Neplatné:

```json
{
  "conditionTypeId": "CND-000001",
  "evaluationMode": "descriptive",
  "notes": "notes alone are not condition data"
}
```

## 13. Compatibility considerations

`Condition` je kompatibilný s prijatou architektúrou EOS, pretože:

- je value object bez vlastného ID,
- používa `conditionTypeId` iba ako odkaz na budúci katalógový význam,
- neimplementuje Condition Type Catalog,
- neobsahuje zdroje ani verifikačný workflow,
- neobsahuje vlastnú hodnotu merania ani vlastnosť,
- opakovane používa `Quantity` a `ValueRange`.

## 14. Known limitations

- `conditionTypeId` zatiaľ nemá autoritatívny katalógový záznam.
- `referenceId` je obmedzený na existujúce centrálne podporované EOS ID formáty.
- Kontrakt nevie posúdiť, či je zvolená hodnotová forma vhodná pre daný typ podmienky.
- Kontrakt nevie vyhodnotiť, či je podmienka splnená.

## 15. Deferred concepts

Odložené sú:

- Condition Type Catalog,
- Condition evaluation engine,
- condition applicability rules,
- condition composition,
- time validity,
- priority,
- method-specific comparison,
- dimension compatibility,
- relationship to future `PropertyRecord` and `Observation` semantics.

## 16. Acceptance criteria

Míľnik je prijateľný, ak:

- existuje tento contract review dokument,
- existuje JSON Schema pre `Condition`,
- `CND` je centralizovaný identifikátor,
- `Condition` je dostupný cez `schemas/index.schema.json`,
- platné fixture prejdú,
- neplatné fixture zlyhajú,
- existujú regresné testy pre `Quantity`, `ValueRange` a `MeasurementQuality`,
- nevznikne Condition Type Catalog ani iný nesúvisiaci Knowledge Core Contract.

## 17. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-08-01 | 0.1 | 0 | Codex | Initial Condition contract draft for Phase 0.2B.1.4. |
