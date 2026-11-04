# CDR-0002 - ValueRange Contract

Project: EOS – Engineering Operating System

Contract Review ID: CDR-0002

Contract: ValueRange

Version: 0.1

Revision: 0

Status: Review

Document basis: Accepted EOS architecture

## 1. Purpose

Tento dokument definuje Knowledge Core Contract pre hodnotový objekt `ValueRange`.

`ValueRange` predstavuje jednorozmerný numerický interval s jedným autoritatívnym identifikátorom jednotky. Je určený ako opakovane použiteľná vnorená štruktúra pre budúce znalostné kontrakty, ktoré potrebujú vyjadriť rozsah, nie jednu skalárnu hodnotu.

## 2. Scope

Kontrakt pokrýva iba:

- voliteľnú dolnú hranicu `minValue`,
- voliteľnú hornú hranicu `maxValue`,
- povinný spoločný `unitId`,
- voliteľnú inkluzivitu dolnej hranice `lowerInclusive`,
- voliteľnú inkluzivitu hornej hranice `upperInclusive`,
- voliteľné lokálne `notes`,
- zákaz neznámych polí,
- zákaz metadát entít a lifecycle polí.

Aspoň jedna hranica musí byť prítomná.

## 3. Non-goals

Tento kontrakt nedefinuje:

- menovitú hodnotu s toleranciou,
- neistotu merania,
- rozlíšenie merania,
- presnosť merania,
- štatistickú distribúciu,
- viac disjunktných intervalov,
- zoznam povolených hodnôt,
- podmienky platnosti,
- zdrojovú evidenciu,
- význam vlastnosti,
- stav overenia,
- prevod jednotiek,
- zobrazovacie formátovanie,
- Unit Catalog,
- konkrétne jednotky,
- konkrétne technické, materiálové, výrobné alebo obchodné dáta.

Tieto významy patria do budúcich kontraktov alebo vrstiev, napríklad `MeasurementQuality`, `Condition`, `PropertyRecord`, `SourceLink`, Unit Catalog alebo aplikačná logika.

## 4. Dependencies

Kontrakt závisí od:

- JSON Schema Draft 2020-12,
- centrálneho registra schém EOS,
- `schemas/common/identifiers.schema.json#/$defs/UNT`,
- budúceho Unit Catalog modelu.

Unit Catalog ešte nie je implementovaný. `unitId` sa preto v tejto fáze overuje iba štrukturálne.

## 5. Field Model

### minValue

Voliteľné pole.

Typ: JSON number.

Význam: numerická dolná hranica intervalu bez doménového minima.

### maxValue

Voliteľné pole.

Typ: JSON number.

Význam: numerická horná hranica intervalu bez doménového maxima.

### unitId

Povinné pole.

Typ: string.

Formát: `UNT-xxxxxx`.

Význam: spoločný odkaz na budúcu autoritatívnu jednotku pre všetky numerické hranice rozsahu.

### lowerInclusive

Voliteľné pole.

Typ: boolean.

Význam: určuje, či je dolná hranica súčasťou intervalu. Je významové iba vtedy, keď existuje `minValue`. Ak je vynechané, sémantická predvolená hodnota je `true`; JSON Schema predvolená hodnota sa nepoužíva ako mutácia dát.

### upperInclusive

Voliteľné pole.

Typ: boolean.

Význam: určuje, či je horná hranica súčasťou intervalu. Je významové iba vtedy, keď existuje `maxValue`. Ak je vynechané, sémantická predvolená hodnota je `true`; JSON Schema predvolená hodnota sa nepoužíva ako mutácia dát.

### notes

Voliteľné pole.

Typ: string.

Význam: lokálna poznámka k použitiu hodnotového objektu v rodičovskom kontexte.

`notes` nesmie niesť význam jednotky, toleranciu, neistotu, podmienky platnosti, zdrojovú citáciu, konverznú logiku ani technickú interpretáciu hodnoty.

## 6. Invariants

| Invariant | Validation |
| --- | --- |
| `unitId` je vždy prítomný. | JSON Schema structural validation |
| Aspoň jedna hranica je prítomná. | JSON Schema structural validation |
| Ak existujú obe hranice, `minValue <= maxValue`. | EOS application validation |
| `lowerInclusive` nesmie byť uvedené bez `minValue`. | JSON Schema structural validation and EOS application validation |
| `upperInclusive` nesmie byť uvedené bez `maxValue`. | JSON Schema structural validation and EOS application validation |
| Numerické polia musia byť JSON numbers. | JSON Schema structural validation |
| `NaN` a `Infinity` nie sú platné hodnoty. | JSON syntax and EOS application validation |
| Neznáme polia sú odmietnuté. | JSON Schema structural validation |
| Obe hranice používajú rovnaký `unitId`. | Guaranteed by field model |
| `ValueRange` neobsahuje lifecycle ani entity metadata. | JSON Schema structural validation |

## 7. Structural Validation

Štrukturálna validácia vyžaduje:

- objekt typu `object`,
- povinné `unitId`,
- aspoň jedno z polí `minValue` alebo `maxValue`,
- `minValue` a `maxValue` ako JSON number, ak existujú,
- `unitId` podľa centrálneho vzoru `UNT-xxxxxx`,
- `lowerInclusive` a `upperInclusive` ako boolean, ak existujú,
- `notes` ako neprázdny string, ak existuje,
- `lowerInclusive` iba spolu s `minValue`,
- `upperInclusive` iba spolu s `maxValue`,
- `additionalProperties: false`.

Štrukturálna schéma neporovnáva `minValue` a `maxValue`.

## 8. Application Validation

EOS aplikačná validácia dopĺňa:

- odmietnutie obrátených hraníc, keď `minValue > maxValue`,
- odmietnutie `lowerInclusive` bez `minValue`,
- odmietnutie `upperInclusive` bez `maxValue`,
- odmietnutie nekonečných alebo nečíselných numerických hodnôt.

Referenčná existencia `unitId` bude kontrolovaná až po implementácii Unit Catalog.

## 9. Valid Examples

Uzavretý rozsah:

```json
{
  "minValue": 1,
  "maxValue": 5,
  "unitId": "UNT-000001",
  "lowerInclusive": true,
  "upperInclusive": true
}
```

Otvorený rozsah:

```json
{
  "minValue": 1,
  "maxValue": 5,
  "unitId": "UNT-000002",
  "lowerInclusive": false,
  "upperInclusive": false
}
```

Dolne ohraničený rozsah:

```json
{
  "minValue": 0,
  "unitId": "UNT-000004"
}
```

## 10. Invalid Examples

Chýbajúci `unitId`:

```json
{
  "minValue": 1,
  "maxValue": 5
}
```

Žiadna hranica:

```json
{
  "unitId": "UNT-000001"
}
```

Obrátené hranice:

```json
{
  "minValue": 5,
  "maxValue": 1,
  "unitId": "UNT-000001"
}
```

Zakázané metadáta entity:

```json
{
  "minValue": 1,
  "maxValue": 5,
  "unitId": "UNT-000001",
  "id": "RNG-000001"
}
```

## 11. Compatibility Considerations

`ValueRange` je kompatibilný s prijatou architektúrou EOS, pretože:

- je value object bez globálnej identity,
- používa jeden spoločný `unitId`,
- nevkladá dve samostatné `Quantity` hranice,
- nezavádza lifecycle mimo rodičovského objektu,
- nezavádza zdrojové odkazy ani stav overenia,
- necháva referenčnú existenciu jednotky budúcemu Unit Catalog,
- dá sa použiť ako vnorená štruktúra v PostgreSQL, Graph DB, REST API a AI vrstve.

`Quantity` reprezentuje jednu skalárnu numerickú hodnotu a jeden `unitId`. `ValueRange` reprezentuje jeden interval a jeden `unitId`.

## 12. Known Limitations

- Unit Catalog ešte neexistuje.
- `unitId` sa overuje iba štrukturálne.
- Kompatibilita jednotky s významom vlastnosti nie je súčasťou tohto kontraktu.
- Rozsah nepodporuje viac disjunktných intervalov.
- Rozsah neobsahuje toleranciu, neistotu ani kvalitu merania.
- Sémantická predvolená inkluzivita sa nedopĺňa do dát.

## 13. Acceptance Criteria

Kontrakt je pripravený na review, keď:

- existuje JSON Schema pre `ValueRange`,
- schéma používa Draft 2020-12,
- schéma je dostupná cez centrálny schema index,
- `unitId` používa centrálny vzor `UNT-xxxxxx`,
- platné fixture záznamy prejdú validáciou,
- neplatné fixture záznamy zlyhajú validáciou,
- obrátené hranice zlyhajú ako aplikačná validácia,
- inkluzivita bez príslušnej hranice je odmietnutá,
- neznáme polia a entity metadata sú odmietnuté,
- nevznikli konkrétne jednotky ani technické dáta.

## 14. Change History

| Revision | Date | Change |
| --- | --- | --- |
| 0 | 2026-08-01 | Initial ValueRange contract draft for Phase 0.2B.1.2. |
