# CDR-0005 - Classification Pre-design Review

Project: EOS – Engineering Operating System

Contract Review ID: CDR-0005

Contract: Classification

Review type: Pre-design

Version: 0.1

Revision: 1

Status: Review

Document basis: Accepted EOS architecture

## 1. Purpose

Posúdiť najmenší bezpečný budúci kontrakt `Classification` pre míľnik `Phase 0.2B.1.5-prep`. Review oddeľuje prijatý význam od odporúčaného serializačného modelu. Tento dokument neprijíma nové architektonické pravidlá ani neimplementuje schému.

Revision 1 zachováva pre-design posúdenie v §1 až §17 a dopĺňa finálne implementačné rozhodnutie a výsledok `Phase 0.2B.1.5` v §19. Pri rozdiele medzi odporúčaním pre-design a výsledným tvarom platí implementačné spresnenie §19. Existujúce CDR používajú Status Review; tento stav sa zachováva bez zavedenia nového lifecycle.

Záver review: jednoduchý vnorený katalógový odkaz je odôvodnený, ale všeobecný zákaz `sourceLinks` by odporoval RFC-0001 §4.6. Odporúčaný minimálny model preto zachováva povinné `classificationId` a podmienené `sourceLinks`.

## 2. Scope

Posúdené sú typ objektu, identita, pomenovanie referencie, hodnotová reprezentácia, zdrojovanie, metadáta, hierarchia, násobnosť a hranica medzi `0.2B.1` a `0.2B.2`.

Pre-flight dňa 2026-09-07:

- Vetva: `feature/phase-0.2b-knowledge-contracts`.
- HEAD: `e7742fe` - `Implement Condition knowledge core contract`.
- Pracovný strom pred review: clean.
- RFC-0001 Revision 4, RFC-0002 Revision 3 a RFC-0003 Revision 3: Accepted.
- ADR-0014, ADR-0015 a ADR-0016: Accepted.
- Schémy `Quantity`, `ValueRange`, `MeasurementQuality` a `Condition` existujú; ich regresné testy prešli.
- Existujúca sada: `Ran 80 tests in 3.157s`, `OK`; 80 úspešných, 0 zlyhaní, 0 chýb, 0 preskočených.
- Počet súborov `*.schema.json` v `schemas/`: 13. ADR Markdown súborov: 17 vrátane ADR-0000 Template. RFC Markdown súborov: 4 vrátane cross-consistency review; samotné RFC sú tri.
- Inventár repozitára, schémy, index, kód a fixtures neobsahujú implementáciu Classification ani Classification Catalog. Phase 0.2B.2 nebola začatá.

Prečítané vstupy:

| Vstup | Použitie v review |
| --- | --- |
| `AGENTS.md`, `EOS-000_Development_Manifesto.md` | Disciplína implementácie, dohľadateľnosť a oddelenie znalostí od kódu |
| `EOS-003_Identification_and_Versioning.md` Revision 2 | Aktuálna autorita pre význam a stav `CLS` |
| `EOS-009_Architecture_Closure_Plan.md`, `EOS-010_Architecture_Readiness_Review.md` | Freeze, povolený rozsah a hranica katalógov |
| `RFC-0001_Engineering_Property_Model.md` Revision 4 | Classification §4.6, PropertyRecord §4.4, Condition §4.7 |
| `RFC-0002_Engineering_Object_Taxonomy.md` Revision 3 | §3.2, §3.3, §3.9, §5.7, §9, §11 až §14, §16 a §18 |
| `RFC-0003_EOS_Engineering_Glossary.md` Revision 3 | G-0008 až G-0014, G-0021 až G-0025, G-0039, G-0053, G-0063, G-0070, G-0077 až G-0081 |
| `ADR-0015_Establish_engineering_knowledge_layer.md` | Value Object, Catalog Entry, DDD a hranica serializácie |
| `CDR-0004_Condition_Contract.md`, `condition.schema.json` | Implementačný precedens; nenahrádza autoritu RFC |
| `schemas/common/identifiers.schema.json`, `schemas/index.schema.json`, `schemas/common/source-link.schema.json` | Reálne podporované ID, discovery a existujúci SourceLink |
| `CHANGELOG.md`, `ROADMAP.md`, `BACKLOG.md` | Kontext implementačnej fázy a odložených prác |

Záznamy počtov a revízií v EOS-009/EOS-010 opisujú historický closure míľnik. Aktuálny stav bol overený priamo v repozitári; historické čísla sa nepovažujú za dnešný inventár.

## 3. Authoritative Findings

`AUTHORITATIVE` znamená explicitné prijaté pravidlo; `IMPLIED` je označený odvodený záver; `OPEN` nemá prijaté presné riešenie; `DEFERRED` patrí do neskoršej fázy. Odporúčania v ďalších kapitolách nie sú dodatočnými Accepted pravidlami.

| Bod | Klasifikácia | Zistenie a opora |
| --- | --- | --- |
| Classification | AUTHORITATIVE | Vnorený Value Object vyjadrujúci zaradenie do riadeného významu; RFC-0001 §4.6, RFC-0002 §5.7, RFC-0003 G-0081, ADR-0015 |
| Referenčná forma v core | AUTHORITATIVE | V `0.2B.1` je dovolený value-object kontrakt alebo odkaz bez katalógovej entity; RFC-0002 §9.4 a §18, RFC-0003 G-0081 |
| Embedded reference value object | IMPLIED | Opis realizácie povolenej referenčnej formy, nie nová kategória EOS |
| Catalog | AUTHORITATIVE | Riadený autoritatívny zoznam stabilizujúci význam; RFC-0003 G-0010 |
| Catalog Entry | AUTHORITATIVE | Položka so stabilnou identitou, vlastným lifecycle a históriou; RFC-0002 §3.9, RFC-0003 G-0011 |
| Reference Object | AUTHORITATIVE | Autoritatívny referenčný objekt s identitou; nie každé ID pole je Reference Object; RFC-0002 §3.3, RFC-0003 G-0009 |
| Reference Catalog | AUTHORITATIVE | Referenčné významy; Classification Catalog patrí do tejto skupiny; RFC-0002 §9.0, RFC-0003 G-0077 |
| Knowledge Catalog | AUTHORITATIVE | Interné EOS významy, napríklad Property Catalog a Condition Type Catalog; RFC-0003 G-0078 |
| CLS-xxxxxx | AUTHORITATIVE | Active prefix pre Classification Catalog Entry; EOS-003 §2 a §3.1. Neidentifikuje vnorené použitie |
| Classification Catalog | DEFERRED | Kontrakt, obsah a detailná správa patria do `0.2B.2` podľa schváleného rozsahu; RFC-0002 §9.4, EOS-009 §9 |
| Ownership | AUTHORITATIVE | Inštancia je vlastnená rodičom, opakovane sa používa štruktúra; RFC-0002 §5.7 a §16 |
| Identity | AUTHORITATIVE | Classification nemá vlastné stabilné ID; ID cieľovej položky nie je ID použitia; RFC-0002 §13.3 |
| Lifecycle a revízia | AUTHORITATIVE | Cez rodiča, immutable v rámci jeho schválenej revízie; RFC-0002 §12.3, §14 a §16 |
| sourceLinks | AUTHORITATIVE | RFC-0001 §4.6 ich vyžaduje pri klasifikácii z externého systému, normy alebo zdrojového dokumentu. RFC-0002 §3.2 a §16 ich povoľuje vo Value Objecte |
| verificationStatus | AUTHORITATIVE | Classification nemá vlastný verificationStatus; RFC-0002 §5.7. To neruší vlastný stav overenia vnoreného SourceLink |
| Referenčné pole | OPEN | Žiadne Accepted RFC neurčuje názov `classificationId`, `classificationTypeId` ani `classificationEntryId` |
| Systém, kód, verzia a platnosť | AUTHORITATIVE | Kód sa nesmie interpretovať bez systému a relevantnej verzie alebo platnosti; RFC-0001 §4.6 |
| Presné mapovanie CLS na externý význam | DEFERRED | Schéma katalógu a reprezentácia vydania či platnosti ešte neexistujú; základná požiadavka jednoznačného významu však už platí |
| notes | AUTHORITATIVE | RFC-0001 §4.6 ich uvádza medzi navrhovanými poľami; nevyžaduje ich v minimálnom kontrakte |
| Hierarchia a násobnosť | OPEN | Presný serializačný model, dedenie, poradie a exkluzivita klasifikácií nie sú prijaté |

V starších návrhových pasážach RFC-0002 §13.2 a RFC-0003 G-0081 je `CLS` ešte opísané ako budúci prefix. Jeho dnešný stav jednoznačne určuje EOS-003 Revision 2 a potvrdzuje EOS-009. Nejde o dôvod zavádzať ďalší prefix.

## 4. Open Questions

| Otázka | Dopad a spôsob ohraničenia |
| --- | --- |
| Má sa v budúcnosti povoľovať iba reference-only Classification bez vlastných sourceLinks? | Teraz sa taký zákaz neodporúča. Vyžadoval by explicitné zosúladenie RFC-0001 §4.6 a umiestnenia dôkazu o zaradení; minimálny model nižšie existujúce pravidlo zachováva |
| Ako katalóg naviaže CLS na systém, externý kód, vydanie a platnosť? | `0.2B.2`; pred reálnym interpretovaním CLS musí byť význam jednoznačný. Teraz iba štrukturálne odkazy |
| Ako sa zachová historické rozlíšenie významu pri zmene externého systému? | `0.2B.2`; určiť pravidlá pre nové CLS, revíziu položky, náhradu a historické čítanie. Nepridávať naslepo version pole do Value Objectu |
| Ako sa presne adresuje klasifikačné tvrdenie v zozname rodiča? | Pri integrácii rodičovských kontraktov určiť stabilné pravidlá SourceLink a citácie v revízii rodiča; samotný index poľa nie je globálna identita |
| Sú viacnásobné klasifikácie exkluzívne, usporiadané alebo dedené? | Katalógové a doménové pravidlá neskôr; jednoduchý objekt tieto rozhodnutia nepotrebuje |
| Ako sa spravujú interné klasifikácie a mapovania medzi systémami? | Následné katalógové review; nezamieňať automaticky Classification Catalog za Knowledge Catalog |

Otázky o katalógu neblokujú syntaktický kontrakt s obmedzeniami v §16. Neoprávňujú vytvárať autoritatívne klasifikačné dáta pred existenciou riadeného významu.

## 5. Object Type Assessment

| Možnosť | Posúdenie |
| --- | --- |
| A. Value Object | Áno, explicitná architektonická kategória. Bez vlastnej identity a lifecycle, mení sa cez rodiča |
| B. Reference Object | Nie pre vnorenú inštanciu. V EOS označuje samostatný autoritatívny cieľ s identitou |
| C. Catalog Entry | Nie. Definuje klasifikačný význam a je cieľom odkazu, nie konkrétnym zaradením rodiča |
| D. Embedded reference value object | Preferovaná realizácia A; nesie odkaz na význam a podľa potreby dôkaz jeho použitia. Nezavádza novú taxonomickú kategóriu |
| E. Samostatná entita, tag alebo first-class Relationship | Neodôvodnené pre tento míľnik. Zmenilo by to identitu alebo rozšírilo scope |

Vnorená Classification a referencovaná katalógová položka majú rozdielne vlastníctvo. Rodič vlastní iba svoje zaradenie; nevlastní ani neprepisuje autoritatívnu katalógovú položku.

## 6. Identifier Semantics

`CLS-xxxxxx` identifikuje Classification Catalog Entry. Neidentifikuje klasifikačný systém ako celok, typ poľa, objekt klasifikovaný do kategórie ani jednotlivú vnorenú Classification.

| Názov poľa | Hodnotenie |
| --- | --- |
| `classificationId` | Preferovaný: stručná referencia na riadený klasifikačný význam, obdobne ako `propertyId` a `unitId`. Dokumentácia musí explicitne vylúčiť identitu vnorenej inštancie |
| `classificationTypeId` | Neodporúčaný: zamieňa vybranú klasifikačnú položku za typ klasifikácie; EOS-003 pre CLS neurčuje type catalog |
| `classificationEntryId` | Zrozumiteľný, ale dlhší názov s rovnakým cieľom. Neprijať ako paralelný alias |
| `catalogEntryId` | Príliš všeobecný; skrýva, že cieľom musí byť práve Classification Catalog Entry |

Presne jeden odporúčaný názov je `classificationId`. Ide o návrh serializačného pomenovania, nie už existujúci názov nariadený RFC. `CND` je naopak explicitne identifikátor typu podmienky; analógia s `conditionTypeId` neodôvodňuje `classificationTypeId`.

## 7. Candidate Models

| Kandidát | Sémantika a identita | Kompatibilita core / budúceho katalógu | Duplicita a voľný text | Záver |
| --- | --- | --- | --- | --- |
| A: iba classificationId | Jedna referencia na CLS, nie ID inštancie | Dobrá referenčná forma; ako uzavretý úplný kontrakt nepokrýva podmienené zdroje podľa RFC-0001 | Nízka duplicita, bez textovej obchádzky | Dobrý referenčný základ, nepostačuje ako jediná povolená forma pre všetky prípady |
| B: iba classificationTypeId | Naznačuje typ namiesto konkrétnej kategórie | Riziko nesprávneho mapovania CLS na budúci type catalog | Nízka duplicita, bez voľného textu; zdroje chýbajú | Odmietnuť pomenovanie |
| C: classificationId + textValue | Dva možné nositele klasifikačnej hodnoty | Nejasná autorita pri rozdiele medzi textom a katalógom | Vysoké riziko duplicity a obchádzania katalógu | Odmietnuť |
| D: catalogId + entryId | Pridáva identitu kontajnera bez prijatého ID kontraktu | Predčasne viaže core na organizačnú štruktúru katalógu | Duplicita príslušnosti položky; neznámy formát catalogId | Odložiť, nie minimálny model |
| E: classificationId + podmienené sourceLinks | Jeden riadený význam a oddelený dôkaz použitia | Spája dovolenú referenčnú formu s RFC-0001 §4.6; znovu používa existujúci SourceLink | Bez duplicitného významu; text v SourceLink opisuje tvrdenie alebo interpretáciu, nie náhradnú kategóriu | Odporúčaný najmenší bezpečný model |

Variant E nekopíruje katalógový systém, kód, vydavateľa, verziu ani význam do každého použitia. RFC-0002 §9.4 a §18 povoľujú referenčnú formu; presun interpretácie kódu na riadený cieľ je možný, ak sa pred jeho reálnym použitím zachovajú pravidlá RFC-0001 §4.6.

## 8. Recommended Minimal Model

| Pole | Povinnosť v budúcej štruktúre | Význam |
| --- | --- | --- |
| `classificationId` | Povinné | Jeden odkaz vo formáte `CLS-xxxxxx` na budúcu Classification Catalog Entry |
| `sourceLinks` | Štrukturálne nepovinné; podmienene povinné podľa pôvodu tvrdenia | Pole existujúcich SourceLink; pri uvedení odporúčané neprázdne. Zachováva dôkaz podľa RFC-0001 §4.6 |

Žiadne ďalšie voliteľné polia sa teraz neodporúčajú. Samotné `sourceLinks` nestačia bez `classificationId`.

Fiktívny príklad referenčnej štruktúry, nie autoritatívny záznam ani fixture:

```json
{
  "classificationId": "CLS-000001"
}
```

Tento príklad nepreukazuje existenciu cieľa ani externý pôvod; nemôže demonštrovať úplnú aplikačnú platnosť. Pri externom pôvode sa doplnia `sourceLinks` podľa existujúceho kontraktu. CDR nevytvára žiadnu CLS ani SRC položku.

| Reprezentácia | Rozhodnutie pre nasledujúci kontrakt | Dôvod |
| --- | --- | --- |
| Katalógová referencia ako jediná klasifikačná hodnota | INCLUDE NOW | Jeden riadený význam; doplnkové evidence nie sú druhá klasifikačná hodnota |
| Enum klasifikačných hodnôt | REJECT | Zabudoval by katalógový obsah do schémy a vyžadoval zmenu kontraktu pri zmene zoznamu |
| Voľný text ako hodnota | REJECT | Nezaručuje riadený význam |
| Text fallback | REJECT | Umožnil by obísť katalóg bez architektonickej opory |
| Viac CLS v jednom objekte | REJECT | Násobnosť patrí rodičovskej kolekcii |
| Hierarchy path | DEFER | Vlastnosť alebo odvodené zobrazenie taxonómie |
| Parent classification | DEFER | Väzba medzi katalógovými položkami |
| Classification system identifier | DEFER | Identifikácia a správa systému patria do katalógového návrhu; bez systému sa externý kód nesmie interpretovať |

Odporúčaný budúci štrukturálny rozsah: objekt, uzavreté polia, povinné `classificationId`, centrálny CLS pattern a znovupoužitie SourceLink cez `$ref`. Aplikačná vrstva má odlišovať syntaktickú platnosť, existenciu cieľa a dôkaz správneho zaradenia. Samostatná schéma bez rodičovského a katalógového kontextu nevie určiť externý pôvod ani životný stav rodiča; nesmie tieto kontroly reportovať ako vykonané.

## 9. Catalog Boundary

V `0.2B.1` môže po samostatnom implementačnom zadaní vzniknúť Value Object kontrakt, centrálny CLS formát, discovery, fiktívne fixtures a testy jeho štruktúry. `CLS` je Active už teraz, ale v `identifiers.schema.json` zatiaľ nie je implementované. Doplnenie existujúceho formátu v budúcom míľniku nebude zavedením nového prefixu.

CLS referencie môžu pred katalógom existovať štrukturálne, obdobne ako UNT a CND v dnešných kontraktoch. Platný formát nie je referenčná integrita podľa RFC-0003 G-0070. Nemožno predstierať existenciu, riadený význam, schválenie, technickú správnosť ani kompatibilitu cieľovej položky.

Do `0.2B.2` patria: Classification Catalog kontrakt, riadené prideľovanie položiek, mapovanie systému a externého kódu, relevantné vydanie a platnosť, autoritatívny význam, aliasy, deprecácia a náhrady, hierarchia a pravidlá správy Reference Catalog. Po zavedení katalógu musí aplikačná validácia riešiť existenciu a použiteľnosť cieľa; režim iba štrukturálnych testov nesmie pretrvať ako falošná úplná validácia produkčných dát.

Zdroj definície kategórie a dôkaz zaradenia konkrétneho rodiča sú dve odlišné tvrdenia. Zdroj na Catalog Entry automaticky nepotvrdzuje, že ľubovoľný objekt do kategórie patrí. Naopak, SourceLink pri Classification nenahrádza autoritatívnu definíciu cieľa. Samotná existencia katalógu teda nie je dôvod odstrániť `sourceLinks` z kontraktu.

## 10. Relationship to Condition and Property

Pre `Tag`, `Label` a `Category` ide iba o vysvetľujúce pracovné rozlíšenie. Accepted glossary ich nezavádza ako samostatné EOS objekty; review im neprideľuje kontrakt ani identitu.

| Pojem | Akú otázku zodpovedá | Identita / vnorenie | Umiestnenie | Zdroje a overenie |
| --- | --- | --- | --- | --- |
| Classification | Do ktorej riadenej kategórie objekt patrí? | Bez vlastného ID; vnorené použitie CLS | Knowledge Core | SourceLink podmienene áno; vlastný verificationStatus nie |
| Condition | Za akých okolností táto znalosť platí? | Bez vlastného ID; vnorená, CND je cieľ typu | Knowledge Core; typy v katalógoch | Implementovaný minimálny CDR-0004 zdroje a verificationStatus vylučuje; RFC-0001 §4.7 však pozná samostatne zdrojované podmienky |
| Property | Aká technická charakteristika sa opisuje? | Riadený význam PRP; nie konkrétna hodnota | Property Catalog, Knowledge Catalog | Definícia a jej zdroje na katalógovej položke; stav správy položky |
| PropertyRecord | Aké tvrdenie o tejto vlastnosti platí pre rodiča? | Bez vlastného globálneho ID; vnorený claim | Knowledge Core | Vlastné sourceLinks a verificationStatus podľa RFC-0001 §4.4 |
| Catalog Entry | Aký riadený význam identifikuje toto katalógové ID? | Vlastné ID, samostatná položka | Knowledge Catalogs fáza, Reference alebo Knowledge Catalog podľa významu | Zdroje podľa významu, vlastný lifecycle; presné verifikačné polia katalógov odložené |
| Reference Object | Na aký autoritatívny zdroj či referenčný význam sa odkazuje? | Vlastná identita; cieľ sa referencuje | Foundation referencie alebo budúce katalógy v Engineering Knowledge Layer | Zdroje podľa obsahu, lifecycle; konkrétne overenie podľa typu |
| Tag | Akým pomocným označením chcem objekt vyhľadať? | V EOS neurčené; nevytvárať identitu | Žiadny prijatý core ani katalógový kontrakt | Nepriznávať autoritu ani stav overenia klasifikácie |
| Label | Aký text sa má zobraziť? | Text sám nie je stabilné ID; prípadné pole | Zobrazovací text alebo názov riadený katalógom | Sám nepotvrdzuje zaradenie; prípadný pôvod patrí nositeľovi textu |
| Category | Akú triedu pomenúvame? | Žiadny samostatný Accepted objekt; v tomto kontexte význam cieľovej CLS položky | Ak ide o riadenú klasifikáciu, budúci Reference Catalog | Podľa pravidiel položky; neodvodzovať autoritu z názvu |
| Relationship | Aký vzťah spája objekty? | Teraz ID referencia alebo vnorená väzba; first-class REL odložené | Core pravidlá väzieb, neskôr príslušný kontrakt | Zdrojované väzby sú možné; vlastná identita a audit vyžadujú ďalšie rozhodnutie |

`evaluationMode` sa do Classification neodporúča: podľa RFC-0001 §4.7 určuje spôsob posudzovania Condition. Nie je to klasifikačná hodnota ani vlastnosť CLS položky.

`Designation` odpovedá na otázku, ako je objekt označený; jeho existencia je ďalším dôvodom nevkladať aliasy a voľné názvy do Classification. Rozdiel medzi CDR-0004 a širším zdrojovým modelom podmienok nie je dôkazom, že všetky Value Objects musia zakazovať zdroje. Tento review Condition nemení ani opätovne neschvaľuje.

## 11. Metadata Boundary

| Pole alebo metadáta | Odporúčanie | Architektonický dôvod |
| --- | --- | --- |
| `id` | Nie | ID CLS patrí cieľu, nie vnorenej inštancii |
| `revision` | Nie | Revízia použitia ide cez rodiča |
| `status` | Nie | Classification dedí lifecycle rodiča |
| Ostatné lifecycle a record metadata | Nie | Žiadna samostatná entita ani auditný záznam |
| `sourceLinks` | Áno, podmienene | Výslovná opora RFC-0001 §4.6; ich plošný zákaz nie je prijaté pravidlo |
| `verificationStatus` priamo na Classification | Nie | Výslovné pravidlo RFC-0002 §5.7 |
| `notes` | Vynechať z minima | Nie sú povinné podľa RFC. Bez samostatného účelu by duplikovali význam alebo interpretáciu |

SourceLink má vlastné `verificationStatus` už v existujúcom foundation kontrakte. Jeho vnorenie nemení Classification na objekt s vlastným verificationStatus. Zdrojové triedy N/L/P/V v SourceLink nie sú klasifikačné hodnoty CLS ani governance pôvod tohto dokumentu.

Poznámky nie sú zakázané architektúrou všeobecne. V tomto minimálnom návrhu sú nepotrebné; nemajú slúžiť ako náhradné kategórie, definície, citácie alebo stav. Interpretácia použitia zdroja má existujúce miesto v SourceLink, nie v novej paralelnej poznámkovej štruktúre.

## 12. Hierarchy Decision

Odporúčanie: odložiť parent/child taxonómiu, `path`, `level`, namespace a classification system do katalógového návrhu. Nepridávať ich do počiatočného vnoreného objektu.

Presný typ hierarchie nie je prijatý: review nepredpokladá strom, DAG ani automatické dedenie. Uloženie cesty v každej Classification by duplikovalo taxonómiu a spôsobilo nezhodu pri zmene zaradenia položky. Budúci katalóg má rozhodnúť cykly, viacerých rodičov a verzie; zobrazovacia cesta môže byť odvodená.

## 13. Multiple Classification Decision

Odporúčanie: jedna Classification odkazuje na presne jednu CLS položku. Viac klasifikácií reprezentovať ako pole Classification vlastnené rodičom, ak to jeho kontrakt potrebuje.

Toto je odvodený návrh minimálnej serializácie, nie už prijatá cardinality schéma. Review neurčuje názov rodičovského poľa, poradie, unikátnosť, primárnu kategóriu ani vzájomnú výlučnosť položiek. Rovnaké CLS v dvoch rodičoch nie je jedna zdieľaná inštancia; lokálne evidence môžu byť rozdielne.

## 14. Risks

| Priorita | Riziko | Opatrenie |
| --- | --- | --- |
| High | Vylúčenie sourceLinks podľa neplatného pravidla „Value Object nemá zdroje“ | Zachovať podmienené sourceLinks; reference-only zákaz by vyžadoval samostatnú korekciu RFC |
| High | Zámena dôkazu definície kategórie za dôkaz správneho zaradenia rodiča | Oddeliť katalógový význam a dôkaz použitia; overiť pokrytie tvrdenia v rodičovskom kontexte |
| High | Platný CLS pattern vydávaný za existujúci, správny alebo schválený cieľ | Výslovne reportovať iba štrukturálnu platnosť pred katalógom |
| Medium | Rovnaký externý kód v rozdielnych systémoch alebo vydaniach | Pred reálnym použitím vyžadovať jednoznačné mapovanie a historický význam v katalógu |
| Medium | Kopírovanie textu, aliasov a hierarchie do každého použitia | Jediná referencia; detailné významy a taxonómia v katalógu |
| Medium | SourceLink cesty prestanú ukazovať na správne zaradenie po zmene poľa rodiča | Pri rodičovskej integrácii určiť citovanie v konkrétnej revízii a pravidlá aktualizácie väzieb |
| Low | Zámena classificationId za vlastné ID | Výslovný opis cieľovej identity, zákaz koreňového id |

Nie je zistený Critical blocker. Riziká High sú ohraničiteľné zachovaním existujúceho evidence modelu a podmienok §16. Review neidentifikovalo nevyhnutný rozpor medzi Accepted dokumentmi: RFC-0002 a RFC-0003 povoľujú referenciu, ale nerušia zdrojovú povinnosť RFC-0001. Rozpor by vznikol pri implementácii plošného zákazu zdrojov.

## 15. Deferred Concepts

- Classification Catalog a reálne CLS položky.
- Katalóg klasifikačných systémov, externé kódy a namespace kontrakty.
- Presné mapovanie vydania, platnosti, revízií a náhrad položiek.
- Parent/child taxonómia, path, level, dedenie a mapovanie medzi systémami.
- Pravidlá násobnosti, exkluzivity a doménovej prípustnosti v rodičovských kontraktoch.
- Textové aliasy a zobrazovacie názvy spravované katalógom.
- Samostatný klasifikačný rozhodovací proces, automatické klasifikovanie a first-class Relationship.

Odloženie neznamená schválenie týchto objektov, názvov alebo polí. `Tag`, `Label` a `Category` nezískavajú týmto dokumentom nové autoritatívne definície.

## 16. Implementation Preconditions

Následná jednoduchá implementácia môže pokračovať za týchto presných obmedzení:

1. Použiť Value Object s jediným povinným `classificationId` a podmienene povinným `sourceLinks`. Neprijať plošný zákaz zdrojov ako implicitné architektonické pravidlo.
2. Zachovať RFC-0001 §4.6: klasifikácia z externého systému, normy alebo dokumentu potrebuje SourceLink. Nesmie sa automaticky predpokladať, že zdroj na rodičovi alebo na katalógovej položke spĺňa požiadavku na konkrétne použitie.
3. Oddeliť štrukturálnu kontrolu od kontextových pravidiel. Pred reálnym zdrojovaným použitím preukázať, kde sa kontroluje povinnosť a pokrytie SourceLink, jeho referenčná integrita a rodičovský kontext; chýbajúcu kontrolu nesmie nahradiť úspech standalone schémy.
4. Použiť Active CLS podľa EOS-003 cez centrálnu definíciu doplnenú až v implementačnom míľniku; nevytvoriť nový prefix. SourceLink opakovane použiť cez existujúci kontrakt, vrátane jeho vnoreného verificationStatus.
5. Nepridať vlastné ID, lifecycle, koreňový verificationStatus, evaluationMode, voľný text, enum hodnôt, notes ani hierarchiu.
6. Pred katalógom používať iba fiktívne štrukturálne príklady a testy. Neinterpretovať neexistujúci CLS cieľ, neprideľovať mu reálny externý význam a nehlásiť overenú klasifikáciu.
7. Jednu Classification obmedziť na jednu CLS referenciu. Rodičovské kolekcie a ich pravidlá riešiť pri príslušnom kontrakte.
8. Pred reálnymi dátami v `0.2B.2` uzavrieť jednoznačné mapovanie systému, kódu, relevantného vydania alebo platnosti a historické čítanie referencie.

Tieto podmienky nevyžadujú nový ADR ani zmenu EOS-003. Ak sa namiesto zachovania zdrojov zvolí striktne jednopólový kontrakt zakazujúci sourceLinks, treba najprv samostatne upraviť a znovu prijať dotknuté RFC podľa existujúceho lifecycle. Tento review takú zmenu nevykonáva.

## 17. Readiness Verdict

Jednoduchá implementácia je možná bez novej architektúry, ak dodrží §16. Referenčná forma aj podmienené zdroje majú oporu v Accepted dokumentoch. Preto sa neodporúča blokovať kontrakt čakaním na celý katalóg, ale ani schváliť neobmedzenú reference-only implementáciu bez evidence pravidiel.

Verdikt sa vzťahuje výlučne na pripravenosť návrhu Classification. Nemení globálny stav EOS-010, neukončuje celé `0.2B.1` a nezačína `0.2B.2`. Jediný výsledný verdict je uvedený na konci dokumentu za auditnou históriou.

## 18. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-09-07 | 0.1 | 0 | Codex | Pre-design review podľa Accepted RFC; odporúčaný klasifikačný odkaz s podmienenými SourceLink, katalógové hranice, riziká a implementačné podmienky; bez schémy alebo zmeny architektúry |
| 2026-09-07 | 0.1 | 1 | Codex | Doplnenie finálneho Classification kontraktu a implementačného výsledku; zachovanie existujúcej multiplicity SourceLink vrátane prázdneho poľa a odloženie katalógovej kontroly zdrojového pôvodu do 0.2B.2 |

## 19. Implementation Outcome

Implementovaný je embedded reference Value Object `Classification` vo fáze `0.2B.1.5`. Vlastní ho rodič a reviduje sa cez rodiča. Nie je samostatná entita, Reference Object ani Catalog Entry. JSON Schema zostáva iba serializačným kontraktom Accepted znalostného modelu.

### Final Field Model

| Pole | Štrukturálna povinnosť | Implementácia a význam |
| --- | --- | --- |
| `classificationId` | Povinné | String cez `common/identifiers.schema.json#/$defs/CLS`; formát `CLS-xxxxxx` identifikuje jednu budúcu Classification Catalog Entry, nie vnorenú inštanciu |
| `sourceLinks` | Nepovinné | Pole existujúcich `common/source-link.schema.json` objektov cez `$ref`; bez lokálnej redefinície |

Schéma: `schemas/knowledge-core/classification.schema.json`, canonical ID `https://eos.local/schemas/knowledge-core/classification.schema.json`. Discovery: `schemas/index.schema.json#/$defs/classification`; index prijíma kolekciu `classifications`.

Pre `sourceLinks` sa zachováva multiplicita existujúceho `common/metadata.schema.json`: nula alebo viac položiek, bez požiadavky `uniqueItems`. Pole môže byť vynechané alebo prázdne; `null`, iný typ a neplatné položky sú odmietnuté. Pôvodné odporúčanie neprázdneho poľa v §8 sa v tomto implementačnom profile nepoužilo, v súlade so zadaním zachovať existujúce pravidlá EOS. Ide o jedinú odchýlku od odporúčaného pre-design obmedzenia, nie od Accepted architektúry.

### Structural Invariants

JSON Schema Draft 2020-12 kontroluje typ object, povinné `classificationId`, centrálny CLS formát, typ a položky `sourceLinks` a `additionalProperties: false`. SourceLink vrátane svojich vnorených referencií a verificationStatus sa opakovane používa bez zmeny.

Classification nemá vlastné `id`, `status`, `revision`, lifecycle metadata, koreňový `verificationStatus`, `evaluationMode`, `notes`, textovú hodnotu, fallback, enum klasifikácií, kód systému ani hierarchiu. Predstavuje presne jednu klasifikáciu; viac zaradení tvoria viaceré Classification objekty vlastnené rodičom. Hierarchia patrí budúcemu katalógu.

### Application Boundary

RFC-0001 §4.6 stále sémanticky vyžaduje sourceLinks, ak klasifikácia pochádza z externého systému, normy alebo dokumentu. Zo samotného classificationId nemožno bez katalógu určiť pôvod. Preto sourceLinks nie sú univerzálne povinné a katalógová kontrola podmienenej povinnosti je odložená do `0.2B.2`, nie odstránená.

Zatiaľ sa nekontrolujú existencia CLS položky, aktívny stav, systém, kompatibilita s rodičom, hierarchia ani interný/externý pôvod. Ani prepínač existujúceho validátora `has_verifiable_claims` tento chýbajúci kontext nevytvára. Úspešný výsledok pre Classification je štrukturálny výsledok, nie overenie správneho zaradenia alebo referenčnej integrity voči budúcemu katalógu.

Nová aplikačná validácia nebola potrebná. `scripts/validation/` zostáva nezmenené. Existujúca rekurzívna kontrola formátu sourceReferenceId sa na vnorené SourceLink naďalej uplatňuje a môže vydať `reference_integrity.invalid_source_reference_id` popri schema chybe; nepotvrdzuje však existenciu SRC záznamu. Toto je zachované správanie, nie nová katalogizácia alebo detekcia pôvodu.

### Verification And Scope

Vstup implementácie: vetva `feature/phase-0.2b-knowledge-contracts`, HEAD `b333c80`, pracovný strom clean, 80 pôvodných testov úspešných. Nové pokrytie tvorí 4 platných a 26 neplatných fixtures a 12 testov. Kompletná sada 92 testov zahŕňa všetky predchádzajúce Knowledge Core regresie. Fixtures sú výhradne fiktívne štruktúry, nie autoritatívne CLS alebo SRC záznamy.

Implementačné kontroly zahŕňajú unittest, UTF-8, JSON syntax, Draft202012Validator.check_schema pre všetky schémy a vyriešenie lokálnych aj cross-file `$ref`. Akceptačným kritériom je úspech všetkých kontrol bez zmeny Accepted RFC, ADR, závislostí a predchádzajúcich kontraktov.

Skutočný výsledok verifikácie dňa 2026-09-07: `Ran 92 tests in 2.124s`, `OK`; 92 úspešných, 0 zlyhaní, 0 chýb a 0 preskočených. JSON syntax: 169 súborov PASS; `Draft202012Validator.check_schema`: 14 schém PASS; lokálne a cross-file `$ref`: 65 výskytov PASS; Python compile: 6 súborov PASS; UTF-8: 232 projektových súborov PASS. Runtime: Python 3.12.14, jsonschema 4.26.0, referencing 0.37.0. Schémy: 13 -> 14; ADR súbory: 17 -> 17 vrátane šablóny; RFC súbory: 4 -> 4 vrátane cross-review. Diff potvrdil nezmenené Accepted dokumenty, validačný kód, SourceLink, závislosti a všetky štyri predchádzajúce core schémy.

Dokončený je iba implementačný rozsah `0.2B.1.5`; celý `0.2B.1` zostáva rozpracovaný. Stav CDR je Review. Classification Catalog, reálne CLS položky, nové ADR/RFC, governance, PropertyRecord ani Observation nevznikli. `0.2B.2` nebola začatá. Konkrétna následná úloha katalógovej validácie je zaznamenaná v BACKLOG.md.

READY WITH CONDITIONS
