# CDR-0021 Machine Entity Pre-design Review

Project: EOS – Engineering Operating System
Contract Review ID: CDR-0021
Contract: Machine
Review type: Pre-design
Phase: 0.2C.4-prep
Version: 0.1
Revision: 0
Status: Review
Document basis: Accepted EOS architecture + completed Material, Supplier and ManufacturingProcess phases

## 1. Purpose

Určiť najmenší bezpečný Machine v1 pred implementáciou. Review oddeľuje prijaté autority od návrhov, najmä fyzickú jednotku od typu/modelu, špecifikáciu od capability a meranie od claim. Review sám nenahrádza chýbajúce doménové rozhodnutie.

## 2. Scope

Iba tento CDR. Bez schémy Machine/MachineModel/MachineCapability, fixtures, runtime zmien, reálnych strojov alebo zmien RFC/ADR/governance/plánovania. Odporúčané polia sú návrhom pre následné explicitné rozhodnutie, nie už povolenou implementáciou.

## 3. Reviewed Artifacts

Vstup: vetva `feature/phase-0.2c-knowledge-entities`, HEAD `e859f47d51fde4e072d3afd82471725486eb59ec`, clean tree, tracking `origin/feature/phase-0.2c-knowledge-entities` s lokálnym rozdielom 0/0; nebol vykonaný nový fetch. Material, Supplier a ManufacturingProcess sú uzatvorené podľa CDR-0016/0018/0020; staršie plánovacie top sekcie ešte opisujú predchádzajúci closure krok a tento review ich nemení.

Autority: AGENTS, EOS-000/003/006/007/009/010, Accepted RFC-0001/0002/0003 a relevantné ADR-0013/0014/0015/0016. Precedenty CDR-0015 až CDR-0020; tri entity schémy; PropertyRecord, Classification, Observation, Condition, Quantity, ValueRange, MeasurementQuality; PRP/CLS/CND/UNT katalógy; common identifiers/metadata/SourceLink a index. Runtime CatalogRegistry/ValidationContext a validator; aktuálne BACKLOG/ROADMAP/CHANGELOG a schemas/scripts/tests README.

Skutočný full run: **290 passed, 0 failed, 0 errors, 0 skipped**, `Ran 290 tests in 27.375s`, `OK`. Všetkých 23 schém prešlo check_schema aj EOS schema-definition kontrolou. Knowledge Core 7, katalógy 4, entity 3 (Material/Supplier/ManufacturingProcess). ADR 17 súborov vrátane template, RFC 4 dokumenty vrátane cross-review. Žiadny Machine, MachineModel, MachineCapability, CuttingTool, StockMaterial, Job alebo Operation kontrakt. Register je katalógový, nie generic entity resolver. data/ obsahuje iba README; bez reálnych Machine záznamov.

## 4. Authoritative Findings

| Otázka | Stav | Dôkaz / záver |
| --- | --- | --- |
| Knowledge Entity / Entity | AUTHORITATIVE | RFC-0002 vrstva entít a §16; ADR-0015 |
| Aggregate Root a vlastný lifecycle | AUTHORITATIVE | RFC-0002 §4.4 a §10.3 |
| Fyzický kus vs riadený typ | OPEN, BLOCKING | RFC-0002 §4.4: „konkrétne výrobné zariadenie alebo riadený typ zariadenia podľa budúceho rozhodnutia domény“ |
| Rovnaká otvorená identita | OPEN, BLOCKING | RFC-0003 G-0046: typ vs konkrétny stroj môže vyžadovať spresnenie |
| MAC syntax | AUTHORITATIVE | EOS-003, identifiers, RFC-0002 §16, G-0046 zhodne MAC-xxxx |
| PropertyRecord ownership | AUTHORITATIVE PERMISSION | RFC-0002 §4.4/10.3 a RFC-0001 |
| Classification reuse | IMPLIED / RECOMMENDED | RFC-0001 §4.6 všeobecné zaradenie objektu a existing kontrakt; Machine-specific zoznam ho výslovne nevymenúva |
| Observation | AUTHORITATIVE / IMPLEMENTED | ADR-0016, numeric evidence profile, subjectId zahŕňa MAC |
| Capability | AUTHORITATIVE CONCEPT, DEFERRED CONTRACT | RFC-0001 §4.8 povoľuje owned VO s možným budúcim povýšením; nie povinný nový aggregate |
| Availability/CommercialObservation | AUTHORITATIVE PERMISSION, EXCLUDED FROM PROPOSED v1 | Povolenie širšieho modelu neznamená povinné v1 polia |
| Kontinuita po retrofit | OPEN POLICY | Common revision sama neurčuje fyzickú identity hranicu |
| MachineModel, WorkCenter, configuration history | DEFERRED | Bez prijatých implementovaných kontraktov |

Nenašiel sa konflikt MAC regexu. Blokér MI-0001 je výslovne odložené rozhodnutie o referentovi MAC, nie chyba identifikátora alebo existujúcich schém.

## 5. Machine Domain Meaning

Odporúčam presne kandidát A: **jedna individuálne identifikovateľná fyzická jednotka výrobného alebo kontrolného zariadenia**. Rozšírenie na kontrolné zariadenia musí byť zahrnuté v explicitnom identity rozhodnutí; review ho nepovažuje za samostatne prijatú taxonómiu. Nie model/type (B), trieda (C), WorkCenter (D), ľubovoľný resource abstraction (E) ani capability profil (F). Výber A je odporúčanie pre MI-0001, nie údajne už Accepted fakt.

## 6. Object Type

Knowledge Entity, Entity a Aggregate Root sú autoritatívne. Stabilné MAC, vlastná revízia/verzie, provenance, lifecycle a nezávislá referencia. Môže vlastniť embedded VOs, nie iný Aggregate Root. Nie Reference Object, Catalog Entry, Value Object alebo WorkCenter kolekcia. Chýbajúca physical-vs-model hranica tento typ nemení, ale blokuje bezpečné prideľovanie MAC.

## 7. Identifier

Autoritatívne: `MAC-xxxx`, presný regex `^MAC-[0-9]{4}$`, central `$defs/MAC` v `schemas/common/identifiers.schema.json`. Canonical ref: `https://eos.local/schemas/common/identifiers.schema.json#/$defs/MAC`. EOS-003 riadok 40, RFC-0002 §16 a RFC-0003 G-0046 súhlasia. Odporúčané pole `id`; žiadny lokálny regex ani nový prefix. Syntax je pripravená, význam identity ešte nie.

## 8. Machine Identity Semantics

Navrhované pravidlá čakajúce na MI-0001:
- Jedno MAC označuje jednu kontinuálne evidovanú fyzickú jednotku, nie jeden model, vlastníka, konfiguráciu alebo label.
- Premenovanie, presun a zmena vlastníka samy nemenia MAC.
- Software upgrade, control retrofit, spindle replacement a major overhaul nemenia MAC, **ak je doložená kontinuita tej istej jednotky**. Vyžadujú nové posúdenie dotknutých claims, nie automatické zachovanie capability.
- Nová samostatná fyzická jednotka, úplná náhrada stroja iným kusom alebo novovytvorená jednotka po prestavbe vyžaduje nové MAC; pôvodné MAC sa nerecykluje.
- Rebuild, merge/split zariadení alebo výmena zásadných nosných celkov s neistou kontinuitou sa nesmú automaticky rozhodnúť podľa percenta dielov či sériového čísla. Pred použitím sa odložia na identity review.

Tieto pravidlá nepovažovať za schválené dovtedy, kým nie je MI-0001 explicitne uzavreté. MAC nie je serialNumber a modelová zhoda nepreukazuje identitu.

## 9. Physical Machine vs MachineModel

Odporúčam fyzickú jednotku iba. Dve fiktívne jednotky rovnakého modelu majú dve MAC; model má potenciálne jednu budúcu modelovú definíciu, ktorej prefix sa teraz neurčuje. Zmiešaný physical/model kontrakt alebo discriminator sa neodporúča: reference na MAC by nebola jednoznačná. Budúci MachineModel a modelId sú deferred; review nevytvára modelovú dedičnosť.

## 10. Name Model

Odporúčam required neprázdny `name`, optional neprázdny `description` a optional common `notes`. Name je interný ľudský label, nie unique kľúč. Description môže vysvetliť hranicu jednotky, ale nesmie ukrývať serial/external mapping, config alebo capability. Pri neistom physical referentovi nemožno schváliť záznam len na základe labelu. Povinný description problém MI-0001 nevyrieši.

## 11. Manufacturer / Model

Vybrať B: structured manufacturer/model/modelDesignation polia odložiť. Žiadny Manufacturer objekt a žiadna priama supplierId väzba. SourceReference môže identifikovať vydavateľa dokumentácie, ale to nie je náhrada štruktúrovanej identity výrobcu alebo model relation. Poznámky nesmú slúžiť ako budúci compatibility kľúč. MachineModel nie je nevyhnutný pre minimum fyzickej jednotky po identity rozhodnutí.

## 12. Serial / External Identifiers

SerialNumber je potenciálny dôkaz fyzickej identity, nie globálne jedinečné EOS ID. AssetNumber/machineCode/inventoryNumber/ERP kódy sú scheme-scoped externé identifikátory. Všetky dedicated polia v1 odložiť na ExternalIdentifier návrh vrátane namespace, normalizácie, histórie a prístupových pravidiel. Reálny onboarding musí preukázať jednotku dostupnými zdrojmi; neukladať proprietárne identifikátory do testov ani sa nespoliehať na voľný string.

## 13. Machine vs WorkCenter

WorkCenter môže združovať zariadenia, osoby a fixtures; nie je fyzický stroj. V1 nebude obsahovať members, resource pools ani kapacitný plán pracoviska. Aj keď jeden workcenter dnes obsahuje jediný stroj, identity sa nesmú stotožniť. WorkCenter návrh je samostatná budúca téma.

## 14. Location Boundary

Bez location/site/supplierSite/locationId. Presun pri zachovaní fyzickej jednotky navrhujem bez zmeny MAC. Časovo platné umiestnenie potrebuje samostatný model; adresa ani miesto nie sú permanentná Machine identita.

## 15. Ownership Boundary

Bez ownerId, ownerSupplierId alebo supplierId. Právne vlastníctvo, prevádzkovateľ a servisný vzťah sú odlišné potenciálne časové väzby. Ich zmena neprepisuje MAC na SUP. Žiadny nový Organization alebo Location kontrakt.

## 16. ManufacturingProcess Relationship

Bez processIds a bez reverse machineIds v ManufacturingProcess. RFC umožňuje referencie, ale nevynucuje ich v prvom profile. Tvrdenie o realizovateľnosti TEC je scoped capability, nie dôsledok MAC identity alebo CLS zaradenia. Existencia TEC kontraktu nie je dôvod na convenience array.

## 17. MachineCapability

Konceptuálne schopnosť konkrétneho zariadenia/konfigurácie za podmienok vykonávať činnosť s obmedzeniami. Process/material/geometry/tool/site/qualification context sa nesmie stratiť. Bez capability root polí v1. Presný future ownership neurčený: Accepted Capability môže byť embedded VO; nevynucovať samostatný MachineCapability Aggregate Root len z názvu.

## 18. Specification vs Capability

Špecifikácia je zdrojovo doložené deklarované technické tvrdenie o danej jednotke; capability je tvrdenie o uskutočniteľnosti činnosti/výsledku v kontexte. Menovitý údaj či medza osi nie sú dôkaz dosiahnuteľnej tolerancie pre konkrétny diel. Numeric formát PropertyRecord sám tieto významy nerozpozná; hranica vyžaduje PRP sémantiku a authoring review.

## 19. PropertyRecord

Odporúčam A: optional `properties: PropertyRecord[]`, po uzavretí MI-0001, iba pre source-backed numeric specification claims aplikovateľné na túto jednotku. Opora je explicitná RFC ownership permission, na rozdiel od process v1 nejde o univerzálne settings metódy. Ponechať paralelné/konfliktné claims, bez automatického dedup či výberu najvyššej hodnoty. Žiadne nové polia PropertyRecord, derived capability, runtime state, current command, planned value, maintenance alebo ceny. Textové controller/model/interface údaje do numeric claim nepatria. PRP/CND/UNT validácia neurčuje Machine applicability ani current configuration.

## 20. Classification

Odporúčam optional 0..N `classifications: Classification[]` na základe všeobecnej Classification sémantiky RFC-0001 §4.6 a existujúceho kontraktu. Explicitne potvrdiť pri rozhodnutí profilu; Machine-specific zoznam RFC ho neuvádza, preto to nie je predstieraná explicitná Machine autorita. Owned je assignment, nie CLS entry. Viac tried je povolených, sourceLinks na assignment oddelené od root. MachineType enum odmietnuť; category nie je capability.

## 21. Observation

Existujúci Observation subjectId union už podporuje central MAC podľa RFC-0001 a ADR-0016. Machine nesmie embedovať observations/observationIds. Merané hodnoty sú evidence, nie automatické schválené špecifikácie. Promotion do claim vyžaduje riadené rozhodnutie/governance, nie kopírovanie posledného merania. Žiadny Observation schema update.

## 22. Runtime State

Running/stopped/fault/maintenance/unavailable/idle sú časové prevádzkové stavy, nie common RecordStatus. Bez runtimeStatus, currentState alebo state logs. AvailabilityRecord koncept je Accepted širšia možnosť, nie súčasť tohto úzkeho v1.

## 23. Maintenance

Bez lastMaintenanceDate/nextMaintenanceDate/maintenanceHistory alebo maintenance rootu. Udalosti, plán a servisná evidencia patria budúcemu časovému modelu. Neurčuje sa ešte MaintenanceRecord prefix ani aggregate kategória.

## 24. Calibration

Bez calibrationDate/calibrationStatus/certificate root shortcutov. Kalibrácia má rozsah, platnosť, merací kontext a dokumentový dôkaz. Source-backed špecifikácia nepreukazuje aktuálnu kalibračnú platnosť; budúci CalibrationRecord sa nevytvára.

## 25. Qualification

Bez qualified/qualificationStatus na root. Production approval závisí od process/customer/site/time/specification; Approved EOS record neznamená qualified equipment. Nevytvárať qualification voľným CLS assignmentom alebo textom.

## 26. Axis / Architecture

Root axisCount odmietnuť. Presne definovaný číselný PRP môže neskôr reprezentovať počet podľa jasného counting scope; jednotka musí byť riadená, nie nový unitless shortcut. Scalar nevyjadruje simultaneous/indexed motion, geometriu a konfigurovateľnosť. Tieto vzťahy vyžadujú budúci configuration model, nie enum alebo odhad z počtu osí.

## 27. Work Envelope

Bez xTravel/yTravel/zTravel/maxTurningDiameter/maxTurningLength/workEnvelope root polí. Source-backed jednotlivé numeric specification claims môžu ísť cez PRP s presným významom. Viaceré scalars netvoria automaticky geometriu pracovného priestoru ani garantovaný obrobiteľný diel. Nekonštruovať machine-type-specific schema varianty.

## 28. Spindle / Power / Torque

Menovitá alebo deklarovaná maximálna špecifikácia môže byť numeric PropertyRecord s príslušným PRP/UNT/contextom; current command a skutočné otáčky nie. Bez spindleSpeed/spindlePower/spindleTorque root polí. Menovitá elektrická prípojka, mechanický výkon a krivka výkonu/krútiaceho momentu sa nesmú zlúčiť; curve/configuration model v1 nevzniká.

## 29. Accuracy / Repeatability

Deklarovaná špecifikácia patrí claim s podmienkami a zdrojom, konkrétne meranie do Observation. Kalibrovaný výsledok sa nestáva globálnou current capability. Root positioningAccuracy/repeatability/runout sa odmietajú. MeasurementQuality charakterizuje metrológiu konkrétneho číselného claim/result, nie všeobecnú presnosť stroja.

## 30. Tool Interface

Deferred. ToolInterface string alebo kód nesmie byť compatibility kľúč. Budúci interface catalog a scoped tooling/configuration vzťah potrebujú vlastnú autoritu. Žiadne reálne interface kódy ani tool katalógové položky v tomto review.

## 31. Controller

Deferred. Controller/model/firmware nie sú fyzická identita ani numeric PropertyRecord shortcut. Výmena riadenia pri doloženej kontinuite jednotky navrhovane zachová MAC, ale môže zmeniť claims/capability. Žiadna controller taxonómia alebo root manufacturer string.

## 32. Configuration / Retrofit

Návrh: MAC je stabilná jednotka, recordVersion/revision auditujú zmenu jej knowledge záznamu. Po retrofit treba preskúmať platnosť dotknutých claims a zachovať dohľadateľnosť. Samotné revision pole NEPOSKYTUJE historický configuration snapshot, časovú platnosť alebo výber správnej konfigurácie pre starú operáciu. V1 môže byť obmedzený evidence-backed register claims, nie autorita pre plánovanie historických/realtime konfigurácií. Ambicióznejší scope vyžaduje samostatný návrh.

## 33. Claimed vs Measured vs Planned Values

| Význam | Umiestnenie |
| --- | --- |
| Výrobcom deklarovaná špecifikácia aplikovateľná na konkrétnu jednotku | PropertyRecord s vlastným zdrojom a podmienkami |
| Konkrétne namerané správanie | Observation s časom/subject/context |
| Aktuálny príkaz alebo skutočný prevádzkový stav | Budúca execution/state vrstva; meranie prípadne Observation |
| Plánovaná hodnota pre operáciu | Budúca Operation/parameter vrstva |
| Schválené odvodené capability tvrdenie | Budúci capability/decision model |

Číselné príklady zadania nie sú preberané ako technické fakty alebo odporúčania. Claim a evidence sa nezlučujú podľa rovnakého názvu veličiny.

## 34. CuttingTool Relationship

Bez cuttingToolIds/toolIds/currentTool. Tool compatibility, installed tooling a selection sú rôzne context-dependent vzťahy. Machine nevlastní CuttingTool aggregate; jeho schéma ani nový setup model nevzniká.

## 35. Material / StockMaterial Relationship

Bez materialIds/stockMaterialIds/supportedMaterials. Tvrdenie o opracovateľnosti materiálu je capability/context, nie identita zariadenia. Polotovar a konkrétne vstupy patria operácii; Material a Supplier sa nemenia.

## 36. Job / Operation Boundary

Bez jobIds/operationIds/currentJob. Budúca operácia môže priradiť stroj podľa kontextu a referencie; Machine neobsahuje zákazky ani vykonané operácie. Návrh nevytvára Operation schému.

## 37. Programs / Setup / Fixtures

Bez ncPrograms/gCode/camPrograms/programIds, fixtureIds/setupIds/workholding. Program, setup a upnutie patria budúcim execution/document/resource kontraktom; nie embedded inventory Machine.

## 38. Time Boundary

Bez cycleTime/setupTime alebo univerzálneho času stroja. Plánovaný/skutočný/odvodený čas sa viaže na operáciu a kontext, nie na MAC identitu.

## 39. Cost Boundary

Bez hourlyRate/machineRate/costPerHour. Časová platnosť, účtovná politika a využitie patria costing/application vrstve. Ani PropertyRecord nesmie prebrať tieto obchodné významy len preto, že sú číselné.

## 40. Utilization / OEE

Bez utilization/OEE/availability root polí. Sú to časové analytics alebo availability údaje, nie stabilná špecifikácia a nie record lifecycle. Nevytvára sa nový availability algoritmus.

## 41. Energy Boundary

Deklarovaná menovitá výkonová špecifikácia môže byť PRP claim s jasným významom; spotreba energie je operation/time-dependent evidence alebo odvodený výsledok. Bez root energy/currentConsumption a bez univerzálnej spotreby z menovitého výkonu.

## 42. Documents

DocumentRecord už existuje. Priame documentIds/manuals/certificates a role/version/applicability väzby odložiť. SRC/SourceLink môže podporovať identitu alebo konkrétny claim, nie predstierať dokumentový inventár. Root sourceLinks nesupluje claim-specific provenance.

## 43. Norms

NormReference existuje, no machine conformity/applicability je samostatný scoped význam. Bez normIds/standards alebo voľných normových zoznamov. Citácia normy automaticky neustanovuje zhodu stroja ani záväznosť pre každú operáciu.

## 44. Root Provenance

Root sourceLinks má dokazovať identitu a definíciu fyzickej jednotky po uzavretí MI-0001. Každý specification claim nesie vlastné PropertyRecord.sourceLinks; zaradenie má assignment provenance a meranie Observation provenance. Root Approved so zdrojom nesmie byť interpretované ako overenie všetkých claims. Existujúci parent-lifecycle enforcement pre nested sourceLinks nie je úplne vyriešený; pozri §54 a §61.

## 45. Lifecycle

Navrhujem common RecordStatus bez rozšírenia. Approved = schválený EOS record, nie výrobná qualification; Archived = archivovaný record, nie nutne fyzicky vyradený stroj. Revision, recordVersion a schemaVersion zostávajú tri rozdielne významy. Žiadny root verificationStatus.

## 46. Replacement

Replaces/replacedBy odložiť. Record duplicate cleanup, fyzická náhrada iným kusom a retrofit sú odlišné udalosti. Nový fyzický kus sa nesmie pretypovať pod starým MAC; retrofit podľa navrhovanej kontinuity nevytvára automaticky nový kus. Material replacement model nie je povinný precedent.

## 47. MachineModel Future Risk

Medium po explicitnom physical identity rozhodnutí, High ak sa ponechá zmiešaný význam MAC. Datasheet claim možno neskôr priradiť fyzickej jednotke iba s doloženou applicability na jej variant/konfiguráciu a vlastným zdrojom; bez implicitnej model inheritance. Nesmie sa masovo kopírovať modelové tvrdenie ako unit-specific istota. Budúci MachineModel mapping musí zachovať MAC a históriu; žiadny modelId/prefix sa teraz neurčuje.

## 48. Minimum Useful Machine

Po uzavretí MI-0001 odporúčam minimum Draft: common required metadata, MAC id, neprázdny name a required sourceLinks, ktoré môžu byť v Draft prázdne. Description/classifications/properties/notes optional. Výrobca, model a serial nie sú štrukturálne required; reálny schválený záznam však musí mať dôkaz identity. Minimum umožní inkrementálne autorovanie, nie produkčné plánovanie bez znalostí.

## 49. Candidate Models

| Kandidát | Posúdenie |
| --- | --- |
| A: identity + optional description/notes | Bezpečný iba po identity rozhodnutí; príliš úzky na schválené specification claims |
| B: identity + Classification | Vhodný kategorizovaný register, ale odkladá legitímne RFC PropertyRecord bez nutnosti |
| C: identity + Classification + PropertyRecord | Odporúčaný úzky profil: fyzická jednotka a sourced numeric specifications; žiadne capability/settings |
| D: nový MachineModel/configuration/capability framework | Pre minimum nie je potrebný; nevytvárať |

Vyberá sa presne C ako návrh pre následné rozhodnutie, nie implementovateľná schválená alternatíva k nevyriešenému MI-0001.

## 50. Recommended v1 Model

Po uzavretí identity a potvrdení scope: required id, schemaVersion, recordVersion, revision, status, createdAt, createdBy, updatedAt, updatedBy, sourceLinks, changeSummary, name. Optional description, classifications, properties, notes. Closed shape; central MAC/common metadata refs a existing Classification/PropertyRecord refs. Arrays 0..N, bez predčasnej uniqueness alebo automatického claim výberu. Žiadne ďalšie root polia. Status tohto návrhu: odporúčaný, **nesmie sa teraz implementovať**.

## 51. Field Inventory

NOW znamená iba **odporúčaný profil po uzavretí MI-0001**, nie povolenie implementovať teraz.

| Pole | Stav | Dôvod |
| --- | --- | --- |
| id | REQUIRED NOW | Po MI-0001 central MAC; nie serial. |
| common metadata | REQUIRED NOW | Verzie, revízia, lifecycle a audit cez common refs. |
| name | REQUIRED NOW | Neprázdny label, nie unique identity. |
| description | OPTIONAL NOW | Neprázdne vysvetlenie jednotky, nie skrytý model. |
| classifications | OPTIONAL NOW | 0..N assignments; explicitne potvrdiť reuse. |
| properties | OPTIONAL NOW | 0..N unit-specific numeric specification claims. |
| sourceLinks | REQUIRED NOW | Root identity provenance. |
| notes | OPTIONAL NOW | Common notes, nie odložené štruktúry. |
| manufacturer | DEFER | Scheme/model/organization identity nie je schválená. |
| model | DEFER | Scheme/model/organization identity nie je schválená. |
| serialNumber | DEFER | Scheme/model/organization identity nie je schválená. |
| assetNumber | DEFER | Scheme/model/organization identity nie je schválená. |
| machineType | REJECT | Použiť optional Classification, nie single enum. |
| axisCount | REJECT | Nie root field; iba presne definovaný numeric specification PRP, ak sémantika postačuje, inak future configuration. |
| workEnvelope | REJECT | Nie root field; iba presne definovaný numeric specification PRP, ak sémantika postačuje, inak future configuration. |
| xTravel | REJECT | Nie root field; iba presne definovaný numeric specification PRP, ak sémantika postačuje, inak future configuration. |
| yTravel | REJECT | Nie root field; iba presne definovaný numeric specification PRP, ak sémantika postačuje, inak future configuration. |
| zTravel | REJECT | Nie root field; iba presne definovaný numeric specification PRP, ak sémantika postačuje, inak future configuration. |
| maxTurningDiameter | REJECT | Nie root field; iba presne definovaný numeric specification PRP, ak sémantika postačuje, inak future configuration. |
| maxTurningLength | REJECT | Nie root field; iba presne definovaný numeric specification PRP, ak sémantika postačuje, inak future configuration. |
| spindleSpeed | REJECT | Nie root field; iba presne definovaný numeric specification PRP, ak sémantika postačuje, inak future configuration. |
| spindlePower | REJECT | Nie root field; iba presne definovaný numeric specification PRP, ak sémantika postačuje, inak future configuration. |
| spindleTorque | REJECT | Nie root field; iba presne definovaný numeric specification PRP, ak sémantika postačuje, inak future configuration. |
| positioningAccuracy | REJECT | Nie root field; iba presne definovaný numeric specification PRP, ak sémantika postačuje, inak future configuration. |
| repeatability | REJECT | Nie root field; iba presne definovaný numeric specification PRP, ak sémantika postačuje, inak future configuration. |
| toolInterface | DEFER | Riadená interface/compatibility sémantika. |
| controller | DEFER | Nie identity; model/configuration taxonomy. |
| processIds | REJECT | Root shortcut pre odložený scoped/temporal vzťah. |
| materialIds | REJECT | Root shortcut pre odložený scoped/temporal vzťah. |
| supplierId | REJECT | Root shortcut pre odložený scoped/temporal vzťah. |
| locationId | REJECT | Root shortcut pre odložený scoped/temporal vzťah. |
| ownerId | REJECT | Root shortcut pre odložený scoped/temporal vzťah. |
| capabilities | DEFER | Samostatný scoped návrh; nie v1. |
| runtimeStatus | REJECT | Temporal state nie RecordStatus. |
| maintenance | DEFER | Temporal udalosti/history. |
| calibration | DEFER | Scope/time/evidence model. |
| qualificationStatus | REJECT | Nie globálna vlastnosť rootu. |
| cycleTime | REJECT | Operation/costing/temporal analytics, nie identity/specification. |
| setupTime | REJECT | Operation/costing/temporal analytics, nie identity/specification. |
| hourlyRate | REJECT | Operation/costing/temporal analytics, nie identity/specification. |
| OEE | REJECT | Operation/costing/temporal analytics, nie identity/specification. |
| programIds | DEFER | Chýba role/context/applicability model; mimo v1. |
| fixtureIds | DEFER | Chýba role/context/applicability model; mimo v1. |
| documentIds | DEFER | Chýba role/context/applicability model; mimo v1. |
| normIds | DEFER | Chýba role/context/applicability model; mimo v1. |
| replaces | DEFER | Record supersession nie fyzická náhrada. |
| replacedBy | DEFER | Nekopírovať Material semantics. |

CONDITIONALLY REQUIRED: neprázdny root sourceLinks obsah pre Review/Approved. Claim-specific provenance a datasheet applicability vyžadujú explicitný authoring/workflow postup; nie automatické dedenie root zdrojov.

## 52. Aggregate Ownership Matrix

| Objekt | Kategória v návrhu | Hranica |
| --- | --- | --- |
| Classification | OWNED EMBEDDED VALUE | Navrhované assignment, nie CLS entry. |
| PropertyRecord | OWNED EMBEDDED VALUE | Navrhovaný specification claim, nie stream meraní. |
| Observation | SEPARATE AGGREGATE | MAC subject referencia zvonka; nikdy embedded. |
| Condition | OWNED EMBEDDED VALUE | Iba nested v legitimate PropertyRecord; root array deferred. |
| MeasurementQuality | OWNED EMBEDDED VALUE | Iba v legitimate numeric claim/result; root score rejected. |
| Material | SEPARATE AGGREGATE | Žiadny priamy v1 odkaz. |
| StockMaterial | DEFERRED | Budúci entity/operation input; žiadny embedding. |
| ManufacturingProcess | SEPARATE AGGREGATE | TEC referencia až so schválenou relation/capability sémantikou. |
| CuttingTool | DEFERRED | Budúca kategória podľa vlastného návrhu; žiadny embedding. |
| Supplier | SEPARATE AGGREGATE | Nie vlastník vložený do Machine. |
| Job | SEPARATE AGGREGATE | Accepted root, budúci kontrakt; nie child Machine. |
| Operation | DEFERRED | JobOperation je job-owned, nie Machine child. |
| MachineModel | DEFERRED | Presná kategória/ownership sa týmto review neurčuje. |
| MachineCapability | DEFERRED | Presná kategória/ownership sa týmto review neurčuje. |
| MachineState | DEFERRED | Presná kategória/ownership sa týmto review neurčuje. |
| MaintenanceRecord | DEFERRED | Presná kategória/ownership sa týmto review neurčuje. |
| CalibrationRecord | DEFERRED | Presná kategória/ownership sa týmto review neurčuje. |
| Location | DEFERRED | Presná kategória/ownership sa týmto review neurčuje. |
| DocumentRecord | SEPARATE AGGREGATE | Priame Machine applicability field deferred. |
| NormReference | REFERENCED / DEFERRED FIELD | Reference objekt existuje, Machine väzba nie. |
| SourceReference | REFERENCED | Existujúci SourceLink; žiadny embedded SRC root. |

Aggregate Root nikdy nevlastní iný Aggregate Root. Neimplementované názvy nepovyšovať na roots iba podľa názvu.

## 53. Provenance Matrix

| Vlastník provenance | Čo podporuje | Čo automaticky nepodporuje |
| --- | --- | --- |
| Machine root | Identity/definition konkrétnej jednotky | Všetky špecifikácie alebo qualification. |
| PropertyRecord | Konkrétny sourced specification claim | Current command, plán alebo automatická pravda merania. |
| Classification | Priradenie kategórie | Schopnosť vykonať konkrétnu operáciu. |
| Observation | Konkrétne merané evidence | Automatická promotion na claim. |
| Budúca MachineCapability | Scoped capability claim | Univerzálna vhodnosť stroja. |
| Budúci CalibrationRecord | Kalibračný dôkaz/scope/čas | Bezčasová root qualification. |
| Budúci MaintenanceRecord | Servisná udalosť a jej dôkazy | Current state bez časového kontextu. |
| Budúca Operation | Plánované/vykonané použitie | Definícia fyzickej identity. |

## 54. Validation Responsibility

| Vrstva | Navrhovaná zodpovednosť a limit |
| --- | --- |
| schema_validation | Closed Machine shape, MAC/common refs, required fields a nested VO syntax |
| application_validation | Existujúci root source/lifecycle helper; numeric ValueRange/MQ invariants cez kompozíciu, nie nové machine rules |
| reference_integrity | PRP/CND/UNT/CLS existencia a typ v explicitnom katalógovom kontexte; nie existencia MAC/SRC alebo iných entít |
| catalog_validation | Povolený value type/unit/condition a lifecycle; CLS lifecycle; nie machine applicability/capability |
| workflow/governance | Physical identity, datasheet applicability, specification vs runtime význam, vlastné dôkazy claims a ich promotion |
| persistence/history | Unikátnosť MAC, verzované snapshots, concurrency a historické configuration väzby neskôr |

PropertyRecord.sourceLinks je required array, ale môže byť štrukturálne prázdne. BACKLOG už vedie parent-lifecycle source pravidlo ako otvorené. V1 review nesmie tvrdiť, že Approved root automaticky vynucuje zdroj každého claim: pred implementáciou explicitne potvrdiť existujúcu hranicu manual review vs runtime alebo samostatne schváliť doplnenie pravidla. Žiadna nová implicitná validácia sa týmto CDR nezavádza.

## 55. Entity Resolver Requirement

Nie pre navrhovaný profil. Žiadne priame process/material/tool/supplier/location/owner refs ani replacement graf. Existujúci CatalogRegistry postačuje na PRP/CND/UNT/CLS; Condition reference syntax neznamená entity existence. SourceReference existencia ostáva známym limitom. Generic entity resolver sa nevytvára.

## 56. MachineCapability Dependency

Machine môže existovať pred MachineCapability **až po MI-0001** a pri úzkom profile špecifikácií. Nepredstiera výrobnú vhodnosť alebo dostupnosť. Samotný chýbajúci capability kontrakt nie je blokér identity registra; aktuálny NOT READY vyplýva z neuzavretej identity, nie z požiadavky vybudovať celú MES vrstvu.

## 57. Real Data Boundary

Nevznikajú reálne Machine záznamy, modelové specs, serial numbers, asset codes alebo konfigurácie. Mená produktov, interfaces a numerické údaje zo zadania sú len motivačné príklady a nepreberajú sa ako overené znalosti. Žiadny strojový katalóg alebo fixtures.

## 58. Future Real-data Requirements

Minimum: explicitná physical identity politika, source-backed dôkaz individuálnej jednotky, label, audit a kontrola duplicít. Manufacturer/model/serial dokumentácia môže byť dôkaz, ale nie automatický externý kľúč. Pri použitých Classification/PropertyRecord treba platné CLS/PRP/CND/UNT významy, vlastné claim zdroje a applicability na jednotku. Plné plánovanie navyše potrebuje current configuration, capability/qualification/calibration, operation a historické väzby; tieto nie sú súčasťou minimum Draft.

## 59. Risks

| Priorita | Riziko | Opatrenie |
| --- | --- | --- |
| High / blocking MI-0001 | Machine zamieňaný s MachineModel | Explicitne schváliť physical unit boundary pred MAC záznamami. |
| High | Machine zamieňaný s WorkCenter alebo capability | Úzky profil a samostatné future vzťahy. |
| High | Runtime hodnoty ukladané cez PropertyRecord | Specification vs evidence vs planned/command pravidlá a review. |
| High | ProcessIds/materialIds implikujú univerzálnu kompatibilitu | Bez convenience arrays. |
| High | Modelový datasheet vydávaný za istú unit capability | Unit applicability a source-backed claim bez inheritance. |
| Medium | Tool-interface string sa stane compatibility key | Odložiť riadený interface model. |
| Medium | Výrobca ako voľná identita; serial ako global ID | ExternalIdentifier/model návrh oddelene. |
| Medium | Machine-type-specific root polia a obrovské variantné schema | Reuse PRP; geometriu/configuration nedopisovať ad hoc. |
| High | Merané údaje sa zlúčia s deklarovanými špecifikáciami | Samostatná Observation a riadená promotion. |
| High | Record lifecycle preberie prevádzkový stav | Bez runtime/availability enumu. |
| Medium | Maintenance/calibration ako statické dátumy | Deferred temporal records. |
| Medium | Ceny a OEE v engineering identity | Costing/analytics vrstvy mimo v1. |
| High | Lokalita/vlastník zapečený do MAC identity | Navrhovaná kontinuita; temporal relationships deferred. |
| High | Revision predstiera configuration history | Explicitný limit; reálne plánovanie až po vhodnom modeli. |
| Medium | Approved root maskuje prázdne claim zdroje | Vyjasniť existing workflow/runtime limit pred implementáciou; neprehlasovať úplnú validáciu. |
| High | Predčasná reálna populácia | Žiadne reálne dáta do identity rozhodnutia a onboarding review. |

Iba MI-0001 je tu konkrétny blokér identity rozhodnutia. Ostatné riziká určujú hranice navrhovaného profilu a preconditions; nepredstierajú preukázané chyby existujúceho runtime.

## 60. Deferred Concepts

MachineModel/model inheritance, Manufacturer/Organization mapping, serial/external identifiers, WorkCenter, Location/ownership, configuration snapshots/history, MachineCapability a process/material/tool compatibility, runtime state/AvailabilityRecord, maintenance/calibration/qualification, setup/programs/fixtures, Operation/Job assignment, time/cost/OEE/resources, document/norm applicability, replacement a real-data onboarding. Root Condition/MQ, tool-interface/controller taxonómie a machine-type-specific root polia sa nezavádzajú. Odloženie NIE JE povolenie uložiť tieto významy do notes, PropertyRecord alebo Classification.

## 61. Implementation Preconditions

### MI-0001 - Machine identity granularity (High, OPEN, blocking)

Dôkaz: RFC-0002 §4.4 necháva konkrétnu jednotku ALEBO riadený typ na budúce rozhodnutie; RFC-0003 G-0046 ho tiež necháva otvorené. Syntax MAC ani aggregate status to nerozhodujú. Dopad: tie isté MAC referencie by mohli znamenať fyzické kusy aj modely; Observation, capability, configuration, ownership a future Operation by neboli interpretovateľné jednoznačne.

Odporúčané uzavretie: explicitne vybrať individuálnu fyzickú výrobnú/kontrolnú jednotku; oddeliť model a WorkCenter; schváliť pravidlá continuity/retrofit/nového kusu a výnimku pre nejasný rebuild podľa §8. Zaznamenať rozhodnutie a znovu posúdiť tento CDR. Ak ide iba o využitie otvoreného doménového rozhodnutia, nemusí byť nutná zmena Accepted RFC; ak sa mení prijatý význam, dodržať RFC/ADR lifecycle a freeze. Tento review nevytvára ADR ani nevracia RFC do Review.

Po uzavretí MI-0001 potvrdiť:
1. Profil C a optional description; žiadny mixed physical/model discriminator.
2. Optional Classification reuse ako explicitný Machine profil; bez machineType enumu.
3. Optional numeric PropertyRecord výhradne ako unit-specific specification claim, nie runtime/capability/planned setting.
4. Root vs claim provenance, konfigurácia/applicability a existujúci nested source enforcement limit z §54; žiadny falošný automatický dôkaz.
5. Bez direct process/material/tool/supplier/location/owner refs; bez generic resolvera.
6. Bez runtime state, maintenance/calibration/qualification, času/ceny a replacement.
7. Revision je audit záznamu, nie implementovaný configuration history engine.
8. Fiktívne implementačné fixtures a plné root/nested/catalog regresie po samostatnom schválení implementácie.

MachineCapability ani kompletný MachineModel nie sú podmienkou uzavretia MI-0001. Do jeho uzavretia žiadna Machine schema.

## 62. Readiness Verdict

Implementácia teraz nesmie začať. Odporúčanie fyzickej jednotky a profilu C je jasné, ale nie je autoritatívnym uzavretím výslovne odloženého rozhodnutia v Accepted architektúre. Fyzická jednotka a model vedú k nekompatibilnému významu MAC, hoci môžu mať rovnaký JSON tvar. Preto nejde o bezpečné READY WITH CONDITIONS pre okamžitú implementáciu. Nasleduje samostatné Machine identity boundary rozhodnutie a aktualizácia readiness, nie schéma alebo ďalšia entita.

## 63. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-10-20 | 0.1 | 0 | Codex | Machine pre-design: autoritatívny MAC/aggregate rámec, otvorená identity granularita MI-0001, návrh fyzickej jednotky a profilu C, specification/evidence/capability hranice, matrices a deferred scope. |

NOT READY
