# EOS-008 - Architecture Baseline

**Project:** EOS - Engineering Operating System  
**Document ID:** EOS-008  
**Version:** 0.1  
**Revision:** 0  
**Status:** Draft  
**Author:** Codex  
**Last updated:** 2026-07-25  
**Document basis:** Internal governance proposal  

## 1. Purpose

Tento dokument definuje pracovnú architektonickú baseline pre EOS pred začatím fázy `0.2B.1 Knowledge Core Contracts`.

Baseline zachytáva aktuálne vrstvy, zodpovednosti, povolené závislosti, otvorené otázky a vstupné podmienky. Dokument neakceptuje RFC-0001, RFC-0002 ani RFC-0003 a nevytvára dátové kontrakty.

## 2. Scope

Dokument pokrýva:

- architektonické vrstvy EOS,
- zodpovednosti jednotlivých vrstiev,
- povolené a zakázané závislosti,
- autoritatívne dokumenty,
- aktuálny stav RFC-0001 až RFC-0003,
- prijaté a predbežne zosúladené princípy,
- otvorené blokujúce a neblokujúce otázky,
- vstupné podmienky pre `Phase 0.2B.1`.

Dokument nepokrýva:

- JSON schémy technických entít,
- materiálové, technologické, strojové alebo obchodné dáta,
- kalkulačky,
- používateľské rozhranie,
- databázový server,
- REST API implementáciu,
- Graph DB implementáciu,
- AI vrstvu.

## 3. Current Architecture Layers

### 3.1 Governance Layer

**Responsibility:**  
Definuje pravidlá vývoja, dokumentácie, identifikácie, verzovania, validácie, lifecycle a architektonického rozhodovania.

**Authoritative documents:**  
`EOS-000` až `EOS-008`, prijaté ADR a prijaté RFC po ich formálnom schválení.

**Allowed dependencies:**  
Môže referencovať všetky nižšie vrstvy na úrovni pravidiel, nie na úrovni implementácie.

**Forbidden dependencies:**  
Nesmie závisieť od konkrétnej databázy, UI, kalkulačného enginu alebo runtime implementácie.

### 3.2 Engineering Knowledge Layer

**Responsibility:**  
Definuje všeobecné znalostné koncepty EOS: vlastnosti, jednotky, podmienky, pozorovania, dôkazy, rozhodnutia, katalógy, porovnateľnosť a odvodené výsledky.

**Authoritative documents:**  
RFC-0001, RFC-0002 a RFC-0003 po prijatí; zatiaľ sú iba návrhové alebo review dokumenty.

**Allowed dependencies:**  
Môže závisieť od Governance Layer a môže definovať pravidlá pre Knowledge Core Contracts, Knowledge Catalogs a Knowledge Entities.

**Forbidden dependencies:**  
Nesmie závisieť od konkrétnej entity ako `Material`, `Machine` alebo `Job` tak, aby všeobecné pravidlo prestalo byť opakovateľné naprieč doménami.

### 3.3 Knowledge Core Contracts

**Responsibility:**  
Definuje minimálne zdieľané kontrakty pre `Quantity`, `ValueRange`, `MeasurementQuality`, `PropertyRecord`, `Observation`, `SourceLink`, `verificationStatus`, lifecycle väzby a identifikátory.

**Authoritative documents:**  
Budúce kontrakty fázy `0.2B.1`, odvodené iba z prijatých RFC a ADR.

**Allowed dependencies:**  
Môže závisieť od Governance Layer a Engineering Knowledge Layer.

**Forbidden dependencies:**  
Nesmie obsahovať konkrétne technické hodnoty, materiálové dáta, strojové dáta, cenové dáta alebo pravidlá konkrétneho enginu.

### 3.4 Knowledge Catalogs

**Responsibility:**  
Definuje autoritatívne katalógové položky pre významy, jednotky, typy podmienok, klasifikácie a ďalšie riadené identifikátory.

**Authoritative documents:**  
Budúce dokumenty a kontrakty fázy `0.2B.2`.

**Allowed dependencies:**  
Môže závisieť od Knowledge Core Contracts.

**Forbidden dependencies:**  
Nesmie závisieť od konkrétnej knowledge entity ani od výstupov kalkulačného enginu.

### 3.5 Knowledge Entities

**Responsibility:**  
Definuje konkrétne znalostné entity ako `Material`, `StockMaterial`, `Machine`, `ManufacturingProcess`, `CuttingTool`, `Supplier` a ďalšie entity schválené pre fázu `0.2C` alebo neskôr.

**Authoritative documents:**  
Budúce RFC, ADR a JSON schémy po schválení.

**Allowed dependencies:**  
Môže závisieť od Knowledge Core Contracts, Knowledge Catalogs, `SourceReference` a governance pravidiel.

**Forbidden dependencies:**  
Nesmie vlastniť iný aggregate root ako vnorený objekt. Nesmie obsahovať nezdrojované overiteľné technické tvrdenia v stave `Review` alebo `Approved`.

### 3.6 Calculation Layer

**Responsibility:**  
Vykonáva výpočty nad vstupnými kontraktmi a produkuje odvodené výsledky, odporúčania alebo kontroly.

**Authoritative documents:**  
Budúce engine RFC, ADR a testované implementácie.

**Allowed dependencies:**  
Môže čítať Knowledge Core Contracts, Knowledge Catalogs a Knowledge Entities cez stabilné rozhrania.

**Forbidden dependencies:**  
Nesmie byť autoritatívnym zdrojom znalostí. Nesmie obsahovať hardcoded technické hodnoty bez zdroja.

### 3.7 Application Layer

**Responsibility:**  
Koordinuje použitie validačnej vrstvy, referenčnej integrity, workflow, aplikačných pravidiel, API a budúcich používateľských operácií.

**Authoritative documents:**  
Budúce aplikačné štandardy, API kontrakty a workflow dokumenty.

**Allowed dependencies:**  
Môže závisieť od všetkých nižších dátových a knowledge vrstiev cez schválené kontrakty.

**Forbidden dependencies:**  
Nesmie meniť význam prijatého RFC cez implementačnú skratku. Nesmie obchádzať source, lifecycle alebo revision pravidlá.

### 3.8 Integration Layer

**Responsibility:**  
Zabezpečuje import, export, synchronizáciu, externé systémy, budúce graph exporty a integračné adaptére.

**Authoritative documents:**  
Budúce integračné RFC, ADR a API kontrakty.

**Allowed dependencies:**  
Môže závisieť od Application Layer a schválených verejných kontraktov.

**Forbidden dependencies:**  
Nesmie používať export ako autoritatívny zdroj znalostí. Nesmie obísť validačnú vrstvu pri zápise údajov späť do EOS.

## 4. Dependency Rules

Povolený smer závislostí:

1. Governance Layer
2. Engineering Knowledge Layer
3. Knowledge Core Contracts
4. Knowledge Catalogs
5. Knowledge Entities
6. Calculation Layer
7. Application Layer
8. Integration Layer

Nižšia implementačná vrstva môže používať pravidlá vyššej normatívnej vrstvy. Normatívna vrstva nesmie byť technicky závislá od konkrétnej implementačnej vrstvy.

Zakázané závislosti:

- JSON schéma nesmie meniť význam prijatého RFC.
- Kalkulačný engine nesmie definovať autoritatívne znalostné hodnoty.
- UI nesmie určovať lifecycle ani zdrojové pravidlá.
- Export alebo import nesmie nahradiť `SourceReference`, `SourceLink` alebo governance audit.
- Aggregate root nesmie vlastniť iný aggregate root ako vnorený objekt.
- `Observation`, `Derived Result` alebo `Recommendation` nesmie automaticky prepísať autoritatívny `PropertyRecord` bez schváleného rozhodovacieho mechanizmu.

## 5. Current RFC State

| RFC | Title | Current status | Baseline interpretation |
| --- | --- | --- | --- |
| RFC-0001 | Engineering Property Model | Review, Revision 1 | Koncepčne použiteľný, ale pred 0.2B.1 potrebuje revíziu názvu `MeasurementQuality`, Observation scope a Decision boundary |
| RFC-0002 | Engineering Object Taxonomy | Review, Revision 1 | Hlavný návrh taxonómie, zatiaľ nie Accepted; potrebuje nadväzné ADR a zosúladenie prefixov |
| RFC-0003 | EOS Engineering Glossary | Draft, Revision 0 | Potrebný autoritatívny slovník, ale pred 0.2B.1 musí doplniť chýbajúce jadrové pojmy |

Baseline nesmie byť interpretovaná ako prijatie týchto RFC.

## 6. Accepted Architectural Principles

Tieto princípy už vyplývajú z existujúcej governance bázy alebo zo schválených predchádzajúcich rozhodnutí:

- EOS používa UTF-8 a slovenskú dokumentáciu s diakritikou.
- Programové identifikátory, JSON polia a názvy tried sú v angličtine.
- Kód počíta, databáza nesie znalosti a dokumentácia vysvetľuje.
- Overiteľné technické, výrobné, dodávateľské alebo obchodné tvrdenia potrebujú zdrojové väzby podľa lifecycle pravidiel.
- `SourceReference` je samostatná autoritatívna entita.
- `SourceLink` viaže tvrdenie alebo pole na zdroj, použitie zdroja a stav overenia.
- `schemaVersion`, `recordVersion` a `revision` majú odlišný význam.
- Štrukturálna JSON validácia používa štandardný JSON Schema Draft 2020-12 validátor.
- EOS aplikačná validácia zostáva oddelená od JSON Schema validácie.

Tieto princípy sú predbežne zosúladené v RFC, ale ešte potrebujú formálne prijatie pred implementáciou kontraktov:

- `Engineering Knowledge Layer` ako samostatná vrstva medzi governance a konkrétnymi knowledge entitami.
- Hybridná DDD taxonómia objektov.
- `Observation` ako first-class evidence entity.
- `PropertyRecord` ako embedded claim-like value object.
- Oddelenie `Reference Catalog` a `Knowledge Catalog`.

## 7. Open Blocking Questions

Tieto otázky blokujú začatie alebo schválenie `0.2B.1`:

- Má byť `MeasurementQuality` jediný autoritatívny názov namiesto `ValueQuality`?
- Je `Observation.observationScope` povinné pole pre všetky first-class observations?
- Je `Observation` vždy globálna entita s `OBS-xxxxxx`, alebo sa povolia job-owned embedded observations?
- Je `Decision` súčasťou `0.2B.1`, alebo len rezervovaný budúci objekt?
- Ak je `Decision` ukladaný objekt, aký prefix používa?
- Ktoré prefixy sa doplnia do `EOS-003` pred prvou JSON schémou?
- Má RFC lifecycle samostatné ADR alebo aktualizáciu governance štandardu?
- Ktoré chýbajúce glossary pojmy musia byť doplnené pred kontraktmi?

## 8. Nonblocking Deferred Questions

Tieto otázky nemusia blokovať `0.2B.1`, ak nie sú súčasťou prvých kontraktov:

- Kedy vznikne first-class `Relationship` object?
- Kedy vznikne všeobecný `Event` object?
- Kedy vznikne `Classification Catalog`?
- Kedy vznikne `Condition Type Catalog`?
- Má `Snapshot` samostatný prefix a vlastný lifecycle?
- Budú `Measurement` a `Inspection` subtype objektmi `Observation`, alebo samostatnými entitami?
- Ako presne sa bude mapovať EOS model do Graph DB?
- Ktoré pravidlá budú vyžadovať aplikačnú validáciu namiesto JSON Schema?

## 9. Entry Conditions For Phase 0.2B.1

Fáza `0.2B.1 Knowledge Core Contracts` môže začať až po splnení týchto podmienok:

- RFC-0001, RFC-0002 a RFC-0003 sú prijaté alebo explicitne schválené ako dostatočný vstup pre 0.2B.1.
- Cross-consistency findings so severity `Critical` sú uzavreté alebo formálne odložené s dôvodom.
- Všetky prefixy použité v 0.2B.1 sú schválené v `EOS-003` alebo v prijatom ADR s nadväznou úlohou.
- `Engineering Knowledge Layer` je schválená architektonickým rozhodnutím.
- Rozhodnuté je, či `Observation` je first-class aggregate root v 0.2B.1.
- Rozhodnuté je, či `Decision` patrí do 0.2B.1.
- Chýbajúce glossary pojmy potrebné pre kontrakty sú doplnené v RFC-0003.
- Validácia JSON Schema a EOS aplikačná validácia zostávajú oddelené.
- Testy existujúcej validačnej vrstvy prechádzajú.

## 10. RFC And Implementation Governance Rules

Po prijatí tejto baseline platia pre ďalšie architektonické práce tieto pravidlá:

- Nový RFC po baseline má vzniknúť iba pri reálnom architektonickom probléme alebo významnej zmene rozsahu.
- Implementácia nesmie meniť význam Accepted RFC bez nového RFC alebo ADR.
- JSON schéma môže spresniť formu, ale nesmie potichu zmeniť význam pojmu.
- Ak implementácia odhalí rozpor medzi RFC a schémou, problém sa najprv zdokumentuje a až potom opraví.
- Draft alebo Review RFC sa nesmie používať ako finálny kontrakt bez explicitného schválenia.

## 11. Decisions Still Needing ADR

Pred alebo počas uzatvárania baseline sú odporúčané tieto ADR:

- Adopt hybrid DDD engineering object taxonomy.
- Establish RFC governance lifecycle.
- Establish Engineering Knowledge Layer.
- Treat Observation as first-class evidence entity.
- Separate Reference Catalogs and Knowledge Catalogs.

ADR o oddelení Reference Catalogs a Knowledge Catalogs je potrebné najneskôr pred `0.2B.2`. Ostatné uvedené ADR sú odporúčané pred začatím `0.2B.1`, ak majú byť ich pravidlá použité v prvých kontraktoch.

## 12. Change History

| Date | Version | Revision | Author | Summary |
| --- | --- | --- | --- | --- |
| 2026-07-25 | 0.1 | 0 | Codex | Initial architecture baseline draft before Phase 0.2B.1 |
