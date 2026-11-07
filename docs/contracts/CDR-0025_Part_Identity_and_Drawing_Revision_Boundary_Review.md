# CDR-0025: Identita dielu a hranica revízie výkresu

Project: EOS – Engineering Operating System  
Contract Review ID: CDR-0025  
Review type: Doménové rozhodnutie pred návrhom kontraktu  
Version: 0.1  
Revision: 1  
Status: Review  
Document basis: Existujúca architektúra EOS a používateľom prijaté doménové rozhodnutia PI-0001 a PI-0002

## Účel a kontext

Keď sa zmení výkres, môže ísť o nový súbor, nové vydanie dokumentu, nové vydanie definície toho istého dielu alebo o iný diel. Pre kalkulanta je podstatné, **ktoré požiadavky platili pri vydaní jeho ponuky**. Cieľom nie je rozhodnúť podľa názvu súboru ani zaviesť entitu Part.

CDR-0024 a anonymizovaný prípad 001 boli pri review lokálnymi návrhmi mimo hlavnej vetvy. Sú nenormatívnym kontextom, nie autoritou pre názvy, identitu alebo zhodu položiek. Základ posúdenia: main po PR #8, `f0aeec5`.

## Inventár terminológie a precedensov

| Výraz | Čo už EOS rozlišuje | Kolízia, ktorej sa treba vyhnúť |
| --- | --- | --- |
| Part, component, engineering item, manufactured item; diel, komponent | V inventári RFC-0002 a slovníku RFC-0003 nie je stanovený preferovaný názov pre stabilnú definíciu hotového dielu. Komponent môže označovať aj rolu v zostave. | „Diel“ je tu pracovný názov. Nie je to jeden vyrobený kus, položka formulára ani nový schválený typ. |
| Item, product, workpiece; položka, výrobok, obrobok | Položka má význam podľa vlastníka (napr. katalóg); predmet ponuky a fyzický obrobok nie sú tým istým ako opakovane použiteľná definícia. | Obchodný produkt môže zoskupovať viac vyhotovení; jednotlivý kus môže mať históriu kontroly. Ani jedno neurčuje identitu návrhu. |
| Stock, StockMaterial, Material | RFC-0003 G-0048 odlišuje polotovar od materiálového pojmu. | Forma vstupu ani šarža nenahrádza definíciu výstupu. |
| Drawing, document, DocumentRecord | EOS-005 §3 pracuje s výkresmi, modelmi a špecifikáciami; EOS-004 pri Job uvádza drawingReferences. DocumentRecord eviduje riadený dokument. | Výkresový odkaz zákazky nie je dôkazom zhody dielov. Číslo zákazníckeho výkresu nie je automaticky interné ID dokumentu. |
| Revision, issue, version | EOS-003 §5, ADR-0007, RFC-0003 a document-record.schema.json odlišujú verziu/revíziu záznamu od údajov o dokumente. | Vydanie dokumentu, technická revízia a obchodná verzia ponuky majú rôznych vlastníkov. |
| Variant, configuration | V posudzovaných kontraktoch nie je pravidlo pre identitu variantu hotového dielu. | Konfigurácia môže označovať presnú zostavu požiadaviek; nie je synonymom alternatívne objednateľného dielu. |

ADR-0004 oddeľuje stabilnú identitu od názvu súboru. CDR-0015/0016: Material nie je obchodný názov ani zásoba; CDR-0017/0018: Supplier je organizácia, nie jej ponuka; CDR-0019/0020: ManufacturingProcess je opakovateľná metóda, nie jej vykonanie; CDR-0021/0023: Machine je fyzická jednotka, nie model. Spoločný precedens: najprv určiť **čo** má pokračovať v čase, až potom porovnávať označenia. Žiadny z precedensov neurčuje, kedy zákazník schváli zámenu dielov.

## Oddelenie konceptov: prijatý model D

- **Stabilná technická identita** označuje jednu rozlíšiteľnú, opakovane špecifikovateľnú položku v riadenej línii návrhu. Nie celú rodinu, súbor, zásobu ani kus. Premenovanie ju nemení. Dva podobné návrhy nesplynú len preto, že sú zameniteľné v jednom použití.
- **Technické vydanie** je spätne a jednoznačne adresovateľná, po uvoľnení nemenná definícia daného dielu: požiadavky, aplikovateľné časti podkladov a ich presné vydania. Má vlastnú identitu vydania v rámci dielu; netreba rozhodnúť, či bude globálna alebo zložená. Dve uvoľnené revízie môžu súčasne platiť pre rôzne požiadavky.
- **Výkres** je dokument s vlastnou kontinuitou. Jeho číslo je v kontexte vydavateľa významný identifikátor, nie univerzálny kľúč dielu. Prečíslovanie môže zachovať dokumentovú identitu iba pri preukázanej kontinuite.
- **Vydanie výkresu** musí byť jednoznačne adresovateľné v rámci dokumentu. Samotné „A“, názov súboru alebo prepísateľná cesta nestačia. Pôvodné označenie dodávateľa sa nesmie potichu meniť na celočíselné EOS documentRevision.
- **Variant** je samostatne rozlišovaná alternatíva, nie nasledujúce vydanie. Keď výber ľavého namiesto pravého či jednej súbežne predpísanej alternatívy zmení požadovanú položku, potrebuje vlastnú stabilnú identitu. Príslušnosť k rodine je voliteľná väzba; spoločná rodina nepovoľuje zámenu.
- **Požiadavka na výrobu** vyberá vydanie a konkrétne množstvo či osobitné podmienky. **Obchodný riadok** určuje, čo bolo nacenené, za akých predpokladov a pre aké množstvo. Nevlastní technickú identitu.

**Rozhodovací test:** Zmenil sa len nosič alebo označenie? Zachovať diel. Je to autorizovaný následník v rovnakej línii, pričom staré požiadavky zostávajú adresovateľné a zámena je explicitne posúdená pre dané použitie? Zachovať diel, oddeliť technické vydania. Ide o samostatne vyberanú alternatívu alebo úmyselne iný nezameniteľný predmet? Nová identita. Ak chýba zámer, autorita alebo dôkaz použiteľnosti, nerozhodovať automaticky; zachovať obe evidencie oddelene. Nahradenie nie je totožnosť a neprepíše historický výber.

## Matica scenárov

S = SAME ENGINEERING IDENTITY; N = NEW ENGINEERING IDENTITY; R = REQUIRES GOVERNED DECISION. Hodnotí sa kontinuita dielu, nie právo použiť novšie vydanie v už prijatej zákazke.

| # | Zmena | Výsledok | Rozhodujúci princíp |
| --- | --- | --- | --- |
| 1 | Preklep v poznámke, bez zmeny významu | S | Nové vydanie dokumentu nemení požiadavku. |
| 2 | Opravená tolerancia pri rovnakom nominále | R | Mení sa prípustná množina kusov; overiť pôvodný zámer a akceptáciu. |
| 3 | Náhrada jednej triedy materiálu druhou | R | Autorizovaný následník a samostatná materiálová alternatíva sú rozdielne situácie. |
| 4 | Zmena priemeru otvoru | R | Posúdiť funkčné rozhranie aj rozsah schválenej zámeny. |
| 5 | Zmena požadovanej kvality povrchu | R | Môže meniť funkciu aj kritérium prevzatia; nestačí nezmenený tvar. |
| 6 | Zmena predpísaného tepelného spracovania | R | Zmena vlastnosti hotového výrobku nie je automaticky len zmena postupu. |
| 7 | Len rozloženie výkresu alebo razítko | S | Bez zmeny technickej požiadavky, vydania dokumentu sa naďalej rozlišujú. |
| 8 | Prečíslovanie pri doloženej migrácii dokumentov | S | Doložená kontinuita návrhu; zachovať staré referencie. |
| 9 | Nové číslo od zákazníka, funkčne zhodný komponent | R | Podobná funkcia nedokazuje spoločnú návrhovú autoritu ani identitu. |
| 10 | Rovnaké číslo výkresu, nová revízia | R | Číslo nedokazuje obsah zmeny; vyžaduje porovnanie vydaní. |
| 11 | Dve schválené revízie toho istého dielu súčasne | S | Požiadavka vyberá presné vydanie, nie automaticky najnovšie. |
| 12 | Ľavé a pravé vyhotovenie | N | Úmyselne rozlišované polohy; výber strany je výber položky. |
| 13 | Rovnaká geometria, dva odlišne predpísané materiálové varianty | N | Súbežné rozlíšené vyhotovenia, nie dva vstupy povolené jednou definíciou. Pri postupnej náhrade platí 3. |
| 14 | Rovnaký tvar a materiál, dve samostatne požadované tolerančné triedy | N | Rozlíšené alternatívy pri výbere. Ak ide o zmenu jednej požiadavky v čase, platí 2. |
| 15 | Iná vstupná forma pri nezmenenej schválenej definícii | S | Forma zásoby neurčuje diel. Ak je povinnou konštrukčnou požiadavkou, treba nové posúdenie. |
| 16 | Iná výrobná trasa, definícia nezmenená | S | Plán výroby nie je stabilná identita výrobku. |
| 17 | Iný dodávateľ | S | Samotná zmena organizácie nemení návrh; oprávnenie vyrábať posúdiť zvlášť. |
| 18 | Iný stroj | S | Pridelenie zdroja nie je definícia dielu. |
| 19 | Nový zákaznícky obchodný kód | S | Obchodný alias nemení technickú identitu. |
| 20 | Nový výkres po vydaní ponuky, dopad neznámy | R | O kontinuite rozhodne zmena obsahu. Pôvodná ponuka zostáva v každom prípade viazaná na starý základ. |

## Porovnanie modelov

A = hlavnou identitou je revízia dielu. B = stabilný diel + nemenné technické vydanie. C = stabilný diel + dokument a jeho vydanie, bez samostatného technického vydania. D = **B s nezávislými identitami dokumentov a ich vydaní**. Ide o koncepty, nie návrh štyroch tabuliek.

| Kritérium | A | B | C | D |
| --- | --- | --- | --- | --- |
| Stabilné referencie a história | Každá zmena pretrhne stabilný odkaz; treba doplniť líniu. | Línia a vydania explicitné. | Diel stabilný; jeho história roztrúsená po dokumentoch. | Línia dielu aj história jeho presných základov. |
| Ponuka a výroba | Možno pripnúť revíziu, ťažšie spájať objednávky toho istého dielu. | Obe pripnú technické vydanie. | Jeden výkres nestačí pri viacerých podkladoch. | Obe pripnú vydanie a osobitne požiadavky riadka. |
| Zákaznícke čísla, duplicity, viac dokumentov | Zvádzajú k tvorbe nových dielov. | Vydanie možno pripnúť, ale model sám nevysvetlí pôvod kópií. | Dobre eviduje dokumenty; nevyberá platnú kombináciu. | Rozlišuje vydavateľa, vydanie aj rozsah podkladov bez zlúčenia dielov. |
| Náhrada a súbežná platnosť | Náhrada môže vyzerať ako nový diel. | Následník a variant sa odlišujú. | Náhrada dokumentu nevyjadruje náhradu definície. | Následníctvo zostáva vo vlastnej línii; spätné použitie potrebuje rozhodnutie. |
| BOM, Job a Operation | Presné odkazy možné, stabilný komponent chýba. | Podporí stabilný komponent aj výber vydania. | Výber dielu možný, vykonávacia základňa neistá. | Komponent možno plánovať stabilne a vydať pre presnú konfiguráciu. |
| Kontrola a dôkazy | Pozná revíziu; význam dokumentácie neistý. | Pozná požadované vydanie, pôvod kritéria môže chýbať. | Pozná dokument, nemusí poznať položku či použiteľný detail. | Možno rozlíšiť požadované kritérium, jeho podklad a pozorovanú skutočnosť. |
| Cena zložitosti a riziko zámeny významov | Nízka na začiatku; revízia zastupuje diel. | Stredná; môže skryť dokumentovú identitu. | Stredná; revízia dokumentu zastupuje revíziu definície. | Vyššia pri vydaní; ani diel, dokument, ani transakcia nezastupujú ostatné. |

## Diel nie je výkres; technické vydanie nie je verzia záznamu

EOS-005 pripúšťa ako vstupy aj modely a špecifikácie. To podporuje návrh nepodmieňovať existenciu dielu výkresom; **nedokazuje**, že puzdrá boli definované bez výkresu. Pre uvoľnenie na výrobu musí byť základ každopádne dostatočný. Model má umožniť kombináciu modelu, výkresu a špecifikácie a tiež použitie časti jedného dokumentu pre viac položiek (napr. zostava a pozícia). Sú to testy použiteľnosti návrhu, nie tvrdenia o konkrétnych podkladoch prípadu 001.

**`recordVersion`/EOS `revision` ≠ engineering revision.** `schemaVersion` označuje kontrakt dát; `recordVersion` a `revision` sa týkajú evidovaného záznamu EOS. `DocumentRecord.documentVersion` a `documentRevision` opisujú riadený dokument. Oprava registračného údaja sama nevydáva nový výkres ani technickú definíciu. Naopak, nový schválený predpis môže zmeniť technickú definíciu aj pri nezmenenom výkrese. **Samostatná doménová identita technického vydania je potrebná**; samotná dvojica čísiel zo záznamu ju nepreukazuje. Cesta k súboru ani aktuálny obsah registra nie sú nemenný podklad.

## Skúška prípadu 001 a budúcich väzieb

Na preukázanie zhody treba oddelene doložiť: (1) vydavateľom potvrdenú väzbu externých označení na stabilný diel, (2) výber konkrétneho variantu, nie iba rodinu, (3) jednoznačné technické vydanie a relevantné vydania dokumentov vrátane pozície, (4) príslušný riadok a množstvo s jednotkou pre každý variant, (5) väzbu vydania ponuky na presný dopyt a jeho výnimky. Interných 48 kusov a externé tri riadky po 16 kusov preukazujú len rovnosť súčtov. **Spoločný diel, revízia, rozdelenie interného množstva aj cenový základ zostávajú nepotvrdené.**

Prijaté pravidlo: vydaný ponukový riadok odkazuje na **nemenný základ konkrétnej požiadavky**: presné technické vydanie dielu, použité dokumentové vydania (cez technické vydanie alebo ako výslovnú doplňujúcu požiadavku), množstvo, jednotku a prijaté výnimky/predpoklady. Nestačí odkaz na stabilný diel ani na „aktuálnu“ verziu dopytu. Pri neznámej revízii možno uchovať doručený podklad a stav neistoty; bez potvrdenia ho neoznačiť za presnú zhodu. Nové vydanie vedie k posúdeniu či novej ponuke, nie k zmene minulého riadka.

| Budúci kontext | Čo ostane dohľadateľné |
| --- | --- |
| CustomerRequirement, RequestLine | Pôvodná požiadavka, vybraný variant/vydanie a množstvo; nie automatické schválenie náhrady. |
| QuotationLine, SupplierOfferLine | Vlastná a prijatá ponuka sa viažu každá na svoj základ; ich rovnosť sa preukazuje, nepredpokladá. |
| Job, Operation | Výroba aj jej kroky odkážu na uvoľnený rozsah. Rovnaký cieľ možno vyrobiť rôznymi metódami a strojmi. Odhad a skutočný náklad zostávajú mimo dielu. |
| BOM | Vydanie zostavy rozlíši pozíciu, komponent a jeho povolené vydanie; zmena potomka neprepíše vydanú zostavu. |
| Inspection, Observation | Kritérium pochádza z vydania definície; čo sa zistilo na konkrétnom kuse je samostatný dôkaz. Observation sa nestáva definíciou. |
| Požiadavka na materiál | Predpis pre vydanie odkazuje na materiálový význam; odber polotovaru a skutočne použitá šarža sú iná väzba. |

## Zistenia a prijaté rozhodnutia

| ID | Priorita | Zistenie a stav |
| --- | --- | --- |
| PI-0001 | Critical | **CLOSED / Accepted.** Prijatý je model D: stabilný diel, jeho presné technické vydanie, samostatný výkres a vydanie výkresu majú odlišný význam. Vydaná ponuka zostáva viazaná na presné technické vydanie a podklady použité pri nacenení. Neskoršia revízia ich spätne neprepíše. |
| PI-0002 | High | **CLOSED / Accepted.** Pri nejednoznačnej zmene EOS nepredpokladá kontinuitu identity ani zameniteľnosť vydaní. Oboje musí v príslušnom rozsahu doložiť vlastník technickej definície. Pri zákazníckom návrhu musí rozhodnutie podložiť príslušná technická autorita zákazníka. |
| PI-0003 | High | Rovnaké číslo, súčet alebo funkcia nedokazujú identitu. **V tomto review vyriešené:** žiadne odvodené párovanie ani zmena vydanej ponuky. |
| PI-0004 | Medium | **DEFERRED.** Dokumentové označenia a viacpodkladové definície nemajú vyriešené ukladanie. Odložiť prefixy, tvar kľúčov a archiváciu do samostatného pre-designu po rozhodnutí. |
| PI-0005 | Low | **DEFERRED.** Part, EngineeringItem ani názov pre jeho vydanie nie sú týmto review schválené termíny. Názov vybrať až po rozhodnutí o význame. |

**Prijatý model identity: D (Accepted).** Schválenie sa týka významu identity, nie jej implementácie. Nevzniká schéma `Part`, nový prefix ani implementácia. Dokument čaká na kontrolu pred publikovaním.

## História zmien

| Verzia | Revízia | Zmena |
| --- | --- | --- |
| 0.1 | 0 | Prvý doménový rozbor: 20 scenárov, štyri modely a dve rozhodnutia na schválenie. |
| 0.1 | 1 | Zapísané schválenie PI-0001 a PI-0002; model D prijatý, PI-0004 a PI-0005 zostávajú odložené. |

READY FOR USER REVIEW BEFORE GIT PUBLISH
