# CDR-0010 - Condition Type Catalog Pre-design Review

Project: EOS – Engineering Operating System

Contract Review ID: CDR-0010

Contract: Condition Type Catalog

Review type: Pre-design

Phase: 0.2B.2.2-prep

Version: 0.1

Revision: 0

Status: Review

Document basis: Accepted EOS architecture + Unit Catalog v1

## 1. Purpose

Tento dokument posudzuje najmenší bezpečný kontrakt položky `Condition Type Catalog`, ktorá dá autoritatívny význam existujúcim odkazom `CND-xxxxxx` v hodnotovom objekte `Condition`.

Review rozhoduje hranicu medzi významom typu podmienky, konkrétnou hodnotou `Condition`, budúcim `Property Catalog` a aplikačnou validáciou. Neimplementuje schému, katalógové dáta ani rule engine.

## 2. Scope

Review pokrýva:

- rolu katalógu a objektový typ jeho položky,
- význam identity `CND-xxxxxx`,
- minimálne polia prvej verzie,
- povolené hodnotové formy a cieľové rodiny `referenceId`,
- hranice `evaluationMode`, jednotiek, multiplicity a logických kombinácií,
- lifecycle, metadata a zdrojovú dohľadateľnosť,
- zodpovednosti JSON Schema, katalógovej, referenčnej a aplikačnej validácie,
- podmienky začatia implementačného míľnika.

Mimo rozsahu sú zmeny `Condition`, `Property Catalog`, reálne CND položky, vyhodnocovanie podmienok a všetky zmeny Accepted RFC alebo ADR.

## 3. Reviewed Artifacts

Review vychádza z:

- `AGENTS.md`,
- `docs/governance/EOS-003_Identification_and_Versioning.md`,
- `docs/governance/EOS-006_Data_Validation_Standard.md`,
- `docs/governance/EOS-007_Validation_Capability_Matrix.md`,
- `docs/rfc/RFC-0001_Engineering_Property_Model.md`,
- `docs/rfc/RFC-0002_Engineering_Object_Taxonomy.md`,
- `docs/rfc/RFC-0003_EOS_Engineering_Glossary.md`,
- `adr/ADR-0015_Establish_engineering_knowledge_layer.md`,
- `docs/contracts/CDR-0004_Condition_Contract.md`,
- `docs/contracts/CDR-0008_Knowledge_Core_Integration_Review.md`,
- `docs/contracts/CDR-0009_Unit_Catalog_PreDesign_Review.md`,
- existujúcich Knowledge Core, common a Unit Catalog schém,
- `schemas/README.md`, `CHANGELOG.md`, `ROADMAP.md` a `BACKLOG.md`.

RFC-0001, RFC-0002, RFC-0003 a ADR-0015 sú `Accepted`. CDR-0008 Revision 1 uzatvára Knowledge Core s verdiktom `READY FOR 0.2B.2`. Unit Catalog v1 je implementovaný bez reálnych jednotkových záznamov.

## 4. Authoritative Findings

| Finding | Classification | Consequence |
| --- | --- | --- |
| Condition Type Catalog patrí medzi Knowledge Catalogs. | AUTHORITATIVE | Nie je Reference Catalog; definuje interný EOS význam používaný v znalostných tvrdeniach. |
| Condition Type Catalog je samostatný autoritatívny katalóg typov podmienok. | AUTHORITATIVE | Voľný text ani lokálny enum nesmie nahradiť význam CND položky. |
| Jeho položka je `Catalog Entry` so stabilnou identitou, lifecycle, versioningom, revíziou a auditom. | AUTHORITATIVE | Položka nie je Value Object ani konkrétna inštancia Condition. |
| `CND-xxxxxx` identifikuje Condition Type Catalog Entry. | AUTHORITATIVE | Neidentifikuje Condition inštanciu, hodnotu, jednotku ani `evaluationMode`. |
| `Condition` je rodičom vlastnený immutable Value Object bez vlastnej identity a lifecycle. | AUTHORITATIVE | `conditionTypeId` je referencia na význam, nie identita vloženej Condition. |
| Condition vyžaduje `conditionTypeId`, `evaluationMode` a presne jednu z piatich existujúcich hodnotových foriem. | AUTHORITATIVE | Katalóg nesmie pridať šiestu formu ani meniť tvar konkrétnej Condition. |
| Katalógy zdieľajú spoločný metadata základ, no Knowledge a Reference Catalog majú odlišný governance význam. | AUTHORITATIVE | Unit Catalog je technický precedens pre tvar, nie dôvod označiť CND katalóg ako Reference Catalog. |
| Catalog Entry s vlastným ID, lifecycle a auditom tvorí samostatnú konzistenčnú hranicu. | IMPLIED | Condition Type Catalog Entry sa má implementovať ako samostatný Aggregate Root, nie vnoriť do iného agregátu. |
| Katalóg má určovať povolenú hodnotovú formu typu podmienky. | IMPLIED | Bez `allowedValueForms` by prvá verzia nedala CND odkazu strojovo použiteľný význam. |
| Pre `referenceId` treba určiť povolenú cieľovú rodinu pre konkrétny typ. | IMPLIED | KCI-0003 nemožno riešiť bezhlavým rozširovaním statického unionu všetkými prefixmi. |
| Presné obmedzenia evaluation mode podľa typu podmienky nie sú prijaté. | OPEN | V1 nesmie zaviesť default ani fixed mode ako nový workflow význam. |
| Dimenzia, quantity kind a všeobecná kompatibilita jednotiek nie sú modelované. | OPEN | V1 nesmie predstierať unit compatibility. |
| Význam viacerých Conditions s rovnakým `conditionTypeId` nie je určený. | OPEN | Duplicita zostáva prípustná štrukturálne, ale bez významu AND, OR alebo váhy. |
| Property-specific povinnosť, jednotky, multiplicita a evaluation constraints patria do budúceho Property Catalogu. | DEFERRED | CND katalóg nemá duplikovať pravidlá použitia konkrétnej property. |
| Reálne CND položky a ich zdrojovo skontrolovaný obsah neexistujú. | DEFERRED | Populácia katalógu musí byť samostatný source-reviewed míľnik. |

## 5. Catalog Role

Condition Type Catalog je **Knowledge Catalog**, nie Reference Catalog.

Reference Catalog reprezentuje externý, všeobecný alebo technicky referenčný význam. Knowledge Catalog definuje interný EOS význam používaný pri znalostných tvrdeniach alebo rozhodovaní. RFC-0002 §9.0 a RFC-0003 G-0078 uvádzajú Condition Type Catalog výslovne ako Knowledge Catalog.

Jedna Condition Type Catalog Entry je:

- autoritatívna `Catalog Entry`,
- samostatná entita so stabilným ID,
- prakticky samostatný Aggregate Root, pretože má vlastný lifecycle, versioning, revíziu a audit,
- nezávisle uložená a referencovateľná,
- samostatne revidovaná,
- vybavená povinným poľom `sourceLinks`, ktorého neprázdnosť závisí od obsahu a lifecycle pravidiel.

Nie je Reference Object v úzkom zmysle externého zdroja, Value Object ani konkrétna Condition. Označenie Aggregate Root je bezpečný dôsledok prijatej taxonómie, nie nový typ doménového obsahu.

## 6. CND Identifier Semantics

`CND-xxxxxx` identifikuje presne jednu Condition Type Catalog Entry alebo stabilný autoritatívny význam tejto položky.

Položka má používať pole `id`, rovnako ako Unit Catalog Entry a spoločná konvencia EOS entít. `conditionTypeId` zostáva referenčným poľom v `Condition`; na koreni katalógovej položky by nesprávne zdvojovalo identitu.

`CND-xxxxxx` neidentifikuje:

- konkrétnu vnorenú Condition,
- hodnotu podmienky,
- `evaluationMode`,
- Quantity alebo ValueRange,
- property,
- unit,
- pravidlo vyhodnotenia alebo logickú skupinu.

## 7. Relationship to Condition

Rozdelenie zodpovedností je nasledovné:

- `Condition` ukladá konkrétnu kontextovú hodnotu a jej konkrétny `evaluationMode`.
- `Condition Type Catalog Entry` definuje autoritatívny význam `conditionTypeId` a povolené serializačné formy hodnoty.
- Ak je formou `referenceId`, katalóg určí povolené cieľové ID rodiny.
- Budúci Property Catalog určí, ktoré condition types sú pre property povolené alebo povinné a aké property-specific obmedzenia platia.
- Aplikačná alebo rule vrstva vyhodnotí splnenie, kombinácie, rozpory a referenčnú existenciu.

Katalógová položka neukladá konkrétnu hodnotu Condition. Condition nepreberá lifecycle, sourceLinks ani revíziu katalógovej položky.

## 8. Candidate Field Inventory

| Field | Classification | Reason |
| --- | --- | --- |
| `id` | REQUIRED NOW | Stabilné `CND-xxxxxx`; identita jednej Catalog Entry. |
| `schemaVersion` | REQUIRED NOW | Verzia serializačného kontraktu. |
| `recordVersion` | REQUIRED NOW | Významová verzia položky. |
| `revision` | REQUIRED NOW | Menšia oprava bez zmeny významu. |
| `status` | REQUIRED NOW | Nezávislý lifecycle Catalog Entry. |
| `createdAt`, `createdBy`, `updatedAt`, `updatedBy` | REQUIRED NOW | Audit a dohľadateľnosť. |
| `sourceLinks` | REQUIRED NOW | Spoločné entity metadata; obsah je lifecycle a claim aware. |
| `changeSummary` | REQUIRED NOW | Audit zmeny. |
| `name` | REQUIRED NOW | Kanonický ľudsky čitateľný názov, nie identita. |
| `description` | OPTIONAL NOW | Vysvetlenie významu; nesmie nahradiť štruktúrované pravidlá. |
| `allowedValueForms` | REQUIRED NOW | Jedno alebo viac povolených polí z existujúceho Condition unionu. |
| `allowedReferencePrefixes` | CONDITIONALLY REQUIRED | Povinné a neprázdne iba vtedy, keď `allowedValueForms` obsahuje `referenceId`; smie obsahovať iba už riadené a Condition podporované ID rodiny. |
| `allowedEvaluationModes` | DEFER | Bez parent/property kontextu by predčasne obmedzovalo použitie. |
| `defaultEvaluationMode` | REJECT IN V1 | Condition už vyžaduje explicitný mode; default by skrýval významovú voľbu. |
| `fixedEvaluationMode` | REJECT IN V1 | Mieša typ podmienky s konkrétnym spôsobom jej použitia. |
| `allowedUnitIds` | DEFER | Explicitný allow-list je technicky možný, ale bez quantity-kind/dimension modelu hrozí duplicita Property Catalog pravidiel. |
| `requiredUnitId` | REJECT IN V1 | Neprimerane viaže typ na jednu jednotku a zamieňa reprezentáciu so sémantikou. |
| `quantityKind` | REJECT | Voľný text by vytvoril neautoritatívnu ontológiu. |
| `dimension` | DEFER | Neexistuje prijatý význam ani dátový tvar. |
| `allowMultiple` | DEFER | Kardinalita závisí od rodiča a property; jednoduchý boolean nevyrieši AND/OR ani konflikty. |
| `uniquenessScope` | REJECT IN V1 | Bez modelu scope a logiky by išlo o nejasné pravidlo. |
| `verificationStatus` | REJECT AT ROOT | Stav tvrdenia alebo SourceLink nie je lifecycle katalógovej položky. |
| `notes` | OPTIONAL NOW | Lokálna doplnková poznámka bez autoritatívnej sémantiky. |
| `replaces`, `replacedBy` | OPTIONAL NOW | Konzistentné CND referencie pre historicky resolvovateľný lifecycle; existencia a cykly sú aplikačné pravidlá. |
| aliases | DEFER | RFC ich povoľuje pre migráciu, no v1 nemá typ, jazyk ani collision policy. |
| ďalší metadata wrapper | REJECT | Musí sa znovu použiť common entity metadata, nie vytvoriť druhý model. |

## 9. Name / Description

`name` je povinný, neprázdny, kanonický ľudsky čitateľný názov. Nie je identitou, unique key ani náhradou `CND-xxxxxx`.

`description` je voliteľný neprázdny vysvetľujúci text. Nesmie niesť jedinú strojovo potrebnú informáciu o povolenej hodnotovej forme, cieľovej referencii, jednotke, multiplicite alebo evaluation mode.

## 10. Allowed Value Forms

Odporúča sa povinné pole `allowedValueForms` ako neprázdne pole s unikátnymi položkami. Povolené hodnoty sú výlučne:

- `quantity`,
- `valueRange`,
- `textValue`,
- `booleanValue`,
- `referenceId`.

Model podporuje **jednu alebo viac** povolených foriem na typ podmienky. Jedna konkrétna Condition naďalej obsahuje presne jednu formu podľa existujúcej schémy.

Viac foriem je bezpečnejšie než povinná presne jedna forma: umožní kontrolovanú migráciu a legitímne alternatívne reprezentácie bez vytvorenia fallback mechanizmu. Každá konkrétna forma zostáva explicitná. Neodporúča sa preferred form ani implicitné konverzie; poradie poľa nemá prioritu.

Model bez katalógového obmedzenia by neriešil základný účel míľnika. Model s ľubovoľnými novými formami by bol v rozpore s uzavretým Condition kontraktom.

## 11. Evaluation Mode Decision

`evaluationMode` patrí konkrétnej Condition a vyjadruje, ako sa má posudzovať v kontexte rodiča. Nie je identitou ani hodnotovou formou condition type.

V1 nemá obsahovať:

- `allowedEvaluationModes`,
- `defaultEvaluationMode`,
- `fixedEvaluationMode`.

Condition naďalej explicitne používa jednu z existujúcich hodnôt `mandatory`, `limiting`, `descriptive`, `recommended` alebo `contextual`. Prípadné obmedzenie podľa property alebo workflow patrí do Property Catalogu alebo aplikačnej vrstvy. Katalóg nesmie zaviesť implicitný default, ktorý by menil význam chýbajúceho údaja; pole je v Condition povinné.

## 12. Unit Restriction Decision

V1 nemá obsahovať `allowedUnitIds`, `requiredUnitId`, `quantityKind` ani `dimension`.

Unit Catalog v1 poskytuje identitu, lifecycle, názov a symbol, ale neposkytuje dimenziu, quantity kind ani konverznú kompatibilitu. Explicitný UNT allow-list by bol technicky validovateľný, no bez rozdelenia intrinsic condition-type obmedzení a property-specific obmedzení by sa pravidlá ľahko zdvojili.

Do prijatia spoločného sémantického modelu platí:

- vnorené Quantity a ValueRange nesú vlastné `unitId`,
- schéma kontroluje iba formát UNT,
- existencia UNT je referenčná integrita,
- povolenosť jednotky pre konkrétnu property patrí do Property Catalogu,
- dimenzionálna kompatibilita a konverzia zostávajú nedostupnou capability, nie voľným textom.

## 13. Multiplicity Decision

V1 nemá obsahovať `allowMultiple` ani `uniquenessScope`.

Existujúce polia `conditions` môžu obsahovať viac Conditions a aktuálne nezakazujú opakovaný `conditionTypeId`. Opakovanie preto zostáva štrukturálne povolené, ale nesmie sa interpretovať ako AND, OR, vyššia váha ani automaticky ako chyba.

Kardinalita je spravidla vlastnosťou použitia condition type pri konkrétnej property alebo rodičovi. Budúci Property Catalog môže určiť property-specific minimum, maximum alebo unikátnosť. Aplikačná vrstva musí neskôr kontrolovať presné duplicity, redundanciu a rozpory podľa prijatých pravidiel.

## 14. Condition Combination Boundary

Condition Type Catalog v1 nemodeluje:

- AND alebo OR,
- precedenciu a zátvorkovanie,
- skupiny podmienok,
- vzájomné vylúčenie,
- implikácie,
- pravidlá splnenia,
- contradiction detection.

Tieto významy patria do budúcej applicability/rule vrstvy. Poradie Conditions v JSON poli nemá autoritatívny logický význam.

## 15. Reference Value Boundary

`referenceId` nesmie zostať generickým neobmedzeným odkazom. Ak CND položka povoľuje formu `referenceId`, musí uviesť neprázdne `allowedReferencePrefixes`.

Odporúča sa prefixová politika, nie `allowedReferenceTypes`, pretože EOS má autoritatívne centralizované ID rodiny, ale nemá samostatný object-type catalog. Hodnoty musia byť uzavretý enum existujúcich aktívnych rodín, ktoré podporuje aktuálny Condition `referenceId` union. Katalóg nesmie automaticky povoliť každý nový EOS prefix.

Pravidlá:

- `allowedReferencePrefixes` je neprítomné, ak `referenceId` nie je povolená forma,
- pri povolenom `referenceId` je pole povinné, neprázdne a bez duplicít,
- konkrétny target musí patriť do jednej z uvedených rodín,
- validný prefix nepotvrdzuje existenciu ani použiteľnosť cieľa,
- rozšírenie Condition unionu na novú rodinu je samostatná verziovaná zmena, nie automatický dôsledok katalógového záznamu.

Tým sa uzatvára návrhová časť KCI-0003 bez vytvorenia všeobecného graph relationship modelu.

## 16. Source Traceability

`sourceLinks` je povinné pole common entity metadata a používa existujúci SourceLink kontrakt bez duplikácie.

- `Draft` položka môže mať `sourceLinks: []`.
- `Review` alebo `Approved` položka s overiteľným technickým, výrobným, dodávateľským, obchodným alebo externým normatívnym tvrdením musí mať relevantný SourceLink.
- Čisto interná EOS taxonomická definícia nie je automaticky externé technické tvrdenie; nesmie sa pre ňu vymýšľať falošný externý zdroj ani source class.
- Governance schválenie interného významu musí zostať auditovateľné cez record metadata a príslušný governance proces. Budúce pravidlo môže vyžadovať interný SourceReference, ak jeho klasifikácia bude autoritatívne vyriešená.
- Názov zdroja v `description` alebo `notes` nie je náhrada SourceLink.

Neprázdnosť je aplikačné alebo governance pravidlo závislé od obsahu, nie univerzálny `minItems: 1` v JSON Schema.

## 17. Lifecycle

Condition Type Catalog Entry používa rovnaký record lifecycle ako Unit Catalog Entry:

- `Draft`,
- `Review`,
- `Approved`,
- `Deprecated`,
- `Archived`.

Nevzniká stav `Active`. Deprecated položka sa nemaže a zostáva historicky resolvovateľná. Voliteľné `replaces` a `replacedBy` používajú CND identity; existencia cieľa, self-reference a cykly patria referenčnej alebo katalógovej validácii.

`status` katalógovej položky nie je `Condition.evaluationMode`. Root nemá `verificationStatus`; prípadný verification status zostáva na SourceLink alebo konkrétnom tvrdení.

## 18. Metadata Model

Položka znovu používa rovnaký common entity metadata význam ako Unit Catalog Entry:

- `id`,
- `schemaVersion`,
- `recordVersion`,
- `revision`,
- `status`,
- `createdAt`, `createdBy`,
- `updatedAt`, `updatedBy`,
- `sourceLinks`,
- `changeSummary`.

Implementácia nesmie vytvoriť druhý metadata model. Ak uzavretý common metadata objekt nemožno priamo rozšíriť, môže sa použiť overený property-level `$ref` postup Unit Catalog v1 bez zmeny významu.

## 19. Candidate Models

### Candidate A

Common metadata + `id`, `name`, `allowedValueForms`.

- Minimality: vysoká.
- Semantic usefulness: dostatočná pre nereferenčné formy.
- Riziko: pri `referenceId` neuzatvára cieľovú politiku KCI-0003.
- Verdict: nedostatočný bez zákazu `referenceId` alebo doplnenia target policy.

### Candidate B

Candidate A + `allowedEvaluationModes`.

- Minimality: stredná.
- Semantic usefulness: potenciálna, ale význam závisí od parent/property kontextu.
- Coupling: predčasné workflow obmedzenie.
- Verdict: neodporúča sa pre v1.

### Candidate C

Candidate A + `allowedUnitIds` + `allowMultiple`.

- Minimality: nízka.
- Semantic usefulness: iba čiastočná bez dimension a parent kontextu.
- Coupling: vysoké riziko duplicity s Property Catalogom.
- Verdict: neodporúča sa pre v1.

### Candidate D

Common metadata + `id`, `name`, `allowedValueForms`, podmienene `allowedReferencePrefixes`; voliteľne `description`, `notes`, `replaces`, `replacedBy`.

- Minimality: vysoká; pridáva iba pravidlo nevyhnutné pre bezpečný `referenceId`.
- Semantic usefulness: CND určuje význam, povolené formy a pri referencii jej cieľovú rodinu.
- Compatibility: nemení Condition a nepreberá Property Catalog pravidlá.
- Migration: budúce polia sa dajú pridať cez novú schema/record verziu.
- Risk: prefixová politika je zámerne viazaná na governované ID rodiny a pri ich rozšírení vyžaduje vedomú verziovanú zmenu.
- Verdict: odporúčané.

## 20. Recommended Minimal Model

Odporúča sa Candidate D:

```json
{
  "id": "CND-xxxxxx",
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
  "name": "Fictional condition type",
  "allowedValueForms": ["textValue"]
}
```

Pri type povoľujúcom `referenceId` sa navyše vyžaduje napríklad fiktívna policy:

```json
{
  "allowedValueForms": ["referenceId"],
  "allowedReferencePrefixes": ["SRC"]
}
```

Príklady ilustrujú štruktúru, nie reálny CND záznam ani schválený condition type.

Model nedáva katalógu evaluation engine, unit model, logické operátory ani property-specific pravidlá.

## 21. Field Requirement Matrix

| Field | V1 status |
| --- | --- |
| `id` | REQUIRED |
| `schemaVersion` | REQUIRED |
| `recordVersion` | REQUIRED |
| `revision` | REQUIRED |
| `status` | REQUIRED |
| `createdAt` | REQUIRED |
| `createdBy` | REQUIRED |
| `updatedAt` | REQUIRED |
| `updatedBy` | REQUIRED |
| `sourceLinks` | REQUIRED; obsah môže byť podľa pravidiel prázdny |
| `changeSummary` | REQUIRED |
| `name` | REQUIRED |
| `allowedValueForms` | REQUIRED; 1 až 5 unikátnych existujúcich foriem |
| `allowedReferencePrefixes` | CONDITIONALLY REQUIRED pri `referenceId`; inak neprípustné |
| `description` | OPTIONAL |
| `notes` | OPTIONAL |
| `replaces` | OPTIONAL |
| `replacedBy` | OPTIONAL |
| `allowedEvaluationModes` | DEFERRED |
| `defaultEvaluationMode` | REJECTED IN V1 |
| `fixedEvaluationMode` | REJECTED IN V1 |
| `allowedUnitIds` | DEFERRED |
| `requiredUnitId` | REJECTED IN V1 |
| `quantityKind` | REJECTED |
| `dimension` | DEFERRED |
| `allowMultiple` | DEFERRED |
| `uniquenessScope` | REJECTED IN V1 |
| root `verificationStatus` | REJECTED |
| aliases | DEFERRED |

## 22. Validation Responsibility

### JSON Schema structural validation

- uzavretý tvar Catalog Entry,
- povinné common metadata,
- CND formát `id`,
- lifecycle enum,
- neprázdny `name`,
- neprázdne unikátne `allowedValueForms` z piatich existujúcich hodnôt,
- podmienená prítomnosť/neprítomnosť `allowedReferencePrefixes`,
- uzavretý enum už podporovaných cieľových prefixov,
- tvar SourceLink,
- CND formát replacement odkazov.

### EOS application validation

- lifecycle-aware povinnosť zdrojov podľa povahy tvrdení,
- version/revision a timestamp pravidlá presahujúce štruktúru,
- neskôr kompatibilita Condition formy s CND položkou,
- neskôr kompatibilita konkrétneho `referenceId` s target policy,
- neskôr duplicity, rozpory a pravidlá použitia.

### Catalog-aware validation

- `Condition.conditionTypeId` odkazuje na existujúcu a použiteľnú CND položku,
- konkrétna hodnotová forma je v `allowedValueForms`,
- pri `referenceId` prefix patrí do `allowedReferencePrefixes`,
- prípadné budúce evaluation, unit a multiplicity constraints,
- používanie Deprecated alebo Archived položiek podľa prijatej policy.

### Reference integrity

- existencia CND položky,
- existencia cieľa `referenceId`,
- existencia cieľov replacement väzieb,
- self-reference a cykly replacement vzťahov.

### Property Catalog

- povolené a povinné condition types pre konkrétnu property,
- property-specific jednotky a hodnotové obmedzenia,
- property-specific multiplicita,
- prípadné property-specific evaluation mode obmedzenia.

### Rule/Application Layer

- splnenie konkrétnej Condition,
- AND/OR a grouping,
- dedenie, priorita a konflikty,
- contradiction detection,
- rozhodnutie o použiteľnosti tvrdenia alebo pozorovania.

## 23. Property Catalog Interaction

Jedno pravidlo musí mať jedného vlastníka:

| Rule | Owner |
| --- | --- |
| Autoritatívny význam `CND-xxxxxx` | Condition Type Catalog |
| Intrinsic povolené hodnotové formy CND | Condition Type Catalog |
| Povolené cieľové prefixy referenčnej formy CND | Condition Type Catalog |
| Či property smie alebo musí použiť určitý CND | Property Catalog |
| Property-specific jednotky alebo rozsahy Condition | Property Catalog |
| Property-specific počet Conditions daného typu | Property Catalog |
| Konkrétny `evaluationMode` a jeho prípustnosť v parent kontexte | Condition instance + budúca Property Catalog/application policy |
| Existencia a lifecycle CND/UNT/reference targetu | Reference-integrity/catalog-aware validation |
| Splnenie, kombinácia a rozpor Conditions | Rule/Application Layer |

Condition Type Catalog nesmie opakovať property-specific pravidlá. Property Catalog nesmie nanovo definovať globálny význam CND ani jeho základné hodnotové formy; smie z nich vytvoriť užší kontextový profil.

## 24. Real Data Boundary

Tento review nevytvára žiadny reálny CND záznam. Príklady sú výlučne fiktívne a demonštrujú tvar.

Obsah ako konkrétne environmentálne, procesné, materiálové, povrchové, nástrojové alebo iné technické podmienky patrí do samostatného source-reviewed population míľnika. Schéma ani dokumentácia nesmie taký obsah predstierať ako prijatú znalosť.

## 25. Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Katalóg sa zmení na generický rule engine. | High | V1 obmedziť na význam, value forms a reference target policy. |
| Príliš veľa povolených foriem urobí CND nejednoznačným. | Medium | Vyžadovať explicitný neprázdny unique zoznam; pri population review odôvodniť každú formu. |
| `referenceId` zostane nekontrolovaný alebo bude automaticky prijímať nové prefixy. | High | Podmienené `allowedReferencePrefixes`; každé rozšírenie je vedomá verziovaná zmena. |
| Condition schema union a katalógová prefixová policy sa rozídu. | High | V1 povoľuje iba prienik s aktuálnym Condition unionom; contract tests musia kontrolovať súlad. |
| CND katalóg zdvojí Property Catalog pravidlá. | High | Property-specific units, required conditions a multiplicitu vlastniť v Property Catalogu. |
| Predčasné unit restrictions predstierajú dimension compatibility. | High | V1 neobsahuje `allowedUnitIds`, quantity kind ani dimension. |
| Lifecycle sa zamení s `evaluationMode`. | Medium | Root používa `status`; instance používa explicitný `evaluationMode`; bez root verification status. |
| Viac Conditions sa začne implicitne chápať ako AND. | High | Poradiu a duplicite nepripisovať logický význam; rule semantics odložiť. |
| SourceLinks sa vynútia fiktívnym zdrojom pre čisté interné rozhodnutie. | Medium | Rozlíšiť povinnosť poľa od claim-aware neprázdnosti a nevymýšľať source class. |
| Deprecated CND sa vymaže alebo prestane resolvovať. | High | Zachovať lifecycle históriu a CND replacement referencie. |
| Aliasy obídu autoritatívne CND ID. | Medium | Aliasy vo v1 odložiť; názov nie je identity ani lookup key. |

## 26. Deferred Concepts

Odložené sú:

- `allowedEvaluationModes`, default a fixed evaluation mode,
- `allowedUnitIds`, quantity kind, dimension a conversion compatibility,
- multiplicita, uniqueness scope a presné duplicate rules,
- AND/OR, grouping, precedence a contradiction model,
- aliases, localization a collision policy,
- property-specific allowed/required conditions,
- applicability a evaluation engine,
- reálne CND položky a ich zdrojové datasety,
- catalog-aware validácia naprieč uloženými záznamami,
- rozšírenie Condition `referenceId` unionu o ďalšie ID rodiny.

Odloženie znamená, že capability nie je dostupná. Neznamená povolenie uložiť jej autoritatívny význam do `description` alebo `notes`.

## 27. Implementation Preconditions

Implementácia Condition Type Catalog Entry v1 môže začať, ak splní tieto podmienky:

1. Katalóg zostane Knowledge Catalog a položka samostatný Catalog Entry Aggregate Root.
2. Schéma použije `id` s centrálnym CND `$ref` a rovnaký common metadata/lifecycle význam ako Unit Catalog v1.
3. Povinné `allowedValueForms` bude neprázdny unique zoznam iba piatich existujúcich Condition foriem.
4. `allowedReferencePrefixes` bude povinné iba pri povolenom `referenceId`, inak neprípustné, a nebude automaticky prijímať nové prefixy.
5. V1 nepridá evaluation mode policy, unit restrictions, quantity kind, dimension, multiplicitu ani logické operátory.
6. `sourceLinks` bude povinné pole; neprázdnosť sa bude riadiť existujúcimi claim/lifecycle pravidlami bez fiktívneho zdroja.
7. Root nebude mať `verificationStatus`; lifecycle zostane oddelený od `Condition.evaluationMode`.
8. Existujúca Condition schéma sa v tomto katalógovom míľniku významovo nezmení.
9. Fixtures budú výlučne fiktívne a nevznikne žiadna reálna CND položka.
10. Catalog-aware validácia Condition proti uloženému katalógu bude jasne označená ako samostatný následný integračný krok, ak ju v1 entry contract ešte neposkytne.

## 28. Readiness Verdict

Najmenší Condition Type Catalog Entry je možné implementovať bez zmeny Accepted architektúry. Prijaté dokumenty jednoznačne určujú Knowledge Catalog, CND identitu, Catalog Entry lifecycle a vzťah k hodnotovému objektu Condition.

Implementácia musí dodržať explicitné hranice: v1 riadi iba autoritatívny význam, povolené hodnotové formy a pri `referenceId` cieľové prefixy. Evaluation mode constraints, jednotky, multiplicita, logické kombinácie a property-specific použitie zostávajú odložené. Samotná entry schéma ešte nepotvrdí existenciu ani kompatibilitu Condition odkazu; to patrí do katalógovo uvedomelej integračnej validácie.

Implementácia môže začať po splnení podmienok v sekcii 27. Verdikt je `READY WITH CONDITIONS`.

## 29. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-09-10 | 0.1 | 0 | Codex | Initial pre-design review of Condition Type Catalog role, CND identity, value-form and reference-target policy, lifecycle, Property Catalog boundary and implementation readiness. |

READY WITH CONDITIONS
