# CDR-0006 PropertyRecord Pre-design Review

Project: EOS – Engineering Operating System  
Contract Review ID: CDR-0006  
Contract: PropertyRecord  
Review type: Pre-design  
Version: 0.1  
Revision: 1
Status: Review  
Document basis: Accepted EOS architecture

## 1. Purpose

Určiť najmenší bezpečný budúci kontrakt `PropertyRecord` bez implementácie schémy a bez zmeny Accepted architektúry. Výstupom je odporúčanie pre `Phase 0.2B.1.6`, nie jej schválenie ani dokončenie.

## 2. Scope

Review pokrýva identitu, vlastníctvo, reprezentáciu hodnoty, kvalitu merania, podmienky, zdroje, verifikáciu a hranice voči katalógom, dôkazom a rozhodnutiam. Nevytvára dáta, prefixy, pravidlá katalógov, workflow ani nové kontrakty.

Preskúmané vstupy:

- `AGENTS.md` a `EOS-000_Development_Manifesto.md`.
- `EOS-003_Identification_and_Versioning.md`, `EOS-009_Architecture_Closure_Plan.md`, `EOS-010_Architecture_Readiness_Review.md`.
- Accepted `RFC-0001_Engineering_Property_Model.md`, `RFC-0002_Engineering_Object_Taxonomy.md`, `RFC-0003_EOS_Engineering_Glossary.md`.
- Accepted ADR-0014, ADR-0015 a ADR-0016; obsahové hranice podľa `ADR-0015_Establish_engineering_knowledge_layer.md` a `ADR-0016_Treat_observation_as_first_class_evidence_entity.md`.
- CDR-0001 Quantity, CDR-0002 ValueRange, CDR-0003 MeasurementQuality, CDR-0004 Condition a CDR-0005 Classification Pre-design Review vrátane následného implementačného spresnenia.
- Všetkých päť schém v `schemas/knowledge-core/`, spoločné schémy identifikátorov, `SourceLink`, lifecycle a metadát, `schemas/index.schema.json`.
- `scripts/validation/`, existujúce testy, `CHANGELOG.md`, `ROADMAP.md`, `BACKLOG.md`.

Pre-flight: vetva `feature/phase-0.2b-knowledge-contracts`, HEAD `aab5385`, čistý pracovný strom. RFC-0001 až RFC-0003 a ADR-0014 až ADR-0016 zostávajú Accepted. Existuje päť Knowledge Core schém; `PropertyRecord` ani Property Catalog nie sú implementované. Phase 0.2B.2 nezačala. Existujúcich 92 testov prešlo bez zlyhania alebo chyby. Tieto testy nepreukazujú funkčnosť ešte neexistujúceho `PropertyRecord`.

## 3. Authoritative Findings

`AUTHORITATIVE` znamená explicitné pravidlo Accepted dokumentu. `IMPLIED` je odvodenie alebo odporúčaná implementačná konkretizácia, nie nový autoritatívny výrok. `OPEN` označuje nerozhodnutý detail. `DEFERRED` označuje rozhodnutie alebo schopnosť odloženú do ďalšej vrstvy/fázy.

| Oblasť | Klasifikácia | Zistenie a autorita |
| --- | --- | --- |
| Typ objektu | AUTHORITATIVE | Embedded claim-like Value Object; RFC-0001 §4.4, RFC-0002 §5.4 a §16, RFC-0003 G-0024/G-0065. |
| Identita | AUTHORITATIVE | Nemá vlastné stabilné ID vnorenej inštancie; `propertyId` nie je ID záznamu; RFC-0001 §4.4, RFC-0002 §13.3. |
| Vlastníctvo a verzovanie | AUTHORITATIVE | Patrí rodičovskej entite; zmeny a história patria rodičovi, nie samostatnej evidencii PropertyRecord; RFC-0002 §5.4/§16, RFC-0003 G-0069. |
| Lifecycle | AUTHORITATIVE | Nemá plný vlastný record lifecycle, ale má vlastnú verifikáciu tvrdenia; RFC-0001 §4.4, RFC-0002 §12. |
| `propertyId` | AUTHORITATIVE | Povinný autoritatívny názov poľa; identifikuje katalógový význam vlastnosti cez aktívny `PRP-xxxxxx`; RFC-0001 §4.4, EOS-003 §2, RFC-0003 G-0079. |
| Typ a hodnota | AUTHORITATIVE | `valueType` je povinný. RFC-0001 §4.4 povoľuje viac reprezentácií vrátane `quantity` a `valueRange`; neurčuje kompletný enum ani presný union kontrakt. |
| Počiatočný union | IMPLIED | Presne jedna číselná forma s korešpondujúcim `valueType` je odporúčaný minimálny profil, nie doslovne prijaté pravidlo `oneOf`. |
| Podmienky | AUTHORITATIVE | Voliteľné `conditions` nesú podmienky platnosti; RFC-0001 §4.4. Implementovaný Condition je rodičom vlastnený Value Object. |
| Poradie a duplicity podmienok | OPEN | Accepted text neurčuje prioritu podľa poradia ani unikátnosť podľa `conditionTypeId`; nepovažovať ich za zavedené pravidlá. |
| MeasurementQuality | AUTHORITATIVE | Voliteľné `measurementQuality` patrí aj do PropertyRecord; RFC-0001 §4.3/§4.4. Výlučné presunutie do Observation by bolo v rozpore s touto možnosťou. |
| Zdroje | AUTHORITATIVE | `sourceLinks` je povinné pole; neprázdnosť je podmienená Review/Approved a overiteľným tvrdením; RFC-0001 §4.4, spoločné pravidlá zdrojov. |
| Verifikácia | AUTHORITATIVE | `verificationStatus` je povinný a odlišný od lifecycle rodiča; RFC-0001 §4.4. Existujúci enum je konkretizovaný v spoločnej schéme, nie nanovo definovaný týmto review. |
| Classification | AUTHORITATIVE | RFC-0001 §4.4 výslovne podporuje voliteľné singulárne `classification`. Jeho vynechanie z prvého profilu nie je zákaz v architektúre. |
| Observation | AUTHORITATIVE | Observation je dôkaz, nie rozhodnutie ani automatická zmena autoritatívneho tvrdenia; ADR-0016, RFC-0003 G-0015. |
| Decision | AUTHORITATIVE | Prijatie/povýšenie tvrdenia vyžaduje vedomý schvaľovací krok a audit; ADR-0015/0016, RFC-0002 §7. |
| Uložený Decision a evidence relationship | DEFERRED | Samostatný kontrakt a presná persistovaná väzba na konkrétnu vnorenú inštanciu nie sú podmienkou samotnej štruktúry; RFC-0002 §7, ADR-0016. |
| Property Catalog | AUTHORITATIVE | Autoritatívne definície, povolené hodnoty a doménové pravidlá patria katalógu; RFC-0001 §4.4/§5, RFC-0002 §9. |
| Katalógové kontroly | DEFERRED | Existencia a použiteľnosť PRP, rozmery, povolené formy, rozsahy a povinné podmienky čakajú na katalógy v 0.2B.2. |

## 4. Open Questions

1. Ako bude budúca rodičovská validácia odovzdávať lifecycle, identitu a cestu ku konkrétnemu tvrdeniu? Samostatný kontrakt nesmie chýbajúci kontext nahradiť stavom `verificationStatus`.
2. Aké evidence a oprávnenia budú presne potrebné na jednotlivé prechody VerificationStatus? Enum existuje, ale samotný enum nie je transition policy.
3. Ako bude katalóg určovať povolené `valueType`, potrebné podmienky, jednotky a zmysluplnosť MeasurementQuality pri intervalovom výsledku?
4. Ako sa budú vyhodnocovať kombinácie podmienok, konflikty a redundantné záznamy? Zatiaľ nevytvárať implicitný AND/OR engine ani prioritu podľa poradia.
5. Kedy doplniť nečíselné hodnoty a singulárne `classification`, a ako rozlíšiť klasifikáciu hodnoty od ostatného kontextu?
6. Ako adresovať historickú vnorenú inštanciu pri Decision/evidence väzbe bez pridania globálnej identity PropertyRecord?

Tieto otázky nevyžadujú opravu Accepted RFC/ADR pre obmedzený štrukturálny profil. Vyžadujú explicitné obmedzenia jeho použitia; nesmú byť vykázané ako vyriešená významová validácia.

## 5. Object Type Assessment

| Kandidát | Posúdenie |
| --- | --- |
| A. Value Object | Správna všeobecná kategória, ale nezachytáva vlastné zdroje a verifikáciu tvrdenia. |
| B. Embedded claim-like Value Object | Odporúčaný a autoritatívne potvrdený typ. |
| C. Entity | Nesprávne: vymýšľal by samostatnú identitu a správu záznamu. |
| D. Reference Object | Nesprávne: objekt nesie konkrétnu hodnotu/tvrdenie, nielen odkaz. |
| E. Aggregate | Nesprávne: transakčnú hranicu a vlastníctvo poskytuje rodič. |
| F. Samostatný Claim objekt | Neodôvodnené v tejto fáze; Claim zostáva konceptom. |

PropertyRecord nemá vlastné `id`, nezávislý lifecycle ani nezávislé verzie/revízie inštancie. Schválený obsah sa nemení potichu; jeho náhrada sa zachytí v histórii rodiča. Je nositeľom tvrdenia o vlastnosti, nie iba nesúvisiacim údajom podporujúcim iné tvrdenie. Nemá však samostatnú identitu entity Claim.

## 6. propertyId Semantics

Odporúčaný názov je výhradne `propertyId`, explicitne ustanovený v RFC-0001 §4.4. `PRP-xxxxxx` identifikuje Property Catalog Entry alebo stabilný katalógový význam vlastnosti. Neidentifikuje PropertyRecord inštanciu, jej vlastníka, Observation ani výslednú hodnotu. Rovnaké PRP sa môže opakovať u viacerých rodičov aj pri odlišných podmienkach.

`propertyEntryId` by síce zdôraznil katalógový cieľ, ale zbytočne by menil prijatý názov. `propertyName` ani voľný text nie sú alternatívnou identitou. `PRP` je Active v EOS-003; nie je potrebná jeho zmena ani nový prefix. Centrálna `identifiers.schema.json` zatiaľ neobsahuje PRP definíciu. Jej doplnenie podľa existujúceho EOS-003 je úloha budúcej implementácie, nie tohto review.

## 7. Value Model Assessment

| Kandidát | Význam a typová bezpečnosť | Rozšíriteľnosť a katalóg | Text, existujúce kontrakty a zložitosť |
| --- | --- | --- | --- |
| A. Quantity only | Jasný skalár, bezpečný typ. | Príliš úzky pre prijatú intervalovú reprezentáciu; rozšírenie bude potrebné skoro. | Bez voľného textu hodnoty, priame opätovné použitie Quantity, nízka zložitosť. |
| B. ValueRange only | Jasný interval, neprimerané modelovať každý skalár ako interval. | Rovnaké obmedzenie opačným smerom; katalóg musí rozlišovať skalár/interval. | Priame opätovné použitie ValueRange; sémantické kontroly hraníc zostávajú potrebné. |
| C. Exactly one quantity/valueRange | Jasná číselná alternatíva, bez dvoch súčasných hodnôt. | Dobrý základ; katalóg neskôr zúži povolenú alternatívu podľa PRP. | Bez voľného textu hodnoty, používa oba kontrakty; nízka až stredná zložitosť. Vyžaduje doplniť povinné `valueType`. |
| D. Numeric/text/boolean/referenceId | Typové vetvy sa dajú uzavrieť, ale význam textu a generickej referencie nie je vymedzený. | Predčasne široký profil; `referenceId` nie je schválené univerzálne pole PropertyRecord. | Text môže obísť katalóg; opakovanie unionu Condition nie je autorita pre PropertyRecord; vyššia zložitosť. |
| E. Generic value union | Bez uzavretých vetiev nebezpečný; aj s nimi zavádza nový obal. | Zmenil by prijaté adresovanie `quantity`/`valueRange` a cesty zdrojov. | Zbytočné vnorenie; nie je potrebné pre opätovné použitie schém. Neodporúča sa. |
| F. Tagged numeric union | Kandidát C s povinným `valueType` a väzbou na konkrétnu vetvu. | Zodpovedá povinným poliam RFC, rozšírenie je riadené verziou kontraktu. | Odporúčaný minimálny profil; jedna kontrolovaná redundancia typu a názvu poľa. |

Počiatočne odporúčame presne jednu formu `quantity` alebo `valueRange`, nie ľubovoľné JSON `value`. Text a boolean sú možnosti prijatej širšej architektúry, ale v tomto profile sa odložia. Voľný `referenceId` sa nepridá; jeho existencia v Condition nie je dôvodom na univerzálnu referenciu vlastnosti. Toto obmedzenie nezakazuje text v už existujúcich vnorených kontraktoch, napríklad `Condition.textValue` či `Quantity.notes`.

## 8. MeasurementQuality Placement

Voliteľné `measurementQuality` priamo v PropertyRecord je explicitne podporované RFC-0001 §4.4. Nie je povinné pre každý záznam a nepatrí výhradne do Observation. Má význam pri meranej, pozorovanej alebo reportovanej číselnej hodnote, pre ktorú je metrologická charakteristika známa; nie je mierou pravdivosti ľubovoľného tvrdenia.

Použiť existujúci kontrakt bez rozšírenia: `uncertainty`, `resolution`, `confidenceLevel` a doplnkové `notes` podľa CDR-0003 a schémy. Nepridávať odložené accuracy, metódu, zdroje ani workflow. MeasurementQuality nenahrádza dôkaz merania, prístroj alebo kalibračný dokument a nepredstavuje výrobnú toleranciu.

Pri `valueRange` môže charakterizovať reportovaný intervalový výsledok, ale nesmie sa automaticky interpretovať ako neistota oboch koncových bodov ani ako šírka intervalu. Konkrétna použiteľnosť a význam čakajú na metódu/katalógový kontext. Schéma môže overiť štruktúru, nie túto interpretáciu. Observation môže niesť pôvodnú kvalitu merania; PropertyRecord nesie kvalitu prijatého tvrdenia so zdrojovou dohľadateľnosťou, nie kópiu celého dôkazového záznamu.

## 9. Condition Multiplicity

Odporúčame voliteľné pole `conditions`, pole samostatných rodičom vlastnených Condition objektov. Viaceré podmienky sú prípustné a každá používa existujúci Condition kontrakt.

| Voľba | Rozhodnutie pre minimálny profil |
| --- | --- |
| Bez poľa | Neodporúča sa: nevyužilo by prijatú hranicu platnosti hodnoty. |
| Singulárne `condition` | Neodporúča sa: zbytočne obmedzí multiplicitu a odchýli sa od poľa odporúčaného RFC-0001 §4.4. |
| Voliteľné `conditions` array | Odporúčané; neprítomnosť alebo `[]` znamená, že nie sú zaznamenané podmienky, nie univerzálnu platnosť. |
| `minItems: 1` pri prítomnosti | Nepridávať bez vecného dôvodu; Accepted dokumenty takú povinnosť neurčujú. |
| Poradie | Zachovať poradie serializácie, ale nepripisovať mu prioritu alebo logický operátor. Sémantika vyhodnotenia nie je zavedená. |
| Unikátnosť | Nepridávať `uniqueItems` ani unikátnosť `conditionTypeId` ako nové doménové pravidlo. |

Opakované `conditionTypeId` nemusí byť chyba: môže sa líšiť hodnota alebo `evaluationMode`. Ani presnú duplicitu zatiaľ štrukturálne nezakazovať; nesmie sa interpretovať ako silnejší dôkaz alebo viacnásobná váha. Rozpor, redundancia a kombinovateľnosť podmienok patria neskoršej významovej validácii. Žiadny implicitný condition engine sa týmto review nevytvára.

## 10. SourceLinks Rules

Rozlišovať povinnosť poľa od povinnosti jeho neprázdneho obsahu:

- `sourceLinks` je vždy prítomné pole podľa RFC-0001 §4.4.
- Prázdne pole je štrukturálne platné. Rozpracované tvrdenie môže existovať bez dôkazu; tým sa nestáva overenou autoritatívnou znalosťou.
- Pri rodičovskom stave `Review` alebo `Approved` a overiteľnom technickom, výrobnom, dodávateľskom alebo obchodnom tvrdení musí existovať zdrojový odkaz podporujúci dané tvrdenie. Toto je aplikačné pravidlo s kontextom rodiča.
- Viac odkazov je prípustných. Zachovať spoločný SourceLink kontrakt bez nového obmedzenia multiplicity či `uniqueItems`.
- Normatívne alebo dokumentom podložené tvrdenie vyžaduje dohľadateľný zdroj. Jeho nepriloženie v Draft znamená chýbajúcu evidenciu, nie trvalú výnimku. Názov normy v texte nie je náhrada SourceLink.
- `verificationStatus` tvrdenia nie je rodičovské `status`. Nenahrádzať `Reviewed` za `Review` ani automaticky aplikovať lifecycle pravidlo podľa podobnosti názvu.

Presná matica dôkazových požiadaviek a prechodov podľa VerificationStatus je otvorená. Jej absencia neoprávňuje označiť záznam s `Approved` a prázdnymi zdrojmi za dôveryhodný. Samostatná štrukturálna validácia takého objektu nepreukazuje schválenie ani splnenie evidence policy.

Každý SourceLink sa opätovne použije zo `schemas/common/source-link.schema.json`, vrátane vlastného VerificationStatus, `sourceClass`, použitia a `supportedClaim` alebo `supportedField`. Platný formát `sourceReferenceId` ešte nedokazuje existenciu SourceReference, správnosť zdroja ani to, že podporuje uvedené tvrdenie. Nenahrádzať SRC identifikátorom Observation alebo dokumentu.

## 11. VerificationStatus Boundary

`verificationStatus` je REQUIRED. Použije sa existujúca definícia:

`https://eos.local/schemas/common/lifecycle-status.schema.json#/$defs/VerificationStatus`

Povolené hodnoty sú `Draft`, `Reviewed`, `Approved`, `Disputed`. Nezavádzať alternatívne stavy `Review`, `Accepted`, `Rejected` ani `Deprecated`. Tento zoznam je existujúci spoločný kontrakt; review nevytvára nové prechody.

Verifikácia patrí tvrdeniu, lifecycle a verzovanie patria rodičovi. Jednotlivé vlastnosti môžu mať odlišný stav overenia. String `Approved` nie je podpis, dôkaz právomoci schvaľovateľa ani audit rozhodnutia. Prechody a použitie overeného tvrdenia musia byť kontrolované aplikačnou/governance vrstvou.

## 12. Classification Boundary

Accepted RFC-0001 §4.4 podporuje voliteľné `classification` v singulári. Nemožno tvrdiť, že Classification v PropertyRecord architektúra zakazuje. Pre prvý číselný profil odporúčame jeho implementáciu odložiť; jednotné množné `classifications` nie je autoritatívne pole tohto objektu.

| Význam | Miesto/hranica |
| --- | --- |
| Klasifikovať rodiča | Pole rodičovskej entity; neplatí automaticky ako hodnota vlastnosti. |
| Klasifikovať definíciu vlastnosti | Property Catalog Entry; neopakovať definíciu v každom tvrdení. |
| Klasifikovať konkrétnu hodnotu | Možné budúce singulárne `classification` podľa RFC; vyžaduje explicitný vzťah k modelu hodnoty. |
| Klasifikácia ako kontext | Nesmie nepozorovane nahradiť Condition alebo zmeniť význam PRP. |
| Klasifikácia ako dôkaz | Samotné CLS nie je dôkaz; použitie zdroja patrí SourceLink. |

Existujúci Classification kontrakt sa nemení a nesmie sa automaticky vkladať iba preto, že už existuje schéma.

## 13. Claim / Observation / Decision Boundary

PropertyRecord vyjadruje konkrétne tvrdenie o vlastnosti; je claim-like uložením, nie samostatnou entitou Claim. Observation uchováva dôkaz, Derived Result odvodený výsledok. Ani jeden nie je rozhodnutím o platnosti alebo prijatí tvrdenia.

Observation ani Derived Result nesmú priamo a automaticky meniť autoritatívny PropertyRecord. Prípadná automatická príprava návrhu na review musí zostať návrhom, nie schváleným zápisom; tento dokument nezavádza taký workflow. Prijatie, odmietnutie alebo povýšenie dôkazov či výsledku do autoritatívnej znalosti vyžaduje Decision alebo ekvivalentný schválený governance mechanizmus s auditom podľa ADR-0016.

Autorita vyplýva z dohľadateľných zdrojov, overenia, oprávneného prijatia a histórie rodiča, nie zo samotnej prítomnosti PropertyRecord, PRP ID, úspešnej schémy alebo stringu `Approved`. Samostatný stored Decision kontrakt zostáva odložený. Nepridávať `decisionId`, `observationId`, vlastné Claim ID ani vnorený Observation aggregate do navrhovaného profilu. Konkrétna evidence väzba sa nesmie vymyslieť preťažením SourceLink.

## 14. Property Catalog Boundary

V 0.2B.1 môžu existovať štrukturálne PRP referencie ešte pred implementáciou katalógu, keďže EOS-003 už povoľuje stabilné PRP významy. Vo fixture budúcej implementácie smú byť len označené fiktívne identifikátory, nie neoverené reálne vlastnosti. Bez katalógu sa overí tvar ID, nie existencia alebo význam položky.

| Kontrola | Pred katalógom |
| --- | --- |
| Formát `propertyId` | Áno, podľa existujúceho EOS-003 a budúcej centrálnej definície. |
| Existencia/aktuálna použiteľnosť PRP | Nie. |
| Presne jedna forma a súlad s `valueType` | Áno, štruktúra profilu. |
| Povolená forma hodnoty pre konkrétne PRP | Nie, až pravidlá Property Catalog. |
| Štruktúra jednotky UNT | Áno, existujúci Quantity/ValueRange kontrakt. |
| Rozmerová a významová kompatibilita jednotiek | Nie, potrebuje Property a Unit Catalog; ani rôzne UNT automaticky neznamenajú nekompatibilitu. |
| Povinné Condition typy pre konkrétnu vlastnosť | Nie, Property a Condition Type Catalog. |
| Povolené doménové rozsahy | Nie; nezamieňať s všeobecným `minValue <= maxValue`. |
| Použiteľnosť MeasurementQuality | Štruktúra áno, konkrétna metrologická interpretácia nie. |

Phase 0.2B.2 musí dodať katalógový význam, nie iba rozšíriť regex. Nedostupné kontroly sa musia reportovať ako nevykonané, nie úspešné. Žiadne katalógové pravidlá ani jednotkové konverzie sa nemajú nahradiť hardcoded údajmi.

## 15. Candidate Models

| Kandidát zo zadania | Výsledok |
| --- | --- |
| A. `propertyId` + `quantity` + verifikácia/zdroje | Chýba povinný `valueType`; po doplnení stále zbytočne úzky skalárny profil. |
| B. Rovnaké s `valueRange` | Chýba `valueType`; interval nie je náhradou každého skalára. |
| C. Číselná alternatíva + podmienky/kvalita | Najbližší odporúčaniu, ale bez `valueType` by porušil RFC-0001 §4.4. |
| D. Vnorený generic `value` | Nepotrebný nový obal a nové autoritatívne cesty; nepoužiť. |
| E. C doplnený o povinný discriminator | Jediný odporúčaný model: tagged numeric union podľa §16. |

## 16. Recommended Minimal Model

Odporúčame uzavretý objekt s ôsmimi povolenými názvami polí: `propertyId`, `valueType`, `quantity`, `valueRange`, `conditions`, `measurementQuality`, `verificationStatus`, `sourceLinks`.

Povinné sú `propertyId`, `valueType`, `verificationStatus`, `sourceLinks` a presne jedna číselná vetva. Navrhované tokeny `valueType` sú `quantity` a `valueRange`, priamo zviazané s rovnomenným poľom. Token `quantity` má precedens v príklade RFC-0001; úplný dvojhodnotový enum je odporúčaná konkretizácia pre tento profil, nie tvrdenie, že Accepted RFC už definuje konečný enum.

`quantity`, `valueRange`, `conditions` a `measurementQuality` opätovne používajú existujúce kontrakty cez referencie. `conditions` a `measurementQuality` sú voliteľné. Bez všeobecného `value`, root `unitId`, identít inštancie, lifecycle metadát alebo voľných rozširujúcich polí.

Minimálny záznam teda obsahuje päť polí: štyri vždy povinné a jednu hodnotovú vetvu. Táto špecifikácia je návrh budúceho kontraktu, nie schéma ani potvrdenie implementácie. Rozšírenie o nečíselné formy bude riadená zmena kontraktu a kompatibility klientov; nesmie sa dosiahnuť povolením ľubovoľného JSON.

## 17. Field Requirement Matrix

| Pole | Kategória | Pravidlo pre odporúčaný profil |
| --- | --- | --- |
| `propertyId` | REQUIRED | Referencia PRP na vlastnosť, nie ID inštancie. |
| `valueType` | REQUIRED | `quantity` alebo `valueRange`, musí súhlasiť s jedinou prítomnou vetvou. |
| `quantity` | CONDITIONALLY REQUIRED | Povinné iba pre `valueType = quantity`; pri druhej vetve zakázané. |
| `valueRange` | CONDITIONALLY REQUIRED | Povinné iba pre `valueType = valueRange`; pri druhej vetve zakázané. |
| `textValue` | DEFERRED | Podporované širším RFC, nie prvým číselným profilom. |
| `booleanValue` | DEFERRED | Rovnaké obmedzenie počiatočného rozsahu. |
| `referenceId` | REJECTED | Bez autoritatívne určeného cieľa a významu pre PropertyRecord. |
| `conditions` | OPTIONAL | Array existujúcich Condition; `[]` prípustné, bez novej unikátnosti. |
| `measurementQuality` | OPTIONAL | Existujúci kontrakt; použitie len so zmysluplným metrologickým významom. |
| `verificationStatus` | REQUIRED | Existujúci VerificationStatus enum. |
| `sourceLinks` | REQUIRED | Array existujúcich SourceLink; neprázdnosť je kontextová povinnosť, nie všeobecné `minItems`. |
| `classification` | DEFERRED | Singulárne pole povolené RFC, zatiaľ mimo číselného profilu. |
| `classifications` | REJECTED | Nová pluralita bez definovaného významu v tomto kontrakte. |
| `notes` | DEFERRED | Nepridávať koreňový textový únik z modelu; nemení existujúce vnorené notes. |
| `cachedDisplayName`, `designation`, `method`, `normReferenceIds`, `confidenceLevel` | DEFERRED | Možnosti širšieho RFC, nie povinnosti prvého profilu; neduplikovať metrologický confidenceLevel. |
| `id`, `schemaVersion`, `recordVersion`, `revision`, `status` | REJECTED | Inštancia nie je samostatný record; verzovanie a lifecycle patria rodičovi. |
| `value`, root `unitId`, `propertyName`, `decisionId`, `observationId` | REJECTED | Nepotrebný obal, duplicita identity/jednotky alebo zatiaľ nedefinovaná väzba. |

`DEFERRED` neznamená aktuálne povolené rozširujúce pole; budúci uzavretý profil ho zatiaľ odmietne.

## 18. Validation Boundary

| Vrstva | Predpokladané kontroly |
| --- | --- |
| JSON Schema | Object, povinné polia, uzavreté názvy, formát PRP cez centrálnu definíciu, enum `valueType`, presne jedna vetva a jej súlad s typom; referencie na Quantity/ValueRange/Condition/MeasurementQuality/SourceLink/VerificationStatus; array a vnorené štruktúry. |
| EOS application validation | Existujúce významové invarianty vnorených kontraktov: poradie hraníc ValueRange, nezáporná uncertainty, kladná resolution, konečné čísla; zdrojová povinnosť s explicitným kontextom rodiča; presné cesty chýb a rozlíšenie od `schema_validation`. |
| Property/Unit/Condition Catalog-aware validation v 0.2B.2 | Existencia a použiteľnosť položiek, povolený typ hodnoty pre PRP, dimenzie a jednotky, potrebné podmienky, doménové rozsahy, metrologická a klasifikačná kompatibilita. |
| Decision/workflow neskôr | Právomoc a audit schválenia, prechody verifikácie, kvalita/dostatočnosť dôkazov, prijatie a povýšenie tvrdenia, historická väzba na rodiča a jeho revíziu. |

Konkrétna implementačná medzera je overená v `scripts/validation/validator.py`: `_validate_value_range_rules` a `_validate_measurement_quality_rules` sa spúšťajú iba pri presnom top-level `schema_id` daného kontraktu. `$ref` prenáša štrukturálne kontroly, nie tieto aplikačné pravidlá. Pri budúcom PropertyRecord preto nemožno sľúbiť správnu vnorenú sémantiku iba zaregistrovaním schémy. To sa týka aj ValueRange vnoreného v Condition.

`_validate_source_links_rule` číta top-level `status` a vstupné `has_verifiable_claims`; PropertyRecord vlastné `status` nemá. Budúca implementácia musí explicitne prenášať rodičovský kontext alebo jasne oddeliť samostatnú štrukturálnu validáciu od kontextovej. Nesmie kontext odhadovať zo samotného `verificationStatus`.

Rekurzívna kontrola konečnosti čísel už existuje. `_validate_source_link_ids` kontroluje formát SRC aj vnorených odkazov, nie existenciu autoritatívnych záznamov; názov kategórie `reference_integrity` nie je dôkaz kompletnej referenčnej integrity. Kontrola obsahu a kompatibility zdroja vyžaduje dostupný register a kontext.

Budúce kompozičné aplikačné kontroly majú opätovne používať existujúce pravidlá s vedomím schémy a úplnou cestou, nie detegovať typ objektu iba podľa podobných názvov polí. V tomto review sa kód ani testy nemenia a uvedené medzery sa nepovažujú za opravené.

## 19. Risks

| Priorita | Riziko | Odporúčaná kontrola |
| --- | --- | --- |
| High | Vynechanie `valueType` alebo nesúlad typu a hodnoty. | Povinný discriminator a uzavretá číselná alternatíva. |
| High | Vnorené ValueRange/MQ obídu aplikačné invarianty. | Pred dokončením implementácie doplniť kompozíciu pravidiel a regresie vnorených ciest. |
| High | Zdrojová povinnosť sa stratí pri absencii root `status`. | Explicitný kontext rodiča; `sourceLinks` nesmie byť voliteľné všade. |
| High | Úspešná schéma alebo `Approved` sa vydáva za autoritatívnu znalosť. | Oddeliť dôkaz, verifikáciu, rozhodnutie a audit; žiadne automatické povýšenie. |
| High | Syntaktické PRP/UNT sa považujú za existujúce a kompatibilné položky. | Reportovať neuskutočnené katalógové kontroly a nepoužiť záznam ako overený vstup enginu. |
| Medium | PropertyRecord sa zmení na univerzálny objekt pre všetko. | Malý uzavretý profil, odložené nepovinné rozšírenia. |
| Medium | Voľný text obíde katalógový význam. | Bez root textValue/notes v prvom profile; nepreceňovať štrukturálnu validáciu textu v Condition. |
| Medium | Duplicitné Observation a workflow metadáta. | Nevkladať dôkazový aggregate ani lifecycle do claim-like Value Object. |
| Medium | Neistota sa zamieňa s toleranciou alebo intervalom prijateľnosti. | Zachovať MeasurementQuality boundary a katalógovo/metodicky podmienený význam. |
| Medium | Nestabilný union a nadmerné vnorenie. | Priame pomenované vetvy, žiadny generický obal; budúce zmeny riadiť verziou kontraktu. |
| Medium | Poradie/duplicity Condition dostanú náhodný význam. | Žiadne implicitné priority, agregovanie váh ani nový condition engine. |
| Low | Premenovanie `propertyId` alebo pluralizácia classification. | Zachovať prijaté názvy; nepoužívať synonymá v kontrakte. |

Nezistený Critical rozpor v Accepted architektúre pre odporúčaný obmedzený profil. High riziká sú podmienky implementácie a použitia, nie dôvod na tichú zmenu RFC.

## 20. Deferred Concepts

- Property, Unit, Condition Type a Classification Catalog vrátane reálnych položiek a doménových pravidiel.
- Nečíselné vlastnosti, singulárne `classification`, designation, method a ďalšie nepovinné polia širšieho modelu.
- Condition engine, porovnávanie a normalizácia jednotiek, konverzie a doménové tolerancie.
- Stored Decision, Claim identita, persistovaná evidence relationship a konkrétne schvaľovacie workflow.
- Automatické návrhy tvrdení z Observation/Derived Result, inference a použitie v enginoch.

## 21. Implementation Preconditions

1. Samostatne schváliť tento minimálny profil: povinné štyri polia, tagged numeric union, voliteľné conditions/MQ a odložené rozšírenia. Review nie je implementačné povolenie.
2. V budúcej úlohe doplniť centrálnu PRP definíciu podľa už aktívneho EOS-003, bez nového prefixu alebo governance zmeny.
3. Pri implementácii zabezpečiť kompozíciu existujúcich aplikačných invariantov vo všetkých povolených vnorených kontraktoch a otestovať presné cesty; nemení sa ich význam.
4. Určiť rozhranie explicitného kontextu rodiča pre zdroje. Bez kontextu reportovať len vykonaný rozsah, nikdy plnú evidence/lifecycle validáciu; neodvodzovať ho z VerificationStatus.
5. Udržať katalógové a rozhodovacie kontroly výslovne odložené. Štrukturálne platný záznam nesmie dostať implicitnú autorizáciu na výrobu, kalkuláciu alebo autoritatívny zápis.
6. Budúce testy musia pokryť diskriminátor, chýbajúcu/zdvojenú hodnotu, zdroje s rodičovským kontextom, vnorené sémantické chyby a regresie všetkých piatich existujúcich kontraktov. V tejto úlohe sa nevytvárajú.

Bezpečný rozsah 0.2B.1.6 je uzavretý štrukturálny PropertyRecord profil, jeho registrácia, fiktívne fixtures, testy a nevyhnutná kompozícia už existujúcich aplikačných pravidiel. Nie je ním implementácia katalógov, rozhodovacieho workflow ani automatické uznanie znalosti. Nie je potrebná zmena Accepted RFC/ADR, pokiaľ sa dodržia tieto obmedzenia.

## 22. Readiness Verdict

Odporúčanie je podmienečne pripravený číselný kontrakt. Autorita jednoznačne určuje typ objektu, `propertyId`, povinné `valueType`, verifikáciu a zdroje. Nevyžaduje opravu architektúry; presný počiatočný union a odloženie nepovinných foriem sú implementačná konkretizácia na schválenie.

Podmienky sú explicitne uvedené v §21. Najdôležitejšie sú zachovanie povinného `valueType`, vnorená aplikačná validácia a prenášanie rodičovského kontextu zdrojov. Katalógová pravdivosť a rozhodovacia autorita zostávajú mimo tohto kontraktu. Phase 0.2B.2 nezačala.

### Implementation Outcome

Phase 0.2B.1.6 implementuje odporúčaný profil bez odchýlky od CDR:

- finálne polia: `propertyId`, `valueType`, `quantity`, `valueRange`, `measurementQuality`, `conditions`, `verificationStatus`, `sourceLinks`,
- vždy povinné: `propertyId`, `valueType`, `verificationStatus`, `sourceLinks`,
- presne jedna podmienečne povinná vetva: `quantity` alebo `valueRange`, viazaná na `valueType`,
- voliteľné: `measurementQuality` a `conditions`; prázdne polia `conditions` a `sourceLinks` sú štrukturálne prípustné,
- centrálna definícia `PRP-xxxxxx` bola doplnená podľa existujúceho EOS-003; Property Catalog ani reálne PRP položky nevznikli,
- existujúce významové pravidlá ValueRange a MeasurementQuality sa rekurzívne aplikujú aj pri vnorení v PropertyRecord; rovnaká orchestrácia pripravuje Condition na budúce významové pravidlá,
- kontextová povinnosť neprázdnych zdrojov, katalógová kompatibilita a rozhodovacie workflow zostávajú odložené.

Kontrakt je dostupný v `schemas/knowledge-core/property-record.schema.json` a cez centrálny index. Implementácia nemení Accepted RFC/ADR a neposkytuje autoritu tvrdeniu iba na základe úspešnej štrukturálnej validácie alebo hodnoty VerificationStatus.

## 23. Change History

| Dátum | Version | Revision | Autor | Zmena |
| --- | --- | --- | --- | --- |
| 2026-09-08 | 0.1 | 0 | Codex | Pre-design review PropertyRecord nad Accepted architektúrou a piatimi existujúcimi kontraktmi; odporúčaný minimálny číselný profil, hranice validácie a podmienky budúcej implementácie. Bez zmeny existujúcich kontraktov. |
| 2026-09-08 | 0.1 | 1 | Codex | Zaznamenanie implementačného výsledku: uzavretý číselný profil, centrálny PRP formát, registrácia schémy, fixtures, testy a rekurzívna aplikácia existujúcich vnorených významových pravidiel. Status zostáva Review. |

READY WITH CONDITIONS
