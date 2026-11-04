# CDR-0003 - MeasurementQuality Contract

Project: EOS – Engineering Operating System

Contract Review ID: CDR-0003

Contract: MeasurementQuality

Version: 0.1

Revision: 0

Status: Review

Document basis: Accepted EOS architecture

## 1. Purpose

Tento dokument definuje Knowledge Core Contract pre hodnotový objekt `MeasurementQuality`.

`MeasurementQuality` opisuje vybrané metrologické charakteristiky alebo obmedzenia súvisiace s meranou, pozorovanou alebo reportovanou numerickou hodnotou. Neobsahuje samotnú meranú hodnotu.

## 2. Scope

Počiatočný kontrakt obsahuje iba:

- `uncertainty`,
- `resolution`,
- `confidenceLevel`,
- `notes`.

Aspoň jedno zo štruktúrovaných polí `uncertainty`, `resolution` alebo `confidenceLevel` musí byť prítomné. `notes` je iba podporný text a sám o sebe nestačí na platný objekt.

## 3. Non-goals

Tento kontrakt nedefinuje:

- meranú hodnotu,
- význam vlastnosti,
- výrobnú, konštrukčnú alebo akceptačnú toleranciu,
- požiadavkový model,
- podmienky platnosti,
- zdrojovú evidenciu,
- workflow overenia,
- metódu merania ako samostatnú entitu,
- prístroj,
- kalibračný záznam,
- jednotkové konverzie,
- pass/fail výsledok.

## 4. Terminology

`uncertainty` znamená deklarovanú neistotu merania, nie výrobnú toleranciu.

`resolution` znamená najmenší rozlíšiteľný krok meracieho systému alebo reportovaného výsledku, nie toleranciu.

`confidenceLevel` je normalizované číslo od 0 do 1 vrátane. Hodnota `0.95` znamená 95 percent confidence, ale sama o sebe nedokazuje štatistickú platnosť metódy.

Produktová tolerancia je požiadavka alebo akceptačný limit produktu. Nie je `MeasurementQuality` a je odložená do budúceho requirement/tolerance kontraktu.

## 5. Dependencies

Kontrakt závisí od:

- JSON Schema Draft 2020-12,
- centrálneho registra schém EOS,
- `schemas/knowledge-core/quantity.schema.json`,
- budúceho rodičovského objektu, ktorý bude vlastniť `MeasurementQuality`.

`MeasurementQuality` nepoužíva root-level `unitId`. Jednotky sú nesené iba cez vnorené objekty `Quantity`.

## 6. Field Model

### uncertainty

Voliteľné pole.

Typ: `Quantity`.

Význam: deklarovaná neistota merania. `uncertainty.value` musí byť väčšie alebo rovné nule. Nula je povolená, ak ju rodičovský kontext dokáže významovo obhájiť.

### resolution

Voliteľné pole.

Typ: `Quantity`.

Význam: najmenší rozlíšiteľný krok meracieho systému alebo reportovaného výsledku. `resolution.value` musí byť striktne väčšie ako nula.

### confidenceLevel

Voliteľné pole.

Typ: JSON number.

Rozsah: `0 <= confidenceLevel <= 1`.

Význam: normalizovaná confidence informácia. Nezastupuje metódu ani zdroj.

### notes

Voliteľné pole.

Typ: string.

Význam: podporná poznámka. Nesmie obsahovať meranú hodnotu, toleranciu, zdrojovú citáciu, lifecycle stav ani náhradu dôkazu.

## 7. Invariants

| Invariant | Validation |
| --- | --- |
| `MeasurementQuality` je objekt. | JSON Schema structural validation |
| Neznáme polia sú odmietnuté. | JSON Schema structural validation |
| Aspoň jedno z `uncertainty`, `resolution`, `confidenceLevel` je prítomné. | JSON Schema structural validation |
| `notes` samotné nestačí na platný objekt. | JSON Schema structural validation |
| `uncertainty` je platný `Quantity`. | JSON Schema structural validation |
| `resolution` je platný `Quantity`. | JSON Schema structural validation |
| `uncertainty.value >= 0`. | EOS application validation |
| `resolution.value > 0`. | EOS application validation |
| `confidenceLevel` je od 0 do 1 vrátane. | JSON Schema structural validation |
| Entity metadata a lifecycle metadata sú zakázané. | JSON Schema structural validation |
| `sourceLinks` a `verificationStatus` sú zakázané. | JSON Schema structural validation |
| Tolerance polia sú zakázané. | JSON Schema structural validation |
| Jednotky sú iba vo vnorených `Quantity`. | JSON Schema structural validation |
| `NaN` a `Infinity` nie sú platné hodnoty. | JSON syntax and EOS application validation |

## 8. Structural Validation

Štrukturálna validácia vyžaduje:

- objekt typu `object`,
- `additionalProperties: false`,
- `uncertainty` a `resolution` cez `$ref` na `Quantity`,
- `confidenceLevel` ako JSON number v intervale 0 až 1 vrátane,
- aspoň jedno štruktúrované pole z `uncertainty`, `resolution`, `confidenceLevel`,
- `notes` ako neprázdny string, ak existuje.

## 9. Application Validation

EOS aplikačná validácia dopĺňa:

- `uncertainty.value` nesmie byť záporné,
- `resolution.value` musí byť väčšie ako nula.

Tieto pravidlá sa riešia aplikačne, aby sa neduplikovala ani nemenila všeobecná schéma `Quantity`.

## 10. Valid Examples

Neistota:

```json
{
  "uncertainty": {
    "value": 1,
    "unitId": "UNT-000201"
  }
}
```

Resolution:

```json
{
  "resolution": {
    "value": 0.1,
    "unitId": "UNT-000202"
  }
}
```

Confidence level:

```json
{
  "confidenceLevel": 0.95
}
```

## 11. Invalid Examples

Notes-only objekt:

```json
{
  "notes": "Insufficient by itself."
}
```

Záporná neistota:

```json
{
  "uncertainty": {
    "value": -1,
    "unitId": "UNT-000201"
  }
}
```

Tolerancia:

```json
{
  "tolerance": {
    "value": 1,
    "unitId": "UNT-000201"
  }
}
```

## 12. Compatibility Considerations

`Quantity` nesie jednu skalárnu hodnotu a `unitId`.

`ValueRange` nesie jeden interval a `unitId`.

`MeasurementQuality` opisuje vybrané metrologické charakteristiky súvisiace s hodnotou. Neobsahuje meranú hodnotu, nevkladá `ValueRange`, neidentifikuje property a nenesie zdroje.

Budúci `Observation` môže niesť `MeasurementQuality` ako súčasť evidence záznamu. Budúci `PropertyRecord` môže spájať property význam, hodnotu, podmienky, overenie a zdroje.

## 13. Known Limitations

- `accuracy` nie je prijaté pole.
- Repeatability a reproducibility nie sú implementované.
- Method reference, instrument a calibration reference nie sú implementované.
- Existencia Unit Catalog položiek sa nekontroluje.
- `confidenceLevel` nepreukazuje štatistickú platnosť bez metódy.

## 14. Deferred Concepts

Odložené koncepty:

- `accuracy`,
- `declaredError`,
- `maximumPermissibleError`,
- `repeatability`,
- `reproducibility`,
- `methodReference`,
- `instrumentId`,
- `calibrationReference`,
- `tolerance`,
- `upperTolerance`,
- `lowerTolerance`.

Tieto koncepty potrebujú samostatnú stabilizáciu významu, autority, jednotiek alebo lifecycle hraníc.

## 15. Acceptance Criteria

Kontrakt je pripravený na review, keď:

- existuje JSON Schema pre `MeasurementQuality`,
- schéma používa Draft 2020-12,
- schéma je dostupná cez centrálny schema index,
- vnorené `uncertainty` a `resolution` používajú `$ref` na `Quantity`,
- platné fixture záznamy prejdú validáciou,
- neplatné fixture záznamy zlyhajú validáciou,
- záporná neistota a nekladné rozlíšenie zlyhajú ako aplikačné pravidlá,
- notes-only objekt je neplatný,
- nevznikol tolerance, requirement, condition, property alebo observation kontrakt.

## 16. Change History

| Revision | Date | Change |
| --- | --- | --- |
| 0 | 2026-08-01 | Initial MeasurementQuality contract draft for Phase 0.2B.1.3. |
