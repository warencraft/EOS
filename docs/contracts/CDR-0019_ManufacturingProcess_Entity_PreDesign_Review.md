# CDR-0019 ManufacturingProcess Entity Pre-design Review

Project: EOS – Engineering Operating System
Contract Review ID: CDR-0019
Contract: ManufacturingProcess
Review type: Pre-design
Phase: 0.2C.3-prep
Version: 0.1
Revision: 0
Status: Review
Document basis: Accepted EOS architecture + completed Material and Supplier phases

## 1. Purpose

Určiť bezpečný prvý profil ManufacturingProcess pred implementáciou. Rozhodujúca hranica je medzi definíciou typu procesu a jeho konkrétnym použitím, nastavením, schopnosťou, výkonom a obchodným ocenením. JSON tvar nesmie tieto významy potichu zlúčiť.

## 2. Scope

Review rieši identity, kategóriu objektu, ownership, minimálne polia, parametre, capability, operation/routing hranice, provenance, lifecycle a rozšíriteľnosť. Vytvára iba tento dokument. Nezavádza ManufacturingProcess schému, reálne procesné záznamy, taxonómiu, parametre ani ďalšiu entitu.

## 3. Reviewed Artifacts

Autority a precedent:

- AGENTS.md, EOS-000, EOS-003, EOS-006, EOS-007, EOS-009 a EOS-010;
- Accepted RFC-0001, RFC-0002 a RFC-0003, relevantné Accepted ADR-0015 a ADR-0016;
- CDR-0015 až CDR-0018 vrátane aktuálnych corrective outcomes;
- Material a Supplier schémy; všetkých sedem Knowledge Core a štyri katalógové schémy;
- central identifiers, common metadata, SourceLink, lifecycle a index; existujúce NormReference a DocumentRecord;
- CatalogRegistry, ValidationContext a validator composition;
- BACKLOG, ROADMAP, CHANGELOG a schemas/scripts/tests README.

Pre-flight 2026-10-15: čistá vetva `feature/phase-0.2c-knowledge-entities`, HEAD `4c14a3e670833a8a99a02bf7f6d5ee5c63ada3f2`, tracking `origin/feature/phase-0.2c-knowledge-entities`, lokálny tracking rozdiel 0/0. Material aj Supplier COMPLETE; SEC-0001/0002/0003 CLOSED. Existujúca sada: 263 tests, 263 passed, 0 failed, 0 errors, OK. Schémy: 22 total, 7 Knowledge Core, 4 catalogs, 2 entities (Material/Supplier). ADR dokumenty 17, RFC dokumenty 4 vrátane cross-review. ManufacturingProcess, Machine, CuttingTool, StockMaterial a Job schémy neexistujú. Runtime má katalógový register, nie generic entity resolver. Nenájdené reálne ManufacturingProcess záznamy; fiktívne TEC referencie nie sú populáciou entity.

## 4. Authoritative Findings

| Oblasť | Stav | Autorita a záver |
| --- | --- | --- |
| Doménový význam | AUTHORITATIVE | RFC-0002 §4.3, RFC-0003 G-0050: typ výrobného alebo kontrolného procesu, nie vykonanie operácie |
| Kategória | AUTHORITATIVE | RFC-0002 §4.3, §10.4, §16; ADR-0015: Knowledge Entity, Entity, Aggregate Root |
| Identita | AUTHORITATIVE | EOS-003 Active TEC, central identifiers a RFC súhlasia na TEC-xxxx |
| Transakčná hranica | AUTHORITATIVE | RFC-0002 §10.4: definícia typu procesu |
| Vnorené hodnoty | AUTHORITATIVE PERMISSION | RFC povoľuje Capability, Condition, PropertyRecord a Classification; netvrdí, že všetky musia byť required v prvom profile |
| Operácia | AUTHORITATIVE | G-0044: JobOperation je jedna job-owned operácia, nie definícia typu |
| Čas | AUTHORITATIVE | G-0045 a RFC-0002 §10.4: čas viazaný na operáciu/context, nie garantovaný generický čas |
| Kontrolné procesy | AUTHORITATIVE | Výslovne súčasť G-0050 a §4.3 |
| Process Type Catalog | DEFERRED | RFC-0002 §9.5: až po základných ManufacturingProcess kontraktoch; ID neurčené |
| Observation | AUTHORITATIVE / IMPLEMENTED | Samostatný root; subjectId už povoľuje central TEC |
| Hierarchia/parametre/qualification | DEFERRED | Žiadny implementovaný riadený kontrakt pre požadovanú sémantiku |
| NormReference a DocumentRecord | IMPLEMENTED | Foundation schémy už existujú; chýba špecifický process applicability/relationship profil |

Nasledujúce v1 odporúčania sú implementačným zúžením dovoleného modelu, nie zmenou Accepted architektúry. Nezakazujú budúci riadený Capability alebo PropertyRecord model.

## 5. Domain Meaning

Primárny význam v1 je kandidát A: **znovupoužiteľná inžinierska definícia jedného typu výrobnej alebo kontrolnej metódy**. Nie je to konkrétna operácia, operation template, routing step, machine capability, supplier service listing ani vykonaná udalosť.

Procesná rodina môže byť predmetom konceptuálneho členenia, ale jej názov sám nezakladá konkrétnu TEC identitu. V1 eviduje source-backed definíciu typu s explicitným scope; nevytvára generic service catalog alebo taxonomický strom.

## 6. Examples / Counterexamples

Nasledujúce názvy sú iba používateľom navrhnuté konceptuálne ilustrácie, nie autoritatívne EOS položky alebo overené technologické tvrdenia. Žiadne ID ani technické hodnoty sa im nepriraďujú.

| Označenie | Posúdenie pre typ procesu |
| --- | --- |
| Turning | Kandidát opakovane použiteľnej metódy; scope musí vysvetliť definícia |
| Milling | Kandidát typu, nie konkrétne frézovanie dielu |
| Drilling | Kandidát typu, nie konkrétny otvor alebo krok |
| Cylindrical grinding | Kandidát užšieho definovaného typu |
| Honing | Kandidát metódy, bez implicitných quality/capability hodnôt |
| Welding | Široký termín; pred onboardingom rozlíšiť všeobecný typ a čisto klasifikačnú rodinu |
| TIG welding | Kandidát špecifickejšieho typu; tento review nepotvrdzuje synonymá ani normové kódy |
| Nitriding | Kandidát typu; nie konkrétny časovo-teplotný recept |
| Induction hardening | Kandidát typu; nie konkrétny výsledný stav dielu |
| Laser cutting | Kandidát typu; nie schopnosť konkrétneho stroja |
| Bending | Kandidát typu; nie požadovaný uhol a polomer dielu |
| Heat treatment | Široká rodina/typ; bez scope definície nevytvárať automaticky TEC |
| Painting | Kandidát výrobnej/povrchovej metódy pri definovanom scope |
| Dimensional inspection | Kandidát kontrolného typu, výslovne v Accepted rozsahu |

| Neprocesový príklad | Kam význam patrí |
| --- | --- |
| Sústružiť konkrétny priemer, toleranciu a dĺžku | Operation + požiadavky dielu |
| Obrábať na konkrétnom CNC sústruhu | Výber stroja/setup v operácii |
| Konkrétny počet minút sústruženia | Plánovaný/skutočný čas operácie alebo výpočet |
| Použiť konkrétnú doštičku | Tool selection/recommendation v kontexte |
| Operácia 20 | Poradie alebo identita routing/job kroku |
| Dodávateľ zvládne určitý priemer | Scoped supplier/site capability claim |
| Konkrétna hodinová cena | Commercial/costing context |

Číselné a značkové príklady zo zadania sa nepreberajú ako technické dáta ani odporúčania.

## 7. Object Type

ManufacturingProcess je Knowledge Entity, Entity a Aggregate Root podľa RFC-0002 §4.3, §10.4 a §16. Má stabilnú identitu, vlastnú revíziu, lifecycle, provenance a nezávislé referencie. Môže vlastniť dohodnuté embedded Value Objects; nesmie vlastniť iný Aggregate Root.

Nie je Catalog Entry ani Value Object. Budúci Process Type Catalog nemení aktuálnu kategóriu a nesmie sa zaviesť ako druhý vlastník TEC identity bez samostatného rozhodnutia.

## 8. Identifier

Textový formát: `TEC-xxxx`. Presný centrálny regex: `^TEC-[0-9]{4}$`. Definícia: `schemas/common/identifiers.schema.json#/$defs/TEC`, canonical referencia `https://eos.local/schemas/common/identifiers.schema.json#/$defs/TEC`.

Autority: EOS-003 TEC Active; RFC-0002 §16; RFC-0003 G-0050; implementovaný identifier. Všetky sa zhodujú. Vlastné pole odporúčam `id`; nový prefix alebo lokálny regex sa nesmie vytvoriť.

## 9. Identity Semantics

Jedno TEC identifikuje jeden riadený, zdrojovo podložený význam typu výrobnej alebo kontrolnej metódy, znovupoužiteľný nezávisle od konkrétnej zákazky, stroja a dodávateľa. Identitu určuje definovaný význam, nie label, organizácia používateľa alebo sada nastavení.

Zmena názvu, textová oprava, nové zdroje alebo klasifikačné zaradenie pri zachovaní významu nemenia TEC; zmena záznamu sa auditovane verzuje. Nový zásadne odlišný typ/metóda alebo užšia samostatne riadená definícia dostane odlišné TEC. Pôvodné TEC sa nesmie ticho preinterpretovať na nový význam. Samotná zmena parametra, stroja, tool, dielu, času či ceny nové TEC nevyžaduje.

V1 nezavádza algoritmus na rozhodnutie synonymity, taxonomickej úrovne alebo equivalence. Pred reálnym onboardingom musí reviewer pomocou zdrojov určiť, či ide o existujúci význam alebo nový typ; bez toho sa z nejasného názvu nesmie zakladať schválený proces. Tieto authoring pravidlá nevyžadujú ďalšie root polia.

## 10. Process vs Operation

ManufacturingProcess definuje typ metódy; JobOperation je jej použitie v konkrétnej zákazke podľa G-0044. Operation template by bol budúci opakovateľný plán použitia, nie ďalší názov pre ManufacturingProcess.

Target geometry, dimensions, tolerance, skutočný materiál, zvolený stroj/tool, cutting parameters, setup, cycle time a quantity patria do budúceho operation/planning/execution contextu. V1 nič z toho nevnára. Budúca operácia môže referencovať TEC; process root nevlastní operácie.

## 11. Process vs Routing / ProcessPlan

Process je metóda, operation jej aplikácia a ProcessPlan/Routing poradie operácií s kontextom. Work instruction, traveler a technologický postup môžu popisovať alebo riadiť použitie, ale nie sú samotnou TEC identitou.

V1 nemá steps, sequence, routing, operationIds alebo executable template. Presné budúce kontrakty a ich prefixy sa nenavrhujú.

## 12. Process Family / Variant

Odporúčanie: žiadny parentProcessId, processFamily alebo subtype enum. Generic Classification môže kategorizovať definovaný typ; nevytvára hierarchy alebo inheritance.

External/internal turning, facing/threading, face/peripheral/pocket milling, zváracie varianty a skupiny tepelných metód zo zadania sú kandidáti budúcej terminologickej analýzy. Samostatný TEC je vhodný iba pri samostatne definovanom stabilnom type; variant iba v hodnotách nastavenia zostáva operation/recipe variantom. Review neurčuje ich konkrétne členenie ani taxonómiu.

Široká rodina nevytvára implicitný parent TEC a užší typ z nej nededí capability. Existencia rôzne širokých definícií neznamená, že medzi nimi už EOS pozná vzťah.

## 13. Name Model

Odporúčam required neprázdny `name` a **required neprázdny `description`**, ktorý vymedzí význam a scope typu. Povinný opis odlišuje sémanticky definovaný proces od samotného nejednoznačného labelu. Nie je to vykonateľná inštrukcia ani parameter bag.

Name nie je identita ani schema-level unique kľúč. ShortName, code, designation a processCode sa odložia. Notes je voliteľný podporný text, nie náhrada definície alebo štruktúrovaných odložených dát.

## 14. Classification

V1 má voliteľné `classifications: Classification[]`, povoľované RFC-0002 §4.3/§10.4. Supplier precedent ukazuje runtime reuse, ale doménové povolenie pochádza z process architektúry. Prázdne pole aj viac assignments sú povolené, poradie nemá prioritu a bez ďalšej policy sa nezavádza uniqueness podľa CLS.

Owned je assignment, nie catalog entry. Assignment.sourceLinks podporuje zaradenie; root sourceLinks definíciu procesu. CLS existencia a lifecycle sú overiteľné context-aware, process applicability a správnosť kategórie zostávajú authoring/governance zodpovednosťou. Nevytvárajú sa reálne kategórie.

## 15. PropertyRecord

Vyberá sa B/D zo zadania: Classification áno, `properties` odložiť pre v1. RFC procesné PropertyRecord výslovne povoľuje, preto ich tento review nezakazuje v celom EOS. Chýba však presne ohraničený v1 use case intrinsic process claim odlíšený od setting, parameter definition a scoped capability.

Existujúci numeric PropertyRecord nie je ProcessParameterDefinition ani universal key/value store. Neskorší návrh môže povoliť source-backed intrinsic claims s vlastnými Conditions bez reinterpretácie TEC identity. Aktuálny úzky profil ich nepotrebuje.

## 16. Process Parameters

V1 neobsahuje parameter hodnoty ani parameter mapu. Cutting speed/feed/depth, current/voltage/travel speed, temperature/time alebo angle/radius zo zadania sú názvy potenciálnych veličín, nie univerzálne procesné hodnoty.

Ich význam treba odlíšiť ako definition, plánované nastavenie, machine setting alebo pozorovaný výsledok. Jeden údaj nemožno automaticky zaradiť iba podľa názvu. Budúci ProcessParameterDefinition je návrhová téma, nie nový kontrakt tohto review.

## 17. Parameter Definitions vs Values

„Proces používa parameter X“ definuje význam, použiteľnosť a prípadné constraints. „Pre túto operáciu X má plánovanú hodnotu“ patrí recipe/operation. „Skutočne zistené X“ je evidence s časom a subject contextom.

Žiadna z týchto štruktúr nie je required pre identity-only v1. PRP katalóg definuje význam vlastnosti, ale neurčuje automaticky, či je povoleným nastavovaným procesným parametrom. Observation numeric profil takisto nie je všeobecný execution log.

## 18. Material Relationship

Bez materialIds a bez reciprocal processIds v Materiale. Compatibility závisí od okolností použitia; samotný TEC–MAT pair nesmie preukazovať technickú vhodnosť. Budúci scoped compatibility/capability model môže referencovať oba roots, ale tu sa nenavrhuje.

## 19. StockMaterial Relationship

ManufacturingProcess nevlastní stock items, skladové formy ani inventory. Konkrétny vstupný polotovar patrí do operation/planning contextu. V1 nebude mať stockMaterialIds a nevyžaduje existenciu StockMaterial schémy.

## 20. Machine Relationship

Bez machineIds a bez predpisovania processIds na budúcom Machine. Machine capability je kontextové tvrdenie viazané na konfiguráciu/verziu zariadenia a podmienky; jednoduchá root array to nepreukazuje.

RFC povoľuje referencie na Machine, nie povinnosť realizovať ich už teraz. Budúci Machine/Capability návrh určí smer a kardinalitu; nikdy nie embedding rootu.

## 21. CuttingTool Relationship

V1 nemá cuttingToolIds ani konkrétne odporúčané nástroje. Tool selection patrí do operation/setup/recipe/recommendation alebo capability contextu. ManufacturingProcess nevlastní CuttingTool aggregate.

## 22. Supplier Relationship

Proces ani Supplier nevlastnia jeden druhého a v1 nebude obsahovať supplierIds. Poskytovanie služby je sourced supplier/site capability alebo commercial relationship, nie univerzálna vlastnosť procesu. SUP identita organizácie zostáva oddelená od TEC metódy.

## 23. Capability Model

Capability vyjadruje schopnosť za definovaných podmienok; nie každá požiadavka je capability. Rozmery, materiál/stav, geometry, tolerance, roughness, mass, machine/site a quality scope môžu byť jej contextom.

RFC-0001 §4.8 a RFC-0002 povoľujú Capability ako owned Value Object s možným neskorším povýšením, nie automaticky samostatný relationship aggregate. Presné umiestnenie budúcej scoped capability sa preto nepredurčuje. V1 ju odloží; root maxDiameter, minTolerance alebo supportedMaterials by neoprávnene vytvárali univerzálne tvrdenia.

## 24. Input / Output Model

Inputs, outputs, inputTypes a outputTypes sa odložia. Konkrétny stock-to-part tok alebo transformed state patrí do operation/state modelu. V1 nezavádza generic object ports ani skrytý ProcessPlan.

## 25. State Transformation

Procesná definícia môže slovne charakterizovať účel metódy, ale v1 nemodeluje inputState/outputState, executable effects alebo zoznam automaticky transformed properties. Také pravidlá potrebujú workpiece/state/operation model a dôkazy; žiadne transformácie sa nespúšťajú ani neodvodzujú.

## 26. Material Condition

MaterialCondition bol v Material v1 odložený. Process root ho nesmie zaviesť cez requiredMaterialState, treatmentState, temperature alebo voľný recipe text. Conditions platnosti konkrétneho tvrdenia nie sú automaticky identitou dodacieho alebo tepelného stavu materiálu.

## 27. Quality / Result Requirements

Tolerance, achievableTolerance, roughness/Ra, qualityGrade a dimensionalAccuracy nie sú root polia v1. Požadovaný výsledok je requirement; tvrdenie o dosiahnuteľnosti je scoped capability; skutočný výsledok je evidence. Tieto významy sa nesmú zlúčiť ani zameniť s metrologickou neistotou.

## 28. Standards / Norms

Oprava predpokladu zadania: NormReference už existuje v `schemas/norm-reference.schema.json`. Neexistuje však riadená procesná applicability/qualification väzba. V1 preto používa SourceLink provenance, bez standards, normIds alebo voľných štandardových stringov.

Citácia zdroja neustanovuje záväznosť alebo platnosť normy pre každé použitie procesu. Structured normative relationship zostáva ďalším návrhom; interné STD a externé NRM sa nezamieňajú.

## 29. Document Relationship

DocumentRecord už existuje a je registrovaný v indexe. Procesná väzba na work instruction, WPS, procedure alebo setup sheet však ešte nemá určenú rolu, verziu a applicability.

V1 nepridáva documentIds. Dokument môže byť zdrojom cez existujúci SourceReference/SourceLink model; SRC referencia nie je DocumentRecord ID. ManufacturingProcess nevlastní dokumentový aggregate a dokument s inštrukciami sa nestáva process identity.

## 30. Provenance

Root sourceLinks je required common metadata kolekcia podporujúca identitu, definíciu a engineering meaning. Draft môže mať prázdne pole. Review/Approved definície musí mať zdroj cez EOS application rule.

Tieto zdroje automaticky nepreukazujú machine/supplier capability, parameter recommendation, dosiahnuteľnú toleranciu, cycle time ani cenu. Provenance matrix v §55 zachováva samostatné predmety tvrdení.

## 31. Lifecycle

Reuse common RecordStatus. Approved znamená schválený EOS záznam, nie qualified process, industrial maturity, validovaný špeciálny proces alebo shop-enabled stav. Revision/recordVersion auditujú definíciu; schemaVersion opisuje serializačný kontrakt. Root verificationStatus sa nepridáva.

## 32. Process Qualification

Qualified, approvalStatus, qualificationStatus a validationStatus sa v root odmietnu. Qualification potrebuje scope, organization/site, specification, equipment, personnel, dátum a evidence podľa budúceho prijatého modelu. CLS assignment ani root Approved ju nenahrádza.

## 33. Machine Parameters

SpindleSpeed, feedRate, cuttingSpeed, coolant, power a torque ako root hodnoty sa odmietajú. Definícia parametra by bola iný kontrakt; jeho existencia sa nepredstiera tým, že sa hodnota zabalí do Quantity alebo PropertyRecord.

## 34. Setup Time

SetupTime patrí ku kontextu stroja, prípravku, workpiece, batch, tool, obsluhy a plánu. Nie je všeobecnou TEC hodnotou. V1 ho neobsahuje; budúci plánovaný/skutočný TimeRecord sa viaže na operáciu podľa G-0045.

## 35. Cycle Time

CycleTime, timePerPart a processingTime nie sú root fields. Plánovaný výpočet je Derived Result alebo planning údaj; namerané vykonanie patrí TimeRecord/Observation podľa budúceho konkrétneho kontraktu. Žiadne guaranteed times sa v procese neukladajú.

## 36. Cost

HourlyRate, costPerHour, costPerKg, setupCost a processCost sa odmietajú. Patria do costing/commercial contextu s predmetom, časom, menou a zdrojom. ManufacturingProcess zostáva definíciou typu, nie kalkulátorom alebo cenovým cenníkom.

## 37. Energy / Consumables

V1 nemá spotrebu energie ani consumables lists. Shielding gas, coolant, abrasive či atmosphere môžu byť budúce recipe/operation/resource dáta so scope; ich použitie alebo spotreba sa nededí z generického TEC bez samostatného modelu.

## 38. Personnel / Qualification

Personálne oprávnenia alebo požiadavky na obsluhu nepatria do v1 root. Potrebujú kvalifikačný a procesný scope, platnosť a dôkazy. Review nevytvára Person, qualification enum ani implicitné pracovné oprávnenia.

## 39. Inspection Processes

Áno: kontrolné a skúšobné metódy sú v rozsahu ManufacturingProcess, pretože G-0050 a RFC-0002 §4.3 explicitne obsahujú kontrolný proces. Dimensional inspection a ďalšie používateľom uvedené názvy môžu byť kandidátmi definícií typu, nie automaticky produkčnými záznamami.

Metóda kontroly nie je konkrétne meranie, výsledok skúšky alebo pass/fail rozhodnutie; tie zostávajú operation/evidence/decision vrstve.

## 40. Logistics / Non-manufacturing Services

V1 sa obmedzí na výrobné a kontrolné metódy. Transport, storage a generic packaging service sa nepridávajú ako všeobecné služby. Packaging alebo cleaning sa môžu nachádzať na doménovej hranici: konkrétna source-backed výrobná metóda prípravy/povrchovej úpravy môže byť kandidátom, samotný servisný názov nie.

Nie je tu ustanovená univerzálna klasifikácia všetkých čistiacich alebo baliacich činností. Nejasný prípad sa pri onboardingu odloží na domain review; v1 kvôli nemu nevytvára serviceType ani rozšírený service catalog.

## 41. Process Taxonomy

Additive/subtractive/forming/joining/thermal/surface/inspection sú iba ilustračné kategórie z požiadavky. Použiť existujúce Classification assignments, ak neskôr vznikne riadený CLS význam; žiadne hard-coded rodiny alebo reálne CLS entries.

Process Type Catalog podľa RFC-0002 §9.5 zostáva deferred. Nesmie sa teraz rozhodnúť jeho ID ani duplicita voči TEC.

## 42. Hierarchy

ParentProcessId sa odkladá. Strom, DAG, širší/užší pojem a capability inheritance sú rôzne rozhodnutia. Bez governance taxonómie nie je bezpečné vynútiť jediného parenta. Classification dnes tiež neimplementuje taxonomickú hierarchiu.

## 43. Aliases / Synonyms

Bez aliases poľa. Jazykové názvy, obchodné pomenovania a odborné synonymá potrebujú terminologickú autoritu a collision pravidlá. Podobnosť názvu nepreukazuje totožný proces. Pri premenovaní so zachovaným významom sa nemení TEC; história patrí versioningu.

## 44. External Process Codes

ExternalCode, processCode a nekvalifikovaný code sa odložia. ERP/CAM/normový kód musí mať scheme, verziu a mapping provenance. TEC zostáva interná identita a nepreberá automaticky externú taxonómiu.

## 45. Equivalence

Same concept, synonym, equivalent/alternative/substitute process a broader/narrower concept nie sú rovnaké vzťahy. V1 ich neukladá a neodvodzuje z mena, CLS ani podobných parametrov. Substitúcia v konkrétnej zákazke by navyše vyžadovala requirement/capability a rozhodnutie.

## 46. Replacement / Supersession

Odporúčam odložiť `replaces` a `replacedBy` pre v1. RFC povoľuje supersession, ale neurčuje process-specific náhradu duplicate record oproti nahradeniu technickej metódy. Samotný štrukturálny TEC odkaz by ľahko vyzeral ako equivalence alebo technologická substitúcia.

Záznam možno lifecycle riadiť bez replacement grafu. Neskorší model môže zaviesť iba auditovanú record supersession s ochranou historického významu. Material precedent nie je povinnosť kopírovať tieto polia.

## 47. Observation

Existujúca Observation.subjectId union obsahuje central TEC. Je teda možné štrukturálne referencovať proces; existencia TEC ani vhodnosť subject granularity sa dnes neoveruje generic resolverom.

ManufacturingProcess nesmie obsahovať observations ani observationIds. Evidence ostáva samostatný Aggregate Root. Meranie konkrétnej operácie sa nesmie automaticky vydávať za univerzálne pozorovanie generického typu a nesmie ticho meniť jeho definíciu alebo claims.

## 48. MeasurementQuality

Nie je root objektom procesu. Opisuje metrologickú kvalitu konkrétneho numeric result/claim v existujúcom PropertyRecord alebo Observation. Nie je procesný quality score, výrobné tolerance ani qualification. Keďže properties sú v1 deferred, root MQ sa nepridáva.

## 49. Condition

RFC povoľuje procesné Conditions, ale root meaning nie je v prvom profile potrebný. V1 ich odkladá. Existujúci Condition vyjadruje kvalifikátor tvrdenia/pozorovania/capability, nie recept, state-transition program alebo celý machine setup.

Budúci procesný claim môže reuse-nuť CND/Quantity/ValueRange tam, kde je význam riadený. Temperature, machine reference či environment nesmú vytvoriť MaterialCondition alebo parameter model iba tým, že ich autor vloží do Condition.

## 50. Minimum Useful Process

Minimum: common required metadata, TEC `id`, neprázdny `name`, neprázdny `description` a required `sourceLinks` (Draft môže mať `[]`). Optional `classifications` a `notes`.

Povinná definícia umožní inkrementálne autorovanie bez Machine/Material/Supplier/Job závislostí, ale zabráni úplne prázdnemu pomenovaniu bez vysvetlenia typu. Vecnú kvalitu textu overí review, nie iba minLength. Draft nie je schválená technická znalosť.

## 51. Candidate Models

| Kandidát | Výsledok |
| --- | --- |
| A: identity, optional description/notes | Technicky malý; samotný name je príliš slabý pre hranicu typu, vyžaduje povinnú definíciu |
| B: identity + optional Classification | Odporúčaný profil s required description; podporuje viac riadených kategórií bez hierarchie |
| C: B + PropertyRecord | Accepted architektúra umožňuje, ale v1 odložiť pre riziko settings/capability reinterpretácie |
| D: nový parameter/operation/capability framework | Nie je nutný pre definíciu typu; nevytvárať |

Vyberá sa presne jeden profil B s explicitne required description. Nejde o nový domain object ani variantný discriminator.

## 52. Recommended v1 Model

Required: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `createdAt`, `createdBy`, `updatedAt`, `updatedBy`, `sourceLinks`, `changeSummary`, `name`, `description`.

Optional: `classifications`, `notes`. Žiadne ďalšie root polia. Closed object, central TEC a common metadata `$ref`, embedded Classification `$ref`. Name/description sú strings s minLength 1; notes reuse-nuje common definíciu. Classifications je optional array, môže byť prázdne, bez nových uniqueness/hierarchy/applicability pravidiel.

Toto je návrh kontraktu, nie vytvorená JSON Schema. Nevyžaduje zmenu Accepted významu: typ procesu zostáva definíciou metódy a povolené širšie owned concepts sa explicitne odkladajú.

## 53. Field Inventory

NOW označuje navrhovaný nasledujúci v1 profil; DEFER budúci model, REJECT neprípustný root shortcut v tomto profile.

| Pole | Stav | Dôvod |
| --- | --- | --- |
| id | REQUIRED NOW | Central TEC identity |
| common metadata | REQUIRED NOW | Verzie, revízia, audit, lifecycle, changeSummary |
| name | REQUIRED NOW | Canonical label, nie identita |
| description | REQUIRED NOW | Scope a definícia typu |
| classifications | OPTIONAL NOW | Existing embedded assignments |
| properties | DEFER | Odlišovať intrinsic claims od settings/capability |
| sourceLinks | REQUIRED NOW | Provenance definície |
| notes | OPTIONAL NOW | Podporný text, nie skrytá štruktúra |
| processType | REJECT | Neprijatý root discriminator; entity už je typ |
| processFamily | DEFER | Riadená kategorizácia cez CLS, nie enum |
| parentProcessId | DEFER | Hierarchy policy neexistuje |
| aliases | DEFER | Terminológia/language/collisions |
| parameters | REJECT | Generic parameter bag |
| parameterDefinitions | DEFER | Samostatná sémantika |
| inputTypes | DEFER | Input/state contract |
| outputTypes | DEFER | Output/state contract |
| materialIds | REJECT | Nepreukazuje compatibility |
| stockMaterialIds | REJECT | Operation input, nie process ownership |
| machineIds | REJECT | Scoped capability, nie univerzálny zoznam |
| cuttingToolIds | REJECT | Kontextový tool selection |
| supplierIds | REJECT | Scoped service capability |
| capability | DEFER | Accepted koncept bez implementovaného scoped profilu |
| supportedMaterials | REJECT | Univerzálne compatibility tvrdenie |
| maxDiameter | REJECT | Capability scope chýba |
| tolerance | REJECT | Requirement/capability/result nie identity |
| roughness | REJECT | Kontextový claim alebo requirement |
| temperature | REJECT | Nastavenie/výsledok nie univerzálna hodnota |
| cuttingSpeed | REJECT | Operation/recipe setting |
| feedRate | REJECT | Operation/recipe setting |
| spindleSpeed | REJECT | Machine/operation setting |
| setupTime | REJECT | Operation/context |
| cycleTime | REJECT | Operation/execution/calculation |
| hourlyRate | REJECT | Commercial/costing |
| cost | REJECT | Commercial/costing |
| standards | REJECT | Voľný string/array nenahrádza normative applicability |
| documentIds | DEFER | DocumentRecord existuje, process väzba nie |
| qualificationStatus | REJECT | Qualification patrí do scoped workflow |
| replaces | DEFER | Record supersession policy |
| replacedBy | DEFER | Nie equivalence/substitution |
| conditions | DEFER | Root význam nie je súčasť v1 |
| measurementQuality | REJECT | Kvalita konkrétneho výsledku |
| verificationStatus | REJECT | Common record lifecycle nie claim verification |
| observations / observationIds | REJECT | Samostatný evidence root |

CONDITIONALLY REQUIRED: neprázdny obsah sourceLinks pri Review/Approved definície. Nejde o ďalšie optional pole; kolekcia je vždy required.

## 54. Aggregate Ownership Matrix

| Objekt | Klasifikácia pre v1 | Hranica |
| --- | --- | --- |
| Classification | OWNED EMBEDDED VALUE | Assignment, nie catalog entry |
| PropertyRecord | DEFERRED | Accepted možnosť, nie v1 |
| Condition | DEFERRED | Nie recipe/state model |
| Observation | SEPARATE AGGREGATE | TEC subject referencia zvonka |
| MeasurementQuality | REJECTED | Priame root embedding; v budúcnosti iba pri result/claim |
| Material | SEPARATE AGGREGATE | Compatibility až so scope |
| StockMaterial | SEPARATE AGGREGATE | Budúci operation input |
| Machine | SEPARATE AGGREGATE | Bez embedding |
| CuttingTool | SEPARATE AGGREGATE | Bez embedding; jeho presná budúca kategória podľa Accepted review |
| Supplier | SEPARATE AGGREGATE | SUP organizácia, scoped service vzťah deferred |
| Job | SEPARATE AGGREGATE | Vlastní konkrétnu JobOperation |
| Operation | DEFERRED | JobOperation je job-owned entity, nie process child |
| ProcessPlan | DEFERRED | Poradie operácií nie type definition |
| ParameterDefinition | DEFERRED | Nie generic PRP mapping bez rozhodnutia |
| Capability | DEFERRED | RFC povoľuje owned VO; nepredpisovať nový root |
| Qualification | DEFERRED | Context/evidence/workflow |
| DocumentRecord | SEPARATE AGGREGATE | Process reference field deferred |
| NormReference | REFERENCED / DEFERRED FIELD | Konceptuálny reference object, bez v1 applicability poľa |
| SourceReference | REFERENCED | SourceLink SRC reference |

## 55. Provenance Matrix

| Vlastník | Podporovaný význam |
| --- | --- |
| ManufacturingProcess root | Identita, scope a definícia typu |
| Classification assignment | Konkrétne zaradenie typu |
| Budúci PropertyRecord | Konkrétne procesné engineering tvrdenie s contextom |
| Budúci ParameterDefinition | Význam a použiteľnosť parametra |
| Budúca Capability | Scoped machine/supplier/site/process schopnosť |
| Budúca Qualification | Kvalifikačný scope a dôkazy |
| Observation | Meraný/pozorovaný výsledok, nie automatický claim |
| Budúca Operation | Plánovaný/vykonaný kontext a jeho vlastné zdroje |

Root sourceLinks nenahrádza žiadny z downstream dôkazov. SourceLink musí odkazovať SRC a podporované tvrdenie/pole, nie generický zoznam dokumentov.

## 56. Validation Responsibility

| Vrstva | Nasledujúci v1 rozsah a limit |
| --- | --- |
| JSON Schema | Closed shape, required fields, TEC, common metadata, name/description a nested Classification |
| EOS application | Automatická root source povinnosť; reuse helpera bez duplicitnej diagnostiky explicit flagu podľa SEC-0002 |
| Reference integrity | CLS existence/type iba s explicitným CatalogRegistry; žiadny TEC/MAT/SUP resolver |
| Catalog validation | CLS lifecycle vrátane Deprecated warningu; bez process applicability |
| Workflow/governance | Definícia/identity review, schválenie recordu; qualification samostatne |
| Persistence/history | Uniqueness ID, concurrency a historické verzie neskôr |

PRP/CND/UNT consumer validácia nie je potrebná, keďže properties/conditions sú mimo v1. Reuse existujúce kategórie a úplné error paths. Contract-only úspech nepreukazuje catalog/business správnosť; validate_with_context naďalej potrebuje explicitný context aj pri prázdnych klasifikáciách.

## 57. Entity Resolver Requirement

Generic entity resolver nie je potrebný. V1 nemá machine/material/supplier/stock/job ani replacement referencie. CLS ide cez existujúci katalógový kontext. SourceReference existencia zostáva známym deferred limitom, nie predstieranou kontrolou.

## 58. Operation Model Dependency

Áno, typ procesu možno bezpečne implementovať pred Operation: Accepted architektúra ich už odlišuje. Podmienkou je nepreniesť target geometry, settings, routing, časy, náklady a vykonanie do TEC root. Budúca Operation môže referencovať stabilný typ bez zmeny jeho významu.

Ak by sa požadoval vykonateľný proces alebo parameter binding, tento readiness výsledok by už neplatil; najprv by bol potrebný príslušný samostatný návrh.

## 59. Real Data Boundary

Nevzniká žiadny reálny process record, Turning/Milling/Welding/Nitriding populácia, technické hodnoty alebo normová tabuľka. Názvy v §6 sú iba posudzované konceptuálne vstupy zo zadania. Fiktívne existujúce TEC referencie v testoch nedokazujú existenciu procesnej entity.

## 60. Future Real-data Requirements

Minimum onboardingu: riadená terminológia, stabilný scope typu, identity/dedup review, spoľahlivý zdroj a auditable record metadata. CLS taxonomy je potrebná až pre použité assignments; nie pre každý Draft.

Plná engineering knowledge navyše vyžaduje parameter semantics, scoped capability, normative applicability, operation/state model a qualification podľa použitia. Tieto rozšírenia nie sú predpokladom identity kontraktu a nesmú byť nahradené voľným textom.

## 61. Risks

| Riziko | Priorita | V1 ochrana |
| --- | --- | --- |
| Process zamenený za operation alebo routing | High | Explicitná identity a zákaz execution/steps fields |
| Parameter bag alebo PropertyRecord settings store | High | Properties/parameter definitions deferred, parameters rejected |
| Univerzálne capability tvrdenia | High | Scoped capability model mimo v1 |
| machineIds/materialIds/supplierIds predstierajú kompatibilitu | High | Bez root arrays |
| Hard-coded taxonomy alebo parentProcessId | Medium | Optional CLS bez hierarchy/inheritance |
| Parametre bez významu/unit/context | High | Žiadne parameter hodnoty v root |
| Časy a ceny generického procesu | High | Operation/Derived Result/Commercial hranica |
| Root status ako qualification | High | RecordStatus iba záznam; qualification deferred |
| Standards ako free text | Medium | SourceLink provenance, applicability deferred |
| Input/output bez state modelu | Medium | Bez generic ports a transformations |
| Capability bez site/machine scope | High | Nepovyšovať root identity na dôkaz schopnosti |
| Preťažená root provenance | High | Samostatná provenance matrix |
| Nestabilná identita pri synonymách/variantoch | Medium | Required definition a source-backed identity review; nie string-based dedup |
| Predčasná reálna populácia | High | Review-only, onboarding samostatne |
| Duplicitný budúci Process Type Catalog | Medium | Nevytvárať druhý TEC owner alebo nový prefix |

Žiadny z týchto riskov nevyžaduje inventovať novú architektúru pre obmedzený profil B; porušenie scope by však znamenalo nový pre-design gate.

## 62. Deferred Concepts

PropertyRecord intrinsic claims, Conditions, Capability, ParameterDefinition, recipe/settings, Operation/ProcessPlan serializácia, input/output/state, MaterialCondition, requirements/tolerance, norm/document applicability, qualification, resources/personnel, time/cost, hierarchy, aliases/external codes, equivalence/replacement, Process Type Catalog, persistence, generic entity resolver a real-data onboarding.

Odloženie nemení ich Accepted konceptuálnu prípustnosť a nepresúva ich do notes alebo description.

## 63. Implementation Preconditions

Pred následnou implementáciou potvrdiť tento presný obmedzený profil:

1. Jedno TEC znamená riadený typ výrobnej alebo kontrolnej metódy; nie operation instance/template alebo routing.
2. Reuse central TEC a common metadata; nemení sa governance ani identifier formát.
3. Required name a description definujú label a scope; nie unique string identity.
4. Optional Classification assignments; bez hard-coded families, hierarchy a applicability inference.
5. Žiadne PropertyRecord, Condition, parameter, Capability alebo MeasurementQuality root polia v1.
6. Bez Material/Machine/Supplier/StockMaterial/Tool/Job arrays, input/output a state transformations.
7. Required root sourceLinks; Draft môže byť prázdny, Review/Approved vyžaduje provenance definície.
8. Common RecordStatus nie je process qualification a root verificationStatus sa nepridáva.
9. Časy, ceny, tolerance/result requirements, personnel a resources zostávajú mimo profilu.
10. Replacement, norm/document applicability, aliases, kódy a equivalence sa odložia.
11. Observation zostáva samostatný root; current TEC subject union sa nemení.
12. Existing CLS/reference/catalog validation sa reuse-ne bez generic entity resolvera; source helper sa nesmie vykonať dvakrát pri explicitnom flagu.
13. Implementačné fixtures budú iba fiktívne; nový milestone nesmie populovať reálne procesy.

Žiadna nevyriešená otázka nevyžaduje nekompatibilné schémy v rámci tohto profilu. Granularita konkrétnych reálnych pojmov a logistické hraničné prípady sú governance/onboarding rozhodnutia; nie oprávnenie teraz modelovať všetky varianty. Ak sa rozšíri scope nad tieto podmienky, readiness treba prehodnotiť.

## 64. Readiness Verdict

Accepted architektúra jednoznačne odlišuje process type, JobOperation a vykonanie. TEC, Entity/Aggregate Root, provenance, lifecycle aj Classification reuse sú pripravené. Nie je nutná korekcia RFC/ADR ani implementácia Operation pred minimálnou definíciou typu.

Odporúčanie je READY WITH CONDITIONS, pretože bezpečný prvý profil je zámerne užší než širšie procesné knowledge/capability možnosti Accepted architektúry. Implementácia môže začať v samostatnom míľniku iba pre profil B s required description a všetkými 13 podmienkami §63. Nejde o súhlas s parametrami, capability, procesnou hierarchiou alebo reálnou populáciou.

## 65. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-10-15 | 0.1 | 0 | Codex | ManufacturingProcess pre-design: TEC type identity, operation/routing hranice, obmedzený profil B, ownership/provenance/validation matice a explicitné odloženie parametrov, capability a execution dát. |

READY WITH CONDITIONS
