# CDR-0028: EngineeringRelease v1 – zmrazený kontrakt a pripravenosť na implementáciu

Project: EOS – Engineering Operating System\
Contract Review ID: CDR-0028\
Contract: EngineeringRelease\
Version: 0.1\
Revision: 1\
Status: Accepted\
Document basis: CDR-0025/0026, RFC-0003 a rozhodnutia používateľa ER-0001 až ER-0005.

## 1. Účel

Kontrakt v1 eviduje autorizované technické vydania. Nie je pracovným postupom na tvorbu návrhov, schvaľovanie technických definícií ani správu dokumentov. Rozsah polí je zmrazený; implementácia nezačala.

## 2. Kontext

Základ: main po PR #12 (`812e909`). [CDR-0027](CDR-0027_EngineeringItem_Entity_Integration_Closure_Review.md) uzatvoril EngineeringItem: stabilná položka má aktívne EIT a žiadny spätný zoznam vydaní. Material, Supplier, ManufacturingProcess, Machine a EngineeringItem používajú spoločné evidenčné metadáta. Ich názvy, poznámky, klasifikácie a tvrdenia sa tým nestávajú povinnou výbavou inej entity. EOS-003 riadi identifikáciu; EOS-006/007 oddeľujú kontrolu štruktúry od kontextu. EOS-009/010 ani spoločné testy ADR-0017 nenahrádzajú rozhodnutie o obsahu kontraktu.

## 3. Rozhodovacia matica

| Stav | Zdroj a miesto | Význam | Dôsledok pre budúcu implementáciu |
| --- | --- | --- | --- |
| ACCEPTED | RFC-0003 rev. 4, G-0082/0083; CDR-0026 SPER-0001/0004 | Jedno presné autorizované vydanie práve jednej stabilnej položky. Dva nezávislé korene; položka môže existovať bez vydania. | Vydanie má vlastnú adresovateľnú identitu; odkazuje smerom k EIT, nie naopak. |
| ACCEPTED | CDR-0025 PI-0001/0003; CDR-0026 SPER-0002 | Diel, dokument, vydanie dokumentu a vydanie technickej definície nie sú totožné. Ponuka zachováva presný základ. Po uvoľnení zmena záväzného obsahu znamená nové ERL. | Žiadne odvodenie z aktuálneho výkresu alebo recordVersion. Administratívna oprava nesmie zmeniť minulé odkazy. |
| ACCEPTED | CDR-0025 PI-0002; CDR-0026 SPER-0005 | Kontinuitu a rozsah zameniteľnosti dokladá vlastník definície, pri zákazníckej definícii príslušná autorita zákazníka. Novšie vydanie neruší automaticky staršie. | Známe poradie, rovnaká geometria ani dátum nie sú povolením náhrady. |
| ACCEPTED | CDR-0026 SPER-0003, §10–11 | Vo v1 postačuje zachovaný presný externý základ, bez povinného výkresu či správy dokumentov. Predpis materiálu patrí doň; samotná URL nestačí. | Zachytiť vydavateľa, identitu, vydanie, použitý rozsah a možnosť získať alebo overiť ten istý obsah. |
| ACCEPTED | CDR-0026 §17–18; EOS-003 §2–3 | Názov EngineeringRelease; ERL-xxxx, presne štyri číslice; externý štítok nie je ID. EOS ID sa nerecykluje. | ERL zostáva Candidate. Formát `^ERL-[0-9]{4}$` sa v tejto úlohe neregistruje. |
| ACCEPTED | ER-0001 až ER-0004, táto revízia | Používateľ spresnil časovú presnosť, pripnutie podkladu, väzbu na EIT a presné polia. | Záväzné sú §5–14 a §24; predbežné možnosti z CDR-0026 ich nenahrádzajú. |
| DEFERRED | CDR-0026 §10–12, 14, 19 | Štruktúrované požiadavky, pravidlá použiteľnosti, správa súborov a vzťahy náhrady. | Žiadny nový všeobecný subsystém kvôli vydaniu. |
| UNKNOWN | CDR-0026 §20, prípad 001 | Konkrétne identity, zhoda vydaní a autorita pre párovanie nie sú doložené. | Nezakladať ERL ani pri zhodnom súčte množstiev. |

## 4. Čo identifikuje vydanie

Jeden ERL identifikuje jednu uvoľnenú definíciu jedného EIT, nie výkres, DrawingRevision, stabilný diel, editáciu EOS, obchodný riadok, výrobnú trasu ani operáciu. Historický odkaz sa nikdy potichu nepresmeruje na nástupcu.

## 5. Pridelenie ERL

EOS-003 žiada prideliť ID pred vytvorením autoritatívneho záznamu; neurčuje, či autorský koncept má byť vydaním. Registruje sa len **už autorizované** vydanie: overiť dôkaz, tesne pred prvým zápisom prideliť ERL a pevne ho zviazať so základom. Pri historickom importe môže byť autorizácia staršia než registrácia. Koncept pred autorizáciou nemá ERL. Ani zrušenie či archivácia záznamu neuvoľňuje pridelené ERL na opätovné použitie. Ak bol identifikátor rezervovaný pri zlyhanom zápise, nevrátiť ho do obehu; medzera v rade nie je vydanie. Opakovaný import rovnakého dokladu preveriť pred vytvorením ďalšej identity, nie párovať podľa štítka. Bez diskriminačného dôkazu registráciu zastaviť.

## 6. Hranica agregátu

EngineeringItem 1 → 0..N EngineeringRelease. Jediné vlastníctvo vo vydaní sú jeho údaje a hodnoty zachytávajúce podklady. Dokument, SRC, EIT ani budúca kontrola sa nestávajú deťmi vydania. Zmeny názvu položky sa nekopírujú do histórie. Žiadna úprava EngineeringItem.

## 7. Odkaz na položku

`engineeringItemId` je povinný odkaz na práve jeden existujúci EIT (rovnaká konvencia ako `classificationId`). Tvar ID sám nepreukazuje existenciu. Dnešný EOS stav položky nie je podmienkou platnosti ERL: overuje sa existencia, nie aktuálne Approved. Ani Deprecated či Archived nesmie zneplatniť historický odkaz. Historickú autoritu dokazujú `authorization` a `technicalBasis`. Bez kontextu nepotvrdzovať referenčnú integritu. Pri chýbajúcom cieli sa očakáva referenčná chyba na `$.engineeringItemId` s koreňovým ERL a hľadaným EIT, bez následnej chyby životného cyklu. Existujúca kontrola životného cyklu katalógových položiek nie je kontrolou existencie EngineeringItem. Ak budúci integračný mechanizmus tieto pravidlá neoddelí, konflikt treba pred implementáciou predložiť, nie obísť.

## 8. Dva životné cykly

| Situácia | Význam vo v1 |
| --- | --- |
| EOS Draft, definícia ešte neautorizovaná | Nie je EngineeringRelease; koncept mimo v1. EOS Draft s ERL je prípustný iba pri evidencii už autorizovanej definície, napr. čaká na kontrolu prepisu. |
| EOS Approved | Evidencia je schválená. Tento prechod nevytvára autorizáciu ani oprávnenie vyrábať. |
| Autorita uvoľnila definíciu | S preukázateľným predmetom, rozsahom a doloženým dátumom autorizácie je spôsobilá na registráciu podľa §5. |
| Definícia už neplatí pre novú prácu | Treba doložiť rozsah obmedzenia inde; samotné vydanie ostáva historickým faktom. |
| Historická ponuka ho používa | Naďalej číta pôvodné ERL aj podklady. Nepoužiť náhradu pri čítaní. |
| EOS Archived | Archivovaný záznam ostáva identifikovateľný a spätne dohľadateľný; nejde o zrušenie minulej autorizácie. |

Samostatné releaseState, releaseStatus ani authorizationState sú vylúčené. Príslušnosť ku kontraktu spolu s dokladom vysvetľuje, že **autorizácia nastala**, nie že vydanie je dnes použiteľné na každý účel.

## 9. Dôkaz autorizácie

V1 vyžaduje tri fakty v koreňovej hodnote `authorization`: kto v akej technickej právomoci uvoľnil definíciu, kedy a na základe ktorého presného dokladu. Vydavateľ výkresu, schvaľujúci útvar a editor EOS môžu byť traja rôzni aktéri. Doklad musí potvrdiť konkrétnu položku a celý vybraný súbor podkladov; samotný podpis na jednom z viacerých výkresov nestačí, pokiaľ jeho rozsah nie je doložený. Rovnaký dokument môže byť aj podkladom aj dokladom autorizácie, ak preukazuje obe skutočnosti. Žiadny fiktívny schvaľovateľ pri importe.

## 10. Čo zostáva nemenné

| Kategória | Pravidlo |
| --- | --- |
| A: zmrazené | ERL a cieľové EIT; členstvo, identita, presný obsah a rozsah podkladov vrátane označenia vydavateľa, ak existuje; autorita, význam dátumu/času autorizácie a obsah jej dôkazu. Zmena ktoréhokoľvek z týchto významov vyžaduje nové ERL. Staré odkazy sa nepresmerujú. |
| B: administratívne, s auditom | Správa stavu evidencie, recordVersion, revision, aktualizačné metadáta, čisto evidenčné doplnenie sourceLinks či presun archívnej kópie iba pri bajtovo totožnom obsahu, rovnakom SHA-256 a auditovanej zmene lokátora. Tá istá ERL; zachovať aj pôvodné hodnoty. Čas a autor vytvorenia sa bežne neprepisujú. |
| C: odvodené/neautoritatívne | Zobrazený názov položky, skratka revízie v používateľskom rozhraní, počet podkladov či zoradenie pre výpis. Neukladať ako záväzný základ. |

`schemaVersion` opisuje dátový kontrakt; migrácia smie meniť reprezentáciu iba bez zmeny významu a so zachovanou históriou. Kontrola jediného JSON záznamu **nevie** dokázať nemennosť voči minulému zápisu.

## 11. Voľba modelu technického základu

| Kandidát | Záver |
| --- | --- |
| Len root sourceLinks | Odkaz na zdroj a tvrdenie nevyžaduje presné vydanie, obsahový odtlačok ani úplnosť celej zostavy. Nestačí. |
| Iba zoznam ID SourceReference alebo DocumentRecord | SourceReference eviduje citáciu, môže mať URI/verziu, ale samotné SRC nepripne obsah. DocumentRecord má vlastnú registratúrnu a dokumentovú revíziu; nerieši platné časti rozličných externých podkladov. |
| Nová samostatná entita TechnicalSourceReference | Ďalší životný cyklus a identita nemajú pre v1 preukázanú potrebu. |
| **technicalBasis[] s vnorenou hodnotou** | Prijaté: pri vydaní uchovať kvalifikovaný dokumentový odkaz, identitu bajtov a rozsah. Rovnaký tvar použiť pre dôkaz autorizácie. Hodnota nemá vlastné EOS ID ani samostatný životný cyklus. |

**Zmrazený tvar podkladu a autorizačného dôkazu:** rovnaká uzavretá vnorená hodnota bez vlastnej EOS identity. Iné polia ani `null` sa nepripúšťajú.

| Pole | Typ a povinnosť | Význam |
| --- | --- | --- |
| issuer | neprázdny text, povinné | Identifikácia vydávajúcej autority v jej kontexte, nie editor EOS. |
| documentReference | neprázdny text, povinné | Identita dokumentu/modelu u vydavateľa; nie EIT. |
| sourceVersion | neprázdny text, voliteľné v tvare | Ak vydavateľ uvádza verziu/revíziu/issue, zachovať jeho označenie presne. Ak ho neuvádza, pole vynechať; nedopĺňať zástupné N/A, REV 0 ani UNKNOWN. |
| contentSha256 | 64 malých hexadecimálnych číslic, povinné | Overenie totožnosti zachovaného obsahu. Odtlačok sám nepreukazuje technickú autoritu. |
| archiveLocator | neprázdny text, povinné | Trvalý lokátor zachovanej a oprávnene dostupnej kópie; nie príkaz na automatické sťahovanie. |
| scope | neprázdny text, voliteľné | Keď sa uplatní celý podklad, vynechať; pri čiastočnom použití povinne určiť stranu, pozíciu, časť alebo ekvivalent. |

`archiveLocator` určuje, kde sa nachádza zachovaná kópia; `contentSha256` (SHA-256 presných bajtov, 64 malých hexadecimálnych číslic) umožní overiť totožnosť obsahu. Povinné sú obe hodnoty aj pre `authorization.evidence`. Pri chýbajúcom externom označení vydania identitu obsahu zaručuje zachovaná kópia a jej odtlačok. Ani samotná URL, ani samotný hash, ani opis v poznámke nenahradia overiteľný dôkaz. V1 nepredpisuje nový archívny subsystém.

## 12. Viac zdrojov

`technicalBasis`: 1..N, bez povinného výkresu. Napríklad model a samostatná špecifikácia môžu spolu postačovať. Každý prvok identifikuje svoj obsah nezávisle. Poradie zoznamu nedáva prioritu; identické duplicity neprinášajú ďalší dôkaz. Pri protirečení nevyberať posledný prvok: vyžiadať autorizované rozlíšenie rozsahu alebo doplňujúci riadený podklad. Pri neúplnom základe registráciu odmietnuť.

## 13. Označenie vydania

Root releaseDesignation vylúčiť z v1. Výkres môže mať štítok A a špecifikácia 02; zlúčenie do jedného štítka by pripísalo jednému dokumentu platnosť pre všetky. Označenie, ak existuje, patrí do `sourceVersion` konkrétneho podkladu. Prípadné budúce samostatné označenie celej definície musí pochádzať od jej autority; jeho zmena nesmie prepísať historickú identitu.

## 14. Dve úrovne pôvodu

Root `sourceLinks` je povinné pole spoločných metadát. Dokladá evidenciu ERL v EOS, nie technický obsah, dôkaz autorizácie, archív dokumentov ani každé technické tvrdenie. Platí všeobecná politika EOS: v Draft môže byť prázdne; v Review/Approved sa prítomnosť zdroja posudzuje podľa existujúcich pravidiel pre overiteľné tvrdenia. Žiadna výnimka pre ERL nesprísňuje Draft. Aj v Draft zostávajú `authorization` a `technicalBasis` povinné.

## 15–18. Materiál, tvrdenia, klasifikácia a voľný text

- **Materiál:** normatívny predpis ostáva v záväznom podklade. Štruktúrovaný MaterialRequirement aj materialId sú odložené; materiálový pojem, dodávateľská položka, zakúpený polotovar a skutočná tavba nie sú tento predpis.
- **PropertyRecord:** NOT OWNED / DEFERRED; EngineeringRelease v1 nevlastní PropertyRecord[]. Opisné tvrdenie nie je úplný záväzný rozmer/tolerancia. Čiastočný prepis by mohol skryť vynechané kritérium.
- **Classification:** NOT OWNED / DEFERRED; EngineeringRelease v1 nevlastní Classification[]. Stabilné zaradenie patrí EngineeringItem; rozsah použiteľnosti vydania nie je jeho kópia.
- **description, notes, name:** všetky EXCLUDED. Identita a dohľadateľný základ postačujú; voľný text nesmie byť alternatívnym miestom technického predpisu.

## 19–20. Náhrada a použiteľnosť

`supersedes`, `supersededBy`, `replaces`, `previousReleaseId`  , `nextReleaseId`, odkazy current/latest a `replacementScope` odložiť. Rovnaké EIT môže mať súbežne autorizované vydania pre rôznych odberateľov. Náhrada potrebuje autoritu, účel a rozsah. `effectiveFrom`, `effectiveTo`, `applicability`, `validFor` odložiť; čas uvoľnenia neurčuje zákazkovú účinnosť. Bez dokladu nemožno vyhlásiť použiteľnosť pre novú výrobu. Stiahnutie pre nové použitie nikdy nevymaže dôkaz o starom vydaní.

## 21–23. Tlakové skúšky

| Postup | Skúška dohľadateľnosti |
| --- | --- |
| Dopyt a ponuka | Potvrdený RequestLine vyberie presné ERL a nesie množstvo, jednotku a odchýlky. Vydaný QuotationLine zachová jeho nemenný základ vrátane ERL. Vydanie iného ERL zajtra neprepíše nacenený základ. Žiadna cena, množstvo ani „current release“ na koreni vydania. |
| Výroba | Job použije vybrané ERL; Operation pracuje v kontexte zákazky. ManufacturingProcess označuje opakovateľnú metódu a Machine konkrétnu jednotku. Trasa, sadzby, časy a výsledky merania nepatria do definície. |
| Prípad 001 (neautoritatívny) | Vnútri 48 kusov puzdier, externe tri výkresové riadky po 16. Bez dôkazu zostane pre každú väzbu **EIT = UNKNOWN, ERL = UNKNOWN**. Pred potvrdením nie je čo registrovať; 48 = 3 × 16 preukazuje iba číselnú rovnosť, nie zhodu dielov, vydaní, výkresov, revízií ani ponúk. Prípad nie je fixture. |

## 24. Zmrazená matica v1

R = REQUIRED, O = OPTIONAL, X = EXCLUDED. Podklad pre každý riadok je uvedený vpravo. Na koreni **14 R, 0 O**; 11 spoločných polí a 3 doménové. Obidva vnorené typy sú uzavreté. Ďalšie polia sa nepredpokladajú.

| Spoločné pole | Stav a typ | Meniteľné po uvoľnení? | Význam / zdroj |
| --- | --- | --- | --- |
| id | R, ERL | nie | Jedno presné vydanie; EOS-003, G-0083. |
| schemaVersion | R, verzia schémy | iba kompatibilná migrácia | Verzia kontraktu, nie vydanie; ADR-0007. |
| recordVersion | R, verzia záznamu | áno s auditom | Zmena evidencie; ADR-0007. |
| revision | R, nezáporné celé číslo | áno s auditom | Revízia evidencie; EOS-003. |
| status | R, EOS RecordStatus | áno s auditom | Stav registra podľa §8; spoločné metadáta. |
| createdAt | R, date-time | nie | Pôvodný čas registrácie; spoločné metadáta. |
| createdBy | R, text | nie | Pôvodný editor, nie vydávajúca autorita; spoločné metadáta. |
| updatedAt | R, date-time | áno | Čas evidenčnej zmeny; spoločné metadáta. |
| updatedBy | R, text | áno | Editor evidenčnej zmeny; spoločné metadáta. |
| sourceLinks | R, pole SourceLink podľa spoločných metadát EOS | iba evidenčný pôvod, auditovane | §14, ER-0003; prázdne v Draft je prípustné. |
| changeSummary | R, text | áno | Dôvod evidenčnej zmeny; spoločné metadáta. |

| Doménové pole | Stav a typ | Meniteľné po uvoľnení? | Význam / zdroj |
| --- | --- | --- | --- |
| engineeringItemId | R, jeden EIT | nie | Nezávislý koreň EngineeringItem, §7; SPER-0001. |
| technicalBasis | R, zoznam hodnôt §11, 1..N | nie, okrem čisto prevádzkového lokátora pri doloženej zhode | Presný základ jedného vydania; SPER-0002/0003, ER-0002. |
| authorization | R, jedna vnorená hodnota | nie, rovnaká výnimka pre lokátor dôkazu | Kto, kedy a na akom dôkaze uvoľnil tento základ; §9, ER-0001/0002. |

**`authorization` je uzavretý objekt s presne tromi povinnými poľami, bez voliteľných polí:**

| Pole | Typ a pravidlo |
| --- | --- |
| authority | Neprázdny text identifikujúci technickú autoritu tak, ako ju dokladá zdroj. Nie automaticky editor EOS; bez nového koreňa Person/Organization. |
| authorizedAt | Reťazec: platný ISO full-date alebo ISO date-time (RFC 3339 s pásmom). Zachovať doloženú presnosť: samotný deň sa uloží ako dátum, nie ako čas o polnoci. Ak nie je doložený ani deň, záznam ostáva mimo registra ERL. |
| evidence | Jedna zachovaná a overiteľná referencia v presnom tvare §11: rovnaké štyri povinné a dve podmienene uvádzané polia ako pri prvku technicalBasis. Dôkaz musí dokladať autorizáciu tejto definície, nie iba existenciu súboru. |

## 25. Vylúčenia a validácia

Všetky nepomenované polia sú mimo v1, najmä polia §13, §15–20, koreňové releasedBy/releasedAt, releaseState, riadky dopytu a ponuky, operácie, BOM a samotné súbory. Žiadny spätný zoznam vydaní na koreni EngineeringItem. Štrukturálne kontroly tvaru, povinností a kardinality možno neskôr vyjadriť v schéme. Existencia EIT/SRC vyžaduje kontext. Porovnanie so skorším stavom, trvalosť archívnej kópie, úplnosť definície, rozsah použiteľnosti a právomoc podpisujúceho vyžadujú dôkaz mimo samotnej schémy. Nevyhlasujeme tieto kontroly za dnes implementované. Nevyžaduje sa zmena významu spoločného validátora.

## 26. Zistenia

| ID | Priorita / stav | Rozhodnutie a riziko |
| --- | --- | --- |
| ER-0001 | Critical / CLOSED / Accepted with refinement | ID pri prvej registrácii už autorizovaného vydania; povinný doklad, dátum alebo časová pečiatka podľa presnosti zdroja. Bez dátumu nevytvoriť ERL. |
| ER-0002 | Critical / CLOSED / Accepted with refinement | Aspoň jeden presný podklad; zachovaná kópia, lokátor a SHA-256. Externá verzia je voliteľná iba ak ju zdroj nemá; auditovaný presun totožnej kópie nemení ERL. |
| ER-0003 | High / CLOSED / Accepted with refinement | Existujúci EIT bez požiadavky na dnešné Approved. Povinné root sourceLinks so spoločnou EOS politikou; žiadne osobitné pravidlo neprázdnosti v Draft. |
| ER-0004 | Medium / CLOSED / Accepted | Uzavretý koreň 14 R + 0 O (§24); bez PropertyRecord, Classification, názvu, poznámok a štruktúrovaného materiálového predpisu. |
| ER-0005 | Medium / CLOSED / Accepted | Náhrada, účinnosť a použiteľnosť sú vedome odložené. Súbežné vydania môžu existovať; čas autorizácie nie je všeobecný začiatok účinnosti. |

## 27–29. Pripravenosť, rozhodnutie a aktivácia

**EngineeringRelease v1 contract: FROZEN. Implementácia: NOT STARTED. ERL: Candidate.** Používateľ uzavrel ER-0001 až ER-0005. Root aj oba vnorené tvary sú presne vymedzené (§11, §24); nezostal otvorený význam poľa. Nasledujúce schválenie implementácie je samostatný krok. G-0083 ani EngineeringItem sa nemenia.

ERL zostáva **Candidate**. Prijatie matice neaktivuje identifikátory. Až po samostatnom poverení na implementáciu má nasledovať centrálna definícia, schéma a registrácia, skúšky s fiktívnymi podkladmi, overenie dátových aj referenčných hraníc, regresia a integračné uzatvorenie. Až úspešné uzatvorenie môže aktivovať ERL v EOS-003.

## 30. História zmien

| Verzia | Revízia | Zmena |
| --- | --- | --- |
| 0.1 | 0 | Prvý návrh presných polí a pravidiel pre evidenciu autorizovaného technického vydania; implementácia nezačala. |
| 0.1 | 1 | Prijaté ER-0001 až ER-0005 so spresneniami času, externej verzie, zachovaného obsahu, EIT a sourceLinks; zmrazený koreň aj vnorené hodnoty. Bez aktivácie ERL a implementácie. |

READY FOR USER REVIEW BEFORE GIT PUBLISH
