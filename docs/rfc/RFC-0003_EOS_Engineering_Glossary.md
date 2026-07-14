# RFC-0003 - EOS Engineering Glossary

**Project:** EOS - Engineering Operating System  
**RFC ID:** RFC-0003  
**Version:** 0.1  
**Revision:** 0  
**Status:** Draft  
**Author:** Chief Engineering Knowledge Architect + Codex  
**Last update:** 2026-07-14  
**Document basis:** Internal architecture proposal  

---

## 1. Purpose

Tento RFC definuje autoritatívny slovník pojmov EOS.

Dokument nie je určený koncovým používateľom. Je určený architektom, vývojárom a autorom dokumentácie, aby sa rovnaké pojmy používali konzistentne v RFC, ADR, JSON schémach, validačnej vrstve a technickej dokumentácii.

Každý pojem má jeden preferovaný názov, jeden povolený význam a explicitne zakázané použitia.

## 2. Scope

Slovník pokrýva architektonické, znalostné, validačné, dokumentačné a lifecycle pojmy používané v EOS.

Tento RFC:

- nevytvára JSON schémy,
- nemení governance dokumenty,
- nevytvára ADR,
- nezačína Phase 0.2B,
- nezavádza reálne materiálové, technologické, obchodné ani normové dáta.

## 3. Principles

1. Jeden pojem má jeden preferovaný názov.
2. Autoritatívne dokumenty EOS nepoužívajú synonymá pre rovnaký význam.
3. Alias môže byť uvedený iba informatívne, nie ako rovnocenný názov.
4. Pojmy sa nesmú používať vo voľnom alebo hovorovom význame.
5. Definícia pojmu sa nemení bez schváleného RFC alebo ADR.
6. JSON schémy musia používať rovnaké názvy objektov a polí, ak sa pojem premietne do dátového kontraktu.
7. Ak pojem nie je dostatočne definovaný, nesmie byť použitý ako autoritatívny konštrukt v schéme.

## 4. Glossary Entries

### G-0001 Architecture

- Identifier: `G-0001`
- Preferred term: `Architecture`
- Definition: Usporiadanie vrstiev, modulov, zodpovedností, závislostí a pravidiel vývoja EOS.
- Allowed usage: Používa sa pri rozhodnutiach o hraniciach systému, moduloch, dátových kontraktoch a integračných smeroch.
- Not allowed usage: Nepoužíva sa ako synonymum pre ľubovoľný diagram alebo internú štruktúru jedného súboru.
- Examples: `EOS-001` definuje systémovú architektúru.
- Counterexamples: Nazvať zoznam polí v JSON objekte architektúrou.
- Related concepts: `Governance`, `Knowledge Layer`, `ADR`, `RFC`.
- Future implementation notes: Architektonické rozhodnutia majú byť zachytené cez ADR alebo Accepted RFC.

### G-0002 Engineering Knowledge

- Identifier: `G-0002`
- Preferred term: `Engineering Knowledge`
- Definition: Overiteľná alebo riadene evidovaná inžinierska znalosť použiteľná pri návrhu, výrobe, kontrole alebo cenovej príprave.
- Allowed usage: Používa sa pre znalosti uložené v dátových entitách, katalógoch, pozorovaniach alebo rozhodnutiach.
- Not allowed usage: Nepoužíva sa pre samotný výpočtový kód, UI alebo neoverený voľný text.
- Examples: Zdrojovaná vlastnosť materiálu je engineering knowledge.
- Counterexamples: Dočasná poznámka bez zdroja vydávaná za fakt.
- Related concepts: `Knowledge Layer`, `Knowledge Entity`, `SourceLink`, `Decision`.
- Future implementation notes: Znalosti musia byť oddelené od kalkulačného kódu.

### G-0003 Knowledge Layer

- Identifier: `G-0003`
- Preferred term: `Knowledge Layer`
- Definition: Vrstva EOS medzi governance pravidlami a konkrétnymi knowledge entities, ktorá definuje spoločné znalostné primitíva, evidence, rozhodnutia a katalógy.
- Allowed usage: Používa sa pre pravidlá ako `PropertyRecord`, `Observation`, `Decision`, `Derived Result`, katalógy a porovnateľnosť.
- Not allowed usage: Nepoužíva sa ako názov pre databázový server alebo konkrétnu entitu.
- Examples: Unit Catalog patrí do Knowledge Layer.
- Counterexamples: REST endpoint pre materiály nie je Knowledge Layer.
- Related concepts: `Engineering Knowledge`, `Knowledge Entity`, `Catalog`, `Decision`.
- Future implementation notes: Má byť stabilizovaná pred plnými knowledge entity kontraktmi.

### G-0004 Knowledge Entity

- Identifier: `G-0004`
- Preferred term: `Knowledge Entity`
- Definition: Samostatná dátová entita nesúca engineering knowledge so stabilným ID, lifecycle a auditnou históriou.
- Allowed usage: Používa sa pre entity ako `Material`, `Machine`, `ManufacturingProcess` alebo `Supplier`.
- Not allowed usage: Nepoužíva sa pre vnorené value objects ani pre výpočtové výsledky.
- Examples: `Material` je knowledge entity.
- Counterexamples: `Quantity` nie je knowledge entity.
- Related concepts: `Entity`, `Aggregate Root`, `Engineering Knowledge`.
- Future implementation notes: Knowledge entities majú vzniknúť až po core contracts a katalógoch.

### G-0005 Entity

- Identifier: `G-0005`
- Preferred term: `Entity`
- Definition: Objekt so stabilnou identitou, vlastným lifecycle a históriou nezávislou od aktuálnych hodnôt polí.
- Allowed usage: Používa sa pre objekty s vlastným ID a auditom.
- Not allowed usage: Nepoužíva sa pre hodnoty definované iba obsahom.
- Examples: `Job` je entity.
- Counterexamples: `ValueRange` nie je entity.
- Related concepts: `Identity`, `Aggregate Root`, `Lifecycle`.
- Future implementation notes: Entity budú mať `id`, `schemaVersion`, `recordVersion`, `revision` a `status`.

### G-0006 Aggregate

- Identifier: `G-0006`
- Preferred term: `Aggregate`
- Definition: Konzistentná skupina objektov, ktorú riadi jeden aggregate root.
- Allowed usage: Používa sa pre hranice transakcie a integrity.
- Not allowed usage: Nepoužíva sa ako synonymum pre ľubovoľnú kolekciu.
- Examples: `Job` aggregate môže obsahovať job-owned operations.
- Counterexamples: Zoznam všetkých materiálov nie je jeden aggregate.
- Related concepts: `Aggregate Root`, `Entity`, `Value Object`.
- Future implementation notes: Agregáty sa majú mapovať na jasné API a databázové hranice.

### G-0007 Aggregate Root

- Identifier: `G-0007`
- Preferred term: `Aggregate Root`
- Definition: Entita, cez ktorú sa mení a validuje celý aggregate.
- Allowed usage: Používa sa pre entity vlastniace vnorené objekty a pravidlá integrity.
- Not allowed usage: Aggregate root nesmie vlastniť iný aggregate root.
- Examples: `Material` je aggregate root pre svoje `PropertyRecord`.
- Counterexamples: `Quantity` nemôže byť aggregate root.
- Related concepts: `Aggregate`, `Entity`, `Relationship`.
- Future implementation notes: Referencie medzi aggregate roots majú byť cez stabilné ID.

### G-0008 Value Object

- Identifier: `G-0008`
- Preferred term: `Value Object`
- Definition: Objekt definovaný hodnotou, nie samostatnou identitou.
- Allowed usage: Používa sa pre štruktúry vlastnené rodičovskou entitou.
- Not allowed usage: Nepoužíva sa pre objekty vyžadujúce vlastný lifecycle.
- Examples: `Quantity` je value object.
- Counterexamples: `SourceReference` nie je value object.
- Related concepts: `Entity`, `PropertyRecord`, `Condition`.
- Future implementation notes: Value object sa reviduje cez rodiča.

### G-0009 Reference Object

- Identifier: `G-0009`
- Preferred term: `Reference Object`
- Definition: Objekt reprezentujúci autoritatívny zdroj, normu alebo referenčný význam používaný inými objektmi.
- Allowed usage: Používa sa pre `SourceReference`, `NormReference` a vybrané katalógové položky.
- Not allowed usage: Nepoužíva sa pre obyčajný textový odkaz bez identity.
- Examples: `NormReference` je reference object.
- Counterexamples: `sourceLocation` v `SourceLink` nie je reference object.
- Related concepts: `SourceReference`, `NormReference`, `Catalog Entry`.
- Future implementation notes: Reference objects majú byť citovateľné a auditovateľné.

### G-0010 Catalog

- Identifier: `G-0010`
- Preferred term: `Catalog`
- Definition: Riadený autoritatívny zoznam položiek používaných na stabilizáciu významu.
- Allowed usage: Používa sa pre zoznam vlastností, jednotiek, typov podmienok alebo klasifikácií.
- Not allowed usage: Nepoužíva sa pre ľubovoľný adresár súborov.
- Examples: Unit Catalog definuje jednotky.
- Counterexamples: Zložka `docs/` nie je catalog.
- Related concepts: `Catalog Entry`, `Property Catalog`, `Unit Catalog`.
- Future implementation notes: Katalógy sa majú deliť na reference catalogs a knowledge catalogs.

### G-0011 Catalog Entry

- Identifier: `G-0011`
- Preferred term: `Catalog Entry`
- Definition: Jedna autoritatívna položka katalógu so stabilnou identitou.
- Allowed usage: Používa sa pre položky ako `PRP-xxxxxx` alebo `UNT-xxxxxx`.
- Not allowed usage: Nepoužíva sa pre konkrétne vnorené použitie položky v entite.
- Examples: `PRP-000001` je property catalog entry.
- Counterexamples: `PropertyRecord` nie je catalog entry.
- Related concepts: `Catalog`, `Identifier`, `Property`.
- Future implementation notes: Deprecated položky sa nemajú mazať po schválení.

### G-0012 Relationship

- Identifier: `G-0012`
- Preferred term: `Relationship`
- Definition: Významová väzba medzi objektmi.
- Allowed usage: Zatiaľ ako ID referencia; neskôr ako first-class object, ak väzba potrebuje vlastné zdroje, platnosť alebo audit.
- Not allowed usage: Nepoužíva sa ako náhrada za aggregate ownership.
- Examples: `materialId` v `StockMaterial` vyjadruje relationship.
- Counterexamples: Vnorený `Quantity` nie je relationship.
- Related concepts: `Aggregate Root`, `SourceLink`, `Identifier`.
- Future implementation notes: `REL-xxxxxx` je navrhovaný iba pre budúcu fázu.

### G-0013 Identity

- Identifier: `G-0013`
- Preferred term: `Identity`
- Definition: Stabilný význam objektu nezávislý od jeho názvu, umiestnenia alebo aktuálnych hodnôt.
- Allowed usage: Používa sa pri entitách, katalógových položkách a dokumentoch.
- Not allowed usage: Nepoužíva sa pre dočasný zobrazovací názov.
- Examples: Identita materiálu je daná jeho `MAT-xxxx`.
- Counterexamples: `cachedDisplayName` nie je identity.
- Related concepts: `Identifier`, `Entity`, `Revision`.
- Future implementation notes: Identity sa nesmie recyklovať po archivácii.

### G-0014 Identifier

- Identifier: `G-0014`
- Preferred term: `Identifier`
- Definition: Stabilná textová reprezentácia identity objektu.
- Allowed usage: Používa sa ako `id` alebo referenčné pole.
- Not allowed usage: Nepoužíva sa pre ľubovoľný používateľský názov.
- Examples: `SRC-000001` je identifier.
- Counterexamples: `Example material` nie je identifier.
- Related concepts: `Identity`, `EOS-003`, `Catalog Entry`.
- Future implementation notes: Formáty ID sa majú centralizovať v spoločných schémach.

### G-0015 Observation

- Identifier: `G-0015`
- Preferred term: `Observation`
- Definition: Konkrétne pozorovanie, meranie, skúška alebo zistenie s dôkazovým významom.
- Allowed usage: Používa sa pre záznamy s `OBS-xxxxxx` a `observationScope`.
- Not allowed usage: Nepoužíva sa ako všeobecná autoritatívna vlastnosť.
- Examples: Meranie v zákazke môže byť observation.
- Counterexamples: Schválená všeobecná materiálová vlastnosť nie je observation.
- Related concepts: `Evidence`, `Measurement`, `Decision`, `PropertyRecord`.
- Future implementation notes: Jedna observation nesmie automaticky meniť property record.

### G-0016 Evidence

- Identifier: `G-0016`
- Preferred term: `Evidence`
- Definition: Dôkazový podklad podporujúci tvrdenie, rozhodnutie alebo zmenu znalostného záznamu.
- Allowed usage: Používa sa pre zdroje, pozorovania, snapshoty alebo odvodené výsledky použité v rozhodnutí.
- Not allowed usage: Nepoužíva sa ako synonymum pre pravdu alebo schválený fakt.
- Examples: `Observation` môže byť evidence pre `Decision`.
- Counterexamples: AI návrh bez vstupov nie je dostatočné evidence.
- Related concepts: `Observation`, `SourceLink`, `Decision`.
- Future implementation notes: Evidence väzby môžu neskôr vyžadovať first-class relationship.

### G-0017 Measurement

- Identifier: `G-0017`
- Preferred term: `Measurement`
- Definition: Špecializované pozorovanie číselnej alebo kvalitatívnej hodnoty získanej meracou metódou.
- Allowed usage: Používa sa ako subtype alebo typ `Observation`.
- Not allowed usage: Nepoužíva sa pre všeobecnú hodnotu bez meracieho kontextu.
- Examples: Fiktívne meranie hodnoty s `MeasurementQuality`.
- Counterexamples: Katalógová vlastnosť bez merania.
- Related concepts: `Observation`, `Quantity`, `MeasurementQuality`.
- Future implementation notes: Samostatný Measurement kontrakt potrebuje ďalšie RFC.

### G-0018 Inspection

- Identifier: `G-0018`
- Preferred term: `Inspection`
- Definition: Kontrolná aktivita alebo výsledok posúdenia objektu podľa kritérií.
- Allowed usage: Používa sa pre budúce inspection result záznamy.
- Not allowed usage: Nepoužíva sa pre bežnú validáciu JSON schémy.
- Examples: Kontrola zhody v zákazke môže viesť k observation.
- Counterexamples: `Draft202012Validator.check_schema` nie je inspection.
- Related concepts: `Observation`, `Verification`, `Condition`.
- Future implementation notes: Inspection môže byť subtype `Observation` alebo samostatná entita.

### G-0019 Verification

- Identifier: `G-0019`
- Preferred term: `Verification`
- Definition: Posúdenie, či tvrdenie alebo záznam je podložený zdrojom, pozorovaním alebo rozhodnutím.
- Allowed usage: Používa sa pre overovanie významu tvrdení.
- Not allowed usage: Nepoužíva sa ako synonymum pre JSON Schema validation.
- Examples: Overenie `PropertyRecord` cez `sourceLinks`.
- Counterexamples: Kontrola typu poľa v JSON nie je verification.
- Related concepts: `VerificationStatus`, `Evidence`, `Validation`.
- Future implementation notes: Verification bude aplikačné pravidlo, nie iba schémová kontrola.

### G-0020 Validation

- Identifier: `G-0020`
- Preferred term: `Validation`
- Definition: Kontrola, či záznam spĺňa syntaktické, štrukturálne alebo aplikačné pravidlá.
- Allowed usage: Používa sa pre JSON Schema validáciu a EOS aplikačnú validáciu.
- Not allowed usage: Nepoužíva sa ako dôkaz pravdivosti technického tvrdenia.
- Examples: Kontrola `additionalProperties: false`.
- Counterexamples: Validný JSON automaticky neznamená správnu technickú hodnotu.
- Related concepts: `Verification`, `Lifecycle`, `JSON Schema`.
- Future implementation notes: Štrukturálna a aplikačná validácia musia zostať rozlíšené.

### G-0021 Condition

- Identifier: `G-0021`
- Preferred term: `Condition`
- Definition: Podmienka, za ktorej je hodnota, vlastnosť, pozorovanie alebo schopnosť platná.
- Allowed usage: Používa sa ako value object s `conditionType` alebo budúcim `conditionTypeId`.
- Not allowed usage: Nepoužíva sa ako voľný text zmiešaný s hodnotou.
- Examples: Podmienka platnosti vlastnosti.
- Counterexamples: Poznámka bez jasného vzťahu k platnosti.
- Related concepts: `PropertyRecord`, `Capability`, `Condition Type Catalog`.
- Future implementation notes: Typy podmienok majú byť riadené katalógom.

### G-0022 Capability

- Identifier: `G-0022`
- Preferred term: `Capability`
- Definition: Schopnosť entity vykonávať alebo podporovať určitú činnosť v danom kontexte.
- Allowed usage: Používa sa najmä pri `Machine` a `ManufacturingProcess`.
- Not allowed usage: Nepoužíva sa pre konkrétne vykonanie operácie v zákazke.
- Examples: Schopnosť procesu podporovať určitý typ činnosti.
- Counterexamples: `JobOperation` nie je capability.
- Related concepts: `Machine`, `ManufacturingProcess`, `Condition`.
- Future implementation notes: Capability môže byť neskôr povýšená na entitu, ak bude potrebovať vlastnú históriu.

### G-0023 Property

- Identifier: `G-0023`
- Preferred term: `Property`
- Definition: Autoritatívne definovaný typ vlastnosti identifikovaný cez property catalog entry.
- Allowed usage: Používa sa ako význam za `propertyId`.
- Not allowed usage: Nepoužíva sa ako voľný názov poľa alebo opis.
- Examples: Vlastnosť identifikovaná `PRP-xxxxxx`.
- Counterexamples: `cachedDisplayName` nie je property.
- Related concepts: `PropertyRecord`, `Property Catalog`, `Quantity`.
- Future implementation notes: Property musí byť definovaná v Property Catalog pred masovým použitím.

### G-0024 PropertyRecord

- Identifier: `G-0024`
- Preferred term: `PropertyRecord`
- Definition: Vnorený claim-like value object, ktorý zapisuje hodnotu konkrétnej property v rodičovskej entite.
- Allowed usage: Používa sa pre vlastnosti materiálov, strojov, procesov a pozorovaní.
- Not allowed usage: Nepoužíva sa ako samostatná entita s vlastným ID.
- Examples: `PropertyRecord` s `propertyId`, `quantity` a `sourceLinks`.
- Counterexamples: Samostatný súbor iba pre jednu vnorenú vlastnosť.
- Related concepts: `Property`, `Quantity`, `SourceLink`, `VerificationStatus`.
- Future implementation notes: Potrebuje stabilnú cestu pre citovanie polí.

### G-0025 Property Catalog

- Identifier: `G-0025`
- Preferred term: `Property Catalog`
- Definition: Knowledge catalog definujúci autoritatívny význam vlastností.
- Allowed usage: Používa sa pre položky `PRP-xxxxxx`.
- Not allowed usage: Nepoužíva sa ako zoznam aktuálnych hodnôt vlastností.
- Examples: Katalóg vlastností používaných v `PropertyRecord`.
- Counterexamples: Zoznam vlastností jedného materiálu nie je Property Catalog.
- Related concepts: `Property`, `Catalog`, `Catalog Entry`.
- Future implementation notes: Má vzniknúť pred plným napĺňaním entít.

### G-0026 Unit

- Identifier: `G-0026`
- Preferred term: `Unit`
- Definition: Autoritatívne definovaná jednotka hodnoty s rozmerovým a konverzným významom.
- Allowed usage: Používa sa cez `unitId`.
- Not allowed usage: Nepoužíva sa ako voľný text v schválených záznamoch.
- Examples: Jednotka identifikovaná `UNT-xxxxxx`.
- Counterexamples: `rawUnitText` v Approved zázname.
- Related concepts: `Unit Catalog`, `Quantity`, `ValueRange`.
- Future implementation notes: Rozmerová kompatibilita bude aplikačné pravidlo.

### G-0027 Unit Catalog

- Identifier: `G-0027`
- Preferred term: `Unit Catalog`
- Definition: Reference catalog definujúci autoritatívne jednotky.
- Allowed usage: Používa sa pre položky `UNT-xxxxxx`.
- Not allowed usage: Nepoužíva sa pre zoznam hodnôt alebo property definitions.
- Examples: Katalóg jednotiek pre `Quantity`.
- Counterexamples: Textový zoznam jednotiek v poznámke.
- Related concepts: `Unit`, `Catalog Entry`, `Quantity`.
- Future implementation notes: Má obsahovať symbol, rozmer, SI väzbu a pravidlá zobrazenia.

### G-0028 Quantity

- Identifier: `G-0028`
- Preferred term: `Quantity`
- Definition: Value object reprezentujúci jednu hodnotu s jednotkou.
- Allowed usage: Používa sa pre jednu `value` alebo `nominalValue` s `unitId`.
- Not allowed usage: Nemá obsahovať rozsah, toleranciu, neistotu ani presnosť merania.
- Examples: `quantity.nominalValue` s `unitId`.
- Counterexamples: `Quantity` s `minValue` a `maxValue`.
- Related concepts: `Unit`, `ValueRange`, `MeasurementQuality`.
- Future implementation notes: Review/Approved záznamy majú používať `unitId`.

### G-0029 ValueRange

- Identifier: `G-0029`
- Preferred term: `ValueRange`
- Definition: Value object reprezentujúci interval hodnoty.
- Allowed usage: Používa sa pre `minValue`, `maxValue`, inkluzivitu hraníc a `unitId`.
- Not allowed usage: Nepoužíva sa pre menovitú hodnotu alebo neistotu merania.
- Examples: Interval s dolnou a hornou hranicou.
- Counterexamples: Jedna hodnota uložená ako rozsah bez dôvodu.
- Related concepts: `Quantity`, `Unit`, `Condition`.
- Future implementation notes: Nemá duplikovať polia v `Quantity`.

### G-0030 MeasurementQuality

- Identifier: `G-0030`
- Preferred term: `MeasurementQuality`
- Definition: Value object opisujúci toleranciu, neistotu, rozlíšenie, presnosť alebo metódu súvisiacu s hodnotou alebo meraním.
- Allowed usage: Používa sa na oddelenie kvality merania od hodnoty samotnej.
- Not allowed usage: Nepoužíva sa ako náhrada za `Quantity`.
- Examples: Neistota merania uvedená mimo číselnej hodnoty.
- Counterexamples: Tolerancia uložená priamo do `Quantity`.
- Related concepts: `Measurement`, `Quantity`, `Observation`.
- Future implementation notes: Musí rozlišovať toleranciu, neistotu, precision a resolution.

### G-0031 CommercialObservation

- Identifier: `G-0031`
- Preferred term: `CommercialObservation`
- Definition: Embedded observation record pre obchodné zistenie bez právneho alebo cenového záväzku.
- Allowed usage: Používa sa pre časovo označené obchodné pozorovania s confidence a zdrojmi.
- Not allowed usage: Nepoužíva sa ako cena, ponuka alebo právny záväzok.
- Examples: Pozorovanie dodávateľského stavu.
- Counterexamples: Finálna cenová ponuka.
- Related concepts: `Supplier`, `Decision`, `AvailabilityRecord`.
- Future implementation notes: Môže byť vstupom pre quotation decision.

### G-0032 AvailabilityRecord

- Identifier: `G-0032`
- Preferred term: `AvailabilityRecord`
- Definition: Embedded observation record opisujúci dostupnosť objektu v čase.
- Allowed usage: Používa sa s `observedAt`, `validUntil`, `relatedEntityId` a `sourceLinks`.
- Not allowed usage: Nepoužíva sa ako trvalá vlastnosť materiálu alebo polotovaru.
- Examples: Časovo označená dostupnosť skladovej formy.
- Counterexamples: Dostupnosť bez dátumu vydávaná za fakt.
- Related concepts: `Observation`, `StockMaterial`, `CommercialObservation`.
- Future implementation notes: Historická dostupnosť má byť append-only.

### G-0033 Decision

- Identifier: `G-0033`
- Preferred term: `Decision`
- Definition: Auditovateľný záznam o prijatí, odmietnutí alebo podmienenom prijatí evidence alebo derived result engineerom alebo schváleným procesom.
- Allowed usage: Používa sa ako most medzi dôkazmi a autoritatívnou zmenou.
- Not allowed usage: Nepoužíva sa pre samotný výpočet alebo samotné pozorovanie.
- Examples: Engineer approval nad observation a derived result.
- Counterexamples: Automatický AI návrh bez schválenia.
- Related concepts: `Evidence`, `Derived Result`, `Recommendation`.
- Future implementation notes: Pravdepodobne potrebuje vlastný prefix v budúcom RFC.

### G-0034 Derived Result

- Identifier: `G-0034`
- Preferred term: `Derived Result`
- Definition: Výsledok odvodený z explicitných vstupov výpočtom, porovnaním, pravidlom alebo AI modelom.
- Allowed usage: Používa sa pre odhady, porovnania, odporúčania a AI návrhy.
- Not allowed usage: Nepoužíva sa ako zdrojová znalosť alebo schválený fakt.
- Examples: Odhad vytvorený z validovaných vstupov.
- Counterexamples: Hodnota materiálu bez zdroja vydávaná za derived result.
- Related concepts: `Calculation`, `Recommendation`, `Decision`.
- Future implementation notes: Musí niesť vstupy a verziu logiky.

### G-0035 Calculation

- Identifier: `G-0035`
- Preferred term: `Calculation`
- Definition: Spustenie výpočtovej logiky nad explicitnými vstupmi.
- Allowed usage: Používa sa pre proces výpočtu, nie pre autoritatívnu znalosť.
- Not allowed usage: Nepoužíva sa ako miesto uloženia hardcoded technických hodnôt.
- Examples: Výpočet vytvorí derived result.
- Counterexamples: Technická hodnota zapísaná priamo v kóde.
- Related concepts: `Derived Result`, `Snapshot`, `Decision`.
- Future implementation notes: Kalkulácia musí byť reprodukovateľná v primeranom rozsahu.

### G-0036 Recommendation

- Identifier: `G-0036`
- Preferred term: `Recommendation`
- Definition: Návrh alebo odporúčanie odvodené z pravidiel, dát, skúseností alebo AI.
- Allowed usage: Používa sa ako typ derived result alebo vstup rozhodnutia.
- Not allowed usage: Nepoužíva sa ako norma, záväzná požiadavka alebo schválený fakt.
- Examples: Odporúčanie ďalšieho kroku pred engineer approval.
- Counterexamples: Odporúčanie vydávané za `NormReference`.
- Related concepts: `Derived Result`, `Decision`, `NormReference`.
- Future implementation notes: Odporúčania musia byť jasne označené ako návrh.

### G-0037 Source

- Identifier: `G-0037`
- Preferred term: `Source`
- Definition: Pôvod informácie alebo dôkazu.
- Allowed usage: Používa sa všeobecne v texte; autoritatívny záznam je `SourceReference`.
- Not allowed usage: Nepoužíva sa ako náhrada za konkrétny `SourceReference`.
- Examples: Dokument, skúsenosť alebo pozorovanie ako pôvod informácie.
- Counterexamples: Voľná veta bez identifikovateľného pôvodu.
- Related concepts: `SourceReference`, `SourceLink`, `Evidence`.
- Future implementation notes: V dátach používať `SourceReference` a `SourceLink`.

### G-0038 SourceReference

- Identifier: `G-0038`
- Preferred term: `SourceReference`
- Definition: Samostatná autoritatívna entita evidujúca zdroj informácie.
- Allowed usage: Používa sa s ID `SRC-xxxxxx`.
- Not allowed usage: Neobsahuje konkrétnu interpretáciu použitia zdroja pri poli.
- Examples: Zdroj citovaný viacerými záznamami.
- Counterexamples: Interpretácia strany alebo tabuľky vložená do SourceReference namiesto SourceLink.
- Related concepts: `Source`, `SourceLink`, `Evidence`.
- Future implementation notes: Interpretácia patrí do `SourceLink`.

### G-0039 SourceLink

- Identifier: `G-0039`
- Preferred term: `SourceLink`
- Definition: Väzba medzi konkrétnym tvrdením alebo poľom a `SourceReference`.
- Allowed usage: Používa sa na podporu polí, tvrdení a interpretácií.
- Not allowed usage: Nepoužíva sa ako samostatná zdrojová entita.
- Examples: `supportedField` ukazuje na pole podporené zdrojom.
- Counterexamples: Samostatný `SourceLink` bez rodičovského kontextu.
- Related concepts: `SourceReference`, `Evidence`, `Verification`.
- Future implementation notes: Môže potrebovať presné pravidlá path syntaxe.

### G-0040 NormReference

- Identifier: `G-0040`
- Preferred term: `NormReference`
- Definition: Entita evidujúca externú normu, štandard alebo záväzný technický predpis ako referenciu.
- Allowed usage: Používa sa s ID `NRM-xxxx`.
- Not allowed usage: Nepoužíva sa pre interné EOS pravidlá alebo plné znenie normy.
- Examples: Externá normatívna referencia.
- Counterexamples: Interný EOS štandard označený ako NormReference.
- Related concepts: `Reference Object`, `SourceReference`, `STD`.
- Future implementation notes: Musí zostať oddelená od interných `STD-xxx`.

### G-0041 Document

- Identifier: `G-0041`
- Preferred term: `Document`
- Definition: Riadený alebo pracovný textový artefakt EOS.
- Allowed usage: Používa sa pre governance dokumenty, RFC, ADR, štandardy alebo metodiky.
- Not allowed usage: Nepoužíva sa ako autoritatívna databázová entita, ak existuje štruktúrovaný záznam.
- Examples: RFC dokument.
- Counterexamples: Materiálová karta v dátach nie je iba document.
- Related concepts: `DocumentRecord`, `Revision`, `Version`.
- Future implementation notes: Riadené dokumenty majú byť evidované cez DocumentRecord.

### G-0042 DocumentRecord

- Identifier: `G-0042`
- Preferred term: `DocumentRecord`
- Definition: Dátový záznam evidujúci riadený dokument.
- Allowed usage: Používa ID dokumentu, ktorý eviduje.
- Not allowed usage: Nepoužíva sa na uloženie technických hodnôt patriacich do entít.
- Examples: Záznam o RFC alebo EOS dokumente.
- Counterexamples: Technická vlastnosť uložená v DocumentRecord.
- Related concepts: `Document`, `Version`, `Revision`.
- Future implementation notes: Musí odlíšiť document version od schemaVersion.

### G-0043 Job

- Identifier: `G-0043`
- Preferred term: `Job`
- Definition: Konkrétna zákazka alebo prípravný zákazkový prípad.
- Allowed usage: Používa sa s ID `JOB-yyyy-xxxx`.
- Not allowed usage: Nepoužíva sa ako všeobecný výrobný proces.
- Examples: Zákazkový agregát vlastniaci operácie.
- Counterexamples: `ManufacturingProcess` nie je job.
- Related concepts: `JobOperation`, `TimeRecord`, `Observation`.
- Future implementation notes: Job-owned entity používajú hierarchické ID.

### G-0044 JobOperation

- Identifier: `G-0044`
- Preferred term: `JobOperation`
- Definition: Jedna operácia v kontexte konkrétnej zákazky.
- Allowed usage: Používa sa s ID `JOB-yyyy-xxxx-OP-xxx`.
- Not allowed usage: Nepoužíva sa ako definícia typu procesu.
- Examples: Operácia zákazky referencujúca process.
- Counterexamples: Katalógový proces uložený ako JobOperation.
- Related concepts: `Job`, `ManufacturingProcess`, `TimeRecord`.
- Future implementation notes: Je job-owned entity, nie aggregate root.

### G-0045 TimeRecord

- Identifier: `G-0045`
- Preferred term: `TimeRecord`
- Definition: Záznam plánovaného alebo skutočného času naviazaný na operáciu.
- Allowed usage: Používa sa s ID `JOB-yyyy-xxxx-OP-xxx-TM-xxx`.
- Not allowed usage: Nepoužíva sa ako všeobecný čas procesu bez kontextu.
- Examples: Časový záznam operácie.
- Counterexamples: Garantovaný procesný čas bez zdroja.
- Related concepts: `JobOperation`, `Observation`, `Derived Result`.
- Future implementation notes: Historické časy majú byť auditovateľné.

### G-0046 Machine

- Identifier: `G-0046`
- Preferred term: `Machine`
- Definition: Výrobné zariadenie alebo riadený strojový objekt EOS.
- Allowed usage: Používa sa s ID `MAC-xxxx`.
- Not allowed usage: Nepoužíva sa pre výrobný proces alebo operáciu.
- Examples: Stroj ako aggregate root pre capability a property records.
- Counterexamples: `ManufacturingProcess` uložený ako Machine.
- Related concepts: `Capability`, `ManufacturingProcess`, `JobOperation`.
- Future implementation notes: Typ vs konkrétny stroj môže vyžadovať ďalšie spresnenie.

### G-0047 Material

- Identifier: `G-0047`
- Preferred term: `Material`
- Definition: Materiál ako znalostný objekt, nie konkrétny fyzický kus.
- Allowed usage: Používa sa s ID `MAT-xxxx`.
- Not allowed usage: Nepoužíva sa pre skladovú formu alebo dodávateľskú položku.
- Examples: Materiál s property records a designation.
- Counterexamples: Konkrétny polotovar uložený ako Material.
- Related concepts: `StockMaterial`, `PropertyRecord`, `NormReference`.
- Future implementation notes: Materiálové entity vzniknú až po core contracts.

### G-0048 StockMaterial

- Identifier: `G-0048`
- Preferred term: `StockMaterial`
- Definition: Skladová, dodávateľská alebo používaná forma materiálu.
- Allowed usage: Používa sa s ID `POL-xxxx`.
- Not allowed usage: Nepoužíva sa ako náhrada za všeobecný `Material`.
- Examples: Polotovar referencujúci materiál.
- Counterexamples: Všeobecná materiálová norma uložená ako StockMaterial.
- Related concepts: `Material`, `Supplier`, `AvailabilityRecord`.
- Future implementation notes: Dostupnosť nesmie byť trvalá vlastnosť StockMaterial.

### G-0049 Supplier

- Identifier: `G-0049`
- Preferred term: `Supplier`
- Definition: Dodávateľ alebo obchodný partner evidovaný v EOS.
- Allowed usage: Používa sa s ID `SUP-xxxx`.
- Not allowed usage: Nepoužíva sa ako zdroj technickej pravdy bez `SourceLink`.
- Examples: Dodávateľ referencovaný zo StockMaterial.
- Counterexamples: Názov dodávateľa ako voľný text bez ID v schválenom zázname.
- Related concepts: `CommercialObservation`, `StockMaterial`, `SourceReference`.
- Future implementation notes: Citlivé obchodné údaje potrebujú pravidlá prístupu.

### G-0050 ManufacturingProcess

- Identifier: `G-0050`
- Preferred term: `ManufacturingProcess`
- Definition: Typ výrobného alebo kontrolného procesu.
- Allowed usage: Používa sa s ID `TEC-xxxx`.
- Not allowed usage: Nepoužíva sa pre konkrétnu zákazkovú operáciu.
- Examples: Proces referencovaný z `JobOperation`.
- Counterexamples: Reálny čas zákazky uložený ako ManufacturingProcess.
- Related concepts: `JobOperation`, `Machine`, `Capability`.
- Future implementation notes: Procesné typy môžu potrebovať Process Type Catalog.

### G-0051 CuttingTool

- Identifier: `G-0051`
- Preferred term: `CuttingTool`
- Definition: Nástroj alebo nástrojová zostava evidovaná ako znalostný objekt.
- Allowed usage: Používa sa s ID `TOOL-xxxx`.
- Not allowed usage: Nepoužíva sa ako všeobecná vlastnosť procesu.
- Examples: Nástroj referencovaný z operácie alebo procesu.
- Counterexamples: Rezné odporúčanie bez zdroja uložené ako CuttingTool.
- Related concepts: `ManufacturingProcess`, `Supplier`, `PropertyRecord`.
- Future implementation notes: Typ nástroja vs konkrétny nástroj potrebuje doménové rozhodnutie.

### G-0052 Lifecycle

- Identifier: `G-0052`
- Preferred term: `Lifecycle`
- Definition: Povolený sled stavov riadeného objektu.
- Allowed usage: Používa sa pre dokumenty, entity, RFC a katalógové položky.
- Not allowed usage: Nepoužíva sa ako `verificationStatus` konkrétneho tvrdenia.
- Examples: `Draft -> Review -> Approved`.
- Counterexamples: `verified` ako lifecycle dokumentu.
- Related concepts: `Draft`, `Review`, `Deprecated`, `Archived`.
- Future implementation notes: RFC lifecycle môže mať odlišné stavy od dátových entít.

### G-0053 VerificationStatus

- Identifier: `G-0053`
- Preferred term: `VerificationStatus`
- Definition: Stav overenia konkrétneho tvrdenia, väzby alebo vnoreného objektu.
- Allowed usage: Používa sa pri `PropertyRecord`, `SourceLink`, `Observation` alebo `Capability`.
- Not allowed usage: Nepoužíva sa ako lifecycle celej entity.
- Examples: Stav overenia vlastnosti.
- Counterexamples: `Approved` dokumentu používané ako verification status poľa.
- Related concepts: `Verification`, `Lifecycle`, `PropertyRecord`.
- Future implementation notes: Hodnoty verification status treba štandardizovať pred schémami.

### G-0054 Revision

- Identifier: `G-0054`
- Preferred term: `Revision`
- Definition: Menšia zmena v rámci rovnakej verzie bez zásadnej zmeny významu alebo kontraktu.
- Allowed usage: Používa sa pre dokumenty a dátové záznamy podľa pravidiel EOS.
- Not allowed usage: Nepoužíva sa ako náhrada za významovú verziu.
- Examples: Jazyková úprava dokumentu zvýši revision.
- Counterexamples: Zmena dátového kontraktu riešená iba revision.
- Related concepts: `Version`, `recordVersion`, `DocumentRecord`.
- Future implementation notes: Rozdiel medzi document revision a record revision musí zostať jasný.

### G-0055 Version

- Identifier: `G-0055`
- Preferred term: `Version`
- Definition: Významová alebo kontraktová verzia dokumentu, schémy alebo záznamu.
- Allowed usage: Používa sa pre významné zmeny obsahu alebo kontraktu.
- Not allowed usage: Nepoužíva sa pre drobnú opravu textu.
- Examples: Zmena štruktúry kontraktu zvýši version.
- Counterexamples: Preklep zvyšujúci version.
- Related concepts: `Revision`, `schemaVersion`, `recordVersion`.
- Future implementation notes: Dátové entity používajú `schemaVersion` a `recordVersion`.

### G-0056 Draft

- Identifier: `G-0056`
- Preferred term: `Draft`
- Definition: Pracovný stav návrhu alebo záznamu pred review.
- Allowed usage: Používa sa pre neukončené dokumenty alebo záznamy.
- Not allowed usage: Nepoužíva sa pre schválené alebo používané autoritatívne záznamy.
- Examples: RFC-0003 vzniká ako Draft.
- Counterexamples: Dokument používaný ako záväzný v stave Draft.
- Related concepts: `Review`, `Lifecycle`.
- Future implementation notes: Draft môže mať prázdne sourceLinks iba podľa pravidiel EOS.

### G-0057 Review

- Identifier: `G-0057`
- Preferred term: `Review`
- Definition: Stav pripravený na kontrolu pred prijatím alebo schválením.
- Allowed usage: Používa sa pre dokumenty alebo návrhy čakajúce na posúdenie.
- Not allowed usage: Nepoužíva sa ako dôkaz schválenia.
- Examples: RFC-0001 je v Review.
- Counterexamples: Implementácia spustená iba na základe Review RFC bez schválenia.
- Related concepts: `Draft`, `Accepted`, `Approved`.
- Future implementation notes: Review záznamy s tvrdeniami potrebujú zdrojové väzby podľa pravidiel.

### G-0058 Accepted

- Identifier: `G-0058`
- Preferred term: `Accepted`
- Definition: Stav návrhového dokumentu, ktorý bol prijatý ako architektonický alebo znalostný smer.
- Allowed usage: Používa sa najmä pre RFC alebo rozhodnutia návrhového charakteru.
- Not allowed usage: Nepoužíva sa automaticky ako stav dátovej entity, ak jej lifecycle používa `Approved`.
- Examples: Accepted RFC môže odblokovať implementáciu.
- Counterexamples: Materiálová entita označená Accepted namiesto Approved.
- Related concepts: `Review`, `Rejected`, `Superseded`.
- Future implementation notes: RFC lifecycle treba formálne zaviesť v governance.

### G-0059 Rejected

- Identifier: `G-0059`
- Preferred term: `Rejected`
- Definition: Stav návrhu, ktorý bol posúdený a neprijatý.
- Allowed usage: Používa sa pre RFC alebo návrhy, ktoré nemajú byť implementované.
- Not allowed usage: Nepoužíva sa pre zastarané schválené záznamy; tie sú `Deprecated` alebo `Archived`.
- Examples: Zamietnutý návrh dátového modelu.
- Counterexamples: Starý schválený katalógový záznam označený Rejected.
- Related concepts: `Accepted`, `Superseded`, `Deprecated`.
- Future implementation notes: Rejected návrhy sa nemažú, aby ostal audit rozhodnutia.

### G-0060 Superseded

- Identifier: `G-0060`
- Preferred term: `Superseded`
- Definition: Stav návrhu alebo dokumentu nahradeného novším návrhom alebo rozhodnutím.
- Allowed usage: Používa sa pre RFC alebo dokumenty nahradené novou verziou.
- Not allowed usage: Nepoužíva sa pre bežnú archiváciu bez náhrady.
- Examples: RFC nahradené novým RFC.
- Counterexamples: Draft bez pokračovania označený Superseded.
- Related concepts: `Accepted`, `Deprecated`, `Archived`.
- Future implementation notes: Musí uvádzať náhradu.

### G-0061 Deprecated

- Identifier: `G-0061`
- Preferred term: `Deprecated`
- Definition: Stav schváleného záznamu alebo položky, ktorý sa už neodporúča používať, ale zostáva dostupný pre históriu.
- Allowed usage: Používa sa pre katalógové položky, entity alebo dokumenty nahradené novším významom.
- Not allowed usage: Nepoužíva sa na tiché odstránenie záznamu.
- Examples: Deprecated Unit Catalog Entry s náhradou.
- Counterexamples: Vymazanie položky bez histórie.
- Related concepts: `Archived`, `Superseded`, `Lifecycle`.
- Future implementation notes: Deprecated položky musia zostať referencovateľné.

### G-0062 Archived

- Identifier: `G-0062`
- Preferred term: `Archived`
- Definition: Stav historicky uchovaného objektu bez aktívneho používania.
- Allowed usage: Používa sa pre dokumenty alebo entity ponechané pre audit.
- Not allowed usage: Nepoužíva sa ako náhrada za vymazanie pracovného Draft bez významu.
- Examples: Starý dokument uchovaný pre históriu.
- Counterexamples: Aktívne používaný záznam označený Archived.
- Related concepts: `Deprecated`, `Lifecycle`, `Revision`.
- Future implementation notes: Archived objekty majú zostať čitateľné, ale nie aktívne upravované.

## 5. Terminology Rules

1. Každý autoritatívny pojem má jeden preferovaný názov.
2. Alias je povolený iba ako informatívna poznámka, nie ako rovnocenný termín.
3. Autoritatívne dokumenty nesmú používať synonymá pre rovnaký objekt.
4. Definícia pojmu sa nesmie meniť bez RFC alebo ADR.
5. Názvy objektov v JSON schémach musia byť konzistentné s týmto slovníkom.
6. Pojmy sa nesmú používať vo voľnom význame mimo definície.
7. Ak dokument potrebuje nový význam existujúceho pojmu, musí najprv aktualizovať slovník.
8. Ak pojem existuje v slovníku, nové RFC a ADR sa naň majú odkazovať rovnakým názvom.

## 6. Naming Rules

| Category | Naming rule | Example |
| --- | --- | --- |
| Entity | PascalCase | `Material` |
| Value Object | PascalCase | `Quantity` |
| Catalog Entry | PascalCase for object name, stable ID for record | `PropertyCatalogEntry`, `PRP-xxxxxx` |
| Property IDs | `PRP-xxxxxx` | `PRP-000001` |
| Unit IDs | `UNT-xxxxxx` | `UNT-000001` |
| Observation IDs | `OBS-xxxxxx` | `OBS-000001` |
| RFC | `RFC-xxxx` | `RFC-0003` |
| ADR | `ADR-xxxx` | `ADR-0013` |
| EOS governance document | `EOS-xxx` | `EOS-003` |

Programové identifikátory, JSON polia a názvy tried majú byť po anglicky. Projektové vysvetlenia a používateľská dokumentácia majú byť po slovensky s diakritikou.

## 7. Future Governance

Tento slovník má byť referenčným dokumentom pre budúce RFC, ADR, JSON schémy a dokumentáciu.

Odporúčané pravidlá:

1. Nový technický pojem sa najprv doplní do slovníka alebo do RFC, ktoré slovník mení.
2. Zmena významu existujúceho pojmu vyžaduje RFC alebo ADR.
3. Schémy nesmú zavádzať nový objektový názov, ktorý nie je v slovníku alebo schválenom RFC.
4. Governance dokumenty majú rozlišovať terminologické zmeny od architektonických rozhodnutí.
5. Pri konflikte medzi neformálnym použitím a slovníkom má prednosť slovník.

## 8. Open Questions

Tieto pojmy alebo oblasti ešte potrebujú samostatné RFC alebo ADR:

- `EngineeringConcept` - či má vzniknúť sémantická vrstva nad Property Catalog.
- `Decision` - či dostane vlastný prefix a plný kontrakt v `0.2B.1`.
- `Relationship` - kedy sa stane first-class object.
- `Measurement` - či bude subtype `Observation` alebo samostatná entita.
- `Inspection` - či bude subtype `Observation` alebo samostatná entita.
- `Snapshot` - či dostane vlastný prefix a samostatný lifecycle.
- `Derived Result` - či bude univerzálny objekt alebo rodina engine-specific výstupov.
- `Recommendation` - ako odlíšiť AI návrh, pravidlový návrh a engineer-approved decision.
- `VerificationStatus` - presný enum hodnôt.
- `Catalog hierarchy` - presné pravidlá pre Reference Catalog a Knowledge Catalog.
- `Approved` - či sa má používať iba pri dátových entitách alebo aj pri niektorých dokumentoch vedľa `Accepted`.

## 9. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-07-14 | 0.1 | 0 | Chief Engineering Knowledge Architect + Codex | Initial glossary draft |
