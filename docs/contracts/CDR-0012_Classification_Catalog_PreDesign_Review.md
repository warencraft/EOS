# CDR-0012 Classification Catalog Pre-design Review

Project: EOS – Engineering Operating System  
Contract Review ID: CDR-0012  
Contract: Classification Catalog  
Review type: Pre-design  
Phase: 0.2B.2.4-prep  
Version: 0.1  
Revision: 0  
Status: Review  
Document basis: Accepted EOS architecture + implemented Unit, Condition Type and Property catalogs

## 1. Purpose

Určiť najmenší bezpečný kontrakt `Classification Catalog Entry` verzie 1, ktorý dá autoritatívny význam existujúcim odkazom `CLS-xxxxxx` vo vnorenom Value Objecte `Classification`. Review vyberá katalógovú rolu, identitu, minimálne polia, provenance hranicu a odložené systémové a hierarchické semantics bez vytvorenia JSON schémy, reálnych dát alebo validátora.

## 2. Scope

Review pokrýva:

- rolu Classification Catalogu v existujúcej catalog hierarchy;
- objektový typ a lifecycle jednej položky;
- význam CLS identity;
- názov, definíciu, provenance a replacement väzby;
- hranice klasifikačného systému, externého kódu, hierarchie, aliasov a ekvivalencie;
- vzťah k embedded Classification, Property Catalogu a budúcim knowledge entities;
- zodpovednosť štrukturálnej, aplikačnej, katalógovej a referenčnej validácie.

Mimo rozsahu sú Classification Catalog schéma, Classification System Catalog, hierarchy engine, equivalence model, reálne klasifikácie, entity-specific applicability, databáza, API a zmeny Accepted architektúry.

## 3. Reviewed Artifacts

Preskúmané boli:

- `AGENTS.md`;
- `EOS-003_Identification_and_Versioning.md`;
- `EOS-006_Data_Validation_Standard.md`;
- `EOS-007_Validation_Capability_Matrix.md`;
- Accepted `RFC-0001_Engineering_Property_Model.md`;
- Accepted `RFC-0002_Engineering_Object_Taxonomy.md`;
- Accepted `RFC-0003_EOS_Engineering_Glossary.md`;
- Accepted `ADR-0015_Establish_engineering_knowledge_layer.md`;
- `CDR-0005_Classification_PreDesign_Review.md`;
- `CDR-0008_Knowledge_Core_Integration_Review.md`;
- `CDR-0009_Unit_Catalog_PreDesign_Review.md`;
- `CDR-0010_Condition_Type_Catalog_PreDesign_Review.md`;
- `CDR-0011_Property_Catalog_PreDesign_Review.md`;
- implementovaná schéma `Classification`;
- implementované Unit, Condition Type a Property Catalog Entry schémy;
- spoločné schémy identifikátorov, metadát a `SourceLink`;
- schema index, `CHANGELOG.md`, `ROADMAP.md` a `BACKLOG.md`.

Pre-flight bol vykonaný na vetve `feature/phase-0.2b-knowledge-contracts`, na čistom HEAD `7c11db5`. Existuje 19 schém, z toho 7 Knowledge Core a 3 katalógové. Classification Catalog schéma, reálne CLS položky ani catalog-aware/reference-integrity integrácia neexistujú. Kompletných 168 testov prešlo.

## 4. Authoritative Findings

| Oblasť | Klasifikácia | Zistenie a architektonická opora |
| --- | --- | --- |
| Katalógová rola | AUTHORITATIVE | Classification Catalog je Reference Catalog. RFC-0002 §9.0 ho uvádza medzi typickými Reference Catalogs; RFC-0003 G-0077 používa rovnaký príklad. |
| Catalog Entry | AUTHORITATIVE | Položka má stabilnú identitu, vlastný lifecycle, samostatnú existenciu, citovateľnosť, verziu, revíziu a audit podľa RFC-0002 §3.9. |
| Aggregate boundary | IMPLIED | Samostatná položka s vlastným ID, lifecycle a auditom je Aggregate Root; iné aggregates ju iba referencujú stabilným ID. |
| CLS identita | AUTHORITATIVE | Aktívny formát `CLS-xxxxxx` identifikuje Classification Catalog Entry podľa EOS-003 a CDR-0005. |
| Embedded Classification | AUTHORITATIVE | Classification je rodičom vlastnený Value Object bez vlastného ID a lifecycle; `classificationId` je referencia na CLS význam. |
| Klasifikačný systém | AUTHORITATIVE BOUNDARY | RFC-0001 §4.6 vyžaduje, aby sa externý kód neinterpretoval bez systému a relevantnej verzie alebo platnosti. Presný systémový kontrakt je DEFERRED. |
| Hierarchia | OPEN | Accepted dokumenty očakávajú katalógové riešenie, ale neurčujú tree, DAG, parent cardinality, path ani cycle policy. |
| Definition provenance | AUTHORITATIVE | Samostatná katalógová položka má vlastné zdroje svojho významu podľa Catalog Entry a source traceability pravidiel. |
| Assignment provenance | AUTHORITATIVE | Embedded Classification môže niesť `sourceLinks` dokazujúce konkrétne zaradenie rodiča; externý pôvod vyžaduje provenance podľa RFC-0001 §4.6. |
| Lifecycle | AUTHORITATIVE | Catalog Entry používa vlastný record lifecycle a versioning; deprecated položka sa nemaže. |
| Root verification | AUTHORITATIVE | Catalog lifecycle nie je verification status konkrétneho assignmentu alebo SourceLinku. |
| Aliasy | DEFERRED | RFC-0002 ich pripúšťa iba viazané na konkrétny klasifikačný systém; system model ešte neexistuje. |
| Ekvivalencia | DEFERRED | Nie je prijatá identita, cardinality ani provenance model pre mapovanie podobných kategórií. |
| Target compatibility | DEFERRED | Nie je určené, ktoré CLS sú prípustné pre konkrétne entity alebo properties. |

Accepted RFC a ADR si neprotirečia. Otvorené body obmedzujú rozsah v1, ale neblokujú jednoduchý system-neutral entry contract.

## 5. Catalog Role

Classification Catalog je **Reference Catalog**, nie Knowledge Catalog. Autoritatívny základ:

- RFC-0002 §9.0: Classification Catalog je typický príklad Reference Catalogu pre externý, všeobecný alebo technicky referenčný význam.
- RFC-0003 G-0077: Classification Catalog je povolený príklad Reference Catalogu.
- RFC-0003 G-0078: Knowledge Catalog sa používa pre interné EOS rozhodovacie významy, napríklad Property Catalog a Condition Type Catalog.

Jedna Classification Catalog Entry je:

- samostatný `Catalog Entry` a `Entity`;
- prakticky Aggregate Root so stabilnou CLS identitou;
- nezávisle lifecycle-managed, versioned, revised a auditovaná;
- samostatne source-backed a referencovateľná z Classification;
- ponechaná v histórii po deprecácii.

Nie je Value Object ani embedded assignment. Členstvo v Reference Catalogu z nej automaticky nerobí objekt typu `Reference Object`; jej primárna taxonomická kategória je `Catalog Entry`.

## 6. CLS Identifier Semantics

`CLS-xxxxxx` identifikuje presne jednu Classification Catalog Entry a jej stabilný riadený klasifikačný význam. Koreň položky má používať pole `id`; embedded Classification používa referenčné pole `classificationId`.

CLS neidentifikuje:

- embedded Classification inštanciu;
- rodičovskú entitu alebo samotné zaradenie rodiča;
- klasifikačný systém ako celok;
- hierarchy path alebo úroveň;
- externý kód, label, názov alebo alias.

Rovnaký názov alebo externý kód preto nikdy nesmie nahradiť CLS identitu.

## 7. Relationship to Classification Value Object

Embedded Classification zaznamenáva jedno konkrétne zaradenie rodiča odkazom `classificationId`. Je to rodičom vlastnený Value Object bez vlastného ID, verzie, revízie, lifecycle alebo root verification statusu.

Classification Catalog Entry definuje význam cieľového CLS. Vlastní samostatnú identitu, lifecycle, audit a zdroje definície. Rodič nevlastní ani nereviduje katalógovú položku.

Tieto objekty majú odlišné provenance:

- `Classification Catalog Entry.sourceLinks` podporujú definíciu a pôvod klasifikačného významu;
- `Classification.sourceLinks` podporujú tvrdenie, že konkrétny rodič je zaradený do danej CLS kategórie.

Zdroj definície kategórie automaticky nedokazuje správnosť konkrétneho zaradenia. Zdroj assignmentu zase nesmie ticho meniť katalógovú definíciu.

## 8. Candidate Field Inventory

| Pole alebo skupina | Rozhodnutie | Dôvod |
| --- | --- | --- |
| `id` | REQUIRED NOW | Stabilné centrálne `CLS-xxxxxx`. |
| common metadata | REQUIRED NOW | Rovnaký metadata pattern ako tri existujúce katalógy. |
| `name` | REQUIRED NOW | Kanonický neprázdny ľudsky čitateľný názov; nie identita. |
| `description` | REQUIRED NOW | Autoritatívna system-neutral definícia významu; name sám nestačí. |
| `sourceLinks` | REQUIRED NOW | Provenance definície; súčasť common metadata. |
| `status` | REQUIRED NOW | Catalog record lifecycle, nie assignment verification. |
| `notes` | OPTIONAL NOW | Neautoritatívny doplnok; nesmie niesť systémový alebo hierarchický model. |
| `replaces` | OPTIONAL NOW | Priama CLS referencia podľa spoločného katalógového vzoru. |
| `replacedBy` | OPTIONAL NOW | Priama CLS referencia podľa spoločného katalógového vzoru. |
| `code` | DEFER | Bez system identity by bol nejednoznačný. |
| `externalCode` | DEFER | Musí byť viazaný na riadený system/version kontext. |
| `symbol` | REJECT IN V1 | Nie je všeobecným invariantom klasifikačnej položky a môže byť externým kódom alebo labelom. |
| `classificationSystem` | REJECT IN V1 | Voľný text by vytvoril nekontrolovanú identitu systému. |
| `classificationSystemId` | DEFER | Neexistuje riadený identifikátor ani Classification System Catalog kontrakt. |
| `parentId` | DEFER | Predpokladá single-parent tree a nevyriešený system boundary. |
| `parentIds` | DEFER | Predpokladá DAG bez prijatej edge semantics. |
| `hierarchyPath` | REJECT IN V1 | Denormalizuje odvodenú cestu a viaže záznam na konkrétnu štruktúru. |
| `level` | REJECT IN V1 | Je odvodené a nejednoznačné pri DAG alebo viacerých systémoch. |
| `aliases` | DEFER | Chýba system, language, alias type a collision policy. |
| root `verificationStatus` | REJECT | Nesmie sa miešať record lifecycle s assignment alebo SourceLink verification. |
| `allowedTargetTypes` | DEFER | Predčasne viaže referenčný katalóg na budúce entity a ich typový register. |

## 9. Name Model

`name` je povinný neprázdny kanonický ľudsky čitateľný názov položky. Nie je identita, externý kód ani globálne unikátny kľúč.

JSON Schema nemá vynucovať globálnu unikátnosť názvu. V1 ju nevynucuje ani katalógovo, pretože rovnaký label môže mať rozdielny význam v rôznych systémoch alebo kontextoch. Budúca collision policy môže kontrolovať názvy v rámci explicitného systému, jazyka alebo namespace, nie globálne bez kontextu.

## 10. Description Model

`description` je vo v1 povinný neprázdny text definujúci system-neutral zamýšľaný význam CLS položky. Name samotný nestačí na bezpečné rozlíšenie podobných kategórií.

Description nesmie nahrádzať:

- budúcu system identity a external code väzbu;
- hierarchické edges;
- lifecycle alebo source provenance;
- entity applicability;
- equivalence mapovanie.

Ak položka neskôr reprezentuje presný externý systémový kód, autoritatívna interoperabilita musí byť doplnená štruktúrovaným system/code modelom, nie iba prose opisom.

## 11. Classification System Decision

V1 nebude obsahovať klasifikačný systém.

Posúdenie kandidátov:

- **A. Bez system modelu:** bezpečné pre úzky system-neutral CLS význam, ak sa výslovne zakáže interpretovať ho ako interoperabilný externý kód.
- **B. Voľný `classificationSystem`:** odmietnuté; spelling, verzia a názov by sa stali nekontrolovanou identitou.
- **C. `classificationSystemId`:** architektonicky vhodnejší dlhodobý smer, ale dnes nemá prijatú ID rodinu ani cieľový kontrakt.
- **D. Classification System Catalog:** potenciálne dlhodobé riešenie; v tomto review by išlo o nový objekt a predčasnú architektúru.
- **E. Iba SourceLinks:** vhodné pre provenance definície, ale nie ako machine-readable identita systému.

V1 preto podporuje autoritatívny CLS význam bez tvrdenia o riadenom externom system/code bindingu. Externá interoperabilita zostáva explicitne odložená.

## 12. Code / External Code Decision

V1 neobsahuje `code`, `externalCode` ani `symbol`.

Externý kód je významovo neúplný bez klasifikačného systému, relevantnej verzie alebo časovej platnosti. Uloženie samotného kódu by porušilo RFC-0001 §4.6 a umožnilo kolízie medzi systémami.

EOS identita zostáva `CLS-xxxxxx`. Budúci model má externý kód viazať minimálne na riadenú system identity a podľa potreby na system version alebo validity interval. `id` sa na externý kód nesmie preťažiť.

## 13. Hierarchy Decision

Odporúčanie pre v1 je **žiadna hierarchia**.

Accepted architektúra neurčuje:

- či je hierarchia strom alebo DAG;
- či položka môže mať viac rodičov;
- či sú edges iba širší/užší pojem alebo iný vzťah;
- či hierarchia smie prechádzať medzi systémami;
- ako sa verzuje edge a jeho provenance;
- ako sa riešia cykly, root nodes a historická platnosť.

Jednoduchý `parentId` by nevratne predpokladal single-parent tree. `parentIds` by zase zaviedol DAG bez významu edge. `hierarchyPath` a `level` sú odvodené reprezentácie, ktoré sa pri zmene grafu rozchádzajú. Hierarchia sa preto odkladá do samostatného system-aware rozhodnutia.

## 14. Parent Reference Decision

`parentId` ani `parentIds` nepatria do v1.

Ak sa hierarchia neskôr prijme, každý parent target musí byť CLS referencia a application/reference-integrity vrstva musí kontrolovať aspoň existenciu, zákaz self-reference, cykly, system compatibility a lifecycle použiteľnosť. JSON Schema môže kontrolovať iba formát a lokálnu cardinality, nie celý graf.

Kým nie je rozhodnuté tree versus DAG a cross-system policy, nemožno bezpečne určiť optional root semantics ani počet rodičov.

## 15. Alias Model

Aliasy sa vo v1 odkladajú. Môžu reprezentovať odlišné veci:

- alternatívny alebo historický názov;
- lokalizovaný label;
- externý label alebo code;
- migračný lookup token.

Bez alias type, language, system identity, normalizácie a collision policy by aliases vytvorili druhú neautoritatívnu identitu. RFC-0002 §9.4 ich pripúšťa iba viazané na konkrétny klasifikačný systém, ktorý v1 nemodeluje.

## 16. Source Traceability

`sourceLinks` je povinné štrukturálne pole prevzaté zo spoločných metadát a používa existujúci SourceLink kontrakt.

- Draft môže mať prázdne `sourceLinks`.
- Review a Approved Classification Catalog Entry musia mať provenance definície podľa spoločného lifecycle/source pravidla.
- Externe definovaný význam musí mať externú provenance; v1 však nemá machine-readable origin field, preto túto jemnejšiu podmienku ešte nevie odvodiť.
- Interný riadený význam musí byť dohľadateľný k schválenému internému zdroju alebo rozhodnutiu podľa existujúcich provenance pravidiel.
- Entry sourceLinks nesmú nahradiť assignment sourceLinks vo vnorenom Classification.

Nevzniká lokálna kópia SourceLink ani nový source model.

## 17. Lifecycle

Classification Catalog Entry používa rovnaký record lifecycle ako Unit, Condition Type a Property Catalog Entry:

- `Draft`;
- `Review`;
- `Approved`;
- `Deprecated`;
- `Archived`.

Položka má vlastné `schemaVersion`, `recordVersion`, `revision`, auditné timestamps a actor fields a `changeSummary`. Deprecated položka sa nemaže; replacement väzba môže odkázať na nástupcu.

Root nemá `verificationStatus`. Catalog lifecycle opisuje zrelosť definície. Verifikácia SourceLinku alebo dôkazu konkrétneho assignmentu zostáva samostatná.

## 18. Metadata Model

V1 má znovu použiť presne rovnaký common metadata pattern ako tri existujúce katalógy. Nevznikne nový catalog metadata wrapper ani Classification-specific audit model.

Povinné common fields sú:

- `id`;
- `schemaVersion`;
- `recordVersion`;
- `revision`;
- `status`;
- `createdAt`, `createdBy`;
- `updatedAt`, `updatedBy`;
- `sourceLinks`;
- `changeSummary`.

Classification-specific `id` musí odkazovať na centrálny CLS formát. Ostatné metadata polia majú používať property-level `$ref` na existujúcu common metadata schému podľa zavedeného katalógového vzoru.

## 19. Replacement Links

V1 má voliteľne podporiť `replaces` a `replacedBy` pre konzistenciu s existujúcimi katalógmi a pravidlom, že deprecated položky sa zachovávajú.

- obidve polia sú priame CLS referencie;
- nevnárajú Classification Catalog Entry;
- nie sú hierarchia ani equivalence;
- existencia cieľa, self-reference, obojsmerná konzistencia a cykly sú reference-integrity/application pravidlá;
- neimplementuje sa všeobecný Relationship objekt.

## 20. Internal vs External Classifications

V1 nemá samostatné pole pre interný alebo externý pôvod. Boolean `isExternal` sa odmieta, pretože nezachytí systém, vydanie, kombinovaný pôvod ani mapovanie.

SourceLinks poskytujú provenance definície, ale nie machine-readable system identity. Preto:

- v1 môže viesť system-neutral riadené CLS významy;
- externý zdroj môže byť citovaný a interpretovaný;
- v1 nesmie tvrdiť interoperabilné external-code binding;
- automatická politika založená na internom/externom pôvode zostáva odložená do system-aware modelu.

Classification Catalog zostáva Reference Catalog bez ohľadu na to, či konkrétny význam vznikol z externého zdroja alebo interného referenčného usporiadania.

## 21. Assignment vs Definition Provenance

Definition provenance a assignment provenance sú dve samostatné tvrdenia:

| Provenance | Vlastník | Podporované tvrdenie |
| --- | --- | --- |
| Definition | Classification Catalog Entry | Čo CLS znamená a z čoho bol jeho význam odvodený. |
| Assignment | Embedded Classification | Prečo konkrétny rodič patrí do danej CLS kategórie. |

Catalog source sa nesmie automaticky kopírovať do assignmentu ani vydávať za jeho dôkaz. Assignment source nesmie meniť CLS definíciu. Budúca catalog-aware validácia môže podľa pôvodu entry vyžadovať assignment provenance, ale v1 bez origin/system modelu túto podmienku neautomatizuje.

## 22. Multiple Classification Systems

Dve CLS položky môžu reprezentovať podobné alebo rovnako pomenované pojmy z rozdielnych klasifikačných systémov. Ich identity zostávajú odlišné.

V1 nemodeluje systémy ani external codes, preto:

- nevykonáva system-scoped uniqueness;
- nezlučuje podobné entries;
- nepredstiera interoperabilitu;
- vyžaduje odlišné CLS ID a dostatočne presnú definíciu/provenance.

Pred importom reálnych externých systémov musí vzniknúť samostatné system/code rozhodnutie. Jednoduchý v1 kontrakt nie je povolením na hromadný import.

## 23. Identity / Equivalence

Identita klasifikačnej položky je výlučne CLS ID. Nie je ňou:

- name alebo description;
- externý code;
- source document;
- parent alebo hierarchy path;
- podobnosť významu.

Dve semanticky podobné položky môžu zostať oddelené. Ekvivalencia, broader/narrower mapping, exact match a replacement majú rozdielne semantics; v1 modeluje iba lifecycle replacement odkazy. Equivalence engine ani mapovací objekt nevzniká.

## 24. Candidate Models

### Candidate A

Common metadata + `id`, `name`.

- Minimality: najvyššia.
- Semantic clarity: nedostatočná; name sám nevytvára bezpečne odlíšiteľný význam.
- Interoperability: žiadna.
- Migration risk: vysoké riziko duplicitných alebo nejasných CLS.
- Verdict: odmietnuť ako príliš slabý model.

### Candidate B

Common metadata + `id`, `name`, `description`.

- Minimality: vysoká.
- Semantic clarity: dostatočná pre system-neutral CLS význam.
- Core compatibility: plne postačuje ako cieľ `Classification.classificationId`.
- Migration risk: nízky, ak dokumentácia výslovne zakáže external-code a hierarchy interpretáciu.
- Verdict: bezpečné jadro v1.

### Candidate C

Candidate B + `parentId`.

- Hierarchy compatibility: iba single-parent tree.
- Migration risk: vysoké pri DAG alebo cross-system hierarchii.
- Referential burden: vyžaduje cycle a system compatibility pravidlá.
- Verdict: odmietnuť pre v1.

### Candidate D

Candidate B + `classificationSystemId`, `externalCode`, `parentId`.

- Semantic potential: vysoký pre externú interoperabilitu.
- Coupling: vyžaduje nový Classification System contract a hierarchickú politiku.
- Overdesign risk: vysoký; ID formát ani target aggregate nie sú prijaté.
- Verdict: odložiť ako system-aware budúcu verziu.

### Candidate E – odporúčaný

Candidate B + voliteľné `notes`, `replaces`, `replacedBy`.

- Minimality: zachováva iba identitu, definíciu, lifecycle a provenance.
- Semantic clarity: bezpečný system-neutral význam bez voľného system/code modelu.
- Compatibility: zodpovedá embedded Classification a spoločnému katalógovému vzoru.
- Future migration: umožňuje neskôr doplniť systém, kód a hierarchy bez reinterpretácie existujúcich polí.
- Verdict: odporúčaný v1 model.

## 25. Recommended Minimal Model

Odporúčaný Classification Catalog Entry v1 obsahuje:

```json
{
  "id": "CLS-xxxxxx",
  "schemaVersion": "...",
  "recordVersion": "...",
  "revision": 0,
  "status": "Draft",
  "createdAt": "...",
  "createdBy": "...",
  "updatedAt": "...",
  "updatedBy": "...",
  "sourceLinks": [],
  "changeSummary": "...",
  "name": "Fictional classification name",
  "description": "Fictional system-neutral classification definition."
}
```

Príklad je iba tvar kontraktu. Nezakladá reálnu CLS položku ani externý klasifikačný systém.

Voliteľné polia sú `notes`, `replaces` a `replacedBy`. Všetky zobrazené polia sú povinné.

## 26. Field Requirement Matrix

| Pole | V1 stav | Pravidlo |
| --- | --- | --- |
| `id` | REQUIRED | Centrálne `CLS-xxxxxx`. |
| `schemaVersion` | REQUIRED | Common metadata. |
| `recordVersion` | REQUIRED | Common metadata. |
| `revision` | REQUIRED | Nezáporné celé číslo. |
| `status` | REQUIRED | Existujúci RecordStatus. |
| `createdAt`, `updatedAt` | REQUIRED | Existujúci date-time contract. |
| `createdBy`, `updatedBy` | REQUIRED | Neprázdne actor hodnoty. |
| `sourceLinks` | REQUIRED | Definition provenance; Draft môže byť prázdny. |
| `changeSummary` | REQUIRED | Neprázdne. |
| `name` | REQUIRED | Neprázdny kanonický názov; nie identita ani unique key. |
| `description` | REQUIRED | Neprázdna system-neutral definícia. |
| `notes` | OPTIONAL | Neautoritatívna poznámka. |
| `replaces`, `replacedBy` | OPTIONAL | CLS odkazy; integrita sa overí aplikačne. |
| `classificationSystem` | REJECTED IN V1 | Voľný text nesmie tvoriť system identity. |
| `classificationSystemId` | DEFERRED | Chýba cieľový contract a ID governance. |
| `code`, `externalCode` | DEFERRED | Bez system/version kontextu sú nejednoznačné. |
| `symbol` | REJECTED IN V1 | Nie je univerzálny classification invariant. |
| `parentId`, `parentIds` | DEFERRED | Tree/DAG a system boundary nie sú prijaté. |
| `hierarchyPath`, `level` | REJECTED IN V1 | Odvodené a modelovo predčasné. |
| `aliases` | DEFERRED | Chýba system/language/collision policy. |
| root `verificationStatus` | REJECTED | Catalog lifecycle nie je assignment verification. |
| `allowedTargetTypes` | DEFERRED | Predčasné entity coupling. |

## 27. Validation Responsibility

### JSON Schema structural validation

- uzavretý tvar objektu a required fields;
- CLS formát cez centrálny `$ref`;
- common metadata, lifecycle enum a SourceLink tvar;
- neprázdny `name` a `description`;
- CLS formát replacement odkazov;
- zákaz system, code, hierarchy, alias, verification a target-policy polí vo v1.

### EOS application validation

- Review/Approved source provenance podľa existujúceho lifecycle/source pravidla;
- replacement self-reference a základná lifecycle konzistencia, keď bude pravidlo zavedené;
- zákaz tichej reinterpretácie schváleného významu.

### Catalog-aware validation

- budúca system-scoped name/code collision policy;
- budúca hierarchy edge semantics a system compatibility;
- budúca interná/externá origin policy;
- budúca kompatibilita CLS s rodičovským typom alebo property;
- budúce alias a equivalence mapovanie.

### Reference integrity

- `Classification.classificationId` odkazuje na existujúcu a použiteľnú CLS položku;
- `replaces`/`replacedBy` ciele existujú a sú konzistentné;
- budúce parent a classificationSystem ciele existujú;
- SourceLink odkazuje na existujúci SourceReference.

### Application/entity validation

- či je daná classification povolená pre konkrétny parent context;
- či assignment provenance postačuje pre pôvod a workflow;
- či sa nevyskytujú zakázané duplicity alebo konfliktné assignments.

### Governance

- prijatie, deprecácia, archivácia a supersession;
- doménový správca a review externého významu;
- pravidlá importu reálnych systémov a ochrana historickej interpretácie.

## 28. Property Catalog Boundary

Classification Catalog zostáva vo v1 nezávislý od Property Catalogu.

- Property Catalog v1 neobsahuje classification odkazy.
- Classification Catalog nepotrebuje PRP na definovanie system-neutral CLS významu.
- Nevzniká reverse dependency ani cyklus.
- Budúca kategorizácia properties, domain applicability alebo povolené classifications vyžadujú samostatné rozhodnutie po zavedení Classification Catalogu.

Classification Catalog nesmie meniť Property Catalog v rámci svojho prvého entry kontraktu.

## 29. Knowledge Entity Boundary

V1 neobsahuje `allowedTargetTypes` ani iný zoznam Material, Machine, ManufacturingProcess, CuttingTool, Supplier alebo Job typov.

Také pole by:

- viazalo Reference Catalog na ešte neimplementované entity kontrakty;
- vyžadovalo autoritatívny object-type register;
- miešalo význam kategórie s pravidlom jej použitia;
- komplikovalo evolúciu entít a cross-domain classifications.

Entity applicability zostáva catalog-aware/application pravidlom. Ak sa neskôr ukáže ako intrinsic vlastnosť classification systému, musí byť navrhnutá spolu so system modelom.

## 30. Real Data Boundary

Tento review nevytvára žiadnu reálnu CLS položku ani skutočný klasifikačný systém. Príklad v sekcii 25 je výlučne fiktívny tvar kontraktu.

Populácia reálnych material families, machine categories, process classes, industry classes, supplier categories alebo tool classes patrí do samostatného source-reviewed míľnika po prijatí schémy, system/code modelu podľa potreby a import governance.

## 31. Risks

| Riziko | Priorita | Opatrenie |
| --- | --- | --- |
| CLS sa zamení za external code. | Critical | `id` ponechať iba CLS; code/system polia vo v1 odmietnuť. |
| Externý kód sa interpretuje bez systému alebo verzie. | Critical | External-code binding odložiť do system-aware kontraktu. |
| Hierarchia sa predčasne uzavrie na strom. | High | V1 bez `parentId`; tree/DAG rozhodnúť samostatne. |
| Voľný system name vytvorí nekontrolovanú identitu. | High | `classificationSystem` text odmietnuť; neskôr riadené ID. |
| Definition provenance sa vydá za assignment evidence. | High | Zachovať dve samostatné SourceLink plochy a explicitnú dokumentáciu. |
| Name/description sa stanú náhradou structured semantics. | High | Povoliť ich na definíciu v1, ale zakázať code/system/hierarchy inferenciu. |
| Rovnaký name alebo code sa vyhodnotí ako equivalence. | High | Identita je iba CLS; equivalence odložiť. |
| Predčasne vznikne Classification System Catalog. | Medium | Nevytvárať nový aggregate bez samostatného review/rozhodnutia. |
| Katalóg prerastie na domain taxonomy engine. | High | V1 obmedziť na entry identity, definíciu, lifecycle a provenance. |
| `allowedTargetTypes` naviaže katalóg na nehotové entity. | Medium | Target applicability odložiť do application/catalog-aware vrstvy. |
| System-neutral v1 sa mylne vydá za plnú externú interoperabilitu. | High | Uviesť explicitnú limitation v CDR, schéme a dokumentácii. |
| Deprecated CLS zostane bez riadeného nástupcu. | Medium | Povoliť replacement odkazy; integritu kontrolovať neskôr. |

## 32. Deferred Concepts

Odložené sú:

- Classification System Catalog alebo iný system identity contract;
- `classificationSystemId`, system version, issuing organization a validity interval;
- external code, code namespace a system-scoped uniqueness;
- machine-readable interný/externý origin;
- hierarchy tree/DAG model, parent edges, roots, paths, levels a cycle policy;
- edge provenance a edge versioning;
- aliases, localization, historical labels a collision policy;
- semantic equivalence, exact/broad/narrow mappings a cross-system mapping;
- entity/property applicability a `allowedTargetTypes`;
- assignment multiplicity, exclusivity, ordering a conflict rules;
- catalog-aware Classification validácia;
- reálne CLS dáta a import externých systémov.

## 33. Implementation Preconditions

Implementácia Classification Catalog Entry v1 môže začať, ak dodrží tieto podmienky:

1. Classification Catalog zostane Reference Catalog.
2. Položka zostane samostatný Catalog Entry Aggregate Root so stabilným `id` vo formáte CLS.
3. Použije rovnaký common metadata pattern, lifecycle a SourceLink contract ako existujúce katalógy.
4. `name` a `description` budú povinné a neprázdne; nebudú určovať identitu ani globálnu unikátnosť.
5. Voliteľné `notes`, `replaces` a `replacedBy` budú jediné ďalšie v1 fields.
6. Replacement odkazy budú používať iba CLS a nebudú modelovať hierarchy alebo equivalence.
7. Root nebude obsahovať `verificationStatus`.
8. System, code, symbol, hierarchy, aliases, origin flag, equivalence a target applicability nebudú súčasťou v1.
9. Entry sourceLinks budú dokumentované ako definition provenance; embedded Classification sourceLinks ako assignment provenance.
10. V1 bude označené ako system-neutral a nesmie sa používať ako plná external-system interoperability vrstva.
11. Catalog-aware a reference-integrity kontroly zostanú samostatným následným integračným krokom.
12. Fixtures budú výlučne fiktívne a nevznikne reálna CLS položka.
13. Existing Classification, Property Catalog a Accepted architektúra sa významovo nezmenia.

## 34. Readiness Verdict

Classification Catalog Entry v1 je možné implementovať bez opravy Accepted architektúry. Katalógová rola Reference Catalogu, CLS identita, Catalog Entry aggregate boundary, lifecycle, metadata a definition/assignment provenance hranica sú dostatočne jasné.

Implementácia je bezpečná iba ako úzky **system-neutral** kontrakt s povinným názvom a definíciou. Classification system, external code, interný/externý origin, hierarchy, aliases, equivalence a target applicability zostávajú explicitne odložené. V1 preto nebude poskytovať plnú interoperabilitu s externými klasifikačnými systémami ani hierarchy engine.

Po splnení podmienok v sekcii 33 môže implementácia jednoduchého entry kontraktu začať. Catalog-aware validácia a reálna populácia katalógu musia zostať samostatnými následnými míľnikmi.

## 35. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-09-24 | 0.1 | 0 | Codex | Initial pre-design review of Classification Catalog role, CLS identity, system and code boundary, hierarchy, provenance, lifecycle and implementation readiness. |

READY WITH CONDITIONS
