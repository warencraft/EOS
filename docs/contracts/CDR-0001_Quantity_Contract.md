# CDR-0001 - Quantity Contract

Project: EOS – Engineering Operating System

Contract Review ID: CDR-0001

Contract: Quantity

Version: 0.1

Revision: 0

Status: Review

Document basis: Accepted EOS architecture

## 1. Purpose

Tento dokument definuje prvý samostatný Knowledge Core Contract pre hodnotový objekt `Quantity`.

`Quantity` predstavuje jednu skalárnu numerickú hodnotu vyjadrenú odkazom na autoritatívnu jednotku. Je určený ako opakovane použiteľný vnorený objekt pre budúce znalostné entity, pozorovania, katalógové záznamy a výpočtové výsledky.

## 2. Scope

Kontrakt pokrýva iba štruktúru hodnotového objektu `Quantity`:

- povinné pole `value`,
- povinné pole `unitId`,
- voliteľné pole `notes`,
- zákaz neznámych polí,
- zákaz metadát entít a lifecycle polí,
- štrukturálnu referenciu na budúci Unit Catalog cez identifikátor `UNT-xxxxxx`.

`Quantity` je vlastnený rodičovským objektom a nemá samostatnú globálnu identitu.

## 3. Non-goals

Tento kontrakt nedefinuje:

- `ValueRange`,
- toleranciu,
- neistotu,
- rozlíšenie,
- presnosť,
- metódu merania,
- podmienky merania alebo použitia,
- význam vlastnosti,
- stav overenia,
- zdrojovú evidenciu,
- textovú jednotku z externého vstupu,
- zobrazovaciu jednotku,
- prevod jednotiek,
- katalóg jednotiek,
- konkrétne jednotky,
- technické, materiálové, výrobné alebo obchodné hodnoty.

## 4. Dependencies

Kontrakt závisí od:

- JSON Schema Draft 2020-12,
- centrálneho registra schém EOS,
- `schemas/common/identifiers.schema.json#/$defs/UNT`,
- budúceho Unit Catalog modelu, ktorý zatiaľ nie je implementovaný.

`unitId` je štrukturálne overovaný ako identifikátor `UNT-xxxxxx`. Existencia a význam jednotky budú overované neskoršou aplikačnou validačnou vrstvou voči Unit Catalog.

## 5. Proposed Fields

### value

Povinné pole.

Typ: JSON number.

Význam: jedna skalárna numerická hodnota bez doménového minima alebo maxima.

`value` nesmie predstavovať interval, toleranciu, neistotu, nominálnu hodnotu s limitmi ani viacnásobnú hodnotu.

### unitId

Povinné pole.

Typ: string.

Formát: `UNT-xxxxxx`.

Význam: odkaz na budúci autoritatívny záznam v Unit Catalog. Tento kontrakt neimplementuje Unit Catalog ani význam konkrétnych jednotiek.

### notes

Voliteľné pole.

Typ: string.

Význam: lokálna poznámka k použitiu hodnotového objektu v rodičovskom kontexte.

`notes` nesmie niesť význam jednotky, toleranciu, neistotu, zdrojovú citáciu, podmienky, prevod, zobrazovací formát ani technickú interpretáciu hodnoty.

## 6. Invariants

- `Quantity` je value object.
- `Quantity` je nemenný z pohľadu významu hodnoty.
- `Quantity` nemá vlastné `id`.
- `Quantity` nemá `schemaVersion`, `recordVersion`, `revision`, `status`, `sourceLinks` ani `verificationStatus`.
- `Quantity` je vždy vlastnený rodičovským objektom.
- `value` je jedna konečná numerická hodnota.
- `unitId` je vždy štrukturálny odkaz na `UNT-xxxxxx`.
- Neznáme polia sú zakázané.

## 7. Validation Rules

Štrukturálna validácia:

- objekt musí mať typ `object`,
- `value` je povinné,
- `unitId` je povinné,
- `value` musí byť JSON number,
- `unitId` musí zodpovedať centrálnemu vzoru `UNT-xxxxxx`,
- `notes`, ak existuje, musí byť neprázdny string,
- `additionalProperties` musí byť `false`.

Aplikačná validácia:

- numerické hodnoty musia byť konečné,
- `NaN` a `Infinity` nie sú prípustné,
- existencia `unitId` v Unit Catalog bude kontrolovaná až po zavedení Unit Catalog,
- kompatibilita jednotky s významom vlastnosti bude kontrolovaná až v rodičovských kontraktoch.

## 8. Examples

Platný príklad s celým číslom:

```json
{
  "value": 1,
  "unitId": "UNT-000001"
}
```

Platný príklad s desatinným číslom:

```json
{
  "value": 1.25,
  "unitId": "UNT-000002"
}
```

Platný príklad s lokálnou poznámkou:

```json
{
  "value": 5,
  "unitId": "UNT-000005",
  "notes": "Fictional local note without unit meaning."
}
```

## 9. Invalid Examples

Chýbajúce `value`:

```json
{
  "unitId": "UNT-000001"
}
```

Neplatný prefix jednotky:

```json
{
  "value": 1,
  "unitId": "ABC-000001"
}
```

Zakázané metadáta entity:

```json
{
  "value": 1,
  "unitId": "UNT-000001",
  "id": "QTY-000001"
}
```

## 10. Compatibility Considerations

Kontrakt je zlučiteľný s prijatou architektúrou EOS, pretože:

- zachováva hranicu medzi value object a entity,
- nepoužíva lifecycle mimo rodičovského objektu,
- neukladá zdroje ani stav overenia priamo do `Quantity`,
- umožňuje neskoršie použitie v PostgreSQL, Graph DB, REST API a AI vrstve ako vnorený objekt,
- odkazuje na jednotku cez stabilný identifikátor, nie cez textový názov.

Kontrakt úmyselne zužuje prvú implementáciu na minimálny model `value` a `unitId`. Polia ako `nominalValue`, `rawUnitText` alebo `displayUnitId` zostávajú mimo tohto kontraktu, pretože patria do budúcich špecifických kontraktov alebo integračných vstupov.

## 11. Known Limitations

- Unit Catalog ešte neexistuje.
- `unitId` sa overuje iba štrukturálne.
- Kompatibilita jednotky s vlastnosťou nie je súčasťou `Quantity`.
- Kontrakt nevyjadruje intervaly, tolerancie ani neistotu.
- Kontrakt neobsahuje zdrojovú evidenciu.

## 12. Acceptance Criteria

Kontrakt je pripravený na review, keď:

- existuje JSON Schema pre `Quantity`,
- schéma používa Draft 2020-12,
- schéma je dostupná cez centrálny schema index,
- `unitId` používa centrálny vzor `UNT-xxxxxx`,
- platné fixture záznamy prejdú validáciou,
- neplatné fixture záznamy zlyhajú validáciou,
- existujú testy pre zákaz metadát entity,
- existujú testy pre viac chýb naraz,
- existujú testy pre presné cesty k chybným poliam,
- nevznikli konkrétne jednotky ani technické dáta.

## 13. Change History

| Revision | Date | Change |
| --- | --- | --- |
| 0 | 2026-08-01 | Initial Quantity contract draft for Phase 0.2B.1.1. |
