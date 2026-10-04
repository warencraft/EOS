# ROADMAP

## Míľnik 0.2B.2.5 - Catalog-aware / Reference-integrity Integration

Cieľ:

- zaviesť immutable in-memory registry pre UNT, CND, PRP a CLS;
- vyžadovať explicitný ValidationContext pre plnú katalógovú validáciu;
- oddeliť existence/type `reference_integrity` od významovej `catalog_validation`;
- zdieľať UNT, CND a PRP validačné pravidlá vo všetkých relevantných Knowledge Core kontraktoch;
- uplatniť explicitnú default a authoring lifecycle policy;
- zachovať contract-only API, JSON Schema kontrakty a Accepted architektúru;
- používať iba fiktívne test-only catalog entries.

Stav: `COMPLETE`. Kompletná sada má 214 úspešných testov a CDR-0013 Revision 1 má verdict `READY FOR 0.2B.2 CLOSURE`.

Nasleduje: `Phase 0.2B.2-close - Knowledge Catalog Integration Closure Review`. Phase 0.2C nebola začatá.

## Míľnik 0.2B.2.4 - Classification Catalog Contract

Cieľ:

- implementovať Classification Catalog ako Reference Catalog,
- zaviesť samostatný Classification Catalog Entry Aggregate Root so stabilným `CLS-xxxxxx`,
- znovu použiť common entity metadata, lifecycle a SourceLink pravidlá,
- vyžadovať neprázdny human-readable `name` a autoritatívny textový `description`,
- oddeliť definition provenance katalógovej položky od assignment provenance embedded Classification,
- podporiť iba priame CLS replacement odkazy,
- ponechať classification system, external code, hierarchy, aliases, equivalence, target applicability a catalog-aware validáciu mimo v1,
- používať iba fiktívne validačné fixtures bez reálnych classifications.

Stav: `COMPLETE`. Kompletná sada má 182 úspešných testov.

Nasledoval dokončený `Phase 0.2B.2.5 - Catalog-aware / Reference-integrity Integration`. Celá Phase 0.2B.2 čaká na krátke closure review.

## Míľnik 0.2B.2.3 - Property Catalog Contract

Cieľ:

- implementovať Property Catalog ako Knowledge Catalog,
- zaviesť samostatný Property Catalog Entry Aggregate Root so stabilným `PRP-xxxxxx`,
- znovu použiť common entity metadata, lifecycle a SourceLink pravidlá,
- definovať povinný neprázdny unique zoznam podporovaných číselných value types,
- definovať presný povinný UNT allow-list a voliteľný CND allow-list,
- ponechať canonical unit, required Conditions, multiplicitu, MeasurementQuality policy, classifications, aliases, dimension a conversion mimo v1,
- používať iba fiktívne validačné fixtures bez reálnych properties.

Stav: `COMPLETE`. Kompletná sada má 168 úspešných testov.

Nasleduje: `Phase 0.2B.2.4-prep - Classification Catalog Pre-design Review`. Tento míľnik nebol začatý a celá Phase 0.2B.2 zostáva rozpracovaná.

## Míľnik 0.2B.2.2 - Condition Type Catalog Contract

Cieľ:

- implementovať Condition Type Catalog ako Knowledge Catalog,
- zaviesť samostatný Condition Type Catalog Entry Aggregate Root so stabilným `CND-xxxxxx`,
- znovu použiť common entity metadata, lifecycle a SourceLink pravidlá,
- definovať povinný neprázdny unique zoznam existujúcich Condition value forms,
- pri `referenceId` vyžadovať uzavretú policy podporovaných cieľových ID rodín,
- ponechať evaluation mode constraints, jednotky, multiplicitu, logické kombinácie a catalog-aware validáciu mimo v1,
- používať iba fiktívne validačné fixtures bez reálnych condition types.

Stav: `COMPLETE`. Kompletná sada má 152 úspešných testov.

Nasleduje: `Phase 0.2B.2.3-prep - Property Catalog Pre-design Review`. Tento míľnik nebol začatý a celá Phase 0.2B.2 zostáva rozpracovaná.

## Míľnik 0.2B.2.1 - Unit Catalog Contract

Cieľ:

- implementovať Unit Catalog ako prvý Reference Catalog kontrakt,
- zaviesť samostatný Unit Catalog Entry Aggregate Root so stabilným `UNT-xxxxxx`,
- znovu použiť common entity metadata, lifecycle a SourceLink pravidlá,
- oddeliť identitu od name, symbolu a semantic equivalence,
- ponechať quantity kind, dimension, unit system, aliasy a conversion mimo v1,
- používať iba fiktívne validačné fixtures bez reálnych jednotiek.

Stav: `COMPLETE`. Kompletná sada má 137 úspešných testov.

Nasleduje: `Phase 0.2B.2.2 - Condition Type Catalog`. Tento míľnik nebol začatý a celá Phase 0.2B.2 zostáva rozpracovaná.

## Míľnik 0.2B.1-close.1 - Knowledge Core Corrective Closure

Cieľ:

- zabezpečiť fail-closed testovací bootstrap pri chýbajúcom `jsonschema` alebo `referencing`,
- ponechať formát `sourceReferenceId` výlučne v JSON Schema a oddeliť ho od budúcej kontroly existencie referencie,
- uzavrieť blokery KCI-0001, KCI-0002 a KCI-0004 z CDR-0008,
- zosúladiť backlog a validačnú dokumentáciu so skutočným stavom repozitára.

Stav: Completed. Phase 0.2B.1 je `COMPLETE`.

Nasleduje: `Phase 0.2B.2 - Knowledge Catalogs` v poradí Unit Catalog, Condition Type Catalog, Property Catalog, Classification Catalog a katalógovo uvedomelá integračná validácia. Phase 0.2B.2 nebola začatá.

## Míľnik 0.2B.1.7 - Observation Contract

Cieľ:

- implementovať first-class evidence Entity a Aggregate Root so stabilným `OBS-xxxxxx`,
- podporiť jeden riadený `subjectId`, GLOBAL alebo JOB scope a jeden typed property result,
- znovu použiť Quantity, ValueRange, MeasurementQuality, Condition, SourceLink a spoločné entity metadata,
- zachovať hranicu evidence voči PropertyRecord, Decision a Derived Result,
- aplikovať existujúce vnorené významové invarianty bez duplikácie.

Stav: implementačný rozsah Completed, kontrakt Review. Všetkých sedem plánovaných Knowledge Core kontraktov má technickú implementáciu a Phase 0.2B.1 bola po integračnom review a korektívnom kroku formálne uzatvorená.

PROJECT/EXPERIMENT scope, neidentifikované subjekty, všeobecné a nečíselné výsledky, observation type taxonomy, actor/attachment, evidence verification, korekčný lifecycle, referenčná existencia a katalógová kompatibilita zostávajú deferred. Phase 0.2B.2 ani 0.2C nezačala.

## Míľnik 0.2B.1.6 - PropertyRecord Contract

Cieľ:

- zaviesť embedded claim-like Value Object pre jedno štruktúrované technické tvrdenie,
- používať centrálny `PRP-xxxxxx`, povinný `valueType` a presne jednu číselnú vetvu Quantity alebo ValueRange,
- podporiť voliteľné MeasurementQuality a viac rodičom vlastnených Conditions,
- používať povinné pole `sourceLinks` a VerificationStatus tvrdenia bez predstierania lifecycle rodiča,
- zachovať vnorené aplikačné invarianty bez duplikácie validačných pravidiel,
- odložiť Property Catalog, Observation a Decision kontrakty do určených fáz.

Stav: implementačný rozsah Completed, kontrakt Review. Celý `0.2B.1` zostáva In progress.

Do `0.2B.2` zostáva existencia a použiteľnosť PRP, povolené hodnotové formy, jednotková a rozmerová kompatibilita, povinné podmienky, doménové rozsahy a klasifikácia vlastností. Property Catalog ani reálne PRP položky nevznikli; `0.2B.2` nezačala.

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

Stav: Phase 0.2B.1 `COMPLETE`; všetkých sedem plánovaných kontraktov je implementovaných, integračne skontrolovaných a korektívne uzatvorených. Phase 0.2B.2 nezačala.

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

Stav: `COMPLETE`. Sedem plánovaných kontraktov je technicky implementovaných a blokujúce findings z integračného review sú uzavreté.

## Fáza 0.2B.2 - Knowledge Catalogs

Cieľ:

- navrhnúť katalógy v poradí Unit, Condition Type, Property a Classification,
- zaviesť katalógovo uvedomelú kontrolu existencie, lifecycle a kompatibility referencií,
- zapojiť katalógové pravidlá do PropertyRecord a Observation bez zmeny ich evidence/claim hranice,
- používať iba fiktívne testovacie záznamy, kým nie sú schválené autoritatívne technické dáta.

Stav: Next / Not started.

## Fáza 0.3 - Prvé prázdne záznamové šablóny

Predbežný cieľ:

- pripraviť šablóny pre materiál, polotovar, proces, stroj, nástroj a zákazku,
- zachovať zdrojovú klasifikáciu a revízie.

Stav: čaká na schválenie.
