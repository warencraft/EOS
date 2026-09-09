# CDR-0009 - Unit Catalog Pre-design Review

**Project:** EOS - Engineering Operating System  
**Contract Review ID:** CDR-0009  
**Contract:** Unit Catalog  
**Review type:** Pre-design  
**Phase:** 0.2B.2.1-prep  
**Version:** 0.1  
**Revision:** 0  
**Status:** Review  
**Document basis:** Accepted EOS architecture + completed Phase 0.2B.1

## 1. Purpose

Účelom dokumentu je určiť najmenší bezpečný kontrakt položky Unit Catalogu, ktorý dá stabilný autoritatívny význam existujúcim referenciám `UNT-xxxxxx` bez zavedenia dimenzionálnej algebry, konverzného enginu alebo reálnych jednotkových dát.

Review oddeľuje prvú registračnú verziu Unit Catalogu od neskoršej strojovo spracovateľnej semantiky jednotiek. Výsledok je návrhový podklad; nevytvára schému ani katalógový záznam.

## 2. Scope

Review posudzuje:

- architektonickú kategóriu Unit Catalogu a jeho položiek,
- význam `UNT-xxxxxx`,
- identitu, lifecycle, versioning, audit a provenance,
- minimálny model názvu a symbolu,
- hranice quantity kind, dimenzie, systému jednotiek, aliasov a konverzií,
- minimálnu závislosť budúceho Property Catalogu,
- zodpovednosť jednotlivých validačných vrstiev,
- podmienky, za ktorých môže nasledovať implementácia kontraktu.

Mimo rozsahu sú JSON Schema, fixtures, reálne jednotky, dimenzionálna algebra, konverzné pravidlá, výpočtový kód, Property Catalog a ostatné katalógy.

## 3. Reviewed Artifacts

Review vychádza z týchto dokumentov a kontraktov:

- `AGENTS.md`,
- `docs/governance/EOS-003_Identification_and_Versioning.md`,
- `docs/governance/EOS-006_Data_Validation_Standard.md`,
- `docs/governance/EOS-007_Validation_Capability_Matrix.md`,
- `docs/governance/EOS-009_Architecture_Closure_Plan.md`,
- `docs/governance/EOS-010_Architecture_Readiness_Review.md`,
- `docs/rfc/RFC-0001_Engineering_Property_Model.md`,
- `docs/rfc/RFC-0002_Engineering_Object_Taxonomy.md`,
- `docs/rfc/RFC-0003_EOS_Engineering_Glossary.md`,
- `adr/ADR-0015_Establish_engineering_knowledge_layer.md`,
- `docs/contracts/CDR-0008_Knowledge_Core_Integration_Review.md`,
- `schemas/knowledge-core/quantity.schema.json`,
- `schemas/knowledge-core/value-range.schema.json`,
- `schemas/common/identifiers.schema.json`,
- `schemas/common/metadata.schema.json`,
- `schemas/common/source-link.schema.json`,
- `schemas/index.schema.json`,
- `schemas/README.md`,
- `CHANGELOG.md`,
- `ROADMAP.md`,
- `BACKLOG.md`.

RFC-0001, RFC-0002, RFC-0003 a ADR-0015 majú stav `Accepted`. CDR-0008 Revision 1 končí verdiktom `READY FOR 0.2B.2`.

## 4. Authoritative Findings

| Finding | Classification | Consequence |
| --- | --- | --- |
| Unit Catalog je Reference Catalog. | AUTHORITATIVE | Nemá sa označovať ako Knowledge Catalog iba preto, že vzniká vo fáze 0.2B.2 Knowledge Catalogs. |
| Unit Catalog je samostatný autoritatívny katalóg. | AUTHORITATIVE | Voľný text ani lokálny zoznam nemôže nahradiť katalóg. |
| Unit Catalog Entry je `Catalog Entry`. | AUTHORITATIVE | Má stabilnú identitu, samostatnú existenciu, lifecycle, revision/versioning a audit. |
| Súhrnná taxonómia označuje Unit Catalog Entry ako aggregate root. | AUTHORITATIVE | Iné aggregate roots ju iba referencujú cez `UNT`; nevlastnia ju ako vnorený objekt. |
| Unit Catalog Entry používa `UNT-xxxxxx`. | AUTHORITATIVE | `id` musí používať centrálny `$defs/UNT`. |
| `Quantity.unitId` a `ValueRange.unitId` odkazujú na budúci Unit Catalog Entry. | AUTHORITATIVE | Catalog-aware validácia musí neskôr kontrolovať existenciu a použiteľnosť cieľa. |
| Catalog Entry má plný record lifecycle a po schválení sa nemaže. | AUTHORITATIVE | Použijú sa existujúce entity metadata a stavy `Draft`, `Review`, `Approved`, `Deprecated`, `Archived`. |
| Unit Catalog má zachovať deprecated položku a podľa možnosti uviesť náhradu. | AUTHORITATIVE | Historické záznamy musia zostať resolvovateľné. |
| Unit Catalog Entry môže mať aliasy, ale alias nie je autoritatívna identita. | AUTHORITATIVE | Alias nesmie dostať význam rovný `UNT`; presný alias model môže byť odložený. |
| Unit má rozmerový a konverzný význam. | AUTHORITATIVE | Prvá verzia bez strojovej dimenzie a konverzie musí otvorene obmedziť svoje schopnosti; nesmie tvrdiť, že vie kompatibilitu alebo prevody. |
| RFC-0001 navrhuje `name`, `symbol`, `dimension`, SI väzbu, konverzné polia, aliasy, display rules a `sourceLinks`. | IMPLIED | Zoznam určuje smer, ale neprijíma presný dátový tvar ani bezpečnosť scale/offset modelu. |
| Symbol, rozmer, SI väzba a display rules sú budúce implementačné očakávania glossary. | IMPLIED | Symbol je bezpečný v prvej verzii; ostatné položky potrebujú samostatne stabilizovanú semantiku. |
| Presný model quantity kind neexistuje. | OPEN | Nemožno zaviesť free-text, enum ani nový identifikátor bez ďalšieho rozhodnutia. |
| Presný model dimenzie neexistuje. | OPEN | Nemožno potichu zaviesť exponenty SI báz ani nekontrolovaný dimension string. |
| Presný všeobecný konverzný model neexistuje. | OPEN | `conversionFactor` samotný nie je bezpečný všeobecný kontrakt. |
| Reálne Unit Catalog záznamy a ich zdroje neexistujú. | DEFERRED | Populácia katalógu musí byť samostatný source-reviewed míľnik. |

## 5. Unit Catalog Role

Unit Catalog je **Reference Catalog** v Engineering Knowledge Layer. Reprezentuje všeobecný alebo technicky referenčný význam používaný znalostnými tvrdeniami, ale nedefinuje interný EOS rozhodovací význam ako Property Catalog alebo Condition Type Catalog.

Označenie fázy `Knowledge Catalogs` je implementačný umbrella názov. Nemení autoritatívnu taxonómiu Unit Catalogu na `Knowledge Catalog`.

Unit Catalog Entry je špecializovaný `Catalog Entry`, teda entita s vlastnosťami aggregate rootu:

- má stabilné `id`,
- je samostatne referencovateľná a uložiteľná,
- má vlastný lifecycle a auditnú históriu,
- je nezávisle verziovaná a revidovaná,
- môže byť zdrojovo podložená,
- iné agregáty ju nevlastnia, iba referencujú.

Samotný katalóg je riadená kolekcia a governance boundary. Nemá sa modelovať ako jeden monolitický aggregate root, ktorý transakčne vlastní všetky Unit Catalog Entry aggregate roots.

## 6. UNT Identifier Semantics

`UNT-xxxxxx` identifikuje presne **jednu stabilnú Unit Catalog Entry**, ktorá nesie autoritatívny jednotkový význam.

`UNT` neidentifikuje:

- symbol alebo zobrazovací reťazec,
- fyzikálnu dimenziu,
- quantity kind,
- konverzný algoritmus,
- alias,
- jednu konkrétnu hodnotu `Quantity`.

Odporúčaný názov poľa v Unit Catalog Entry je `id`, v súlade s EOS entity convention. Polia `unitId` v `Quantity` a `ValueRange` sú referencie na toto `id`.

Alias nemá dostať samostatné `UNT`, ak je iba ďalším názvom alebo symbolom tej istej položky. Samostatné `UNT` je prípustné iba pre samostatný riadený jednotkový význam, nie kvôli pravopisu alebo prezentácii.

## 7. Identity vs Equivalence

Identita a sémantická ekvivalencia sú dve rozdielne otázky:

- identita je stabilné `UNT-xxxxxx`,
- ekvivalencia je budúca riadená sémantická väzba alebo pravidlo,
- zhodný symbol nedokazuje zhodnú identitu,
- zhodný názov nedokazuje zhodnú identitu,
- zhodné konverzné správanie samo osebe nedokazuje zhodný význam,
- dve rozdielne UNT položky môžu byť sémanticky ekvivalentné alebo prevoditeľné, ak to neskôr potvrdí autoritatívne pravidlo.

Symbol ani konverzný koeficient sa nesmie používať ako primary key alebo implicitný merge key. Prvá verzia nebude ekvivalenciu modelovať.

## 8. Candidate Field Inventory

| Candidate field | Decision | Reason |
| --- | --- | --- |
| `id` | REQUIRED NOW | Stabilná identita Catalog Entry; používa centrálny `UNT`. |
| `name` | REQUIRED NOW | Jeden kanonický, ľudsky čitateľný názov položky. |
| `symbol` | REQUIRED NOW | Kanonický zobrazovací symbol očakávaný Accepted glossary a RFC smerom. |
| `description` | OPTIONAL NOW | Stručné vysvetlenie; nesmie suplovať dimension, quantity kind alebo conversion. |
| `quantityKind` | REJECT | Nekontrolovaný text by vytvoril neautoritatívnu ontológiu. |
| `quantityKindId` | DEFER | Neexistuje schválený prefix ani Quantity Kind Catalog. |
| `dimension` | DEFER | Chýba prijatý dátový tvar a význam pre fyzikálne aj ne-fyzikálne jednotky. |
| `system` | DEFER | Jednoduché `SI`/`non-SI` je nedostatočné a Unit System Catalog neexistuje. |
| `aliases` | DEFER | Accepted architektúra ich povoľuje, ale chýba typovanie názov/symbol/kód/jazyk. |
| `sourceLinks` | REQUIRED NOW | Je súčasťou common entity metadata; pre schválený technický význam sa vyžaduje provenance. |
| `verificationStatus` | REJECT AT ROOT | Stav tvrdenia alebo väzby nie je lifecycle Catalog Entry; SourceLink má vlastný verificationStatus. |
| `status` | REQUIRED NOW | Unit Catalog Entry má plný lifecycle. |
| common entity metadata | REQUIRED NOW | Versioning, revision, timestamps, actors, provenance a audit sú autoritatívne pravidlá entity. |
| `conversion` | DEFER | Chýba všeobecný model lineárnych, afinných, nelineárnych a zložených prevodov. |
| `baseUnitId` | DEFER | Bez prijatej conversion family semantiky by bol význam nejasný. |
| `scale` | REJECT IN V1 | Scale-only model predstiera univerzálnu linearitu. |
| `offset` | REJECT IN V1 | Samostatný offset bez riadeného transformačného modelu je neúplný. |

## 9. Name Model

V prvej verzii je požadovaný jeden povinný `name`:

- je kanonický ľudsky čitateľný názov Unit Catalog Entry,
- musí byť neprázdny,
- nie je identitou a nenahrádza `id`,
- jeho globálna unikátnosť sa nemá vynucovať JSON Schema,
- rovnaký názov môže byť po katalógovom review legitímny v odlišnom kontexte, ale duplicitné názvy majú byť diagnostikované,
- lokalizované názvy a jazykové varianty sa odkladajú.

Názov je autoritatívna prezentačná vlastnosť záznamu, nie dostatočný strojový opis dimenzie alebo konverzie.

## 10. Symbol Model

V prvej verzii je požadovaný jeden povinný `symbol`:

- musí byť neprázdny,
- musí podporovať UTF-8 a Unicode,
- zachováva presný zápis a veľkosť písmen,
- nesmie sa automaticky normalizovať zmenou case alebo transliteráciou,
- nie je globálne unikátny identifikátor,
- dve položky môžu mať rovnaký symbol, ak ich autoritatívny význam nie je totožný; taká situácia musí byť katalógovo posúdená,
- JSON Schema kontroluje iba tvar reťazca, nie katalógovú unikátnosť alebo kolíziu.

Žiadny reálny symbol sa v tomto míľniku nepridáva.

## 11. Quantity Kind Decision

Posúdenie možností:

| Option | Assessment |
| --- | --- |
| A - bez quantity kind vo v1 | Odporúčané pre prvý registračný kontrakt. |
| B - free-text `quantityKind` | Odmietnuté; nekontrolovaný význam a slabá interoperabilita. |
| C - enum | Odmietnuté; vytvoril by uzavretú ontológiu bez Accepted zoznamu. |
| D - `quantityKindId` | Odložené; chýba riadený cieľ, prefix a lifecycle. |
| E - iba dimension signature | Nedostatočné; rovnaká dimenzia nemusí znamenať rovnaký quantity kind. |

`quantityKind` do v1 nepatrí. Unit Catalog v1 preto nesmie tvrdiť, že rozlišuje všetky sémantické measurable kinds. Nový Quantity Kind Catalog nie je podmienkou registračnej Unit Catalog v1, ale otázka quantity-kind identity sa musí vyriešiť pred všeobecnou automatickou kompatibilitou Property Catalogu.

## 12. Dimension Decision

Posúdenie možností:

| Option | Benefit | Risk | Decision |
| --- | --- | --- | --- |
| A - odložiť dimension | Najmenší bezpečný model bez novej ontológie | V1 nevie všeobecnú kompatibilitu | Recommended for v1 |
| B - future dimension reference | Stabilná budúca väzba | Dnes nemá cieľ ani prefix | Deferred |
| C - SI base exponents | Strojová kontrola fyzikálnych rozmerov | Predčasná algebra; nerieši quantity kind ani všetky doménové významy | Rejected for v1 |
| D - dimension signature object | Potenciálne extensible | Bez prijatého vocabulary je význam neúplný | Deferred |
| E - odvodiť z quantity kind | Znižuje duplicitu | Quantity kind model neexistuje | Deferred |

Prvá verzia nemá obsahovať `dimension`. Toto je vedomé funkčné obmedzenie, nie tvrdenie, že jednotka rozmer nemá.

Pred zavedením strojovej dimension semantiky treba rozhodnúť:

- či je dimension lokálny value object, stabilná referencia alebo odvodená vlastnosť,
- ako sa reprezentuje bezrozmernosť, count-like a ratio význam,
- ako sa odlíši dimension od quantity kind,
- ako sa riešia doménové a ne-fyzikálne jednotky,
- čo je kanonická forma a verzovanie podpisu.

Dimenzionálna algebra a kontrola zostávajú mimo Unit Catalog kontraktu a patria aplikačnej alebo Calculation Layer implementácii.

## 13. Property Catalog Dependency

Unit Catalog musí pred Property Catalogom poskytovať minimálne:

- stabilné `UNT` identity,
- autoritatívne resolvovateľné položky,
- lifecycle a použiteľnosť cieľa,
- audit a provenance,
- kanonický názov a symbol pre diagnostiku a prezentáciu.

Tento rozsah umožní budúcemu Property Catalogu bezpečne odkazovať na explicitne povolené UNT identity. Takýto allow-list prístup je bezpečný most, ale jeho presný Property Catalog field model nie je predmetom tohto review.

Pre všeobecnú kompatibilitu podľa dimenzie alebo quantity kind tento model nestačí. Predtým, než Property Catalog začne tvrdiť dimenzionálnu kompatibilitu, musí byť prijatá jedna z možností:

- riadený dimension/quantity-kind model,
- alebo explicitná množina povolených UNT položiek bez inferencie ekvivalencie.

Property Catalog nesmie odvodiť kompatibilitu zo symbolu, názvu alebo neštruktúrovaného description.

## 14. Conversion Boundary

Unit Catalog môže v budúcnosti deklarovať riadené konverzné vzťahy. **Calculation Layer** vykonáva konverziu, normalizáciu a výpočty.

Do v1 nepatria:

- `conversion`,
- `baseUnitId`,
- `scale`,
- `offset`,
- `conversionFactor`,
- `conversionOffset`,
- konverzný výraz alebo spustiteľný kód.

Jednoduchý `conversionFactor` je nebezpečný, pretože nevie všeobecne opísať afinné, offsetové, nelineárne, logaritmické ani zložené jednotky. Dvojica scale/offset síce pokryje časť afinných transformácií, ale nevytvára bezpečný všeobecný model a bez conversion family nevie určiť platný cieľ.

Budúci deklaratívny model musí byť typovaný, zdrojovaný, verziovaný a oddelený od vykonávacieho algoritmu. Unit Catalog nesmie obsahovať spustiteľný výraz bez samostatného bezpečnostného a governance rozhodnutia.

## 15. SI / Non-SI Support

Prvá verzia je systémovo neutrálna:

- nepredpokladá SI ani metric-only svet,
- nepredpokladá lineárnu prevoditeľnosť,
- povoľuje identitu fyzikálnej, bezrozmernej, count-like, ratio alebo doménovej jednotky,
- neposudzuje, či je jednotka base, derived, accepted non-SI, imperial alebo domain-specific,
- nepoužíva `isSI`, pretože boolean nevie vyjadriť členstvo, väzbu, hybridný pôvod ani autoritatívny systém,
- nepoužíva voľný `system` reťazec.

SI väzba, Unit System Catalog a display policy sú odložené. Ich absencia nebráni registrácii identity, ale bráni automatickému systémovému triedeniu a konverzii.

## 16. Source Traceability

`sourceLinks` je povinné pole spoločných entity metadata:

- v `Draft` môže byť prázdne,
- pri `Review` alebo `Approved` Unit Catalog Entry musí obsahovať aspoň jeden relevantný zdroj, pretože definícia jednotky je overiteľný technický alebo referenčný význam,
- externá normatívna definícia sa odkazuje cez existujúce SourceReference/SourceLink pravidlá,
- interne definovaná EOS jednotka bez externého normatívneho zdroja musí mať dohľadateľný interný governance alebo technický zdroj; interný pôvod neznamená absenciu provenance,
- `sourceLinks` sa nesmie duplikovať ani nahrádzať vlastným citation poľom.

Provenance odpovedá na otázku, z čoho význam pochádza. Catalog lifecycle odpovedá na otázku, v akom stave je záznam. Tieto osi sa nesmú zamieňať.

## 17. Lifecycle

Unit Catalog Entry má nezávislý plný record lifecycle. Prvá verzia používa existujúce `status` hodnoty:

- `Draft`,
- `Review`,
- `Approved`,
- `Deprecated`,
- `Archived`.

Nevytvára sa nový stav `Active`. Použiteľnosť Approved, Deprecated alebo Archived položky musí neskôr interpretovať catalog-aware validačná vrstva.

Rozlíšenie osí:

- `status` je lifecycle celej položky,
- `verificationStatus` v SourceLink je stav overenia konkrétnej zdrojovej väzby,
- `schemaVersion` je verzia kontraktu,
- `recordVersion` je významová verzia položky,
- `revision` je menšia oprava bez zmeny významu.

Schválená položka sa nemaže. Pri deprecation zostáva historicky resolvovateľná a môže uvádzať `replacedBy`; náhrada musí byť v budúcej Unit Catalog schéme obmedzená na platné UNT ID.

## 18. Catalog Entry Base

Repozitár má `schemas/common/metadata.schema.json`, ale nemá samostatný composable Catalog Entry base. Existujúci metadata kontrakt je uzavretý cez `additionalProperties: false`, preto ho nemožno bez návrhu kompozície jednoducho rozšíriť cez `allOf` o `name` a `symbol`.

Odporúčanie je **A - pri prvej katalógovej implementácii zaviesť úzky spoločný Catalog Entry base**, ale iba pre už prijaté spoločné entity polia a lifecycle. Base nesmie zavádzať quantity kind, dimension, conversion ani governance rozdiely Reference/Knowledge Catalogu.

Ak sa bezpečná kompozícia nedá zaviesť bez zmeny existujúceho metadata kontraktu, Unit Catalog v1 môže zostať standalone schémou s rovnakými poľami. Duplicitné ručné definície pre všetky štyri budúce katalógy však nie sú odporúčané.

Výber techniky JSON Schema kompozície je implementačná podmienka, nie nový doménový význam a nevyžaduje zmenu Accepted RFC.

## 19. Alias Model

Accepted architektúra aliasy povoľuje ako neautoritatívne lookup hodnoty, ale ich presný model nie je definovaný. Jednoduché `aliases: [string]` by zmiešalo:

- alternatívne názvy,
- alternatívne symboly,
- lokalizované názvy,
- legacy označenia,
- externé kódy.

Aliasy sa preto vo v1 odkladajú. Keď vzniknú, musia byť typované, musia zachovať pôvodný zápis a prípadný jazyk/systém a musia mať catalog-aware collision policy. Alias nikdy nemení identitu a nesmie byť autoritatívnym join key.

## 20. Description / Notes

`description` je vo v1 voliteľné stručné vysvetlenie položky. Spoločné metadata môžu zachovať voliteľné `notes`.

Ani jedno pole nesmie byť použité na uloženie:

- strojovej dimenzie,
- quantity kind identifikátora,
- konverzného faktora alebo algoritmu,
- zoznamu aliasov,
- lifecycle alebo verification stavu,
- zdrojovej citácie.

Ak sa sémantika vyžaduje pre validáciu alebo výpočet, musí neskôr dostať štruktúrované pole. Prose zostáva vysvetľujúce, nie výpočtovo autoritatívne.

## 21. Candidate Models

### Candidate A

`id`, `name`, `symbol`, `sourceLinks`.

- Correctness: správne zachytáva identitu, názov, symbol a provenance.
- Minimality: vysoká.
- Property Catalog compatibility: umožní explicitné UNT referencie, nie dimension inference.
- Conversion compatibility: neutrálna, neblokuje budúci typovaný model.
- Migration cost: nízky až stredný pri doplnení dimension/quantity kind.
- Risk: bez common metadata porušuje lifecycle a audit požiadavky.

Verdict: dobré doménové jadro, ale neúplná entity obálka.

### Candidate B

Candidate A + `quantityKindId`.

- Correctness: cieľ referencie nie je definovaný.
- Minimality: zdanlivá; vytvára nový katalógový dependency edge.
- Property Catalog compatibility: potenciálne dobrá až po stabilizácii quantity kind.
- Migration cost: vysoký, ak sa zvolí nesprávna identita.
- Risk: neexistujúci prefix, lifecycle a resolver.

Verdict: nevhodné pre v1.

### Candidate C

Candidate A + `dimension`.

- Correctness: závisí od chýbajúcej definície dimension.
- Minimality: stredná.
- Property Catalog compatibility: dobrá iba pri správne prijatej semantike.
- Conversion compatibility: dimension sama konverziu nedefinuje.
- Migration cost: vysoký pri zmene reprezentácie.
- Risk: predčasná SI ontológia alebo nekontrolovaný string.

Verdict: odložiť.

### Candidate D

Candidate C + `conversion`.

- Correctness: dnes nedosiahnuteľná bez nového kontraktu.
- Minimality: nízka.
- Property Catalog compatibility: mieša kompatibilitu a execution concerns.
- Conversion compatibility: scale-only model je neúplný.
- Migration cost: veľmi vysoký.
- Risk: falošné alebo nesprávne prevody.

Verdict: odmietnuť pre v1.

### Candidate E - Recommended

Candidate A doplnený o existujúce spoločné entity metadata a voliteľné vysvetľujúce polia:

```json
{
  "id": "UNT-xxxxxx",
  "schemaVersion": "<schema version>",
  "recordVersion": "<record version>",
  "revision": 0,
  "status": "Draft",
  "createdAt": "<RFC3339 timestamp>",
  "createdBy": "<actor reference>",
  "updatedAt": "<RFC3339 timestamp>",
  "updatedBy": "<actor reference>",
  "sourceLinks": [],
  "changeSummary": "<change summary>",
  "name": "<canonical name>",
  "symbol": "<canonical symbol>",
  "description": "<optional explanation>"
}
```

Príklad je iba tvarový placeholder, nie katalógový záznam ani reálna jednotka.

- Correctness: zachováva Catalog Entry identitu, lifecycle, audit a provenance.
- Minimality: obsahuje iba prijaté entity polia a bezpečné prezentačné jadro.
- Property Catalog compatibility: umožní explicitné UNT referencie a lifecycle kontrolu.
- Conversion compatibility: neuzamyká budúci typovaný model.
- Migration cost: vyžaduje budúce versioned rozšírenie pre dimension/quantity kind/conversion.
- Risk: používatelia môžu očakávať kompatibilitu, ktorú v1 neposkytuje; dokumentácia a validácia to musia jasne odmietnuť.

## 22. Recommended Minimal Model

Odporúča sa Candidate E ako **Unit Catalog Registry v1**:

- jedna Unit Catalog Entry je samostatný Catalog Entry aggregate root,
- `id` používa `UNT-xxxxxx`,
- povinné sú spoločné entity metadata, `name` a `symbol`,
- `description`, `notes`, `replaces` a `replacedBy` sú voliteľné vysvetľujúce alebo lifecycle doplnky,
- `sourceLinks` je povinné pole; pre Review/Approved technický význam nesmie byť prázdne,
- quantity kind, dimension, system, aliases a conversion sa nezapisujú ani neodhadujú.

Názov „Registry v1“ opisuje funkčný profil, nie nový EOS objekt. Autoritatívny objekt zostáva `Unit Catalog Entry`.

Kontrakt dá `UNT` autoritatívnu identitu, lifecycle, názov, symbol a provenance. Nedáva mu ešte strojovo vykonateľnú dimenzionálnu alebo konverznú semantiku.

## 23. Field Requirement Matrix

| Field | Classification | Reason |
| --- | --- | --- |
| `id` | REQUIRED | Stabilné `UNT-xxxxxx`; identita Unit Catalog Entry. |
| `schemaVersion` | REQUIRED | Verzia serializačného kontraktu. |
| `recordVersion` | REQUIRED | Významová verzia konkrétnej položky. |
| `revision` | REQUIRED | Menšia oprava v rámci recordVersion. |
| `status` | REQUIRED | Plný Catalog Entry lifecycle. |
| `createdAt` | REQUIRED | Audit vytvorenia. |
| `createdBy` | REQUIRED | Audit autora/aktéra. |
| `updatedAt` | REQUIRED | Audit poslednej zmeny. |
| `updatedBy` | REQUIRED | Audit posledného aktéra. |
| `sourceLinks` | REQUIRED | Provenance; môže byť prázdne iba v povolenom Draft kontexte. |
| `changeSummary` | REQUIRED | Audit významu zmeny. |
| `name` | REQUIRED | Jeden kanonický ľudský názov. |
| `symbol` | REQUIRED | Jeden kanonický symbol; nie identita ani globálne unique key. |
| `description` | OPTIONAL | Vysvetlenie bez strojovej semantiky. |
| `notes` | OPTIONAL | Lokálna poznámka common metadata; nie sémantický fallback. |
| `replaces` | OPTIONAL | Existujúca metadata väzba; ak smeruje na jednotku, musí byť UNT. |
| `replacedBy` | CONDITIONAL | Odporúčaná náhrada deprecated položky, ak existuje; musí smerovať na UNT. |
| `quantityKind` | REJECTED | Nekontrolovaný free text. |
| `quantityKindId` | DEFERRED | Neexistuje riadený cieľ ani prefix. |
| `dimension` | DEFERRED | Chýba prijatý model. |
| `system` | DEFERRED | Chýba typovaný Unit System model. |
| `aliases` | DEFERRED | Chýba typovaný alias a collision model. |
| root `verificationStatus` | REJECTED | Catalog lifecycle nie je claim verification. |
| `conversion` | DEFERRED | Chýba všeobecný deklaratívny kontrakt. |
| `baseUnitId` | DEFERRED | Chýba conversion family semantika. |
| `scale` | REJECTED | Neúplný lineárny predpoklad. |
| `offset` | REJECTED | Neúplný samostatný transformačný parameter. |

## 24. Validation Responsibility

### JSON Schema

- uzavretá štruktúra a zákaz neznámych polí,
- povinnosť common metadata, `name`, `symbol` a `sourceLinks`,
- `id` cez centrálny UNT `$ref`,
- typy, neprázdne texty, version formáty a timestamp formáty,
- lifecycle enum cez existujúci RecordStatus,
- tvar vnorených SourceLink,
- UNT formát `replaces`/`replacedBy`, ak ich Unit kontrakt povolí.

### EOS application validation

- povinnosť neprázdnych `sourceLinks` pri Review/Approved technickom význame,
- timestamp a version/revision pravidlá, ktoré presahujú štruktúru,
- povolené lifecycle transitions,
- zákaz tichej zmeny významu bez recordVersion.

### Catalog validation

- diagnostika duplicitných názvov a symbolov,
- budúca alias collision policy,
- samoreferencia alebo cyklus replacement väzieb,
- použiteľnosť podľa lifecycle,
- budúca semantic equivalence policy,
- kanonickosť záznamu v rámci katalógu.

### Reference integrity

- existencia cieľa `Quantity.unitId` a `ValueRange.unitId`,
- existencia `replaces`/`replacedBy`,
- neskôr existencia `baseUnitId`, ak bude prijatý,
- zákaz interpretovať platný UNT formát ako dôkaz existencie.

### Property Catalog validation

- či Property Catalog Entry povoľuje konkrétny UNT,
- budúca quantity-kind a dimension kompatibilita,
- zákaz odvodenia kompatibility iba zo symbolu alebo názvu.

### Calculation Layer

- vykonanie konverzie,
- normalizácia hodnoty,
- dimenzionálne výpočty,
- spracovanie afinných, nelineárnych, logaritmických alebo zložených transformácií podľa budúceho prijatého modelu.

### Governance

- pridelenie UNT,
- schválenie, deprecation, supersession a archivácia,
- rozhodnutie o autoritatívnom zdroji,
- schválenie budúceho dimension, quantity kind, alias a conversion modelu.

## 25. Real Data Boundary

Unit Catalog Contract definuje štruktúru a pravidlá. Unit Catalog Population vytvára jednotlivé autoritatívne technické záznamy.

Tento review:

- nevytvára žiadnu reálnu jednotku,
- nepriraďuje žiadny reálny symbol k UNT,
- nevkladá normatívnu definíciu, faktor, offset ani dimenziu,
- nevytvára fiktívny JSON fixture, ktorý by mohol byť považovaný za katalógový obsah,
- nepovoľuje použitie README alebo príkladu ako autoritatívneho datasetu.

Populácia Unit Catalogu vyžaduje samostatný source-reviewed míľnik, kontrolu práv na použitie zdrojov a explicitné schválenie každého autoritatívneho významu.

## 26. Future Catalog Dependencies

Unit Catalog Registry v1 nepotrebuje pred implementáciou:

- Quantity Kind Catalog,
- Dimension Catalog,
- Unit System Catalog,
- Property Catalog.

Tým sa zachová acyklický minimálny graf. Quantity a ValueRange referencujú Unit Catalog Entry; Unit Catalog v1 ich nereferencuje späť.

Budúca generalizovaná kompatibilita môže potrebovať quantity-kind alebo dimension semantic layer, ale samostatný katalóg nie je automaticky jediným riešením. Najprv treba samostatným pre-design review rozhodnúť, či bude význam value object, catalog reference alebo riadený podpis.

Property Catalog môže po Unit Catalog v1 bezpečne začať iba vtedy, ak jeho prvá verzia používa explicitné UNT referencie alebo dovtedy vznikne prijatý dimension/quantity-kind model. Nemôže predstierať všeobecnú kompatibilitu z názvu či symbolu.

## 27. Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Zámena identity a symbolu | High | Vždy používať UNT ako jedinú stabilnú identitu. |
| Predpoklad globálnej unikátnosti symbolu | High | Unikátnosť nevynucovať schémou; kolízie posudzovať katalógovo. |
| `conversionFactor` ako univerzálny model | Critical if implemented | Vo v1 odmietnuť; neskôr prijať typovaný deklaratívny model. |
| Predčasné SI exponenty | High | Dimension vo v1 odložiť a nevytvárať algebra engine. |
| Free-text quantity kind | High | Pole odmietnuť bez riadeného vocabulary alebo identity. |
| Aliasy vytvárajú duplicitnú semantiku | Medium | Odložiť a neskôr typovať alias plus collision policy. |
| Nejasný interný verzus externý pôvod | High | Review/Approved význam vždy viazať na SourceLink vrátane interného governance zdroja. |
| Duplicitný lifecycle a verificationStatus | Medium | Root používa status; verificationStatus zostáva na tvrdení alebo SourceLink. |
| Property Catalog odvodí kompatibilitu z textu | High | Použiť explicitné UNT allow-listy alebo prijatý semantic model. |
| Ekvivalentné jednotky sa zlúčia podľa faktora | High | Ekvivalenciu držať ako samostatné budúce pravidlo, nie identity merge. |
| V1 sa bude vydávať za plný unit model | High | Dokumentovať profil Registry v1 a explicitne odmietnuť conversion/dimension capability. |
| Metadata base sa nevhodne skomponuje s uzavretou schémou | Medium | Pred implementáciou zvoliť testovanú Draft 2020-12 composition strategy. |

## 28. Deferred Concepts

Odložené sú:

- quantity kind identity a vocabulary,
- dimension representation a algebra,
- SI base alebo canonical unit väzba,
- Unit System model,
- deklaratívny conversion contract,
- conversion execution,
- semantic equivalence a conversion families,
- typované aliases a localization,
- display rules a display unit policy,
- reálne UNT položky a zdrojové dataset-y,
- Property Catalog compatibility model nad rámec explicitných UNT referencií,
- dimenzionálna kompatibilita v Condition, PropertyRecord a Observation.

Odloženie znamená neprítomnosť capability. Neznamená povolenie ukladať tieto významy do `description` alebo `notes`.

## 29. Implementation Preconditions

Pred implementáciou Unit Catalog schémy musia byť splnené presne tieto podmienky:

1. Implementácia musí zachovať Unit Catalog ako Reference Catalog a Unit Catalog Entry ako samostatný Catalog Entry aggregate root.
2. Schéma musí používať `id` s centrálnym UNT `$ref` a existujúce common entity metadata/lifecycle významy.
3. Musí byť zvolená bezpečná Draft 2020-12 kompozícia Catalog Entry base alebo zdokumentovaný standalone fallback bez zmeny významu.
4. `name` a `symbol` musia byť povinné, neprázdne a nesmú byť identitou ani globálnym unique key.
5. `sourceLinks` musí byť povinné pole; Review/Approved položka musí mať relevantnú provenance.
6. quantity kind, dimension, system, aliases, conversion, baseUnitId, scale a offset musia zostať mimo v1.
7. Dokumentácia a testy musia uvádzať, že v1 rieši resolvovateľnú identitu a lifecycle, nie kompatibilitu alebo konverziu.
8. Fixtures musia byť výlučne fiktívne a nesmú zaviesť reálnu jednotku.

Tieto podmienky nevyžadujú zmenu Accepted RFC alebo ADR.

## 30. Readiness Verdict

Unit Catalog môže byť implementovaný ako úzky registračný kontrakt s identitou, lifecycle, auditom, názvom, symbolom a provenance. Accepted architektúra tento profil podporuje a nevyžaduje nový prefix ani zmenu objektovej taxonómie.

Implementácia však musí zachovať explicitné obmedzenia: v1 nie je dimension model, quantity-kind model ani conversion model. Pred Property Catalog dimension-based kompatibilitou bude potrebné samostatne prijať semantic representation alebo použiť explicitné UNT referencie bez inferencie.

Výsledok je `READY WITH CONDITIONS`. Implementácia Unit Catalog v1 môže začať po splnení ôsmich podmienok v sekcii 29; nemusí čakať na Quantity Kind Catalog, Dimension Catalog ani conversion engine.

## 31. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-09-09 | 0.1 | 0 | Codex | Initial pre-design review of Unit Catalog identity, lifecycle, provenance, semantic boundaries, Property Catalog dependency and implementation readiness. |

READY WITH CONDITIONS
