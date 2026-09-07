# ROADMAP

## Míľnik 0.2B.1.5 - Classification Contract

Cieľ:

- implementovať embedded reference Value Object s jedným povinným `classificationId` na budúcu CLS katalógovú položku,
- znovu použiť SourceLink a ponechať `sourceLinks` štrukturálne nepovinné,
- zachovať sémantickú povinnosť zdrojov pre externý pôvod a odložiť jej katalógové vynucovanie do `0.2B.2`,
- vynechať voľný text, enum klasifikácií, notes, evaluationMode, vlastné ID, lifecycle a koreňový verificationStatus,
- ponechať hierarchiu katalógu a násobnosť kolekcii rodiča.

Stav: implementačný rozsah Completed, kontrakt Review. Celý `0.2B.1` zostáva In progress.

Do `0.2B.2` zostáva existencia a použiteľnosť CLS položiek, systémy, hierarchia, kompatibilita s rodičom a katalógová kontrola povinnosti zdrojov. Classification Catalog ani reálne CLS položky zatiaľ nevznikli; `0.2B.2` nezačala.

## Míľnik 0.2B.1.4 - Condition Contract

Cieľ:

- zaviesť štvrtý minimálny Knowledge Core Contract pre value object `Condition`,
- definovať povinné `conditionTypeId` a `evaluationMode`,
- používať centralizovaný formát `CND-xxxxxx` pre budúci Condition Type Catalog význam,
- vyžadovať presne jednu hodnotovú formu z `quantity`, `valueRange`, `textValue`, `booleanValue` alebo `referenceId`,
- použiť vnorený `Quantity` a `ValueRange` cez `$ref`,
- ponechať existenciu Condition Type Catalog položky, kompatibilitu hodnotovej formy a vyhodnotenie podmienky budúcej aplikačnej validácii,
- nemodelovať manufacturing tolerance, workflow stav ani zdrojové dôkazy.

Stav: Review.

## Míľnik 0.2B.1.3 - MeasurementQuality Contract

Cieľ:

- zaviesť tretí minimálny Knowledge Core Contract pre value object `MeasurementQuality`,
- definovať iba `uncertainty`, `resolution`, `confidenceLevel` a voliteľné `notes`,
- vyžadovať aspoň jedno štruktúrované pole a odmietnuť notes-only objekt,
- použiť vnorený `Quantity` pre metrologické hodnoty s jednotkou,
- oddeliť štrukturálne pravidlá od aplikačných pravidiel `uncertainty.value >= 0` a `resolution.value > 0`,
- nemodelovať výrobnú, konštrukčnú ani akceptačnú toleranciu.

Stav: Review.

## Míľnik 0.2B.1.3-prep - MeasurementQuality Tolerance Boundary Correction

Cieľ:

- odstrániť produktovú, výrobnú a akceptačnú toleranciu z `MeasurementQuality`,
- ponechať `MeasurementQuality` pre metrologické kvalitatívne charakteristiky,
- odložiť tolerance modelling do budúceho requirement/tolerance kontraktu,
- obnoviť Accepted stav opravených RFC pred implementáciou `MeasurementQuality`.

Stav: Completed / Approved.

Ďalší krok: `Phase 0.2B.1.3 - MeasurementQuality Contract`.

## Míľnik 0.2B.1.2 - ValueRange Contract

Cieľ:

- zaviesť druhý minimálny Knowledge Core Contract pre value object `ValueRange`,
- definovať `minValue`, `maxValue`, `unitId`, `lowerInclusive`, `upperInclusive` a voliteľné `notes`,
- použiť centrálny formát `UNT-xxxxxx`,
- oddeliť štrukturálne pravidlá od aplikačného pravidla `minValue <= maxValue`,
- nepridávať Unit Catalog, konkrétne jednotky ani strojárske hodnoty.

Stav: Review.

## Míľnik 0.2B.1.1 - Quantity Contract

Cieľ:

- zaviesť prvý minimálny Knowledge Core Contract pre value object `Quantity`,
- definovať iba `value`, `unitId` a voliteľné `notes`,
- použiť centrálny formát `UNT-xxxxxx`,
- nepridávať Unit Catalog, konkrétne jednotky ani strojárske hodnoty.

Stav: Review.

## Fáza 0.1 - Architektúra a riadenie projektu

Cieľ:

- vytvoriť základnú štruktúru repozitára,
- definovať governance dokumenty,
- zaviesť identifikáciu, verziovanie a ADR,
- pripraviť prázdne dátové kontrakty.

Stav: Completed.

## Míľnik 0.1.1 - Governance Alignment

Cieľ:

- jazykovo stabilizovať manifest,
- odstrániť konflikt prefixu `STD`,
- oddeliť interné štandardy EOS od externých normatívnych referencií,
- potvrdiť `SourceReference` ako samostatnú entitu,
- zaviesť `SourceLink`,
- spresniť metadáta entít pred detailnými schémami.

Stav: Completed / Approved.

## Fáza 0.2 - Schémy a validačné pravidlá

Predbežný cieľ:

- dopracovať JSON-kompatibilné schémy,
- pripraviť pravidlá validácie,
- vytvoriť testy štruktúry bez technických hodnôt.

Stav: In progress.

## Fáza 0.2A - Foundation Data Contracts

Cieľ:

- vytvoriť modulárne schémy pre spoločné metadáta, zdroje, normatívne referencie a riadené dokumenty,
- pripraviť minimálnu aplikačnú validačnú vrstvu,
- pridať netechnické testovacie fixtures,
- zdokumentovať rozdiel medzi syntaktickou a významovou validáciou.

Stav: podmienečne schválené, auditované v 0.2A.1.

## Míľnik 0.2A.1 - Validation Capability Audit

Cieľ:

- zdokumentovať reálne schopnosti aktuálnej validačnej vrstvy,
- zaviesť fail-closed správanie pre nepodporované JSON Schema kľúčové slová,
- doplniť auditné testy,
- pripraviť návrh ADR-0013 pre štandardný JSON Schema validátor.

Stav: Completed / Approved.

## Míľnik 0.2A.2 - Standards-Compliant Validator Integration

Cieľ:

- zaviesť `jsonschema` ako štandardný validátor JSON Schema Draft 2020-12,
- ponechať EOS aplikačné pravidlá v internej validačnej vrstve,
- zaviesť jednotný chybový model,
- pripraviť regresné testy pre štandardné JSON Schema schopnosti,
- zdokumentovať runtime dependency postup.

Stav: Completed / Approved.

## Míľnik 0.2B.0 - Governance Finalization

Cieľ:

- uzavrieť architektonickú fázu EOS,
- doplniť required prefixy do `EOS-003`,
- prijať RFC-0001, RFC-0002 a RFC-0003,
- zmeniť Architecture Readiness Verdict na `READY`,
- zmraziť architektúru pred implementáciou Knowledge Core Contracts.

Stav: Completed / Approved.

## Míľnik 0.2B.1 - Knowledge Core Contracts

Cieľ:

- vytvoriť schémy pre minimálne knowledge core kontrakty schválené architektúrou,
- zachovať oddelenie JSON Schema validácie a EOS aplikačnej validácie,
- neprekročiť schválený scope bez ADR alebo RFC.

Predbežný scope:

- `Quantity`,
- `ValueRange`,
- `MeasurementQuality`,
- `Condition`,
- `Classification`,
- `PropertyRecord`,
- `Observation`.

Stav: In progress.

## Fáza 0.3 - Prvé prázdne záznamové šablóny

Predbežný cieľ:

- pripraviť šablóny pre materiál, polotovar, proces, stroj, nástroj a zákazku,
- zachovať zdrojovú klasifikáciu a revízie.

Stav: čaká na schválenie.
