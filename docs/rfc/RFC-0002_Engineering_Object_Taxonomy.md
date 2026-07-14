# RFC-0002 - Engineering Object Taxonomy

**Project:** EOS - Engineering Operating System  
**RFC ID:** RFC-0002  
**Version:** 0.1  
**Revision:** 0  
**Status:** Draft  
**Author:** Chief Engineering Knowledge Architect + Codex  
**Last update:** 2026-07-14  
**Document basis:** Internal architecture proposal  

---

## 1. Účel

Tento RFC navrhuje základnú taxonómiu objektov EOS pred implementáciou knowledge entity kontraktov vo fáze 0.2B.

Cieľom je určiť:

- ktoré objekty sú samostatné entity,
- ktoré objekty sú vnorené value objects,
- ktoré objekty sú autoritatívne referencie alebo katalógové položky,
- ktoré objekty sú udalosti, pozorovania alebo odvodené výsledky,
- kde sú hranice agregátov,
- ako sa majú používať stabilné ID, lifecycle, verzovanie, audit a `sourceLinks`.

Tento RFC nevytvára JSON schémy, nemení `EOS-003`, nevytvára ADR a nezačína implementáciu Phase 0.2B.

## 2. Východiská

Návrh rešpektuje tieto existujúce rozhodnutia:

- stabilné ID sú dôležitejšie ako názvy súborov,
- dátové entity používajú `schemaVersion`, `recordVersion` a `revision`,
- `SourceReference` je samostatná autoritatívna entita,
- externé normatívne referencie patria do `NormReference`,
- job-owned entity používajú hierarchické ID,
- JSON schémy majú byť Draft 2020-12 a uzavreté podľa `additionalProperties: false`,
- výpočtový kód nesmie byť autoritatívnym zdrojom inžinierskych znalostí.

## 3. Základné kategórie objektov

### 3.1 Entity

Definícia: objekt so stabilnou identitou, vlastným významom a históriou nezávislou od aktuálnych hodnôt polí.

Vlastnosti:

- vlastné stabilné ID: áno,
- vlastný lifecycle: áno,
- samostatná existencia: áno,
- citovateľnosť: áno,
- versioned/revised: áno,
- auditovateľnosť: áno,
- `sourceLinks`: áno, ak obsahuje overiteľné tvrdenia.

Typické príklady v EOS:

- `Material`,
- `StockMaterial`,
- `ManufacturingProcess`,
- `Machine`,
- `CuttingTool`,
- `Supplier`,
- `Job`,
- `SourceReference`,
- `NormReference`,
- `Observation`,
- `DocumentRecord`.

Nepatrí sem:

- jednoduchá hodnota s jednotkou,
- označenie bez samostatnej identity,
- vnorená podmienka platnosti,
- pomocný zobrazovací text.

### 3.2 Value Object

Definícia: objekt definovaný svojou hodnotou, nie samostatnou identitou.

Vlastnosti:

- vlastné stabilné ID: nie,
- vlastný lifecycle: nie,
- samostatná existencia: nie,
- citovateľnosť: iba cez rodiča alebo konkrétny `SourceLink`,
- versioned/revised: cez rodiča,
- auditovateľnosť: cez rodiča,
- `sourceLinks`: môže obsahovať, ak ide o samostatne zdrojované tvrdenie.

Typické príklady v EOS:

- `Quantity`,
- `ValueRange`,
- `MeasurementQuality`,
- `PropertyRecord`,
- `Condition`,
- `Designation`,
- `Classification`,
- `Capability`,
- `AvailabilityRecord`,
- `CommercialObservation`.

Nepatrí sem:

- objekt, ktorý potrebuje vlastné dlhodobé ID,
- objekt s vlastnou históriou nezávislou od rodiča,
- autoritatívny zdroj alebo normatívna referencia.

### 3.3 Reference Object

Definícia: objekt, ktorý reprezentuje autoritatívny odkaz, zdroj alebo externý význam používaný inými objektmi.

Vlastnosti:

- vlastné stabilné ID: áno,
- vlastný lifecycle: áno,
- samostatná existencia: áno,
- citovateľnosť: áno,
- versioned/revised: áno,
- auditovateľnosť: áno,
- `sourceLinks`: áno, ak sám obsahuje overiteľné tvrdenie alebo odvodenú interpretáciu.

Typické príklady v EOS:

- `SourceReference`,
- `NormReference`,
- budúce autoritatívne záznamy katalógov.

Nepatrí sem:

- konkrétne použitie zdroja pri tvrdení. To je `SourceLink`,
- voľný textový odkaz bez stability.

### 3.4 Event

Definícia: záznam o udalosti, ktorá sa stala v čase a má význam pre históriu systému alebo výroby.

Vlastnosti:

- vlastné stabilné ID: podľa významu udalosti,
- vlastný lifecycle: obvykle nie plný lifecycle, skôr append-only stav,
- samostatná existencia: áno, ak ide o významnú udalosť,
- citovateľnosť: áno,
- versioned/revised: opravy cez revíziu alebo korekčný záznam,
- auditovateľnosť: áno,
- `sourceLinks`: áno, ak udalosť podporuje overiteľné tvrdenie.

Typické príklady v EOS:

- `Observation`,
- budúci `InspectionResult`,
- budúce výrobné udalosti,
- budúca `Nonconformance`.

Nepatrí sem:

- trvalý katalógový význam,
- všeobecná vlastnosť materiálu,
- odvodený výpočet bez reálnej udalosti.

### 3.5 Observation

Definícia: konkrétne pozorovanie, meranie, skúška alebo zistenie z výroby, kontroly alebo analýzy.

Vlastnosti:

- vlastné stabilné ID: áno, `OBS-xxxxxx`,
- vlastný lifecycle: áno, ale s dôrazom na append-only audit,
- samostatná existencia: áno,
- citovateľnosť: áno,
- versioned/revised: áno, pri oprave interpretácie alebo metadát,
- auditovateľnosť: áno,
- `sourceLinks`: áno.

Typické príklady v EOS:

- meranie v zákazke,
- kontrolné zistenie,
- výrobné pozorovanie,
- skúšobný výsledok.

Nepatrí sem:

- všeobecná autoritatívna materiálová vlastnosť,
- trvalá dostupnosť,
- cenový záväzok.

### 3.6 Relationship

Definícia: explicitná väzba medzi objektmi s vlastným významom nad rámec obyčajného ID odkazu.

Vlastnosti:

- vlastné stabilné ID: zatiaľ nie; neskôr podľa potreby `REL-xxxxxx`,
- vlastný lifecycle: iba ak vznikne samostatný relationship object,
- samostatná existencia: nie v 0.2B,
- citovateľnosť: áno, ak väzba sama obsahuje tvrdenie,
- versioned/revised: podľa rodiča alebo samostatného objektu,
- auditovateľnosť: podľa rodiča alebo samostatného objektu,
- `sourceLinks`: áno, ak je väzba zdrojované tvrdenie.

Typické príklady v EOS:

- `materialId` v `StockMaterial`,
- `sourceReferenceId` v `SourceLink`,
- budúce `derivedFrom`,
- budúce `supersedes`.

Nepatrí sem:

- samotný cieľový objekt,
- plnohodnotný grafový model.

### 3.7 Document Object

Definícia: objekt evidujúci riadený dokument, jeho stav, verziu, revíziu a umiestnenie.

Vlastnosti:

- vlastné stabilné ID: používa ID dokumentu,
- vlastný lifecycle: áno, ale odlíšený od lifecycle registračného záznamu,
- samostatná existencia: áno,
- citovateľnosť: áno,
- versioned/revised: áno,
- auditovateľnosť: áno,
- `sourceLinks`: iba pri technických tvrdeniach alebo väzbách na zdroje.

Typické príklady v EOS:

- `DocumentRecord`,
- evidencia governance dokumentu,
- evidencia ADR alebo RFC.

Nepatrí sem:

- samotný obsah dokumentu,
- technická hodnota patriaca do dátovej entity.

### 3.8 Aggregate Root

Definícia: entita, ktorá vlastní konzistentnú hranicu zmeny a riadi vnorené objekty.

Vlastnosti:

- vlastné stabilné ID: áno,
- vlastný lifecycle: áno,
- samostatná existencia: áno,
- citovateľnosť: áno,
- versioned/revised: áno,
- auditovateľnosť: áno,
- `sourceLinks`: áno.

Typické príklady v EOS:

- `Material`,
- `StockMaterial`,
- `Machine`,
- `ManufacturingProcess`,
- `Job`,
- `SourceReference`,
- `DocumentRecord`.

Nepatrí sem:

- vnorená hodnota,
- dočasný odvodený výpočet,
- objekt vlastnený iným agregátom.

### 3.9 Catalog Entry

Definícia: autoritatívna položka riadeného slovníka alebo katalógu.

Vlastnosti:

- vlastné stabilné ID: áno,
- vlastný lifecycle: áno,
- samostatná existencia: áno,
- citovateľnosť: áno,
- versioned/revised: áno,
- auditovateľnosť: áno,
- `sourceLinks`: áno, ak význam pochádza zo zdroja alebo rozhodnutia.

Typické príklady v EOS:

- budúci Property Catalog Entry,
- budúci Unit Catalog Entry,
- budúci Condition Type Catalog Entry,
- budúci Classification Catalog Entry.

Nepatrí sem:

- jednorazová hodnota v zázname,
- voľný alias bez autoritatívneho významu.

### 3.10 Snapshot

Definícia: časovo zmrazený obraz objektu alebo vstupov v konkrétnom okamihu.

Vlastnosti:

- vlastné stabilné ID: podľa použitia,
- vlastný lifecycle: obvykle append-only,
- samostatná existencia: áno, ak podporuje audit alebo reprodukovateľnosť,
- citovateľnosť: áno,
- versioned/revised: skôr nahradenie novým snapshotom než editácia,
- auditovateľnosť: áno,
- `sourceLinks`: podľa obsahu.

Typické príklady v EOS:

- budúci snapshot vstupov kalkulácie,
- snapshot zákazky pri cenovej ponuke,
- snapshot dostupnosti v čase rozhodnutia.

Nepatrí sem:

- aktuálny živý stav entity,
- všeobecný katalógový význam.

### 3.11 Derived Result

Definícia: výsledok odvodený výpočtom, porovnaním, pravidlom, odhadom alebo AI návrhom z explicitných vstupov.

Vlastnosti:

- vlastné stabilné ID: podľa potreby budúcej fázy,
- vlastný lifecycle: áno alebo append-only podľa použitia,
- samostatná existencia: áno, ak má byť auditovaný alebo citovaný,
- citovateľnosť: áno,
- versioned/revised: áno, najmä pri zmene vstupov alebo logiky,
- auditovateľnosť: áno,
- `sourceLinks`: na zdroje vstupov, nie ako náhrada za vstupy.

Typické príklady v EOS:

- odhad času,
- odhad ceny,
- porovnanie vlastností,
- odporúčanie výrobného postupu,
- AI návrh.

Nepatrí sem:

- zdrojová znalosť,
- autoritatívna materiálová vlastnosť,
- reálne meranie.

## 4. Entity

### 4.1 `Material`

Identity boundary: materiál ako znalostný objekt, nie konkrétny fyzický kus.

Lifecycle owner: `Material` sám.

Aggregate root: áno.

Môže vlastniť:

- `Designation`,
- `Classification`,
- `PropertyRecord`,
- `Condition`,
- všeobecné poznámky a interné väzby.

Iba referencuje:

- `NormReference`,
- `SourceReference` cez `SourceLink`,
- `StockMaterial`,
- `Observation`,
- katalógové položky.

Používané value objects:

- `PropertyRecord`,
- `Designation`,
- `Classification`,
- `Condition`,
- `Capability` iba ak je význam doménovo odôvodnený.

Archivácia, nahradenie, supersede: áno. Pôvodný záznam sa nemá fyzicky mazať po schválení.

### 4.2 `StockMaterial`

Identity boundary: skladová, dodávateľská alebo používaná forma materiálu.

Lifecycle owner: `StockMaterial` sám.

Aggregate root: áno.

Môže vlastniť:

- `Designation`,
- `PropertyRecord` špecifické pre formu,
- `AvailabilityRecord`,
- `CommercialObservation`.

Iba referencuje:

- `Material`,
- `Supplier`,
- `SourceReference`,
- `NormReference`,
- `Observation`.

Používané value objects:

- `Quantity`,
- `ValueRange`,
- `Designation`,
- `AvailabilityRecord`,
- `CommercialObservation`,
- `Condition`.

Archivácia, nahradenie, supersede: áno, najmä pri ukončení dodávania alebo zmene formy.

### 4.3 `ManufacturingProcess`

Identity boundary: typ výrobného alebo kontrolného procesu, nie konkrétne vykonanie operácie.

Lifecycle owner: `ManufacturingProcess` sám.

Aggregate root: áno.

Môže vlastniť:

- `Capability`,
- `PropertyRecord`,
- `Condition`,
- `Designation`,
- procesné obmedzenia.

Iba referencuje:

- `Machine`,
- `CuttingTool`,
- `NormReference`,
- `SourceReference`,
- budúce Process Type Catalog položky.

Používané value objects:

- `Capability`,
- `PropertyRecord`,
- `Condition`,
- `Classification`.

Archivácia, nahradenie, supersede: áno.

### 4.4 `Machine`

Identity boundary: konkrétne výrobné zariadenie alebo riadený typ zariadenia podľa budúceho rozhodnutia domény.

Lifecycle owner: `Machine` sám.

Aggregate root: áno.

Môže vlastniť:

- `Capability`,
- `PropertyRecord`,
- `AvailabilityRecord`,
- `CommercialObservation` iba pri obchodnom alebo servisnom kontexte.

Iba referencuje:

- `ManufacturingProcess`,
- `SourceReference`,
- `Observation`,
- `JobOperation`.

Používané value objects:

- `Capability`,
- `PropertyRecord`,
- `Condition`,
- `AvailabilityRecord`,
- `Designation`.

Archivácia, nahradenie, supersede: áno.

### 4.5 `CuttingTool`

Identity boundary: nástroj, nástrojová zostava alebo riadený typ nástroja podľa budúceho doménového rozhodnutia.

Lifecycle owner: `CuttingTool` sám.

Aggregate root: áno, ak je nástroj riadený ako znalostný objekt; inak môže byť referenčná položka budúcej fázy.

Môže vlastniť:

- `Designation`,
- `PropertyRecord`,
- `Capability`,
- `Condition`.

Iba referencuje:

- `Supplier`,
- `ManufacturingProcess`,
- `SourceReference`,
- `Observation`.

Používané value objects:

- `Designation`,
- `PropertyRecord`,
- `Capability`,
- `Condition`,
- `Classification`.

Archivácia, nahradenie, supersede: áno.

### 4.6 `Supplier`

Identity boundary: dodávateľ ako obchodný alebo servisný partner.

Lifecycle owner: `Supplier` sám.

Aggregate root: áno.

Môže vlastniť:

- základné identifikačné údaje,
- `CommercialObservation`,
- dodávateľské `Designation` alebo aliasy.

Iba referencuje:

- `StockMaterial`,
- `CuttingTool`,
- `SourceReference`,
- budúce obchodné záznamy.

Používané value objects:

- `CommercialObservation`,
- `Designation`,
- `Classification` podľa potreby.

Archivácia, nahradenie, supersede: áno.

### 4.7 `Job`

Identity boundary: konkrétna zákazka alebo prípravný zákazkový prípad.

Lifecycle owner: `Job` sám.

Aggregate root: áno.

Môže vlastniť:

- `JobOperation`,
- `TimeRecord`,
- `Risk`,
- `QuotationNote`,
- job-scoped observations, ak budú navrhnuté ako vlastnené zákazkou.

Iba referencuje:

- `Material`,
- `StockMaterial`,
- `Machine`,
- `ManufacturingProcess`,
- `CuttingTool`,
- `Supplier`,
- `SourceReference`,
- `NormReference`.

Používané value objects:

- `Condition`,
- `AvailabilityRecord`,
- `CommercialObservation`,
- prípadné snapshoty vstupov.

Archivácia, nahradenie, supersede: áno, ale historický zákazkový kontext sa nemá prepisovať bez auditu.

### 4.8 `SourceReference`

Identity boundary: autoritatívny zdroj informácie.

Lifecycle owner: `SourceReference` sám.

Aggregate root: áno.

Môže vlastniť:

- bibliografické alebo interné metadáta zdroja,
- klasifikáciu zdroja.

Iba referencuje:

- iné zdroje, ak ide o odvodený alebo súvisiaci zdroj,
- dokumenty, ak to bude potrebné.

Používané value objects:

- žiadne povinné value objects okrem prípadných klasifikácií.

Archivácia, nahradenie, supersede: áno. Interpretácia zdroja patrí do `SourceLink`, nie do `SourceReference`.

### 4.9 `NormReference`

Identity boundary: externá norma, štandard alebo záväzný technický predpis ako referencia, nie plné znenie normy.

Lifecycle owner: `NormReference` sám.

Aggregate root: áno.

Môže vlastniť:

- identifikáciu normy,
- rozsah použitia,
- stav alebo poznámky o platnosti.

Iba referencuje:

- `SourceReference`,
- dokumenty a entity, ktoré normu používajú.

Používané value objects:

- `Classification` podľa potreby,
- `SourceLink`.

Archivácia, nahradenie, supersede: áno.

### 4.10 `Observation`

Identity boundary: jedno konkrétne pozorovanie, meranie, skúška alebo udalosť s dôkazovým významom.

Lifecycle owner: `Observation` sám, alebo `Job`, ak bude v budúcnosti zvolený job-owned variant.

Aggregate root: odporúčanie je áno, ak má `OBS-xxxxxx` globálne ID a môže podporovať viac tvrdení.

Môže vlastniť:

- hodnotu pozorovania,
- podmienky,
- metódu,
- zdrojové väzby,
- stav overenia.

Iba referencuje:

- `Job`,
- `PropertyRecord` cez `propertyId`,
- `SourceReference`,
- meraný alebo pozorovaný objekt.

Používané value objects:

- `Quantity`,
- `ValueRange`,
- `MeasurementQuality`,
- `Condition`,
- `Classification`.

Archivácia, nahradenie, supersede: áno, ale odporúčané správanie je append-only s korekciou alebo novým pozorovaním.

### 4.11 `DocumentRecord`

Identity boundary: registračný záznam riadeného dokumentu.

Lifecycle owner: `DocumentRecord` sám, ale musí odlišovať lifecycle dokumentu od lifecycle registračného záznamu.

Aggregate root: áno.

Môže vlastniť:

- registračné metadáta,
- odkazy na súvisiace dokumenty.

Iba referencuje:

- dokument, ktorý eviduje,
- `SourceReference`,
- `NormReference`,
- `ADR` alebo `RFC`.

Používané value objects:

- podľa budúcej schémy, zatiaľ minimálne metadáta.

Archivácia, nahradenie, supersede: áno.

## 5. Value Objects

### 5.1 `Quantity`

Kategória: value object.

Vlastné ID: nie.

Vlastný `verificationStatus`: nie.

Lifecycle: dedí od rodiča.

Znovupoužitie medzi entitami: áno ako štruktúra, nie ako zdieľaná inštancia.

Samostatná citácia: nie; citovať cez rodiča alebo `SourceLink.supportedField`.

Immutability: odporúčané immutable v rámci jednej revízie rodiča.

### 5.2 `ValueRange`

Kategória: value object.

Vlastné ID: nie.

Vlastný `verificationStatus`: nie.

Lifecycle: dedí od rodiča.

Znovupoužitie medzi entitami: áno ako štruktúra.

Samostatná citácia: nie; citovať cez rodiča alebo `SourceLink`.

Immutability: odporúčané immutable v rámci jednej revízie rodiča.

### 5.3 `MeasurementQuality`

Kategória: value object.

Vlastné ID: nie.

Vlastný `verificationStatus`: nie, ak je súčasťou `PropertyRecord`; môže byť súčasťou overenia `Observation`.

Lifecycle: dedí od rodiča.

Znovupoužitie medzi entitami: áno ako štruktúra.

Samostatná citácia: iba cez konkrétne pole.

Immutability: odporúčané immutable.

Poznámka: názov `MeasurementQuality` je pre taxonómiu preferovaný pred `ValueQuality`, pretože jasnejšie oddeľuje meranie od hodnoty samotnej.

### 5.4 `PropertyRecord`

Kategória: value object.

Vlastné ID: nie; používa `propertyId` ako odkaz na budúci Property Catalog, nie ako identitu konkrétneho vnoreného záznamu.

Vlastný `verificationStatus`: áno.

Lifecycle: dedí od rodiča.

Znovupoužitie medzi entitami: áno ako štruktúra; konkrétna inštancia patrí rodičovi.

Samostatná citácia: áno cez rodiča a konkrétny `SourceLink`.

Immutability: odporúčané immutable v rámci schválenej revízie rodiča.

### 5.5 `Condition`

Kategória: value object.

Vlastné ID: nie; `conditionTypeId` je odkaz na budúci katalóg, nie identita konkrétnej podmienky.

Vlastný `verificationStatus`: spravidla nie.

Lifecycle: dedí od rodiča.

Znovupoužitie medzi entitami: áno ako štruktúra.

Samostatná citácia: áno, ak podmienka sama obsahuje overiteľné tvrdenie.

Immutability: odporúčané immutable.

### 5.6 `Designation`

Kategória: value object.

Vlastné ID: nie.

Vlastný `verificationStatus`: nie, môže mať `sourceLinks`.

Lifecycle: dedí od rodiča.

Znovupoužitie medzi entitami: iba ako hodnota, nie ako zdieľaná inštancia.

Samostatná citácia: áno, ak označenie pochádza zo zdroja.

Immutability: odporúčané immutable.

### 5.7 `Classification`

Kategória: value object v 0.2B; neskôr môže vzniknúť Classification Catalog.

Vlastné ID: nie v podobe vnoreného value objectu; budúca katalógová položka môže mať `CLS-xxxxxx`.

Vlastný `verificationStatus`: nie.

Lifecycle: dedí od rodiča.

Znovupoužitie medzi entitami: áno ako štruktúra.

Samostatná citácia: áno, ak klasifikácia pochádza zo zdroja.

Immutability: odporúčané immutable.

### 5.8 `Capability`

Kategória: value object v 0.2B.

Vlastné ID: nie.

Vlastný `verificationStatus`: áno, ak schopnosť obsahuje overiteľné tvrdenie.

Lifecycle: dedí od rodiča.

Znovupoužitie medzi entitami: áno ako štruktúra; konkrétna schopnosť patrí rodičovi.

Samostatná citácia: áno cez `SourceLink`.

Immutability: odporúčané immutable po schválení.

### 5.9 `AvailabilityRecord`

Kategória: value object v 0.2B, potenciálne event-like alebo samostatná entita v budúcnosti.

Vlastné ID: nie v 0.2B.

Vlastný `verificationStatus`: odporúčané áno alebo `observationStatus`, pretože dostupnosť je časovo závislá.

Lifecycle: dedí od rodiča.

Znovupoužitie medzi entitami: áno ako štruktúra.

Samostatná citácia: áno cez `sourceLinks`.

Immutability: odporúčané append-only v rámci historických záznamov dostupnosti.

### 5.10 `CommercialObservation`

Kategória: value object v 0.2B, potenciálne event-like objekt v budúcnosti.

Vlastné ID: nie v 0.2B.

Vlastný `verificationStatus`: odporúčané `observationStatus` a `confidenceLevel`.

Lifecycle: dedí od rodiča.

Znovupoužitie medzi entitami: áno ako štruktúra.

Samostatná citácia: áno cez `sourceLinks`.

Immutability: odporúčané append-only, ak ovplyvňuje rozhodnutie alebo audit.

## 6. Observation

`Observation` má byť posudzovaná samostatne, pretože je zároveň:

- plnohodnotná entita so stabilným ID `OBS-xxxxxx`,
- event-like záznam o tom, čo sa stalo alebo zistilo v čase,
- evidence object, ktorý môže podporovať `PropertyRecord`.

Odporúčanie: `Observation` má byť samostatná entita a aggregate root, nie iba vnorený value object.

Pravidlá:

- `Observation` má vlastné ID `OBS-xxxxxx`.
- Má vlastný lifecycle, ale po schválení má byť prakticky append-only.
- Je auditovateľná.
- Môže byť naviazaná na `Job`, ale nemá byť automaticky vlastnená zákazkou, ak jej dôkazový význam presahuje jednu zákazku.
- K `PropertyRecord` sa viaže cez `propertyId`, `sourceLinks` alebo budúci evidence relationship.
- K `SourceReference` sa viaže cez `SourceLink`.
- `Measurement` a `InspectionResult` môžu byť špecializované typy `Observation` alebo samostatné entity budúcej fázy.
- Jedna `Observation` nesmie automaticky meniť všeobecnú vlastnosť materiálu, stroja alebo procesu.
- Povýšenie pozorovania na autoritatívny `PropertyRecord` musí byť vedomý schvaľovací krok.

## 7. Events

### 7.1 Rozlíšenie pojmov

| Objekt | Odporúčané zaradenie | Poznámka |
| --- | --- | --- |
| `Event` | generická kategória | Zatiaľ nie samostatná entita v 0.2B. |
| `Observation` | entita + event-like evidence object | Má `OBS-xxxxxx`. |
| `JobOperation` | job-owned entity | Má `JOB-yyyy-xxxx-OP-xxx`. Nie je iba event. |
| `TimeRecord` | job-owned entity | Má `JOB-yyyy-xxxx-OP-xxx-TM-xxx`. |
| `InspectionResult` | budúca Observation subtype alebo entita | Patrí do budúcej fázy. |
| `Measurement` | budúca Observation subtype | Patrí do budúcej fázy. |
| `Purchase` | budúca obchodná alebo skladová udalosť | Nie je súčasť 0.2B. |
| `HeatTreatment` | budúca výrobná udalosť alebo procesný záznam | Nie je súčasť 0.2B. |
| `Nonconformance` | budúca kvalitatívna entita/event | Nie je súčasť 0.2B. |

### 7.2 Pravidlá

Samostatné entity:

- `Observation`,
- `JobOperation`,
- `TimeRecord`,
- budúci `InspectionResult`, ak bude potrebovať vlastný lifecycle,
- budúca `Nonconformance`.

Job-owned entities:

- `JobOperation`,
- `TimeRecord`,
- `Risk`,
- `QuotationNote`.

Udalosti bez samostatného dlhodobého lifecycle:

- pomocné interné zmeny stavu,
- dočasné systémové udalosti,
- prechodné výpočtové kroky.

Budúce fázy:

- `Measurement`,
- `InspectionResult`,
- `Purchase`,
- `HeatTreatment`,
- `Nonconformance`,
- všeobecný `Event` model.

## 8. Reference Objects a katalógy

### 8.1 Property Catalog

Typ: samostatný autoritatívny katalóg.

Vlastné ID: áno, `PRP-xxxxxx`.

Autoritatívny zoznam: áno.

Kto ho môže meniť: Chief Engineering Knowledge Architect alebo schválený governance proces.

Versioning: `recordVersion`, `revision`, `status`.

Deprecated položka: nemazať po schválení; označiť `Deprecated` a doplniť náhradu.

Aliasy: povolené ako neautoritatívne lookup hodnoty.

Fáza: navrhnúť pre 0.2B, implementovať až po schválení.

### 8.2 Unit Catalog

Typ: samostatný autoritatívny katalóg.

Vlastné ID: áno, `UNT-xxxxxx`.

Autoritatívny zoznam: áno.

Kto ho môže meniť: governance proces s technickou kontrolou.

Versioning: `recordVersion`, `revision`, `status`.

Deprecated položka: ponechať kvôli historickým záznamom, doplniť odporúčanú náhradu.

Aliasy: áno, ale neautoritatívne.

Fáza: odporúčané riešiť skoro, ale samostatne od prvých entity schém.

### 8.3 Condition Type Catalog

Typ: autoritatívny katalóg typov podmienok.

Vlastné ID: navrhované `CND-xxxxxx`.

Autoritatívny zoznam: áno.

Kto ho môže meniť: governance proces.

Versioning: `recordVersion`, `revision`, `status`.

Deprecated položka: označiť a ponechať.

Aliasy: áno, najmä pre migráciu voľných textov.

Fáza: neskôr než základné value object schémy, ale pred masovým ukladaním dát.

### 8.4 Classification Catalog

Typ: potenciálny autoritatívny katalóg.

Vlastné ID: navrhované `CLS-xxxxxx`.

Autoritatívny zoznam: áno, ak EOS začne často používať rovnaké klasifikácie.

Kto ho môže meniť: governance proces a doménový správca.

Versioning: podľa systému klasifikácie a interného `recordVersion`.

Deprecated položka: ponechať s platnosťou a náhradou.

Aliasy: áno, ale viazané na konkrétny klasifikačný systém.

Fáza: neskoršia fáza, v 0.2B stačí value object.

### 8.5 Process Type Catalog

Typ: budúci katalóg výrobných alebo kontrolných typov procesu.

Vlastné ID: zatiaľ neurčené; môže nadviazať na `TEC`.

Autoritatívny zoznam: áno.

Kto ho môže meniť: governance proces s výrobnou kontrolou.

Versioning: `recordVersion`, `revision`, `status`.

Deprecated položka: ponechať pre historické procesy.

Aliasy: áno.

Fáza: neskôr, po základných `ManufacturingProcess` kontraktoch.

### 8.6 Risk Type Catalog

Typ: budúci katalóg typov rizík.

Vlastné ID: zatiaľ neurčené.

Autoritatívny zoznam: áno.

Kto ho môže meniť: governance proces.

Versioning: `recordVersion`, `revision`, `status`.

Deprecated položka: ponechať.

Aliasy: áno.

Fáza: neskôr, pri rozšírení job/risk modelu.

## 9. Aggregate Boundaries

### 9.1 Material aggregate

Aggregate root: `Material`.

Owned objects:

- `PropertyRecord`,
- `Designation`,
- `Classification`,
- `Condition`.

Referenced objects:

- `SourceReference`,
- `NormReference`,
- `Observation`,
- `Property Catalog Entry`,
- `Unit Catalog Entry`.

Transakčná hranica: význam a stav jedného materiálového znalostného záznamu.

Pravidlá integrity:

- vlastnosti musia používať `propertyId`,
- hodnoty s jednotkou musia používať `unitId` v stave `Review` alebo `Approved`,
- technické tvrdenia musia mať `sourceLinks`.

Nesmie sa vnárať priamo:

- celé normy,
- kompletné zdrojové dokumenty,
- job history,
- konkrétne skladové dostupnosti.

### 9.2 StockMaterial aggregate

Aggregate root: `StockMaterial`.

Owned objects:

- `AvailabilityRecord`,
- `CommercialObservation`,
- `Designation`,
- forma alebo rozmery polotovaru ako value objects.

Referenced objects:

- `Material`,
- `Supplier`,
- `SourceReference`,
- `Observation`.

Transakčná hranica: jedna skladová alebo dodávateľská forma.

Pravidlá integrity:

- musí referencovať materiál, ak je známy,
- dostupnosť musí byť časovo označená,
- obchodné pozorovanie nesmie byť cena ani záväzok.

Nesmie sa vnárať priamo:

- úplný `Supplier`,
- úplný `Material`,
- historické nákupy ako trvalé vlastnosti.

### 9.3 Machine aggregate

Aggregate root: `Machine`.

Owned objects:

- `Capability`,
- `PropertyRecord`,
- `AvailabilityRecord`,
- `Condition`.

Referenced objects:

- `ManufacturingProcess`,
- `SourceReference`,
- `Observation`,
- `JobOperation`.

Transakčná hranica: jeden stroj alebo riadený strojový objekt.

Pravidlá integrity:

- neoverené parametre nesmú byť schválené bez zdroja,
- schopnosti musia byť oddelené od konkrétnych zákazkových výkonov.

Nesmie sa vnárať priamo:

- celé zákazky,
- kompletné procesné katalógy.

### 9.4 ManufacturingProcess aggregate

Aggregate root: `ManufacturingProcess`.

Owned objects:

- `Capability`,
- `Condition`,
- procesné `PropertyRecord`,
- `Classification`.

Referenced objects:

- `Machine`,
- `CuttingTool`,
- `NormReference`,
- `SourceReference`.

Transakčná hranica: definícia typu procesu.

Pravidlá integrity:

- garantované časy nepatria do procesu bez oddeleného overeného záznamu,
- procesné možnosti musia mať kontext.

Nesmie sa vnárať priamo:

- konkrétne zákazkové operácie,
- konkrétne reálne výrobné časy.

### 9.5 Job aggregate

Aggregate root: `Job`.

Owned objects:

- `JobOperation`,
- `TimeRecord`,
- `Risk`,
- `QuotationNote`,
- job-specific snapshots.

Referenced objects:

- `Material`,
- `StockMaterial`,
- `Machine`,
- `ManufacturingProcess`,
- `CuttingTool`,
- `Supplier`,
- `SourceReference`,
- `Observation`.

Transakčná hranica: zákazkový prípad.

Pravidlá integrity:

- job-owned ID musia obsahovať ID zákazky,
- historické záznamy sa nesmú prepísať bez auditu,
- job observation nesmie automaticky meniť všeobecné znalostné entity.

Nesmie sa vnárať priamo:

- úplný materiálový katalóg,
- úplný strojový záznam,
- normové texty.

### 9.6 Source/Reference aggregate

Aggregate root: `SourceReference` alebo `NormReference`.

Owned objects:

- zdrojové metadáta,
- interné poznámky o rozsahu a použití.

Referenced objects:

- dokumenty,
- entity používajúce zdroj cez `SourceLink`.

Transakčná hranica: jeden autoritatívny zdroj alebo normatívna referencia.

Pravidlá integrity:

- interpretácia konkrétneho použitia patrí do `SourceLink`,
- externé normy nesmú byť miešané s internými štandardmi.

Nesmie sa vnárať priamo:

- plné znenia noriem bez oprávnenia,
- technické vlastnosti odvodené zo zdroja.

### 9.7 Document aggregate

Aggregate root: `DocumentRecord`.

Owned objects:

- registračné metadáta dokumentu,
- stav, verzia a revízia evidovaného dokumentu,
- odkazy na súvisiace governance objekty.

Referenced objects:

- dokument na disku,
- `SourceReference`,
- `NormReference`,
- `ADR`,
- `RFC`.

Transakčná hranica: evidencia jedného riadeného dokumentu.

Pravidlá integrity:

- `documentVersion` a `schemaVersion` sa nesmú zamieňať,
- governance pôvod dokumentu nie je technická `sourceClass`.

Nesmie sa vnárať priamo:

- technické hodnoty,
- plné dátové entity.

## 10. Relationships

### 10.1 Odporúčané väzby

| Vzťah | Význam | Modelovanie v 0.2B | Budúci Relationship object |
| --- | --- | --- | --- |
| `owns` | vlastníctvo v agregáte | vnorenie alebo hierarchické ID | nie v 0.2B |
| `references` | stabilný odkaz na iný objekt | ID pole | nie v 0.2B |
| `derivedFrom` | odvodené z objektu alebo vstupu | ID pole alebo zoznam vstupov | áno neskôr |
| `observedIn` | pozorované v kontexte | ID na `Job` alebo entitu | áno neskôr |
| `measuredBy` | merané metódou alebo osobou | pole v `Observation` | neskôr podľa potreby |
| `classifiedAs` | zaradené do klasifikácie | `Classification` value object | áno pri katalógu |
| `supportedBy` | podporené zdrojom alebo pozorovaním | `SourceLink`, `Observation` ID | áno neskôr |
| `supersedes` | nahrádza starší význam | `replaces` alebo `supersedes` pole | áno neskôr |
| `replaces` | náhrada záznamu | ID pole | áno neskôr |
| `applicableTo` | použiteľné pre kontext | ID pole alebo `Condition` | áno neskôr |
| `producedBy` | vyrobené procesom alebo operáciou | ID pole | áno neskôr |
| `suppliedBy` | dodané dodávateľom | ID pole | áno neskôr |

### 10.2 Rozhodnutie

Pre 0.2B sa majú väzby modelovať primárne cez explicitné ID polia a vnorené value objects.

Samostatný `Relationship` object sa zatiaľ neimplementuje. Môže vzniknúť neskôr, ak bude potrebné:

- auditovať samotné vzťahy,
- zdrojovať samotnú väzbu,
- mať časovú platnosť väzby,
- exportovať graf znalostí,
- riešiť mnoho-voči-mnohým vzťahy s vlastnými atribútmi.

Grafová databáza nie je súčasťou tohto návrhu.

## 11. Lifecycle rules

### 11.1 Plný lifecycle

Plný lifecycle `Draft`, `Review`, `Approved`, `Deprecated`, `Archived` používajú:

- hlavné entity,
- aggregate roots,
- `SourceReference`,
- `NormReference`,
- `DocumentRecord`,
- budúce catalog entries,
- samostatné `Observation`, ak sa potvrdí ako entita.

### 11.2 Iba verificationStatus

Iba `verificationStatus` alebo podobný stav majú používať:

- `PropertyRecord`,
- `Capability`,
- `SourceLink`,
- hodnotené časti `Observation`,
- vybrané value objects, ak obsahujú overiteľné tvrdenie.

### 11.3 Iba stav rodiča

Stav rodiča dedia:

- `Quantity`,
- `ValueRange`,
- `MeasurementQuality`,
- `Condition`,
- `Designation`,
- `Classification` ako vnorený value object.

### 11.4 Event immutability

Event-like objekty majú byť po schválení prakticky immutable.

Oprava nemá ticho prepísať historickú udalosť. Preferované možnosti:

- nová revízia s jasným `changeSummary`,
- korekčný záznam,
- nové pozorovanie,
- označenie pôvodného záznamu ako sporného.

### 11.5 Append-only history

Append-only históriu majú používať najmä:

- `Observation`,
- historické `AvailabilityRecord`,
- významné `CommercialObservation`,
- budúce výrobné udalosti,
- budúce inspection alebo measurement záznamy.

### 11.6 Osobitné prípady

`Observation`: samostatná entita, auditovateľná, append-only orientovaná.

`PropertyRecord`: value object bez plného lifecycle, ale s `verificationStatus`.

`AvailabilityRecord`: value object v 0.2B, časovo závislý a ideálne append-only.

`CommercialObservation`: value object, nie záväzok; historicky citlivé záznamy majú byť append-only.

`Catalog Entry`: plný lifecycle, nemazať po schválení.

`Derived Result`: nesmie meniť autoritatívne dáta; má byť reprodukovateľný a auditovateľný.

## 12. Identity rules

### 12.1 Prefixy odporúčané na zavedenie

Tieto prefixy treba zaviesť v `EOS-003` pred alebo počas schvaľovania Phase 0.2B:

- `RFC-xxxx` pre RFC dokumenty,
- `OBS-xxxxxx` pre `Observation`,
- `PRP-xxxxxx` pre Property Catalog Entry,
- `UNT-xxxxxx` pre Unit Catalog Entry.

### 12.2 Prefixy zatiaľ ponechané ako návrh

Tieto prefixy sú užitočné, ale nemusia byť zavedené okamžite:

- `CLS-xxxxxx` pre Classification Catalog Entry,
- `CND-xxxxxx` pre Condition Type Catalog Entry,
- `REL-xxxxxx` pre Relationship object,
- `EVT-xxxxxx` pre všeobecný Event object.

### 12.3 Pravidlá

- Vnorené value objects nemajú vlastné stabilné ID.
- ID katalógovej položky nie je ID konkrétneho vnoreného použitia.
- Job-owned entity majú používať hierarchické ID podľa ADR-0008.
- `DocumentRecord` používa ID dokumentu, ktorý eviduje.
- `SourceLink` nemá byť samostatná entita; je to väzba na `SourceReference`.

Tento RFC nemení `EOS-003`. Navrhuje iba ďalší governance krok.

## 13. Immutability and history

Immutable po schválení majú byť:

- event-like fakty,
- historické pozorovania,
- snapshoty vstupov,
- schválené value object hodnoty v rámci revízie rodiča.

Revidujú sa:

- entity pri zmene významu alebo oprave,
- katalógové položky,
- `DocumentRecord`,
- `SourceReference` a `NormReference`.

Nahrádzajú sa novou verziou alebo náhradou:

- deprecated katalógové položky,
- zastarané materiálové alebo procesné záznamy,
- normatívne referencie po zmene vydania,
- dokumenty po zásadnej zmene.

Append-only majú byť:

- `Observation`,
- významné udalosti,
- historická dostupnosť,
- obchodné pozorovania použité pri rozhodnutí,
- snapshoty vstupov odvodeného výsledku.

Fyzicky odstránené môžu byť iba:

- pracovné `Draft` záznamy bez externého odkazu,
- chybné dočasné záznamy pred pridelením autoritatívneho významu,
- technické pomocné súbory mimo riadenej dokumentácie.

Audit trail sa zachováva cez:

- stabilné ID,
- `recordVersion`,
- `revision`,
- `changeSummary`,
- `createdAt`,
- `createdBy`,
- `updatedAt`,
- `updatedBy`,
- `sourceLinks`,
- append-only udalosti alebo korekčné záznamy.

## 14. Derived Results

`Derived Result` je kategória pre budúce výpočty, odhady, porovnania, odporúčania a AI návrhy.

Príklady:

- odhad výrobného času,
- odhad ceny,
- porovnanie dvoch materiálov,
- odporúčanie technológie,
- AI návrh rizika alebo poznámky.

Pravidlá:

- `Derived Result` nie je zdrojová znalosť.
- Musí niesť vstupy alebo odkazy na snapshot vstupov.
- Musí niesť verziu kalkulačnej logiky alebo rozhodovacieho modelu.
- Musí byť reprodukovateľný v rozsahu, ktorý povoľuje použitý nástroj.
- Musí odlíšiť vypočítaný výsledok od schválenej znalosti.
- Nesmie automaticky meniť autoritatívne dáta.
- Ak sa použije ako podklad rozhodnutia, musí byť auditovateľný.

## 15. Rozhodovacia tabuľka

| Object | Category | Stable ID | Own lifecycle | Aggregate root | Source links | Versioned | Immutable | Owned by | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Material` | Entity | `MAT-xxxx` | Yes | Yes | Yes | Yes | No | Self | Znalostný objekt materiálu. |
| `StockMaterial` | Entity | `POL-xxxx` | Yes | Yes | Yes | Yes | No | Self | Forma alebo dostupný polotovar. |
| `PropertyRecord` | Value Object | No | No | No | Yes | Via parent | After approval | Parent entity | Má `verificationStatus`. |
| `Quantity` | Value Object | No | No | No | Via parent | Via parent | Yes | Parent object | Jedna hodnota s `unitId`. |
| `Condition` | Value Object | No | No | No | Optional | Via parent | Yes | Parent object | Používa `evaluationMode`. |
| `Observation` | Entity / Event-like Evidence | `OBS-xxxxxx` | Yes | Yes | Yes | Yes | Append-only | Self or Job context | Neprepisuje vlastnosti automaticky. |
| `SourceReference` | Reference Object | `SRC-xxxxxx` | Yes | Yes | Optional | Yes | No | Self | Autoritatívny zdroj. |
| `NormReference` | Reference Object | `NRM-xxxx` | Yes | Yes | Yes | Yes | No | Self | Externá normatívna referencia. |
| `Machine` | Entity | `MAC-xxxx` | Yes | Yes | Yes | Yes | No | Self | Výrobné zariadenie. |
| `ManufacturingProcess` | Entity | `TEC-xxxx` | Yes | Yes | Yes | Yes | No | Self | Typ procesu. |
| `Supplier` | Entity | `SUP-xxxx` | Yes | Yes | Yes | Yes | No | Self | Dodávateľ alebo partner. |
| `Job` | Entity | `JOB-yyyy-xxxx` | Yes | Yes | Yes | Yes | No | Self | Zákazkový agregát. |
| `JobOperation` | Job-owned Entity | `JOB-yyyy-xxxx-OP-xxx` | Yes | No | Yes | Yes | No | `Job` | Operácia zákazky. |
| `TimeRecord` | Job-owned Entity | `JOB-yyyy-xxxx-OP-xxx-TM-xxx` | Yes | No | Yes | Yes | Append-only preferred | `JobOperation` | Časový záznam. |
| `AvailabilityRecord` | Value Object / Event-like | No | No | No | Yes | Via parent | Append-only preferred | Parent entity | Časovo závislá dostupnosť. |
| `CommercialObservation` | Value Object / Event-like | No | No | No | Yes | Via parent | Append-only preferred | Parent entity | Nie je cena ani záväzok. |
| `Classification` | Value Object | No | No | No | Optional | Via parent | Yes | Parent entity | Budúci `CLS-xxxxxx` katalóg možný. |
| Unit Catalog Entry | Catalog Entry | `UNT-xxxxxx` | Yes | Yes | Yes | Yes | No | Unit Catalog | Autoritatívna jednotka. |
| Property Catalog Entry | Catalog Entry | `PRP-xxxxxx` | Yes | Yes | Yes | Yes | No | Property Catalog | Autoritatívny význam vlastnosti. |
| `DocumentRecord` | Document Object | Document ID | Yes | Yes | Optional | Yes | No | Self | Eviduje dokument, nie jeho obsah. |
| `Derived Result` | Derived Result | Later | Yes if stored | Maybe | Input links | Yes | Reproducible snapshot | Calculation context | Nie je zdrojová znalosť. |

## 16. Alternatívy

### 16.1 Všetko ako entity

Výhoda: každá vec má vlastné ID a samostatný audit.

Nevýhoda: vysoká komplexita, veľa malých záznamov, ťažkopádna práca pred overením dátových vzorov.

Riziko: z `Quantity`, `Condition` alebo `Designation` by sa stali zbytočne ťažké objekty.

### 16.2 Všetko ako vnorené objects

Výhoda: jednoduché JSON súbory a rýchlejší začiatok.

Nevýhoda: slabá citovateľnosť, slabá história, ťažké zdieľanie zdrojov a katalógových významov.

Riziko: `SourceReference`, `Observation` a katalógy by stratili autoritatívnosť.

### 16.3 Hybridný DDD model

Výhoda: entity majú jasnú identitu, value objects zostávajú jednoduché, katalógy riadia význam a agregáty chránia integritu.

Nevýhoda: vyžaduje disciplínu pri hraniciach agregátov a pri rozhodovaní, kedy objekt povýšiť na entitu.

Riziko: bez dokumentovaných pravidiel môže vzniknúť nekonzistentné používanie relationship objektov.

Odporúčanie: zvoliť hybridný DDD model.

### 16.4 Jednoduchý relačný model bez taxonómie

Výhoda: blízke budúcej databázovej implementácii.

Nevýhoda: predčasne rieši tabuľky namiesto významu znalostí.

Riziko: systém by migroval do databázy bez jasného modelu identity, lifecycle a vlastníctva.

## 17. Dopad na RFC-0001

RFC-0002 potvrdzuje tieto rozhodnutia RFC-0001:

- `Quantity`, `ValueRange` a `MeasurementQuality` majú byť oddelené,
- `PropertyRecord` má byť value object s `verificationStatus`,
- `Observation` má byť oddelený koncept od `PropertyRecord`,
- `propertyId` má používať budúci `PRP-xxxxxx`,
- `unitId` má používať budúci `UNT-xxxxxx`,
- `rawUnitText` nemá byť autoritatívne,
- porovnateľnosť nesmie stáť na názve vlastnosti alebo texte jednotky.

RFC-0002 spresňuje:

- `Observation` má byť samostatná entita a event-like evidence object,
- `MeasurementQuality` je preferovaný názov pred `ValueQuality`,
- `Classification` má zostať value object v 0.2B s možnosťou budúceho katalógu,
- `AvailabilityRecord` a `CommercialObservation` sú value objects s event-like správaním,
- katalógové položky majú byť samostatné catalog entries.

Môže sa neskôr zmeniť:

- či `Observation` bude globálna entita alebo job-owned entita,
- či `Classification Catalog` vznikne v 0.2B alebo neskôr,
- či vznikne samostatný `Relationship` object,
- či vznikne všeobecný `Event` model.

Odporúčanie: RFC-0001 môže po posúdení RFC-0002 prejsť z `Review` do `Accepted`, ak bude prijaté, že RFC-0002 spresňuje taxonómiu bez popretia jadra RFC-0001.

## 18. Governance

Odporúča sa zaviesť prefix:

- `RFC-xxxx`

Navrhovaný lifecycle RFC:

- `Draft`,
- `Review`,
- `Accepted`,
- `Rejected`,
- `Superseded`.

Navrhované pravidlo:

- RFC opisuje návrh,
- ADR zaznamenáva prijaté architektonické rozhodnutie,
- implementácia musí odkazovať na `Accepted` RFC alebo `Accepted` ADR.

Ďalší governance krok:

1. Schváliť alebo upraviť RFC-0002.
2. Aktualizovať `EOS-003` o `RFC-xxxx` a schválené nové prefixy.
3. Podľa rozsahu vytvoriť ADR pre taxonómiu objektov alebo pre RFC proces.
4. Až potom začať implementáciu Phase 0.2B kontraktov.

Tento RFC nemení `EOS-003` a nevytvára ADR.

## 19. Otvorené otázky

- Má byť `Observation` globálna entita alebo job-owned entita?
- Má `Measurement` vzniknúť ako subtype `Observation`, alebo ako samostatná entita?
- Kedy presne zaviesť Property Catalog a Unit Catalog?
- Má mať `Classification Catalog` vlastný prefix `CLS-xxxxxx` už v 0.2B?
- Má mať `Condition Type Catalog` prefix `CND-xxxxxx` už v 0.2B?
- Kedy je potrebný samostatný `Relationship` object?
- Má `Derived Result` dostať vlastný prefix alebo ostať výstupom konkrétneho kalkulačného modulu?
- Ktorý dokument alebo ADR definitívne zavedie RFC lifecycle?

## 20. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-07-14 | 0.1 | 0 | Chief Engineering Knowledge Architect + Codex | Initial RFC draft for engineering object taxonomy |
