# CDR-0007 Observation Pre-design Review

Project: EOS – Engineering Operating System  
Contract Review ID: CDR-0007  
Contract: Observation  
Review type: Pre-design  
Version: 0.1  
Revision: 2  
Status: Review  
Document basis: Accepted EOS architecture

## 1. Purpose

Posúdiť najmenší bezpečný kontrakt `Observation` pred implementáciou a presne oddeliť prijaté architektonické pravidlá od otvorených serializačných a významových otázok. Review má zabrániť tomu, aby sa dôkaz zamenil s tvrdením, aby sa first-class entita stala vnoreným záznamom alebo aby schéma predčasne zaviedla všeobecnú referenčnú či payload architektúru.

Výstup neimplementuje `Observation`. Určuje, či je možné začať `Phase 0.2B.1.7` bez nového architektonického rozhodnutia alebo chýbajúceho core kontraktu.

Revision 1 uzatvára dva blockery z Revision 0 cez RFC-0001 Revision 5. Pri rozdiele medzi pôvodným pre-design posúdením a closure rozhodnutím má prednosť §24 a §25 tejto revízie.

## 2. Scope

Review pokrýva typ objektu, identitu, aggregate boundary, scope, pozorovaný subjekt, dôkazový obsah, čas, zdroje, verifikáciu, nemennosť, korekcie a hranice voči `PropertyRecord`, `MeasurementQuality`, `Condition`, `Decision` a budúcemu `Job`.

Preskúmané vstupy:

- `AGENTS.md`, `EOS-003`, `EOS-009` a `EOS-010`.
- Accepted RFC-0001, RFC-0002 a RFC-0003.
- Accepted ADR-0015 a ADR-0016.
- CDR-0001 až CDR-0006.
- Implementované kontrakty Quantity, ValueRange, MeasurementQuality, Condition, Classification a PropertyRecord.
- Spoločné kontrakty identifikátorov, lifecycle, metadát a SourceLink; SourceReference, index schém, validačná vrstva a testy.
- `CHANGELOG.md`, `ROADMAP.md` a `BACKLOG.md` iba ako kontext, bez zmien.

Pre-flight dňa 2026-09-08: vetva `feature/phase-0.2b-knowledge-contracts`, HEAD `a92a5405f934ce5cc5d6b328cc7886d306bfc609`, čistý pracovný strom. RFC-0001 až RFC-0003 a ADR-0014 až ADR-0016 zostávajú Accepted. Existuje šesť Knowledge Core schém a žiadna Observation schéma. Všetkých 105 existujúcich testov prešlo. Phase 0.2B.2 nezačala.

## 3. Authoritative Findings

`AUTHORITATIVE` označuje explicitné prijaté pravidlo. `IMPLIED` označuje silný dôsledok prijatých pravidiel, ktorý ešte nie je samostatne normatívne formulovaný. `OPEN` označuje nerozhodnutý detail. `DEFERRED` označuje vedome odloženú schopnosť.

| Oblasť | Klasifikácia | Zistenie |
| --- | --- | --- |
| Typ objektu | AUTHORITATIVE | Observation je first-class evidence entity, nie Value Object, Claim, Decision, Derived Result ani workflow event; ADR-0016. |
| Aggregate root | AUTHORITATIVE | RFC-0002 §6 odporúča a jeho aggregate príklad potvrdzuje samostatnú Observation aggregate root; iný aggregate ju nesmie vlastniť ako vnorený objekt. |
| Identita | AUTHORITATIVE | Má stabilné globálne `OBS-xxxxxx`; EOS-003 má prefix Active. |
| Názov ID poľa | AUTHORITATIVE | RFC-0001 navrhuje `id`; spoločné entity používajú `id`. `observationId` je názov referencie z iného objektu, nie vlastného ID. |
| Samostatnosť | AUTHORITATIVE | Má samostatnú existenciu, lifecycle, audit a môže byť referencovaná viacerými tvrdeniami alebo rozhodnutiami. |
| Dôkazový význam | AUTHORITATIVE | Predstavuje pravdu o tom, čo bolo pozorované, nie automaticky pravdu o svete. |
| Scope | AUTHORITATIVE | `observationScope` je povinný koncept; hodnoty sú `GLOBAL`, `JOB`, `PROJECT`, `EXPERIMENT`. |
| Scope referencia | AUTHORITATIVE | Počiatočný profil používa `scopeReferenceId`: GLOBAL ho zakazuje, JOB ho vyžaduje vo formáte `JOB-yyyy-xxxx`; PROJECT a EXPERIMENT zostávajú mimo profilu. RFC-0001 Revision 5. |
| Pozorovaný subjekt | AUTHORITATIVE | RFC-0002 vyžaduje, aby Observation meraný alebo pozorovaný objekt iba referencovala. |
| Tvar subjektu | AUTHORITATIVE | Počiatočný profil vyžaduje jeden `subjectId` obmedzený na schválené doménové ID formáty. Prefix je discriminator; `subjectType` sa neukladá. RFC-0001 Revision 5. |
| Dôkazový payload | AUTHORITATIVE | Observation môže vlastniť hodnotu pozorovania a používať Quantity, ValueRange, MeasurementQuality a Condition. |
| Presný payload union | AUTHORITATIVE | Počiatočný profil vyžaduje `propertyId`, `valueType` a presne jednu zhodnú vetvu Quantity alebo ValueRange. Je to atomický property-measurement profil, nie všeobecný Observation payload. RFC-0001 Revision 5. |
| PropertyRecord | AUTHORITATIVE | Observation je oddelená od PropertyRecord a nesmie ho automaticky vytvoriť, zmeniť ani povýšiť. |
| Evidence relationship | DEFERRED | Presná persistovaná väzba Observation ↔ Claim/PropertyRecord je odložená; kardinalita je mnoho-na-mnoho. |
| MeasurementQuality | AUTHORITATIVE | Môže byť value objectom Observation; opisuje kvalitu konkrétneho meraného alebo reportovaného výsledku. |
| Conditions | AUTHORITATIVE | Observation môže vlastniť podmienky kontextu alebo platnosti cez Condition. |
| Čas | AUTHORITATIVE | Observation je event-like záznam v čase; RFC-0001 navrhuje `observedAt`. |
| Presné timestamp pravidlá | AUTHORITATIVE | `observedAt` je doménový čas pozorovania, `createdAt` čas vytvorenia EOS záznamu; `recordedAt` sa nepridáva. RFC-0001 Revision 5. |
| Zdroje | AUTHORITATIVE | Observation je source-backed evidence, musí mať dohľadateľný zdroj alebo zdrojový kontext a SourceReference používa cez SourceLink. |
| Neprázdnosť zdrojov | AUTHORITATIVE | Pri overiteľnej Observation v stave Review alebo Approved musia byť zdroje prítomné; Draft môže podliehať všeobecnému pravidlu prázdnych `sourceLinks`. |
| Verifikácia | AUTHORITATIVE | Počiatočný profil nemá `verificationStatus`. `status` je lifecycle zrelosť, nie potvrdenie pravdivosti claim; evidence-specific verification zostáva deferred. RFC-0001 Revision 5. |
| Nemennosť | AUTHORITATIVE | Dôkazový obsah sa po vzniku nesmie ticho prepisovať; nový výsledok je nová Observation. |
| Oprava metadát | AUTHORITATIVE | Neúmyselná technická oprava musí byť auditovaná cez revision, changeSummary alebo ekvivalent a nesmie meniť pôvodný dôkazový význam. |
| Korekčný lifecycle | DEFERRED | Presný superseded/disputed/replaced model je výslovne odložený v ADR-0016. |
| Decision | AUTHORITATIVE | Observation sama nerozhoduje. Prijatie alebo povýšenie významu vyžaduje Decision alebo ekvivalentný schválený governance mechanizmus. |
| Stored Decision | DEFERRED | Samostatný Decision kontrakt nie je podmienkou uloženia dôkazu v 0.2B.1. |
| Derived Result | AUTHORITATIVE | Odvodený výstup nie je Observation a nesmie byť uložený ako zdrojové pozorovanie. |

## 4. Open Questions

Closure vyriešilo blocker počiatočného kontraktu obmedzením na jeden property-measurement výsledok jedného už identifikovaného EOS subjektu. Otvorené, ale neblokujúce otázky sú:

1. Aký typed result model pokryje budúce vizuálne zistenie, fotografiu, kontrolu a výstup nástroja?
2. Ako sa reprezentuje subjekt bez EOS identity, napríklad ešte neregistrovaná fyzická vzorka?
3. Aké identifikátory budú mať Project a Experiment?
4. Ako sa Observation viaže na konkrétnu historickú inštanciu embedded PropertyRecord?
5. Aký bude evidence-specific verification a korekčný lifecycle?
6. Bude fotografia payloadom, SourceReference, DocumentRecord alebo budúcim attachment objektom?

Tieto otázky sú mimo uzavretého počiatočného profilu. Nesmú sa riešiť voľným textom, fiktívnym ID ani ľubovoľným JSON payloadom.

## 5. Entity / Aggregate Assessment

Observation je `Entity` aj `Aggregate Root`. Má stabilnú identitu, vlastný lifecycle, samostatné uloženie, audit a referencie z viacerých objektov. V tomto prípade aggregate-root postavenie nie je automatický dôsledok samotného ID: vyplýva aj z explicitného odporúčania RFC-0002, aggregate boundary príkladu v RFC-0003 a zákazu vnoreného vlastníctva v ADR-0016.

Nie je embedded entity ani Value Object. `Job`, `Material`, `Machine` či iný aggregate môže uchovávať jej ID, nie celý first-class Observation objekt. Samostatne pomenovaný job-local observation-like záznam bez OBS identity môže byť embedded, ale nie je týmto kontraktom.

Praktická nemennosť znamená nemeniť dôkazový payload po zachytení. Draft editácia pred vznikom dôkazového záznamu a auditovaná technická oprava metadát nie sú ekvivalentom prepísania pozorovania.

## 6. OBS Identifier Semantics

`OBS-xxxxxx` identifikuje jednu first-class Observation inštanciu. Odporúčaný vlastný názov poľa je `id`, pretože:

- je to prijatý návrh RFC-0001,
- zodpovedá spoločným EOS entity metadátam,
- `observationId` má zostať názvom cudzieho kľúča alebo referencie na Observation,
- nevytvára paralelnú identitu v tom istom objekte.

Budúca schéma musí doplniť OBS do centrálnej definície identifikátorov podľa už prijatého EOS-003; nejde o nový prefix ani o governance zmenu.

## 7. Observation Scope Model

`observationScope` je povinné. Konceptuálne hodnoty zostávajú presne `GLOBAL`, `JOB`, `PROJECT`, `EXPERIMENT`; počiatočný profil implementuje iba `GLOBAL` a `JOB`. Scope vyjadruje kontext interpretácie, nie identitu subjektu.

Posúdenie kandidátov:

| Kandidát | Posúdenie |
| --- | --- |
| A: iba `observationScope` | Štrukturálne minimálny, ale pre JOB/PROJECT/EXPERIMENT neposkytuje konkrétny auditovateľný kontext. |
| B: `observationScope` + `scopeReferenceId` | Najčistejší všeobecný tvar, ale typ a formát referencie nie sú pre PROJECT a EXPERIMENT riadené. |
| C: samostatné `jobId`, `projectId`, `experimentId` | Typovo zrozumiteľný, ale predčasne zmrazuje tri polia a dve neexistujúce identity. |
| D: typovaná reference value object | Rozšíriteľná, ale zaviedla by nový všeobecný reference kontrakt bez Accepted rozhodnutia. |

Vybraný je model B. `GLOBAL` zakazuje `scopeReferenceId`; `JOB` ho vyžaduje vo formáte `JOB-yyyy-xxxx`. PROJECT a EXPERIMENT sa v počiatočnej schéme odmietnu, kým nebudú mať governance schválené ID. Budúce rozšírenie rovnakého poľa je aditívne. Scope referencia a `subjectId` majú rozdielny význam.

## 8. Subject / Target Model

First-class Observation nemá spoliehať na containment, pretože ju nevlastní pozorovaný aggregate. Každá použiteľná Observation musí jednoznačne povedať, čo bolo pozorované. Scope a subject sú rôzne osi: napríklad JOB scope môže obsahovať meranie materiálu, stroja alebo výrobku.

Posúdenie:

- Model A bez subject poľa je nedostatočný pre samostatne uložený dôkaz.
- Samotné `subjectId` je najmenší cieľový tvar, ak prefix jednoznačne určuje typ a cieľ už má EOS identitu.
- `subjectType` + `subjectId` duplikuje typ zakódovaný v mnohých ID a môže sa rozísť.
- Všeobecný `targetReference` by bez spoločného kontraktu vytvoril neriadenú graph edge.
- Navrhnuté `relatedEntityIds` nehovorí, ktorý objekt je predmetom a ktorý iba súvisí s kontextom.

Vybraný je jeden povinný koreňový `subjectId`. Nie je to unrestricted string: musí zodpovedať jednej z centrálnych definícií `MAT`, `POL`, `TEC`, `MAC`, `TOOL`, `SUP`, `JOB` alebo `JOB_OPERATION`. Prefix poskytuje object-type discrimination, preto sa `subjectType` nepridáva. Existencia a použiteľnosť cieľa sa kontroluje aplikačne; samotný pattern nie je referenčná integrita.

Observation subjekt iba referencuje a nikdy ho nevlastní. Objekt bez pridelenej EOS identity nie je podporovaný počiatočným profilom. Jeden záznam má jeden subjekt; viac subjektov znamená viac Observation záznamov.

## 9. Observed Content Model

### Posúdenie možností

- Jeden embedded `PropertyRecord` sa odmieta. PropertyRecord je claim-like objekt s vlastným verificationStatus a zdrojmi; jeho vnorenie by zamiešalo dôkaz a tvrdenie a duplikovalo provenance.
- Pole PropertyRecord sa odmieta z rovnakého dôvodu a navyše by nebolo jasné, či ide o viac dôkazov alebo viac interpretovaných tvrdení.
- Samotná Quantity alebo ValueRange nestačí, pretože bez `propertyId` nehovorí, čo číslo znamená.
- Priamy `propertyId` + jedna hodnotová vetva zodpovedá návrhu RFC-0001 a môže bezpečne reprezentovať jednoduché property measurement evidence.
- Typed payload je potrebný pre všeobecnú Observation, ktorá má pokryť aj textové, obrazové, kontrolné a nástrojové výsledky.
- Evidence-only obálka bez výsledku je citácia udalosti, nie úplný dôkazový záznam o tom, čo bolo zistené.

Počiatočný profil je autoritatívne obmedzený na priamy číselný property result: povinné `propertyId`, `valueType` a presne jedna vetva `quantity` alebo `valueRange`, ktorá zodpovedá discriminatoru. Observation neobsahuje PropertyRecord. Jeden záznam nesie jeden výsledok.

Všeobecný ObservationResult alebo ObservedValue kontrakt nevzniká. Budúce nečíselné a artifact typy vyžadujú samostatné typed rozšírenie a nesmú používať arbitrary payload.

## 10. MeasurementQuality Placement

MeasurementQuality patrí k meranému alebo reportovanému výsledku, nie ku všeobecnej obálke Observation bez väzby na výsledok. Pri plochom jednom-výsledkovom profile môže byť priamo v Observation, pretože jeho kontext je jednoznačný. Pri budúcom poli výsledkov musí byť vnorená v každom konkrétnom výsledku.

MeasurementQuality môže zostať aj v PropertyRecord s odlišnou semantikou: tam opisuje kvalitu reportovanej claim hodnoty. Rovnaký objekt sa nesmie bez pravidla kopírovať z Observation do PropertyRecord; Decision alebo governance mechanizmus musí určiť, čo sa prenáša. Duplicita nie je synchronizácia a obe inštancie patria svojim rodičom.

## 11. Conditions Placement

Observation môže obsahovať `conditions` ako pole existujúcich Condition value objects. V počiatočnom jednom-výsledkovom profile sa vzťahujú na okolnosti Observation aj jej jediného výsledku. Ak budú mať jednotlivé výsledky rozdielne podmienky, podmienky musia prejsť k výsledku a model potrebuje explicitný payload kontrakt.

Pole môže byť vynechané alebo prázdne. Poradie nemá mať význam. Duplicity, rozpory a kompatibilita zostávajú aplikačnou a katalógovou validáciou; review nezavádza implicitný AND/OR engine.

## 12. Timestamp Model

Najmenší auditovateľný model vyžaduje:

- `observedAt`: kedy sa pozorovanie alebo zachytenie dôkazu uskutočnilo,
- `createdAt`: kedy bol entity záznam vytvorený v EOS, ako súčasť spoločných metadát.

Oba údaje sú potrebné a nemusia byť rovnaké; historické pozorovanie možno zaevidovať neskôr. `recordedAt` by bez samostatného významu duplikovalo `createdAt`. `effectiveAt`, `validFrom` a `validUntil` sa do minimálneho modelu nepridávajú; platnosť patrí do Conditions alebo budúceho špecializovaného modelu.

Timestamp má byť validný RFC 3339 `date-time` s časovou zónou. Accepted vstupy neurčujú, či sa má pôvodný offset uchovať alebo normalizovať na UTC; schéma nemá túto politiku predstierať.

## 13. Source / Evidence Model

Observation je evidence objekt, ale aj evidencia musí mať pôvod. `sourceLinks` má byť povinné pole spoločných entity metadát. V Draft môže byť prázdne; Review alebo Approved Observation s overiteľným obsahom musí mať aspoň jeden použiteľný SourceLink podľa existujúceho lifecycle pravidla.

Typické mapovanie bez zavádzania nových entít:

- senzorový alebo strojový výsledok: SourceReference na auditovateľný export, protokol alebo interný zdrojový záznam,
- manuálne meranie: SourceReference na protokol alebo iný riadený záznam pôvodu,
- fotografia: podľa ADR-0016 môže byť reprezentovaná SourceReference; presná attachment architektúra je odložená,
- dokument: SourceReference opisuje použitie zdroja; DocumentRecord riadi dokument, ale nenahrádza SourceLink ku konkrétnemu obsahu.

SourceLink sa nesmie stať skládkom payloadu, metódy, subjektu ani scope. Priamy odkaz na binárny artefakt sa nepridáva bez file/attachment governance.

## 14. Verification Boundary

Dôkaz možno overovať z hľadiska autenticity, integrity, úplnosti alebo správnosti prepisu. To nie je to isté ako potvrdiť pravdivosť claim o svete.

Existujúce Accepted texty nie sú dostatočne presné na bezpečné použitie všeobecného `verificationStatus` na Observation. RFC-0001 ho navrhuje a RFC-0002 povoľuje stav overenia, ale RFC-0003 necháva presný enum otvorený a ADR-0016 neustanovuje jeho význam pre evidence. Slepo prevziať PropertyRecord enum by mohlo znamenať, že `Approved` Observation sa považuje za schválený Claim.

Počiatočný kontrakt nemá `verificationStatus`. Entity `status` riadi zrelosť a použiteľnosť záznamu, nie pravdivosť claim. Budúci EvidenceVerificationStatus sa môže zaviesť až po definovaní autenticity, integrity a oprávnených prechodov; PropertyRecord VerificationStatus sa nerecykluje.

## 15. Immutability and Correction Boundary

Po zachytení sa dôkazový obsah Observation nemení. Nové meranie, nové zistenie alebo zmena interpretácie vytvára nový objekt alebo samostatný Claim/Derived Result, nie editáciu pôvodného payloadu.

Pri chybe:

1. vznikne nová opravujúca Observation,
2. pôvodná zostane dohľadateľná,
3. budúci lifecycle môže pôvodnú označiť ako disputed, superseded alebo replaced,
4. tichý prepis je zakázaný.

`supersedesObservationId` je rozumný budúci korekčný odkaz, ale nie je prijatý presný kontrakt. Do prvého modelu sa nesmie pridať bez uzavretia lifecycle pravidla. Administratívne alebo právne odstránenie je persistence/governance politika; JSON kontrakt ho nevyrieši a auditná stopa sa musí zachovať podľa platných pravidiel.

## 16. Claim / Decision / Derived Result Boundary

| Objekt | Zodpovednosť |
| --- | --- |
| Observation | Zaznamená zdrojový dôkaz a kontext. |
| PropertyRecord | Nesie claim-like tvrdenie o vlastnosti rodičovskej entity. |
| Decision | Auditovateľne prijme, odmietne alebo podmienene prijme význam. |
| Derived Result | Nesie výpočtový, interpretačný alebo modelový výstup z explicitných vstupov. |

Observation nemôže automaticky vytvoriť ani aktualizovať PropertyRecord. Môže byť vstupom návrhu alebo workflow, ale zápis autoritatívneho tvrdenia vyžaduje Decision alebo ekvivalentný explicitne schválený governance mechanizmus.

Observation môže existovať pred stored Decision schémou, pretože uloženie dôkazu a prijatie jeho významu sú oddelené. Bez Decision kontraktu však EOS nesmie predstierať persistovaný audit promotion procesu. Derived Result sa nesmie uložiť ako Observation ani vtedy, keď vychádza z pozorovaných dát.

## 17. Aggregate Ownership Boundary

Najbezpečnejšia voľba je samostatná Observation aggregate root. `Job` môže neskôr obsahovať kolekciu OBS referencií alebo sa väzba môže vyhľadávať z Observation scope; nesmie vlastniť celý Observation objekt.

Stabilná identita sama osebe nevylučuje containment, ale Accepted EOS pravidlo ho pri first-class Observation výslovne vylučuje. Transakcia vytvorenia Observation patrí Observation aggregate. Pridanie referencie do Job je samostatná aggregate operácia alebo budúca koordinovaná aplikačná transakcia. Pred existenciou Job schémy sa nesmie simulovať vnorením.

## 18. Candidate Models

| Kandidát | Evidence/claim | Audit a identita | Budúca kompatibilita | Verdikt |
| --- | --- | --- | --- | --- |
| A: embedded `propertyRecord` | Zlieva evidence s claim a duplikuje verification/provenance. | OBS identita je možná, obsah však má nesprávnu zodpovednosť. | Zlá hranica voči Decision. | Odmietnuť. |
| B: `propertyId` + priama Quantity/ValueRange | Zachováva jednoduchý meraný fakt oddelene od PropertyRecord. | Dobré pre jeden číselný výsledok, ak má subject a source. | Dobré pre measurement subset, nie pre fotografiu, inspection alebo textové zistenie. | Najlepší obmedzený profil, nie univerzálny Observation. |
| C: typed `result` payload | Najčistejšie oddelenie obálky a výsledku. | Dobre škáluje na viac typov evidence. | Vyžaduje nový ObservationResult/ObservedValue kontrakt a discriminator. | Architektonicky sľubné, dnes chýbajúce. |
| D: iba evidence obálka | Claim sa nezlieva. | Má ID a provenance, ale nezachytáva, čo sa zistilo. | Slabá použiteľnosť pre Job, AI aj Decision. | Odmietnuť ako prázdny záznam. |
| E: všeobecný `payload` JSON | Formálne oddelené, významovo nekontrolované. | Audit existuje bez typovej dôvery. | Vedie k nekompatibilným payloadom a obchádzaniu schém. | Odmietnuť. |

## 19. Recommended Minimal Model

Vybraný je obmedzený property-measurement profil B s priamym typed unionom z kandidáta C hodnotového posúdenia:

```json
{
  "id": "OBS-xxxxxx",
  "schemaVersion": "...",
  "recordVersion": "...",
  "revision": 0,
  "status": "Draft",
  "createdAt": "...",
  "createdBy": "...",
  "updatedAt": "...",
  "updatedBy": "...",
  "changeSummary": "...",
  "observationScope": "JOB",
  "scopeReferenceId": "JOB-yyyy-xxxx",
  "subjectId": "MAT-0001",
  "observedAt": "...",
  "propertyId": "PRP-xxxxxx",
  "valueType": "quantity",
  "quantity": {
    "value": 0,
    "unitId": "UNT-xxxxxx"
  },
  "conditions": [],
  "sourceLinks": []
}
```

Príklad je tvarové odporúčanie pre budúcu schému, nie technický ani strojársky údaj. `MAT-0001`, PRP a UNT sú fiktívne formátové príklady; implementácia fixture nimi nesmie predstierať existujúcu entitu alebo katalógový záznam.

Bezpečný rozsah `0.2B.1.7` je Observation entity schema pre tento jediný profil, registrácia v indexe, fiktívne fixtures, testy a nevyhnutná validačná kompozícia. Nie je ním všeobecný ObservationResult, katalóg, Knowledge Entity, Project, Experiment, Decision ani attachment model.

## 20. Field Requirement Matrix

| Pole | Klasifikácia | Odôvodnenie |
| --- | --- | --- |
| `id` | REQUIRED | Vlastná OBS identita entity. |
| `observationId` | REJECTED | Vlastné ID používa `id`; názov patrí referenciám. |
| `metadata` wrapper | REJECTED | Existujúce entity používajú spoločné polia priamo, nie nový wrapper. |
| `schemaVersion` | REQUIRED | Spoločné entity metadata. |
| `recordVersion` | REQUIRED | Spoločné entity metadata. |
| `revision` | REQUIRED | Audit technických opráv metadát. |
| `status` | REQUIRED | Vlastný lifecycle Observation. |
| `createdAt`, `createdBy` | REQUIRED | Audit vytvorenia v EOS. |
| `updatedAt`, `updatedBy` | REQUIRED | Spoločná metadata stopa; nesmie legalizovať zmenu evidence payloadu. |
| `changeSummary` | REQUIRED | Audit každej revízie. |
| `observationType` | DEFERRED | Počiatočný profil má jediný význam; voľný string ani predčasný enum sa nepridáva. |
| `observedBy` | DEFERRED | Actor identita nie je riadená; `createdBy` ani SourceLink sa nesmú nesprávne vydávať za pozorovateľa. |
| `observationScope` | REQUIRED | Autoritatívne povinný kontext. |
| `scopeReferenceId` | CONDITIONALLY REQUIRED | Zakázaný pre GLOBAL; povinný JOB ID pre JOB. PROJECT/EXPERIMENT nie sú v počiatočnom profile. |
| `subjectId` | REQUIRED | Jeden subjekt, obmedzený na vybrané aktívne doménové EOS ID definície. |
| `subjectType` | REJECTED | V prvom smere zbytočne duplikuje typ ID; môže sa prehodnotiť pri externých cieľoch. |
| `observedAt` | REQUIRED | Čas dôkazovej udalosti. |
| `recordedAt` | REJECTED | Bez prijatého odlišného významu duplikuje `createdAt`. |
| `propertyId` | REQUIRED | Počiatočný profil je property-measurement evidence. |
| `valueType` | REQUIRED | Discriminator `quantity` alebo `valueRange`. |
| `quantity` | CONDITIONALLY REQUIRED | Presne jedna vetva a zhoda s `valueType`. |
| `valueRange` | CONDITIONALLY REQUIRED | Presne jedna vetva a zhoda s `valueType`. |
| `measurementQuality` | OPTIONAL | Len pri kompatibilnom meranom/reportovanom výsledku. |
| `conditions` | OPTIONAL | Kontext Observation alebo jediného výsledku. |
| `propertyRecord` | REJECTED | Claim-like objekt nesmie byť payloadom evidence. |
| `sourceLinks` | REQUIRED | Povinné pole pôvodu; neprázdnosť je lifecycle podmienka. |
| `verificationStatus` | DEFERRED | Evidence-verification význam nie je uzavretý. |
| `notes` | OPTIONAL | Neautoritatívny doplnok; nesmie nahradiť payload, subject ani source. |
| `supersedesObservationId` | DEFERRED | Potrebuje korekčný lifecycle. |

`CONDITIONALLY REQUIRED` neznamená, že pole možno ľubovoľne vynechať. Znamená, že presná podmienka musí byť súčasťou budúceho prijatého payload/scope profilu.

## 21. Validation Boundary

| Vrstva | Budúce kontroly |
| --- | --- |
| JSON Schema | Object, uzavreté polia, OBS pattern, spoločné metadata, scope enum, timestamp format, typy polí, presný payload union, `$ref` na Quantity/ValueRange/MeasurementQuality/Condition/SourceLink a podmienená prítomnosť scope referencie. |
| EOS application validation | Append-only politika, povolené zmeny revízie, časová konzistencia `observedAt` voči evidencii, neprázdne zdroje podľa lifecycle, kompozícia sémantických pravidiel vnorených kontraktov a zákaz odvodeného payloadu vydávaného za Observation. |
| Catalog-aware validation | Existencia a stav PRP/UNT/CND, povolený value type, jednotková a rozmerová kompatibilita, povinné podmienky, význam observationType. |
| Parent/scope-aware validation | Existencia Job/Project/Experiment, zhoda scope a reference, existencia a prípustný typ subject, oprávnenosť väzby na Job a zákaz vnoreného vlastníctva. |
| Decision/workflow validation | Promotion evidence na claim, oprávnenia, audit prijatia/odmietnutia, väzba na historickú revíziu a korekčný/supersession postup. |

JSON Schema nemôže potvrdiť existenciu referencovaných objektov, pravdivosť pozorovania, dostatočnosť evidence ani oprávnenie na promotion. Katalógová a parent-aware validácia sa nesmie predstierať iba kontrolou formátu ID.

## 22. Risks

| Priorita | Riziko | Dôsledok |
| --- | --- | --- |
| Critical | PropertyRecord sa vloží ako observed payload. | Evidence a claim sa zlúčia v rozpore s ADR-0016. |
| Critical | Univerzálny payload sa vymyslí priamo v JSON Schema. | Serializácia zavedie novú architektúru bez autority. |
| High | Observation neidentifikuje subjekt. | Dôkaz nie je samostatne interpretovateľný ani auditovateľný. |
| High | Scope nemá konkrétnu referenciu. | JOB/PROJECT/EXPERIMENT je iba label bez referenčnej integrity. |
| High | Číselný property profil sa vydá za všeobecnú Observation. | Fotografie, inspection a nečíselné zistenia budú tlačené do textu alebo obchádzok. |
| High | `verificationStatus` sa prevezme z PropertyRecord. | Schválenie evidence sa zamení so schválením claim. |
| High | Nemennosť nemá korekčnú cestu. | Chyby sa budú ticho opravovať alebo zostanú nepoužiteľné. |
| Medium | SourceLinks sa použijú ako payload alebo attachment úložisko. | Stratí sa význam podporovaného poľa/tvrdenia a pôvod nebude čitateľný. |
| Medium | MeasurementQuality sa duplikuje do Observation a PropertyRecord. | Dve nesynchronizované verzie budú pôsobiť ako jedna metrologická pravda. |
| Medium | Všeobecný target reference sa stane graph edge bez pravidiel. | Typy, kardinality a lifecycle referencií budú neriadené. |
| Medium | Decision sa stane blokátorom každého dôkazového zápisu. | EOS nebude vedieť zachytiť Draft evidence pred interpretáciou. |
| Medium | Job začne vlastniť OBS objekty. | Poruší sa aggregate boundary a zdieľanie evidence medzi claims. |
| Low | `recordedAt` duplikuje `createdAt`. | Časové polia sa rozídu bez jasnej semantiky. |

## 23. Deferred Concepts

- Všeobecný ObservationResult alebo ObservedValue kontrakt a discriminator.
- Nečíselný, obrazový, súborový, inspection a tool-output payload.
- Project a Experiment entity a ich identifikátory.
- Subjekt bez existujúcej EOS identity, vzorka a artifact/attachment model.
- Measurement a Inspection subtype kontrakty.
- Evidence relationship medzi OBS a konkrétnou historickou claim inštanciou.
- Evidence-specific verification stav a transition policy.
- Stored Decision, Derived Result a Snapshot kontrakty.
- Korekčný, disputed, superseded a replaced lifecycle.
- Property, Unit, Condition Type a observation-type katalógy.

## 24. Implementation Preconditions

Architecture closure uzavrelo pôvodné blockery nasledovne:

1. **Subject model:** povinný koreňový `subjectId`, presne jeden subjekt, hodnota cez centrálny union `MAT`, `POL`, `TEC`, `MAC`, `TOOL`, `SUP`, `JOB` alebo `JOB_OPERATION`; `subjectType` ani SubjectReference objekt nevznikajú.
2. **Subject integrity:** JSON Schema kontroluje riadený formát. Aplikačná vrstva kontroluje existenciu, použiteľnosť a povolený typ cieľa. Neexistujúca budúca entita sa nesmie nahradiť fiktívnym ID.
3. **Result model:** povinné `propertyId`, `valueType` a presne jedna zhodná Quantity alebo ValueRange vetva. PropertyRecord sa nevkladá a arbitrary payload je zakázaný.
4. **Profile:** počiatočný Property Measurement Observation s jedným výsledkom a jedným subjektom. Všeobecná Observation zostáva architektonickým pojmom, nie rozsahom prvej schémy.
5. **Observation type:** `observationType` sa odkladá. Jeden profil nepotrebuje voľný string ani nový katalóg.
6. **Scope:** konceptuálne hodnoty sú `GLOBAL`, `JOB`, `PROJECT`, `EXPERIMENT`; prvá schéma povoľuje iba `GLOBAL` a `JOB`. GLOBAL zakazuje `scopeReferenceId`, JOB vyžaduje platný JOB ID.
7. **Time:** `observedAt` je povinný doménový čas; `createdAt` zostáva povinným časom EOS metadát. `recordedAt` nevzniká.
8. **Sources:** `sourceLinks` je povinné pole. Draft povoľuje `[]`; Review a Approved vyžadujú neprázdny zoznam cez workflow/aplikačnú validáciu.
9. **Verification:** Observation nemá claim `verificationStatus`. Evidence-specific verification zostáva deferred.
10. **Immutability:** sémantická oprava vytvára novú Observation; pôvodná ostáva auditovateľná. `supersedesObservationId` a plný korekčný lifecycle zostávajú deferred.
11. **MeasurementQuality:** voliteľné koreňové pole kvalifikuje jediný číselný výsledok. Budúci multi-result model by vyžadoval verziovanú migráciu.
12. **Conditions:** jedno voliteľné koreňové pole `conditions` kvalifikuje kontext jediného výsledku a Observation; nevznikajú duplicitné kolekcie.

Pred dokončením budúcej implementácie treba:

- doplniť `OBS` do centrálnej identifiers schémy podľa už Active EOS-003,
- uzavrieť schému cez `additionalProperties: false` a nepovoliť odložené polia,
- kompozitne spustiť existujúce sémantické pravidlá ValueRange a MeasurementQuality s presnými cestami,
- oddeliť schema, application, catalog a reference-integrity chyby,
- otestovať GLOBAL/JOB podmienky, subject ID union, typed result, zdroje a regresiu všetkých existujúcich kontraktov.

RFC-0001 Revision 5 je jediná potrebná autoritatívna korekcia. RFC-0002 už podporuje samostatnú aggregate root s vlastneným resultom a referencovaným subjektom. RFC-0003 nepotrebuje zmenu, pretože nevznikol nový preferovaný termín, SubjectReference ani ObservationResult objekt. ADR zmena nie je potrebná.

## 25. Readiness Verdict

Počiatočný profil má jednoznačný subjekt, typed result, implementovateľný scope, oddelenie evidence od PropertyRecord, auditovateľný čas, zdrojovú hranicu a jasnú kompozíciu vnorených pravidiel. Nepotrebuje nový reusable value object, nový prefix, Job schému, Property Catalog ani stored Decision.

Phase 0.2B.1.7 môže implementovať iba profil definovaný v §24 a RFC-0001 Revision 5. PROJECT, EXPERIMENT, neidentifikovaný subjekt, nečíselný výsledok, všeobecný ObservationResult, observation type taxonomy, evidence verification a korekčný odkaz zostávajú výslovne mimo rozsahu.

### Implementation Outcome

Phase 0.2B.1.7 implementuje schválený profil bez odchýlky:

- schéma je `schemas/knowledge-core/observation.schema.json` s kanonickým ID `https://eos.local/schemas/knowledge-core/observation.schema.json`,
- ide o first-class Entity a Aggregate Root s vlastným `id` vo formáte `OBS-xxxxxx` a spoločnými EOS entity metadátami,
- `subjectId` povoľuje centrálne rodiny `MAT`, `POL`, `TEC`, `MAC`, `TOOL`, `SUP`, `JOB` a `JOB_OPERATION`; existencia cieľa sa nepredstiera,
- podporované scope sú iba `GLOBAL` bez scope referencie a `JOB` s povinným `scopeReferenceId` vo formáte JOB,
- výsledok vyžaduje `propertyId`, discriminator `valueType` a presne jednu Quantity alebo ValueRange vetvu,
- voliteľné MeasurementQuality a Conditions kvalifikujú jediný výsledok a používajú existujúce schémy cez `$ref`,
- `sourceLinks` je povinné pole; Draft môže byť prázdny, Review/Approved bez zdroja vracia aplikačnú chybu,
- JSON Schema kontroluje štruktúru, ID formáty, scope a result union; EOS aplikačná validácia skladá existujúce pravidlá ValueRange, MeasurementQuality a source lifecycle,
- referenčná existencia subjektu, JOB a PRP, katalógová kompatibilita, persistence immutability a promotion cez Decision zostávajú mimo štrukturálnej validácie,
- všeobecný ObservationResult, nečíselné payloady, PROJECT/EXPERIMENT, actor, attachment, evidence verification a korekčný model nevznikli,
- 10 platných a 45 neplatných fixtures pokrýva profil; 15 nových testov zvýšilo kompletnú sadu zo 105 na 120 a všetky prešli.

Implementácia nemení Accepted RFC ani ADR. JSON Schema zostáva serializačným kontraktom, nie Knowledge Modelom.

## 26. Change History

| Dátum | Version | Revision | Autor | Zmena |
| --- | --- | --- | --- | --- |
| 2026-09-08 | 0.1 | 0 | Codex | Pre-design review Observation nad Accepted EOS architektúrou; identifikované pevné evidence a aggregate hranice, otvorený subject/payload model a podmienky pred implementáciou. Bez zmeny schém alebo architektúry. |
| 2026-09-08 | 0.1 | 1 | Codex | Architecture closure: výber jedného riadeného `subjectId`, atomického property-measurement result unionu, GLOBAL/JOB scope profilu, časovej, zdrojovej, verification a immutable hranice; zaznamenanie RFC-0001 Revision 5 a otvorenie implementačného gate. |
| 2026-09-08 | 0.1 | 2 | Codex | Implementation outcome: Observation schéma, centrálny OBS formát, index, fixtures, testy, rekurzívna významová validácia a potvrdenie všetkých deferred hraníc po míľniku 0.2B.1.7. |

READY FOR IMPLEMENTATION
