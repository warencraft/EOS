# RFC-0001 - Engineering Property Model

**Project:** EOS - Engineering Operating System  
**RFC ID:** RFC-0001  
**Version:** 0.1  
**Revision:** 2  
**Status:** Review  
**Author:** Chief Engineering Knowledge Architect + Codex  
**Last update:** 2026-07-14  
**Document basis:** Internal architecture proposal  

---

## 1. Problém

Phase 0.2B bude potrebovať znalostné entity ako `Material`, `StockMaterial`, `ManufacturingProcess`, `Machine`, `CuttingTool` a `Supplier`.

Tieto entity budú opakovane pracovať s vlastnosťami, hodnotami, jednotkami, rozsahmi, podmienkami platnosti, dostupnosťou, pozorovaniami a obchodnými záznamami.

Ak sa tieto stavebné bloky nenavrhnú vopred, hrozí:

- duplicitné modelovanie rovnakého typu informácie,
- miešanie samotnej hodnoty, rozsahu, tolerancie a neistoty,
- miešanie technických vlastností s pozorovaniami z výroby,
- porovnávanie neporovnateľných vlastností,
- nejasné alebo voľne písané jednotky,
- slabá migrácia do budúcej databázy,
- nekonzistentné použitie `sourceLinks`.

## 2. Ciele

Cieľom RFC je navrhnúť spoločné stavebné bloky pre budúce znalostné entity.

Návrh má určiť:

- ktoré objekty majú byť vnorené value objects,
- ktoré objekty môžu neskôr prerásť do samostatných entít alebo katalógov,
- ako zapisovať hodnotu, interval, jednotku, kvalitu merania a podmienky platnosti,
- ako viazať vlastnosti a pozorovania na `sourceLinks`,
- ako predísť duplicite a neporovnateľným zápisom,
- ktoré identifikátory treba doplniť pred implementáciou Phase 0.2B.

## 3. Mimo rozsahu

Toto RFC nevytvára:

- JSON Schema pre `Material`,
- JSON Schema pre `StockMaterial`,
- JSON Schema pre `ManufacturingProcess`,
- JSON Schema pre `Machine`,
- JSON Schema pre `CuttingTool`,
- JSON Schema pre `Supplier`,
- JSON Schema pre `Observation`,
- katalóg vlastností,
- katalóg jednotiek,
- reálne materiálové údaje,
- reálne normové tabuľky,
- výrobné časy,
- ceny,
- kalkulačky,
- používateľské rozhranie,
- databázový server.

## 4. Navrhovaný model

### 4.1 `Quantity`

Účel: reprezentovať jednu číselnú hodnotu s autoritatívnou jednotkou.

Odporúčanie: `Quantity` má byť vnorený value object.

`Quantity` nesmie miešať samotnú hodnotu, rozsah, technickú toleranciu, neistotu merania ani presnosť alebo rozlíšenie meradla. Tieto významy patria do samostatných objektov.

Povinné polia pre záznamy v stave `Review` alebo `Approved`:

- `unitId`

Nepovinné polia:

- `value`
- `nominalValue`
- `displayUnitId`
- `rawUnitText`
- `notes`

Pravidlá:

- `value` sa používa pre jednoduchú jednu hodnotu.
- `nominalValue` sa používa, keď má hodnota význam menovitej hodnoty.
- `unitId` odkazuje na budúci Unit Catalog a používa formát `UNT-xxxxxx`.
- `displayUnitId` sa použije iba vtedy, keď je potrebné odlíšiť autoritatívnu jednotku od zobrazovacej jednotky.
- `rawUnitText` je povolené iba v pracovných alebo migračných `Draft` záznamoch. Nie je autoritatívne a nesmie sa používať na porovnávanie.

Väzba na `sourceLinks`: `Quantity` samotná nemusí mať vlastné `sourceLinks`, ak je súčasťou `PropertyRecord` alebo `Observation`. Zdrojová väzba má byť primárne na úrovni podporovaného tvrdenia.

Podmienky platnosti: patria mimo `Quantity`, do `Condition` alebo rodičovského záznamu.

Životný cyklus: riadi ho rodičovský záznam.

Riziko duplicity: nízke, ak `Quantity` ostane iba hodnota a nebude obsahovať význam vlastnosti, rozsah ani kvalitu merania.

Budúca použiteľnosť: vysoká pre `Material`, `StockMaterial`, `Machine`, `ManufacturingProcess`, `Observation` a `TimeRecord`.

### 4.2 `ValueRange`

Účel: reprezentovať interval hodnoty bez miešania s jednoduchou číselnou hodnotou.

Odporúčanie: nezačínať ako samostatná entita. Použiť ako vnorený value object tam, kde vlastnosť alebo pozorovanie vyžaduje interval.

Povinné polia pre záznamy v stave `Review` alebo `Approved`:

- `unitId`

Nepovinné polia:

- `minValue`
- `maxValue`
- `lowerInclusive`
- `upperInclusive`
- `rawUnitText`
- `notes`

Pravidlá:

- `minValue` a `maxValue` opisujú dolnú a hornú hranicu intervalu.
- `lowerInclusive` a `upperInclusive` určujú, či sú hranice súčasťou intervalu.
- `unitId` používa formát `UNT-xxxxxx`.
- `rawUnitText` je povolené iba v pracovných alebo migračných `Draft` záznamoch.
- `ValueRange` nemá obsahovať `nominalValue`; menovitá hodnota patrí do `Quantity`.

Väzba na `sourceLinks`: cez rodičovský `PropertyRecord` alebo `Observation`.

Podmienky platnosti: mimo `ValueRange`.

Životný cyklus: riadi ho rodičovský záznam.

Riziko duplicity: nízke, ak sa rozsahy nebudú ukladať paralelne do `Quantity`.

### 4.3 `MeasurementQuality`

Účel: reprezentovať kvalitu hodnoty alebo merania bez zamieňania s hodnotou samotnou.

Odporúčanie: začať ako vnorený value object s názvom `MeasurementQuality`.

`MeasurementQuality` je jediný preferovaný názov. Názov `ValueQuality` sa nemá používať v autoritatívnych dokumentoch ani budúcich schémach.

Nepovinné polia:

- `tolerance`
- `uncertainty`
- `resolution`
- `precision`
- `methodReference`
- `notes`

Pravidlá významu:

- `tolerance` vyjadruje technickú požiadavku alebo povolenú odchýlku. Nie je to neistota merania.
- `uncertainty` vyjadruje neistotu výsledku merania alebo skúšky. Nie je to výrobná tolerancia.
- `resolution` vyjadruje najmenší rozlíšiteľný krok meradla alebo metódy.
- `precision` vyjadruje opakovateľnosť alebo presnosť metódy podľa zvoleného významu, ktorý musí byť vysvetlený v `methodReference` alebo `notes`.
- `methodReference` odkazuje na metódu, postup, interný predpis alebo zdrojový kontext. Ak nejde o samostatnú entitu, môže byť dočasne textové.

Väzba na `sourceLinks`: cez rodičovský `PropertyRecord` alebo `Observation`, prípadne cez samostatný `SourceLink` na konkrétne pole kvality.

Riziko duplicity: stredné, ak sa tolerancia, neistota a presnosť budú miešať do voľného textu.

### 4.4 `PropertyRecord`

Účel: reprezentovať jednu vlastnosť, jej typ hodnoty, hodnotu, podmienky platnosti, kvalitu hodnoty a zdroje.

Odporúčanie: začať ako generický embedded claim-like value object s možnosťou budúcej špecializácie.

Povinné polia:

- `propertyId`
- `valueType`
- `verificationStatus`
- `sourceLinks`

Nepovinné polia:

- `cachedDisplayName`
- `quantity`
- `valueRange`
- `measurementQuality`
- `textValue`
- `booleanValue`
- `designation`
- `classification`
- `conditions`
- `method`
- `normReferenceIds`
- `confidenceLevel`
- `notes`

Pravidlá:

- `propertyId` je autoritatívny identifikátor vlastnosti.
- Navrhovaný formát `propertyId` je `PRP-xxxxxx`.
- `propertyName` sa nemá používať ako autoritatívne pole.
- Ak je potrebný zobrazovací názov, môže existovať iba nepovinné pole `cachedDisplayName`.
- `cachedDisplayName` je odvodená alebo pomocná hodnota a nesmie sa používať na identifikáciu, spájanie ani porovnávanie vlastností.
- Autoritatívne názvy, definície, povolené hodnoty a doménové pravidlá majú patriť do budúceho Property Catalog.
- `PropertyRecord` konceptuálne nesie alebo podporuje `propertyId`, hodnotu, `condition` alebo `conditions`, `verificationStatus` a `sourceLinks`.
- `PropertyRecord` nemá vlastnú globálnu identitu konkrétneho vnoreného záznamu.

Väzba na `sourceLinks`: povinná pri `Review` alebo `Approved`, ak vlastnosť obsahuje overiteľné technické, výrobné, dodávateľské alebo obchodné tvrdenie.

Jednotky: cez `quantity.unitId` alebo `valueRange.unitId`.

Intervaly: cez `valueRange`.

Kvalita hodnoty: cez `measurementQuality`.

Podmienky platnosti: cez pole `conditions`.

Životný cyklus: `PropertyRecord` ostáva embedded claim-like value object bez plného record lifecycle. Má však vlastný `verificationStatus` a `sourceLinks`, pretože overenie jednotlivej vlastnosti nemusí byť totožné so stavom celej rodičovskej entity.

Riziko duplicity: vysoké, ak nebude existovať riadený katalóg `propertyId`.

Budúca použiteľnosť: veľmi vysoká. Použiteľné pre materiály, stroje, procesy aj polotovary.

### 4.5 `Designation`

Účel: reprezentovať označenie, názov, alias alebo identifikátor podľa konkrétneho systému.

Odporúčanie: vnorený value object.

Povinné polia:

- `designation`
- `designationType`

Nepovinné polia:

- `system`
- `language`
- `validFrom`
- `validTo`
- `sourceLinks`
- `notes`

Väzba na `sourceLinks`: potrebná, ak označenie pochádza zo zdroja alebo externého systému.

Rozlíšenie od klasifikácie: `Designation` je názov alebo označenie konkrétneho objektu. `Classification` je zaradenie objektu do triedy, systému alebo kategórie.

Životný cyklus: riadi ho rodičovský záznam.

Riziko duplicity: stredné, hlavne pri aliasoch.

Budúca použiteľnosť: vysoká pre materiály, nástroje, dodávateľské dokumenty a interné názvy.

### 4.6 `Classification`

Účel: reprezentovať zaradenie objektu do klasifikačného systému.

Odporúčanie: začať ako vnorený value object. Ak sa rovnaké klasifikácie začnú používať naprieč viacerými doménami alebo budú potrebovať vlastnú správu verzií, má vzniknúť samostatný Classification Catalog.

Navrhované polia:

- `classificationSystem`
- `code`
- `issuingOrganization`
- `systemVersion`
- `validFrom`
- `validTo`
- `meaning`
- `sourceLinks`
- `notes`

Pravidlá:

- `classificationSystem` určuje systém, v ktorom má kód význam.
- `code` nesmie byť interpretovaný bez systému a verzie alebo platnosti, ak sú relevantné.
- `meaning` je pomocný opis; autoritatívny význam má pochádzať zo zdroja alebo budúceho katalógu.
- `sourceLinks` sú potrebné, ak klasifikácia pochádza z externého systému, normy alebo zdrojového dokumentu.

Rozlíšenie od označenia:

- `Designation` = názov, alias alebo označenie konkrétneho objektu.
- `Classification` = zaradenie objektu do triedy alebo systému.

Riziko duplicity: stredné bez riadeného katalógu často používaných klasifikácií.

### 4.7 `Condition`

Účel: popísať podmienky, za ktorých je hodnota, vlastnosť, schopnosť alebo pozorovanie platné.

Odporúčanie: vnorený value object. Neskôr môže vzniknúť riadený katalóg typov podmienok.

Povinné polia:

- `conditionType`
- `evaluationMode`

Nepovinné polia:

- `conditionTypeId`
- `text`
- `quantity`
- `valueRange`
- `designation`
- `classification`
- `relatedEntityId`
- `sourceLinks`
- `notes`

Navrhované hodnoty `evaluationMode`:

- `mandatory`
- `limiting`
- `descriptive`
- `recommended`
- `contextual`

Pravidlá:

- `conditionTypeId` má byť preferované po zavedení katalógu podmienok.
- `conditionType` môže byť dočasne riadený textový identifikátor.
- Označenia `required` a `optional` sa nemajú používať pre význam podmienky, aby sa nemiešali s JSON Schema keywordom `required`.
- `evaluationMode` vyjadruje, ako sa má podmienka posudzovať v kontexte vlastnosti alebo pozorovania.

Väzba na `sourceLinks`: potrebná, ak podmienka sama obsahuje overiteľné tvrdenie.

Podmienky platnosti: `Condition` je samotný mechanizmus platnosti.

Životný cyklus: riadi ho rodičovský záznam.

Riziko duplicity: vysoké bez riadeného zoznamu `conditionTypeId`.

### 4.8 `Capability`

Účel: popísať schopnosť entity vykonávať alebo podporovať určitý typ činnosti.

Odporúčanie: vnorený value object v 0.2B, s možnosťou budúcej samostatnej entity pri strojoch a procesoch.

Povinné polia:

- `capabilityType`

Nepovinné polia:

- `description`
- `propertyRecords`
- `conditions`
- `limitations`
- `sourceLinks`
- `verificationStatus`
- `notes`

Väzba na `sourceLinks`: potrebná pri overiteľnej schopnosti alebo obmedzení.

Jednotky: cez `propertyRecords`.

Intervaly: cez `propertyRecords`.

Podmienky platnosti: cez `conditions`.

Životný cyklus: riadi ho rodičovská entita, ale môže mať vlastný `verificationStatus`.

Riziko duplicity: stredné, najmä medzi `Machine` a `ManufacturingProcess`.

Budúca použiteľnosť: vysoká pre `Machine` a `ManufacturingProcess`.

### 4.9 `AvailabilityRecord`

Účel: popísať dostupnosť objektu, kapacity, dokumentu, polotovaru alebo dodávateľského stavu v čase.

Odporúčanie: embedded observation record na začiatku; samostatná entita až pri potrebe histórie, plánovania alebo viacerých zdrojov.

`AvailabilityRecord` nepatrí do prvého minimálneho scope `0.2B.1`, pokiaľ samostatné rozhodnutie neurčí inak.

Povinné polia:

- `availabilityType`
- `relatedEntityId`
- `relatedEntityType`
- `observedAt`
- `sourceLinks`

Nepovinné polia:

- `status`
- `validUntil`
- `locationReference`
- `quantity`
- `confidenceLevel`
- `notes`

Pravidlá:

- `supplierId` nemá byť základné pole modelu, pretože dostupnosť sa môže týkať aj stroja, skladu, dokumentu, kapacity alebo internej entity.
- `relatedEntityId` a `relatedEntityType` určujú, čoho sa dostupnosť týka.
- `observedAt` určuje čas pozorovania.
- `validUntil` určuje známu časovú platnosť pozorovania.
- Dostupnosť je časovo závislé pozorovanie, nie trvalá vlastnosť materiálu alebo polotovaru.

Väzba na `sourceLinks`: potrebná, ak dostupnosť pochádza z dodávateľského, obchodného alebo interného záznamu.

Jednotky: cez `quantity`.

Životný cyklus: môže mať vlastný stav v budúcnosti, ak sa z dostupnosti stane samostatná entita. Po schválení sa časovo citlivé dostupnostné pozorovanie nesmie ticho prepisovať.

Riziko duplicity: vysoké, ak sa dostupnosť začne ukladať do viacerých entít bez historického modelu.

Budúca použiteľnosť: vysoká pre `StockMaterial`, `Supplier`, `Machine` a plánovanie kapacít.

### 4.10 `CommercialObservation`

Účel: zaznamenať obchodné pozorovanie bez toho, aby sa miešalo s technickou vlastnosťou, cenou, ponukou alebo právnym záväzkom.

Odporúčanie: embedded observation record, nie technická vlastnosť.

`CommercialObservation` nepatrí do prvého minimálneho scope `0.2B.1`, pokiaľ samostatné rozhodnutie neurčí inak.

Povinné polia:

- `observationType`
- `observedAt`
- `relatedEntityId`
- `sourceLinks`

Nepovinné polia:

- `text`
- `confidenceLevel`
- `observationStatus`
- `validUntil`
- `relatedEntityType`
- `notes`

Pravidlá:

- `CommercialObservation` nie je cena.
- `CommercialObservation` nie je cenová ponuka.
- `CommercialObservation` nie je právny záväzok.
- `CommercialObservation` nie je technická vlastnosť.
- Ak obchodné pozorovanie neskôr ovplyvní cenu alebo ponuku, musí byť prenesené cez samostatný schválený model.

Väzba na `sourceLinks`: potrebná, ak ide o overiteľné obchodné tvrdenie.

Intervaly: časová platnosť cez `observedAt` a `validUntil`.

Životný cyklus: riadi ho rodičovská entita. Po schválení sa časovo citlivé obchodné pozorovanie nesmie ticho prepisovať.

Riziko duplicity: stredné, ak sa obchodné poznámky budú zapisovať aj do technických entít.

Budúca použiteľnosť: vysoká pre `Supplier`, `StockMaterial` a budúce quotation moduly.

### 4.11 `Observation`

Účel: zachytiť konkrétne pozorovanie, meranie, skúšku alebo udalosť s dôkazovým významom.

Odporúčanie: navrhnúť ako first-class evidence entity. Schéma sa v tomto RFC nevytvára.

Navrhovaný ID formát:

- `OBS-xxxxxx`

Navrhované polia:

- `id`
- `observationType`
- `observationScope`
- `observedAt`
- `observedBy`
- `relatedEntityIds`
- `propertyId`
- `quantity`
- `valueRange`
- `textValue`
- `conditions`
- `method`
- `sourceLinks`
- `verificationStatus`
- `jobId`
- `notes`

Pravidlá:

- `Observation` nie je automaticky autoritatívna `PropertyRecord`.
- `Observation` môže byť dôkazom pre vytvorenie alebo aktualizáciu `PropertyRecord`.
- Viac `Observation` záznamov môže podporovať jednu vlastnosť.
- Jednotlivé meranie nesmie automaticky prepísať všeobecnú materiálovú vlastnosť.
- `Observation` musí mať `observationScope`, ktorý určuje kontext pozorovania.
- Konceptuálne povolené hodnoty scope sú `GLOBAL`, `JOB`, `PROJECT` a `EXPERIMENT`. Tento RFC ešte nevytvára JSON enum.
- `jobId` sa použije, ak pozorovanie pochádza zo zákazky alebo výrobnej udalosti.
- Ak pozorovanie obsahuje číselnú hodnotu, jednotka má byť cez `quantity.unitId` alebo `valueRange.unitId`.
- `Observation` alebo `Derived Result` nikdy automaticky nemení autoritatívny `PropertyRecord`.
- Prijatie, odmietnutie alebo povýšenie tvrdenia musí prejsť cez `Decision` alebo ekvivalentný explicitne schválený governance mechanizmus.

Väzba na `sourceLinks`: povinná pri overiteľných pozorovaniach v stave `Review` alebo `Approved`.

Riziko duplicity: stredné, ak nebude jasné, kedy pozorovanie slúži iba ako dôkaz a kedy sa z neho vytvára všeobecná vlastnosť.

## 5. Property Catalog

Budúci Property Catalog má byť autoritatívny zdroj významu `propertyId`.

Navrhovaný prefix:

- `PRP-xxxxxx`

Katalóg zatiaľ nie je súčasťou Phase 0.2B implementácie, ale jeho potreba má byť zohľadnená v návrhu schém.

Budúci záznam vlastnosti má obsahovať najmä:

- `id`,
- autoritatívny názov,
- definíciu,
- doménu použitia,
- povolené `valueType`,
- očakávaný rozmer jednotky,
- odporúčané podmienky,
- pravidlá porovnateľnosti,
- `sourceLinks`.

Bez Property Catalog sa `PropertyRecord` môže používať iba disciplinovane cez riadený `propertyId`, nie cez voľný názov.

## 6. Unit Catalog

Budúci Unit Catalog má byť autoritatívny zdroj významu `unitId`.

Navrhovaný prefix:

- `UNT-xxxxxx`

Navrhované polia jednotkového záznamu:

- `symbol`,
- `name`,
- `dimension`,
- `siBaseUnitId`,
- `conversionFactor`,
- `conversionOffset`,
- `aliases`,
- `displayRules`,
- `sourceLinks`.

Pravidlá:

- `unitId` má byť povinné pre `Review` a `Approved` záznamy, ak záznam obsahuje číselnú hodnotu s jednotkou.
- `rawUnitText` môže byť dočasne povolené iba v `Draft` záznamoch ako migračné alebo pracovné pole.
- `rawUnitText` nie je autoritatívne a nesmie sa používať na porovnávanie ani konverziu.
- Rozmerová kompatibilita jednotiek má byť budúce aplikačné pravidlo, nie iba JSON Schema kontrola.

## 7. Porovnateľnosť vlastností

Automatické porovnanie vlastností je dovolené iba vtedy, keď sú kompatibilné minimálne tieto prvky:

- `propertyId`,
- rozmerová jednotka cez `unitId`,
- `conditions`,
- `method`,
- klasifikačný alebo normatívny kontext,
- `valueType`,
- `measurementQuality`, ak je relevantná.

Navrhovaný výsledok porovnania:

- `comparable`,
- `conditionallyComparable`,
- `notComparable`,
- `unknown`.

Pravidlá:

- Rovnaký zobrazovací názov alebo `cachedDisplayName` nestačí na porovnanie.
- Rovnaký text jednotky nestačí na porovnanie.
- Hodnoty s rozdielnou metódou alebo podmienkami môžu byť iba `conditionallyComparable` alebo `notComparable`.
- Ak chýba autoritatívny `propertyId` alebo `unitId`, výsledok má byť najviac `unknown`.

Toto RFC nevytvára porovnávací engine. Definuje iba minimálne pravidlá pre budúci návrh.

## 8. Alternatívy

### Alternatíva A - Všetko ako voľný text

Výhoda: rýchle zadávanie.

Nevýhoda: slabá validácia, nemožné porovnávanie, vysoké riziko duplicity.

### Alternatíva B - Všetko ako špecializované modely

Výhoda: presné doménové schémy.

Nevýhoda: vysoká komplexita ešte pred tým, ako EOS pozná reálne vzory dát.

### Alternatíva C - Generický základ + neskoršia špecializácia

Výhoda: vyvážený prístup. Spoločné stavebné bloky vzniknú skoro, špecializácia až po overení.

Nevýhoda: vyžaduje disciplínu pri `propertyId`, `unitId`, `conditionTypeId` a `sourceLinks`.

Odporúčaná alternatíva: C.

## 9. Fiktívne netechnické príklady

Príklad `Quantity`:

```json
{
  "nominalValue": 10,
  "unitId": "UNT-000001",
  "displayUnitId": "UNT-000002"
}
```

Príklad `ValueRange`:

```json
{
  "minValue": 1,
  "maxValue": 5,
  "lowerInclusive": true,
  "upperInclusive": false,
  "unitId": "UNT-000001"
}
```

Príklad `PropertyRecord`:

```json
{
  "propertyId": "PRP-000001",
  "cachedDisplayName": "Example property",
  "valueType": "quantity",
  "quantity": {
    "nominalValue": 10,
    "unitId": "UNT-000001"
  },
  "conditions": [
    {
      "conditionType": "SampleCondition",
      "evaluationMode": "contextual",
      "text": "Fictional condition for model demonstration"
    }
  ],
  "verificationStatus": "Draft",
  "sourceLinks": [
    {
      "sourceReferenceId": "SRC-000001",
      "sourceClass": "P",
      "supportedField": "quantity.nominalValue",
      "usageType": "citation",
      "verificationStatus": "Draft"
    }
  ]
}
```

Príklad `Observation`:

```json
{
  "id": "OBS-000001",
  "observationType": "sampleObservation",
  "observationScope": "JOB",
  "observedAt": "2026-07-14T10:00:00Z",
  "observedBy": "example-user",
  "relatedEntityIds": ["MAT-0001"],
  "propertyId": "PRP-000001",
  "quantity": {
    "value": 10,
    "unitId": "UNT-000001"
  },
  "verificationStatus": "Draft",
  "sourceLinks": [
    {
      "sourceReferenceId": "SRC-000001",
      "sourceClass": "V",
      "supportedField": "quantity.value",
      "usageType": "observation",
      "verificationStatus": "Draft"
    }
  ]
}
```

Tieto príklady sú zámerne netechnické a nesmú sa používať ako inžinierske údaje.

## 10. Riziká

- Generický `PropertyRecord` môže byť príliš voľný bez riadeného katalógu vlastností.
- Jednotky bez Unit Catalog môžu viesť k duplicitám.
- Dočasné `rawUnitText` môže prežiť príliš dlho, ak nebude striktne obmedzené na `Draft`.
- Podmienky platnosti môžu prerásť do neprehľadného zoznamu, ak nebude riadený slovník `conditionTypeId`.
- Obchodné pozorovania sa môžu zamiešať s technickými vlastnosťami.
- Jednotlivé pozorovania môžu byť nesprávne povýšené na všeobecné vlastnosti.
- Bez pravidiel porovnateľnosti môžu rôzne hodnoty pôsobiť ako rovnaká vlastnosť.

## 11. Migračné dôsledky

Ak sa návrh prijme, ďalšia práca má byť rozdelená na `0.2B.1 Knowledge Core Contracts`, `0.2B.2 Knowledge Catalogs` a `0.2C Knowledge Entities`.

Odporúčaný poradovník:

1. doplniť governance návrh identifikátorov pre `PRP-xxxxxx`, `UNT-xxxxxx`, `OBS-xxxxxx` a `RFC-xxxx`,
2. `0.2B.1 Knowledge Core Contracts`: `Quantity`, `ValueRange`, `MeasurementQuality`, `Condition`, `Classification`, `PropertyRecord` a `Observation`,
3. `0.2B.2 Knowledge Catalogs`: Property Catalog, Unit Catalog, Condition Type Catalog a Classification Catalog podľa schváleného rozsahu,
4. `0.2C Knowledge Entities`: entity `Material`, `StockMaterial`, `Machine`, `ManufacturingProcess`, `Supplier` a ďalšie doménové entity.

`AvailabilityRecord` a `CommercialObservation` nepatria do prvého minimálneho scope `0.2B.1`, pokiaľ samostatné rozhodnutie neurčí inak.

Toto RFC uvedené kroky iba odporúča. Neimplementuje ich.

## 12. Odpovede na architektonické otázky

### 12.1 Quantity

`Quantity` má reprezentovať jednu hodnotu s jednotkou.

Nemá obsahovať:

- `minValue`,
- `maxValue`,
- `tolerance`,
- `uncertainty`,
- `resolution`,
- `precision`.

Rozsah patrí do `ValueRange`. Kvalita hodnoty alebo merania patrí do `MeasurementQuality`.

### 12.2 ValueRange

`ValueRange` má existovať ako samostatný vnorený value object.

Jednoduché intervaly sa nemajú ukladať do `Quantity`, aby sa nezamieňal význam jednej hodnoty a rozsahu.

### 12.3 MeasurementQuality

Tolerancia, neistota, presnosť a rozlíšenie nesmú byť synonymá.

EOS používa názov `MeasurementQuality`. Názov `ValueQuality` nie je povolený ako autoritatívny názov objektu.

### 12.4 PropertyRecord

Začať generickým `PropertyRecord` ako embedded claim-like value object.

`propertyId` je autoritatívny identifikátor vo formáte `PRP-xxxxxx`.

`propertyName` sa nemá používať. Ak je potrebný zobrazovací text, má ísť o `cachedDisplayName` bez autoritatívneho významu.

`PropertyRecord` konceptuálne obsahuje alebo podporuje `propertyId`, hodnotu, podmienku alebo podmienky, `verificationStatus` a `sourceLinks`.

Špecializované modely zavádzať až po tom, čo sa objavia konkrétne opakované vzory.

### 12.5 Podmienky platnosti

Podmienky platnosti zapisovať cez `Condition`, nie ako voľný text v hodnote.

`Condition` má podporovať najmä:

- stav objektu,
- prostredie,
- smer alebo orientáciu,
- rozsah použiteľnosti,
- procesný kontext,
- zdroj alebo vydanie,
- dátum,
- dodávateľský kontext.

`evaluationMode` má vyjadriť, či je podmienka obmedzujúca, opisná, odporúčaná, kontextová alebo povinná v doménovom význame.

### 12.6 Neporovnateľné hodnoty

Porovnateľnosť má byť založená na kombinácii:

- rovnaký `propertyId`,
- kompatibilný `unitId` a rozmer jednotky,
- kompatibilné `conditions`,
- kompatibilný `method`,
- kompatibilný klasifikačný alebo normatívny kontext,
- kompatibilný `valueType`,
- kompatibilná kvalita merania, ak ovplyvňuje rozhodnutie.

Bez tejto zhody sa hodnoty nesmú automaticky porovnávať.

### 12.7 Jednotky

Pre 0.2B odporúčanie:

- používať `unitId` vo formáte `UNT-xxxxxx`,
- `displayUnitId` používať iba pri potrebe oddeleného zobrazovania,
- `rawUnitText` povoliť iba v `Draft` ako migračné alebo pracovné pole,
- žiadne voľné nekontrolované jednotky v `Review` alebo `Approved` záznamoch.

Budúci smer:

- Unit Catalog,
- SI báza,
- konverzné pravidlá,
- validácia rozmerovej kompatibility.

### 12.8 Všeobecné vs doménové

Všeobecný dátový model má obsahovať:

- množstvo,
- rozsah,
- kvalitu hodnoty alebo merania,
- vlastnosť,
- označenie,
- klasifikáciu,
- podmienku,
- pozorovanie,
- schopnosť,
- dostupnosť,
- obchodné pozorovanie.

Doménové entity majú určovať, ktoré typy vlastností, podmienok a klasifikácií sú povolené v konkrétnom kontexte.

### 12.9 Lifecycle `PropertyRecord`

`PropertyRecord` nemá mať plný samostatný lifecycle ako hlavná entita.

Odporúčanie:

- dedí record lifecycle rodičovskej entity,
- má vlastný `verificationStatus`,
- má vlastné `sourceLinks`.

Tým sa zachová jednoduchosť vnoreného value objectu, ale umožní sa odlíšiť stav overenia konkrétnej vlastnosti od stavu celého záznamu.

### 12.10 Observation

`Observation` má byť oddelený koncept od `PropertyRecord`.

Pozorovanie, meranie alebo skúška môže podporiť vlastnosť, ale nemá ju automaticky nahradiť.

`Observation` má byť first-class evidence entity so stabilným `OBS-xxxxxx` a s poľom `observationScope`. Kontext pozorovania sa má riešiť scope hodnotou, nie vytváraním samostatných typov pre každý kontext.

`Observation` alebo `Derived Result` nikdy automaticky nemení autoritatívny `PropertyRecord`. Prijatie, odmietnutie alebo povýšenie tvrdenia musí prejsť cez `Decision` alebo ekvivalentný explicitne schválený governance mechanizmus.

## 13. RFC proces

Odporúča sa zaviesť nový prefix:

- `RFC-xxxx`

Účel: návrhové dokumenty pred schválením architektonickej alebo dátovej zmeny.

Navrhovaný životný cyklus:

- `Draft`,
- `Review`,
- `Accepted`,
- `Rejected`,
- `Superseded`.

Navrhované pravidlo:

- RFC opisuje navrhovanú zmenu.
- ADR zachytáva prijaté architektonické rozhodnutie.
- Implementácia môže začať až po `Accepted` RFC alebo po príslušnom `Accepted` ADR.

Toto RFC zatiaľ nemení `EOS-003`. Presný ďalší governance krok je samostatne aktualizovať `EOS-003` a prípadne vytvoriť ADR pre RFC proces po schválení tohto návrhu.

## 14. Otvorené otázky

- Kedy zaviesť autoritatívny Property Catalog?
- Má byť Unit Catalog súčasťou 0.2B alebo samostatnej nasledujúcej fázy?
- Má byť `Classification` dlhodobo iba value object, alebo má vzniknúť samostatný Classification Catalog?
- Ako presne validovať kompatibilitu podmienok pri porovnávaní hodnôt?
- Kedy sa `Capability` má stať samostatnou entitou?
- Má byť `Decision` v `0.2B.1` iba konceptuálnou závislosťou, alebo samostatným stored kontraktom?
- Ako oddeliť obchodné pozorovania od budúcich cenových alebo quotation modulov?
- Ktorý governance dokument presne zavedie lifecycle pre RFC?

## 15. Odporúčanie

Odporúča sa pre Phase 0.2B najprv vytvoriť spoločné value object schémy pred entitnými schémami.

Najdôležitejšie rozhodnutia:

- oddeliť `Quantity`, `ValueRange` a `MeasurementQuality`,
- používať autoritatívne `propertyId` vo formáte `PRP-xxxxxx`,
- používať autoritatívne `unitId` vo formáte `UNT-xxxxxx`,
- zaviesť koncept `Observation` s prefixom `OBS-xxxxxx`,
- ponechať `PropertyRecord` ako embedded claim-like value object s vlastným `verificationStatus` a `sourceLinks`,
- zaviesť `observationScope` pre `Observation`,
- nepovýšiť `Observation` ani `Derived Result` na autoritatívny `PropertyRecord` bez `Decision` alebo ekvivalentného schváleného governance mechanizmu,
- nepoužívať názvy vlastností ani text jednotiek ako základ porovnateľnosti.

## 16. Väzby

Súvisiace dokumenty:

- `docs/governance/EOS-003_Identification_and_Versioning.md`
- `docs/governance/EOS-004_Core_Data_Model.md`
- `docs/governance/EOS-006_Data_Validation_Standard.md`
- `docs/governance/EOS-007_Validation_Capability_Matrix.md`
- `adr/ADR-0006_Treat_source_references_as_first_class_entities.md`
- `adr/ADR-0007_Separate_schema_version_from_record_version_and_revision.md`
- `adr/ADR-0013_Use_a_standards_compliant_JSON_Schema_validator.md`

## 17. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-07-14 | 0.1 | 0 | Chief Engineering Knowledge Architect + Codex | Initial RFC draft |
| 2026-07-14 | 0.1 | 1 | Codex | Prepracovanie návrhu pre Review: oddelenie hodnoty, rozsahu a kvality merania; návrh identifikátorov `PRP-xxxxxx`, `UNT-xxxxxx`, `OBS-xxxxxx`; doplnenie Unit Catalog, Property Catalog, Observation, Classification a pravidiel porovnateľnosti |
| 2026-07-25 | 0.1 | 2 | Codex | Architecture Closure revision: uzavretie názvu `MeasurementQuality`, spresnenie `PropertyRecord` ako embedded claim-like value object, doplnenie `Observation.observationScope`, rozhodovacej hranice cez `Decision`, embedded observation records a fázovania `0.2B.1` / `0.2B.2` / `0.2C` |
