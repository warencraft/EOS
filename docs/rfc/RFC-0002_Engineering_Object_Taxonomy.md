# RFC-0002 - Engineering Object Taxonomy

**Project:** EOS - Engineering Operating System  
**RFC ID:** RFC-0002  
**Version:** 0.1  
**Revision:** 2  
**Status:** Review  
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

### 2.1 Engineering Knowledge Layer

Tento RFC navrhuje zaviesť architektonickú vrstvu **Engineering Knowledge Layer** medzi governance pravidlá a konkrétne znalostné entity.

Odporúčané vrstvy EOS:

1. Governance Layer: manifest, identifikácia, lifecycle, ADR, RFC, dokumentačné pravidlá.
2. Engineering Knowledge Layer: taxonómia objektov, vlastnosti, jednotky, podmienky, pozorovania, rozhodnutia, porovnateľnosť, evidence pravidlá a odvodené výsledky.
3. Knowledge Entity Layer: `Material`, `StockMaterial`, `Machine`, `ManufacturingProcess`, `Supplier`, `Job` a ďalšie doménové entity.
4. Application and Engine Layer: validácia, quotation engine, manufacturing engine, AI layer, exporty a automatizácia.

Účel Engineering Knowledge Layer je zabrániť tomu, aby sa všeobecné znalostné pravidlá opakovane a nekonzistentne implementovali priamo v jednotlivých entitách.

### 2.2 Odporúčané fázovanie po tomto RFC

Pred implementáciou plných knowledge entities sa odporúča rozdeliť nasledujúcu prácu takto:

1. `0.2B.1 Knowledge Core Contracts` - základné value objects, `PropertyRecord`, first-class `Observation`, source/evidence pravidlá a konceptuálna decision boundary.
2. `0.2B.2 Knowledge Catalogs` - Property Catalog, Unit Catalog, Condition Type Catalog a Classification Catalog podľa schváleného rozsahu.
3. `0.2C Knowledge Entities` - `Material`, `StockMaterial`, `Machine`, `ManufacturingProcess`, `Supplier`, `Job` a ďalšie entity.

Toto fázovanie znižuje riziko, že entitné schémy vzniknú skôr než spoločné znalostné primitíva.

`Decision`, `Snapshot` a `Derived Result` sú pre `0.2B.1` architektonicky dôležité pojmy, ale ich samostatné stored kontrakty nemusia patriť do minimálneho prvého scope. Minimálny rozsah má zachovať decision boundary bez predčasného modelovania celého rozhodovacieho a výpočtového auditu.

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

Pravidlo: Aggregate Root nikdy nevlastní iný Aggregate Root. Môže ho iba referencovať stabilným ID. Ak objekt potrebuje vlastné ID, vlastný lifecycle a vlastnú auditnú históriu, nemá byť vnorený ako vlastnený objekt iného agregátu.

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

### 3.12 Decision

Definícia: auditovateľný záznam, že engineer alebo schválený proces prijal, odmietol alebo podmienene prijal tvrdenie, pozorovanie, odvodený výsledok alebo odporúčanie.

Vlastnosti:

- vlastné stabilné ID: odporúčané v budúcej fáze,
- vlastný lifecycle: áno,
- samostatná existencia: áno, ak ovplyvňuje znalostný alebo obchodný výsledok,
- citovateľnosť: áno,
- versioned/revised: áno,
- auditovateľnosť: áno,
- `sourceLinks`: áno, ak rozhodnutie vychádza zo zdrojovaných tvrdení.

Typické vstupy:

- `Observation`,
- `Derived Result`,
- `Snapshot`,
- engineer approval,
- `SourceReference`,
- súvisiace entity alebo katalógové položky.

Nepatrí sem:

- samotné meranie,
- automatický výpočet bez schválenia,
- autoritatívna vlastnosť bez rozhodovacieho kroku.

`Decision` je dôležitý najmä pre budúci Quotation Engine, Manufacturing Engine a AI layer, pretože oddeľuje návrh alebo dôkaz od prijatého inžinierskeho rozhodnutia.

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

Lifecycle owner: `Observation` sám. Kontext vzniku sa nemá riešiť rozdelením na dva typy pozorovania, ale poľom `observationScope`.

Aggregate root: odporúčanie je áno, ak má `OBS-xxxxxx` globálne ID a môže podporovať viac tvrdení.

Rozlíšenie identity: first-class `Observation` má stabilné `OBS-xxxxxx`, vlastný lifecycle a môže byť referencovaná viacerými objektmi. Embedded observation record, napríklad `AvailabilityRecord` alebo `CommercialObservation`, je vlastnený rodičovskou entitou, nemá vlastné globálne `OBS` ID a nemá sa označovať ako plnohodnotná `Observation` entity.

Môže vlastniť:

- hodnotu pozorovania,
- podmienky,
- metódu,
- zdrojové väzby,
- stav overenia,
- snapshot vstupov alebo kontextu, ak je potrebný pre audit.

Iba referencuje:

- `Job`,
- `Project` alebo `Experiment`, ak budú zavedené v budúcnosti,
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

Odporúčané konceptuálne hodnoty `observationScope`:

- `GLOBAL` - pozorovanie má všeobecný dôkazový význam mimo jednej zákazky,
- `JOB` - pozorovanie vzniklo v konkrétnej zákazke a primárne slúži jej auditu,
- `PROJECT` - pozorovanie vzniklo v širšom internom projekte alebo programe,
- `EXPERIMENT` - pozorovanie vzniklo v skúške, experimente alebo overovacej aktivite.

Tento model je preferovaný pred dvoma samostatnými typmi `Observation`, pretože zachováva jednotný evidence model a zároveň umožňuje rozlíšiť kontext vzniku.

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

Kategória: embedded claim-like value object.

Vlastné ID: nie; používa `propertyId` ako odkaz na budúci Property Catalog, nie ako identitu konkrétneho vnoreného záznamu.

Vlastný `verificationStatus`: áno.

Lifecycle: dedí od rodiča.

Znovupoužitie medzi entitami: áno ako štruktúra; konkrétna inštancia patrí rodičovi.

Samostatná citácia: áno cez rodiča a konkrétny `SourceLink`.

Immutability: odporúčané immutable v rámci schválenej revízie rodiča.

Poznámka: `PropertyRecord` nie je obyčajná hodnota. Nesie tvrdenie o vlastnosti, zdroje a stav overenia. Preto má byť v dokumentácii aj validácii chápaný ako vnorený claim-like objekt, nie ako samostatná entita.

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

Kategória: embedded observation record v 0.2B, potenciálne samostatná event-like entita v budúcnosti.

Vlastné ID: nie v 0.2B.

Vlastný `verificationStatus`: odporúčané áno alebo `observationStatus`, pretože dostupnosť je časovo závislá.

Lifecycle: dedí od rodiča.

Znovupoužitie medzi entitami: áno ako štruktúra.

Samostatná citácia: áno cez `sourceLinks`.

Immutability: odporúčané append-only v rámci historických záznamov dostupnosti.

Poznámka: dostupnosť je časovo závislé pozorovanie. Nesmie sa správať ako trvalá vlastnosť materiálu, stroja alebo dodávateľa.

### 5.10 `CommercialObservation`

Kategória: embedded observation record v 0.2B, potenciálne samostatná event-like entita v budúcnosti.

Vlastné ID: nie v 0.2B.

Vlastný `verificationStatus`: odporúčané `observationStatus` a `confidenceLevel`.

Lifecycle: dedí od rodiča.

Znovupoužitie medzi entitami: áno ako štruktúra.

Samostatná citácia: áno cez `sourceLinks`.

Immutability: odporúčané append-only, ak ovplyvňuje rozhodnutie alebo audit.

Poznámka: obchodné pozorovanie môže byť vstupom pre budúci `Decision`, ale samo nie je cena, cenová ponuka ani právny záväzok.

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

## 7. Decision

`Decision` je samostatný budúci objekt Engineering Knowledge Layer.

Účel: zachytiť rozhodnutie, že určitý dôkaz, výsledok alebo odporúčanie bol prijatý, odmietnutý alebo prijatý s podmienkou.

Minimálne budúce polia:

- `id`,
- `decisionType`,
- `decisionStatus`,
- `decidedAt`,
- `decidedBy`,
- `inputObservationIds`,
- `inputDerivedResultIds`,
- `inputSnapshotIds`,
- `relatedEntityIds`,
- `decisionRationale`,
- `conditions`,
- `sourceLinks`,
- `changeSummary`.

Pravidlá:

- `Decision` nie je `Observation`.
- `Decision` nie je `Derived Result`.
- `Decision` je schvaľovací alebo zamietací akt nad vstupmi.
- AI návrh sa môže stať vstupom rozhodnutia, ale nie rozhodnutím samotným.
- Engineer approval musí byť auditovateľný.
- Rozhodnutie môže viesť k vytvoreniu alebo zmene autoritatívneho záznamu, ale táto zmena musí zostať samostatne verzovaná.

Návrh pre minimálny rozsah: `Decision` je v `0.2B.1` konceptuálna závislosť a boundary pravidlo, nie povinný samostatný stored kontrakt. Samostatný kontrakt `Decision` má vzniknúť až po samostatnom governance rozhodnutí alebo vtedy, keď prvé kontrakty potrebujú ukladať prijatie, odmietnutie alebo povýšenie tvrdenia ako auditovateľný objekt.

## 8. Events

### 8.1 Rozlíšenie pojmov

| Objekt | Odporúčané zaradenie | Poznámka |
| --- | --- | --- |
| `Event` | generická kategória | Zatiaľ nie samostatná entita v 0.2B. |
| `Observation` | entita + event-like evidence object | Má `OBS-xxxxxx` a `observationScope`. |
| `JobOperation` | job-owned entity | Má `JOB-yyyy-xxxx-OP-xxx`. Nie je iba event. |
| `TimeRecord` | job-owned entity | Má `JOB-yyyy-xxxx-OP-xxx-TM-xxx`. |
| `InspectionResult` | budúca Observation subtype alebo entita | Patrí do budúcej fázy. |
| `Measurement` | budúca Observation subtype | Patrí do budúcej fázy. |
| `Purchase` | budúca obchodná alebo skladová udalosť | Nie je súčasť 0.2B. |
| `HeatTreatment` | budúca výrobná udalosť alebo procesný záznam | Nie je súčasť 0.2B. |
| `Nonconformance` | budúca kvalitatívna entita/event | Nie je súčasť 0.2B. |
| `Decision` | schvaľovací event-like objekt | V `0.2B.1` je boundary koncept; samostatný stored kontrakt je odložený, ak nebude výslovne schválený. |

### 8.2 Pravidlá

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

## 9. Reference Objects a katalógy

### 9.0 Catalog hierarchy

Katalógy majú mať spoločný metadátový základ, ale governance významovo sa odporúča rozlišovať dve skupiny:

- Reference Catalog,
- Knowledge Catalog.

Reference Catalog obsahuje položky, ktoré reprezentujú externý, všeobecný alebo technicky referenčný význam. Typické príklady:

- Unit Catalog,
- Classification Catalog,
- typy zdrojov,
- externé referenčné systémy.

Knowledge Catalog obsahuje položky, ktoré definujú interný EOS význam používaný pri rozhodovaní a znalostných tvrdeniach. Typické príklady:

- Property Catalog,
- Condition Type Catalog,
- Process Type Catalog,
- Risk Type Catalog,
- Capability Type Catalog, ak vznikne.

Spoločný model katalógovej položky môže zostať jednotný, ale pravidlá správy, schvaľovania a zmeny sa majú líšiť podľa toho, či ide o Reference Catalog alebo Knowledge Catalog.

Fázovanie katalógov:

- Knowledge Core Contracts patria do `0.2B.1`.
- Property Catalog a Unit Catalog patria do `0.2B.2`.
- Classification Catalog a Condition Type Catalog patria do `0.2B.2`.
- Konkrétne Knowledge Entities patria do `0.2C`.

### 9.1 Property Catalog

Typ: samostatný autoritatívny katalóg.

Vlastné ID: áno, `PRP-xxxxxx`.

Autoritatívny zoznam: áno.

Kto ho môže meniť: Chief Engineering Knowledge Architect alebo schválený governance proces.

Versioning: `recordVersion`, `revision`, `status`.

Deprecated položka: nemazať po schválení; označiť `Deprecated` a doplniť náhradu.

Aliasy: povolené ako neautoritatívne lookup hodnoty.

Fáza: plný Property Catalog patrí do `0.2B.2`. Stabilné `PRP-xxxxxx` ID je potrebné pripraviť pred `0.2B.1`.

### 9.2 Unit Catalog

Typ: samostatný autoritatívny katalóg.

Vlastné ID: áno, `UNT-xxxxxx`.

Autoritatívny zoznam: áno.

Kto ho môže meniť: governance proces s technickou kontrolou.

Versioning: `recordVersion`, `revision`, `status`.

Deprecated položka: ponechať kvôli historickým záznamom, doplniť odporúčanú náhradu.

Aliasy: áno, ale neautoritatívne.

Fáza: plný Unit Catalog patrí do `0.2B.2`. Stabilné `UNT-xxxxxx` ID je potrebné pripraviť pred `0.2B.1`.

### 9.3 Condition Type Catalog

Typ: autoritatívny katalóg typov podmienok.

Vlastné ID: navrhované `CND-xxxxxx`.

Autoritatívny zoznam: áno.

Kto ho môže meniť: governance proces.

Versioning: `recordVersion`, `revision`, `status`.

Deprecated položka: označiť a ponechať.

Aliasy: áno, najmä pre migráciu voľných textov.

Fáza: `0.2B.2`. V `0.2B.1` môže `Condition` existovať ako value-object kontrakt alebo odkaz bez autoritatívnej katalógovej entity.

### 9.4 Classification Catalog

Typ: potenciálny autoritatívny katalóg.

Vlastné ID: navrhované `CLS-xxxxxx`.

Autoritatívny zoznam: áno, ak EOS začne často používať rovnaké klasifikácie.

Kto ho môže meniť: governance proces a doménový správca.

Versioning: podľa systému klasifikácie a interného `recordVersion`.

Deprecated položka: ponechať s platnosťou a náhradou.

Aliasy: áno, ale viazané na konkrétny klasifikačný systém.

Fáza: `0.2B.2`, ak sa potvrdí potreba. V `0.2B.1` môže `Classification` existovať ako value-object kontrakt alebo odkaz bez autoritatívnej katalógovej entity.

### 9.5 Process Type Catalog

Typ: budúci katalóg výrobných alebo kontrolných typov procesu.

Vlastné ID: zatiaľ neurčené; môže nadviazať na `TEC`.

Autoritatívny zoznam: áno.

Kto ho môže meniť: governance proces s výrobnou kontrolou.

Versioning: `recordVersion`, `revision`, `status`.

Deprecated položka: ponechať pre historické procesy.

Aliasy: áno.

Fáza: neskôr, po základných `ManufacturingProcess` kontraktoch.

### 9.6 Risk Type Catalog

Typ: budúci katalóg typov rizík.

Vlastné ID: zatiaľ neurčené.

Autoritatívny zoznam: áno.

Kto ho môže meniť: governance proces.

Versioning: `recordVersion`, `revision`, `status`.

Deprecated položka: ponechať.

Aliasy: áno.

Fáza: neskôr, pri rozšírení job/risk modelu.

## 10. Aggregate Boundaries

Všeobecné pravidlo: Aggregate Root nikdy nevlastní iný Aggregate Root. Vzťah medzi aggregate roots musí byť modelovaný referenciou cez stabilné ID, nie vnorením celého objektu.

### 10.1 Material aggregate

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

### 10.2 StockMaterial aggregate

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

### 10.3 Machine aggregate

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

### 10.4 ManufacturingProcess aggregate

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

### 10.5 Job aggregate

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
- Ak je `Observation` samostatný aggregate root s `OBS-xxxxxx`, `Job` ho iba referencuje.
- Ak má byť pozorovanie úplne vlastnené zákazkou, musí byť job-owned entity alebo vnorený job-local observation record bez globálnej identity.

Nesmie sa vnárať priamo:

- úplný materiálový katalóg,
- úplný strojový záznam,
- normové texty.

### 10.6 Source/Reference aggregate

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

### 10.7 Document aggregate

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

## 11. Relationships

### 11.1 Odporúčané väzby

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

### 11.2 Rozhodnutie

Pre 0.2B sa majú väzby modelovať primárne cez explicitné ID polia a vnorené value objects.

Samostatný `Relationship` object sa zatiaľ neimplementuje. Môže vzniknúť neskôr, ak bude potrebné:

- auditovať samotné vzťahy,
- zdrojovať samotnú väzbu,
- mať časovú platnosť väzby,
- exportovať graf znalostí,
- riešiť mnoho-voči-mnohým vzťahy s vlastnými atribútmi.

Grafová databáza nie je súčasťou tohto návrhu.

Odporúčanie: `Relationship` má byť v budúcnosti first-class object, ale nie v 0.2B. Pre `0.2B.1` a `0.2B.2` stačia explicitné ID referencie. First-class `Relationship` má vzniknúť až vtedy, keď vzťah nesie vlastnú identitu, vlastné `sourceLinks`, `verificationStatus`, časovú platnosť, audit alebo lifecycle, vlastné vlastnosti alebo význam pre graph export.

## 12. Lifecycle rules

### 12.1 Plný lifecycle

Plný lifecycle `Draft`, `Review`, `Approved`, `Deprecated`, `Archived` používajú:

- hlavné entity,
- aggregate roots,
- `SourceReference`,
- `NormReference`,
- `DocumentRecord`,
- budúce catalog entries,
- samostatné `Observation`, ak sa potvrdí ako entita.

### 12.2 Iba verificationStatus

Iba `verificationStatus` alebo podobný stav majú používať:

- `PropertyRecord`,
- `Capability`,
- `SourceLink`,
- hodnotené časti `Observation`,
- vybrané value objects, ak obsahujú overiteľné tvrdenie.

### 12.3 Iba stav rodiča

Stav rodiča dedia:

- `Quantity`,
- `ValueRange`,
- `MeasurementQuality`,
- `Condition`,
- `Designation`,
- `Classification` ako vnorený value object.

### 12.4 Event immutability

Event-like objekty majú byť po schválení prakticky immutable.

Oprava nemá ticho prepísať historickú udalosť. Preferované možnosti:

- nová revízia s jasným `changeSummary`,
- korekčný záznam,
- nové pozorovanie,
- označenie pôvodného záznamu ako sporného.

### 12.5 Append-only history

Append-only históriu majú používať najmä:

- `Observation`,
- historické `AvailabilityRecord`,
- významné `CommercialObservation`,
- budúce výrobné udalosti,
- budúce inspection alebo measurement záznamy.

### 12.6 Osobitné prípady

`Observation`: samostatná entita, auditovateľná, append-only orientovaná, s povinným rozhodnutím o `observationScope`.

`PropertyRecord`: embedded claim-like value object bez plného lifecycle, ale s `verificationStatus`.

`AvailabilityRecord`: embedded observation record v 0.2B, časovo závislý a ideálne append-only.

`CommercialObservation`: embedded observation record, nie záväzok; historicky citlivé záznamy majú byť append-only.

`Catalog Entry`: plný lifecycle, nemazať po schválení.

`Derived Result`: nesmie meniť autoritatívne dáta; má byť reprodukovateľný a auditovateľný.

`Decision`: samostatný budúci objekt s plným auditom, ktorý spája dôkazy, odvodené výsledky a engineer approval.

## 13. Identity rules

### 13.1 Prefixy odporúčané na zavedenie

Tieto prefixy treba zaviesť v `EOS-003` pred alebo počas schvaľovania Phase 0.2B:

- `RFC-xxxx` pre RFC dokumenty,
- `OBS-xxxxxx` pre `Observation`,
- `PRP-xxxxxx` pre Property Catalog Entry,
- `UNT-xxxxxx` pre Unit Catalog Entry.

### 13.2 Prefixy zatiaľ ponechané ako návrh

Tieto prefixy sú užitočné, ale nemusia byť zavedené okamžite:

- `CLS-xxxxxx` pre Classification Catalog Entry,
- `CND-xxxxxx` pre Condition Type Catalog Entry,
- `REL-xxxxxx` pre Relationship object,
- `EVT-xxxxxx` pre všeobecný Event object.

### 13.3 Pravidlá

- Vnorené value objects nemajú vlastné stabilné ID.
- ID katalógovej položky nie je ID konkrétneho vnoreného použitia.
- Job-owned entity majú používať hierarchické ID podľa ADR-0008.
- `DocumentRecord` používa ID dokumentu, ktorý eviduje.
- `SourceLink` nemá byť samostatná entita; je to väzba na `SourceReference`.
- `Decision` bude potrebovať vlastný prefix, ak sa v `0.2B.1` potvrdí ako ukladaný objekt.

Tento RFC nemení `EOS-003`. Navrhuje iba ďalší governance krok.

## 14. Immutability and history

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
- rozhodnutia, ktoré už ovplyvnili autoritatívny záznam alebo quotation/manufacturing výstup.

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
- samostatné `Decision` záznamy tam, kde nejde iba o technickú opravu, ale o prijatie alebo odmietnutie významu.

## 15. Derived Results

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
- Ak je prijatý engineerom, výsledkom nemá byť tichá zmena dát, ale samostatný `Decision`.

## 16. Rozhodovacia tabuľka

| Object | Category | Stable ID | Own lifecycle | Aggregate root | Source links | Versioned | Immutable | Owned by | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Material` | Entity | `MAT-xxxx` | Yes | Yes | Yes | Yes | No | Self | Znalostný objekt materiálu. |
| `StockMaterial` | Entity | `POL-xxxx` | Yes | Yes | Yes | Yes | No | Self | Forma alebo dostupný polotovar. |
| `PropertyRecord` | Embedded Claim-like Value Object | No | No | No | Yes | Via parent | After approval | Parent entity | Má `verificationStatus`. |
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
| `AvailabilityRecord` | Embedded Observation Record | No | No | No | Yes | Via parent | Append-only preferred | Parent entity | Časovo závislá dostupnosť. |
| `CommercialObservation` | Embedded Observation Record | No | No | No | Yes | Via parent | Append-only preferred | Parent entity | Nie je cena ani záväzok. |
| `Classification` | Value Object | No | No | No | Optional | Via parent | Yes | Parent entity | Budúci `CLS-xxxxxx` katalóg možný. |
| Unit Catalog Entry | Catalog Entry | `UNT-xxxxxx` | Yes | Yes | Yes | Yes | No | Unit Catalog | Autoritatívna jednotka. |
| Property Catalog Entry | Catalog Entry | `PRP-xxxxxx` | Yes | Yes | Yes | Yes | No | Property Catalog | Autoritatívny význam vlastnosti. |
| `DocumentRecord` | Document Object | Document ID | Yes | Yes | Optional | Yes | No | Self | Eviduje dokument, nie jeho obsah. |
| `Snapshot` | Snapshot | Later | Append-only | Maybe | Input links | Replaced by new snapshot | Yes | Calculation or decision context | Zmrazený obraz vstupov. |
| `Derived Result` | Derived Result | Later | Yes if stored | Maybe | Input links | Yes | Reproducible snapshot | Calculation context | Nie je zdrojová znalosť. |
| `Decision` | Decision | Later | Yes | Maybe | Yes | Yes | Append-only preferred | Engineering Knowledge Layer | Engineer approval nad dôkazmi alebo výsledkami. |

## 17. Alternatívy

### 17.1 Všetko ako entity

Výhoda: každá vec má vlastné ID a samostatný audit.

Nevýhoda: vysoká komplexita, veľa malých záznamov, ťažkopádna práca pred overením dátových vzorov.

Riziko: z `Quantity`, `Condition` alebo `Designation` by sa stali zbytočne ťažké objekty.

### 17.2 Všetko ako vnorené objects

Výhoda: jednoduché JSON súbory a rýchlejší začiatok.

Nevýhoda: slabá citovateľnosť, slabá história, ťažké zdieľanie zdrojov a katalógových významov.

Riziko: `SourceReference`, `Observation` a katalógy by stratili autoritatívnosť.

### 17.3 Hybridný DDD model

Výhoda: entity majú jasnú identitu, value objects zostávajú jednoduché, katalógy riadia význam a agregáty chránia integritu.

Nevýhoda: vyžaduje disciplínu pri hraniciach agregátov a pri rozhodovaní, kedy objekt povýšiť na entitu.

Riziko: bez dokumentovaných pravidiel môže vzniknúť nekonzistentné používanie relationship objektov.

Odporúčanie: zvoliť hybridný DDD model.

### 17.4 Jednoduchý relačný model bez taxonómie

Výhoda: blízke budúcej databázovej implementácii.

Nevýhoda: predčasne rieši tabuľky namiesto významu znalostí.

Riziko: systém by migroval do databázy bez jasného modelu identity, lifecycle a vlastníctva.

### 17.5 Hybridný DDD model s Engineering Knowledge Layer

Výhoda: zachováva jasné entity a value objects, ale dopĺňa medzivrstvu pre znalostné primitíva, evidence, decisions, katalógy a porovnateľnosť.

Nevýhoda: vyžaduje jeden stabilizačný krok navyše pred entitnými schémami.

Odporúčanie: táto alternatíva nahrádza jednoduchý hybridný DDD model ako preferovaný smer.

## 18. Dopad na RFC-0001

RFC-0002 potvrdzuje tieto rozhodnutia RFC-0001:

- `Quantity`, `ValueRange` a `MeasurementQuality` majú byť oddelené,
- `PropertyRecord` má byť embedded claim-like value object s `verificationStatus`,
- `Observation` má byť oddelený koncept od `PropertyRecord`,
- `propertyId` má používať budúci `PRP-xxxxxx`,
- `unitId` má používať budúci `UNT-xxxxxx`,
- `rawUnitText` nemá byť autoritatívne,
- porovnateľnosť nesmie stáť na názve vlastnosti alebo texte jednotky.

RFC-0002 spresňuje:

- first-class `Observation` má byť samostatná entita a event-like evidence object,
- `MeasurementQuality` je preferovaný názov pred `ValueQuality`,
- `Classification` môže v `0.2B.1` zostať value-object kontrakt alebo odkaz s katalógovou entitou odloženou do `0.2B.2`,
- `AvailabilityRecord` a `CommercialObservation` majú byť presnejšie chápané ako embedded observation records,
- `AvailabilityRecord` a `CommercialObservation` nepatria do prvého minimálneho scope `0.2B.1`, pokiaľ samostatné rozhodnutie neurčí inak,
- katalógové položky majú byť samostatné catalog entries,
- `Decision` dopĺňa chýbajúcu boundary medzi pozorovaním, odvodeným výsledkom a autoritatívnou zmenou, ale jeho stored kontrakt môže byť odložený.

Môže sa neskôr zmeniť:

- či `Observation` bude vždy first-class entita s `OBS-xxxxxx`, alebo sa povolí aj job-local embedded observation record bez globálnej identity,
- či `Classification Catalog` vznikne v `0.2B.2` alebo neskôr,
- či vznikne samostatný `Relationship` object,
- či vznikne všeobecný `Event` model.
- či `Decision` dostane vlastný prefix v `EOS-003`.

Odporúčanie: RFC-0001 môže po posúdení RFC-0002 prejsť z `Review` do `Accepted`, ak bude prijaté, že RFC-0002 spresňuje taxonómiu bez popretia jadra RFC-0001.

## 19. Governance

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
3. Rozhodnúť, či `Decision` dostane vlastný prefix, iba ak sa stane samostatným stored kontraktom.
4. Podľa rozsahu vytvoriť ADR pre taxonómiu objektov alebo pre RFC proces.
5. Až potom začať implementáciu Phase 0.2B kontraktov.

Tento RFC nemení `EOS-003` a nevytvára ADR.

## 20. Otvorené otázky

- Má byť `Observation` vždy first-class entita s `observationScope`, alebo sa povolí aj job-local embedded observation record bez `OBS-xxxxxx`?
- Má `Measurement` vzniknúť ako subtype `Observation`, alebo ako samostatná entita?
- Kedy presne zaviesť Property Catalog a Unit Catalog?
- Má mať `Classification Catalog` vlastný prefix `CLS-xxxxxx` pred `0.2B.2`?
- Má mať `Condition Type Catalog` prefix `CND-xxxxxx` pred `0.2B.2`?
- Kedy je potrebný samostatný `Relationship` object?
- Má `Derived Result` dostať vlastný prefix alebo ostať výstupom konkrétneho kalkulačného modulu?
- Má `Decision` dostať vlastný prefix a samostatný stored kontrakt, alebo zostane v `0.2B.1` iba boundary konceptom?
- Má sa catalog hierarchy zaviesť ako samostatný governance dokument alebo iba ako súčasť knowledge core kontraktov?
- Ktorý dokument alebo ADR definitívne zavedie RFC lifecycle?

## 21. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-07-14 | 0.1 | 0 | Chief Engineering Knowledge Architect + Codex | Initial RFC draft for engineering object taxonomy |
| 2026-07-14 | 0.1 | 1 | Codex | Architecture review revision: doplnenie Engineering Knowledge Layer, `Observation.observationScope`, `Decision`, aggregate root pravidla, embedded observation records, catalog hierarchy a odporúčaného fázovania `0.2B.1` / `0.2B.2` / `0.2C` |
| 2026-07-25 | 0.1 | 2 | Codex | Architecture Closure revision: spresnenie minimálneho scope `0.2B.1`, rozlíšenie first-class `Observation` a embedded observation records, ponechanie `Decision` ako boundary konceptu, fázovanie katalógov do `0.2B.2` a zosúladenie prahu pre first-class `Relationship` |
