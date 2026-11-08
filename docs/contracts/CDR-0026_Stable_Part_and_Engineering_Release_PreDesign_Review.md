# CDR-0026: Stabilný diel a presné technické vydanie

Project: EOS – Engineering Operating System\
Contract Review ID: CDR-0026\
Review type: Doménový pre-design\
Version: 0.1\
Revision: 4\
Status: Review\
Document basis: Prijatý model D a rozhodnutia používateľa vrátane PI-0004 a PI-0005 (§17–18).

## 1. Účel

Určiť najmenšiu dvojicu zodpovedností, ktorá prežije zmenu výkresu bez straty odpovede na otázku: čo zákazník požadoval a čo sme vtedy nacenili? Tento dokument neprideľuje ID, neurčuje serializáciu a neoprávňuje implementáciu.

## 2. Kontext

Základ je main po PR #9 (`8f60132`). Autority: EOS-003 §2–5 (ID a verzie), EOS-006/007 (štruktúra, význam a hranice validácie), EOS-009/010 (uzatváranie rozhodnutí), RFC-0002/0003 (typy objektov a slovník), ADR-0004/0006/0007/0012/0015/0017. CDR-0015/0017/0019/0021 a implementované kontrakty rozlišujú materiál, organizáciu, metódu a fyzický stroj. Nedávajú pravidlo pre identitu výrobku. CDR-0024 bol posúdený v samostatnej pracovnej kópii; nie je súčasťou tohto main ani normatívnym vstupom.

## 3. Prijaté obmedzenia

[CDR-0025](CDR-0025_Part_Identity_and_Drawing_Revision_Boundary_Review.md) prijal model D: diel ≠ technické vydanie ≠ vydanie dokumentu; dokument má vlastnú kontinuitu. Zmena výkresu sama nemení diel. Uvoľnená ponuka ostáva viazaná na nacenený základ. Pri nejasnosti sa identita ani zameniteľnosť neodvodzuje. Dôkaz poskytuje vlastník technickej definície; pri zákazníckom návrhu ho musí podložiť príslušná technická autorita zákazníka. CDR-0025 ponechal počet koreňov otvorený; SPER-0001 túto otázku uzatvára.

## 4. Terminológia

| Výrazy | Použitie a hranica v EOS |
| --- | --- |
| Part, EngineeringItem, Item | EngineeringItem je prijatý doménový názov. Part bol pracovný kandidát; samotné Item nerozlišuje technickú identitu od riadka. |
| Component, Product, Workpiece | Komponent je rola v zostave; obchodný produkt môže pokryť viac dielov; obrobok je fyzický kus vo výrobe. Žiadny neurčuje kontinuitu návrhu. |
| Design, Definition | Návrh môže byť rozpracovaný. Definícia opisuje obsah, nie automaticky jeho schválenie či vydanie. |
| Revision, Version, Release, Issue | EOS-003 a RFC-0003 už používajú verziu a revíziu pre záznamy a dokumenty. Issue môže byť označenie vydania u vydavateľa; Release bez určenia predmetu môže znamenať aj publikovanie softvéru. |
| Variant, Configuration | Variant označuje zámerne rozlišovanú alternatívu. Konfigurácia je výber či kombinácia požiadaviek; nemusí to byť nová stabilná položka. |
| Drawing, Document | Výkres je technický dokument. DocumentRecord eviduje dokument; nevymedzuje všetky požiadavky na diel. |

Názvy boli prijaté v §18; ich slovníkové definície G-0082 a G-0083 sú doplnené v [RFC-0003](../rfc/RFC-0003_EOS_Engineering_Glossary.md), revízia 4 prijatá podľa ADR-0014.

## 5. Stabilná technická identita

Jeden stabilný identifikátor označuje jednu opakovane špecifikovateľnú technickú položku naprieč jej riadenými vydaniami. Nie kus, polotovar, SKU, objednávkový riadok, výkres alebo jeho revíziu, výrobnú trasu, rodinu ani triedu komponentov. Dva odkazy identifikujú tú istú položku, keď smerujú na tú istú riadenú identitu alebo keď príslušná autorita doložila mapovanie; samotná zhoda atribútov nestačí.

Položka môže existovať pred prvým vydaním aj bez výkresu. Nemožno ju preto automaticky považovať za uvoľnenú do výroby. Môže mať viac vydaní, aj naraz použiteľných pre rôzne rozsahy. Dve položky môžu mať rovnakú geometriu i spoločný výkres: rozhoduje zvolená položka, konkrétna pozícia a použiteľné požiadavky.

## 6. Technické vydanie

Jedno vydanie je jednoznačne adresovateľná, autorizovane uvoľnená definícia **práve jednej** stabilnej položky. Zahŕňa určitý obsah požiadaviek alebo jeho presné zdrojové vydania, vrátane rozsahu, ktorý z nich platí. Nie je to číslo výkresu, chronologická pozícia, nezáväzný návrh ani „najnovšie dostupné“. Diel nevlastní zoznam kópií vydaní; prijatá väzba vedie z vydania k dielu.

## 7. Kontinuita

Administratívne premenovanie, zmena obchodného kódu alebo vykonávacieho stroja zachováva identitu pri nezmenenom predmete. Samostatne vyberateľné, úmyselne odlišné vyhotovenia majú vlastné identity. Pri zmene funkcie, rozhrania alebo predpisu bez rozhodnutia o následníctve je výsledok **neurčený**, nie automaticky nový ani pôvodný diel. Kontinuita línie nie je povolenie vzájomne nahradiť jej vydania.

## 8. Nemennosť a životný cyklus

| Doménový stav alebo situácia | Navrhované správanie |
| --- | --- |
| DRAFT / REVIEW definície | Príprava a posudzovanie, nie použiteľná identita uvoľneného vydania. V1 nemusí evidovať autorské rozpracovanie. |
| RELEASED | Pri uvoľnení zmraziť odkaz na diel, technický obsah, označenie použité pri vydaní, rozsah a presné podklady; doložiť kto, kedy a s akou právomocou vydal. |
| SUPERSEDED | Nové vydanie môže nahradiť staré iba v doloženom rozsahu. Oznámenie o náhrade sa pripája osobitne, pôvodný obsah ostáva čitateľný. |
| WITHDRAWN / OBSOLETE | Zaznamenať autoritu, čas, dôvod a rozsah obmedzenia budúceho použitia. Nie je to výmaz, spätná zmena ani anulovanie historickej ponuky. |

Nejde o nové hodnoty EOS `status`. Ani EOS Approved neznamená technické uvoľnenie. **recordVersion a EOS revision ≠ technické vydanie.** Administratívny preklep napr. v zobrazení registra možno auditovane opraviť bez nového vydania iba mimo zmrazeného obsahu. Oprava požiadavky, záväzného podkladu alebo jeho rozsahu po vydaní vytvára nové vydanie aj pri rovnakom diele. Zámena nesprávne pripnutého výkresu „opravou metadát“ nie je prípustná. Zachovať pôvodnú vydanú podobu aj pri administratívnej oprave. Súbežnú použiteľnosť vyberá požiadavka podľa účelu a autorizácie, nie maximum dátumu či poradia.

## 9. Modely agregátov

| Model | Presný odkaz, dôkaz a použiteľnosť | História, súbežnosť a konzistentnosť |
| --- | --- | --- |
| 1. Diel vlastní vydania ako deti | Zložený odkaz cez diel môže stačiť pre ponuku, BOM a kontrolu, ak je dieťa nemenné. Value Object bez rozlíšiteľnej identity nestačí. Dôkazy a súbežné vydania musia byť spravované v rodičovi. | Jeden vlastník je prípustný iba ak deti nie sú korene. Archív rastie a nezávislé vydania sa zapisujú cez ten istý agregát. |
| 2. Dva samostatné korene | Vydanie referencuje jeden diel. Ponuka, BOM aj kontrola adresujú presné vydanie s vlastným dôkazom; paralelná platnosť nevyžaduje prepis dielu. | Archív oddelený od editácie názvu dielu; kontrola existencie dielu pri uvoľnení. Žiadny koreň nevlastní iný, v súlade s RFC-0002. |
| 3. Koreň je iba vydanie, diel je značka série | Presné odkazy vrátane BOM a kontroly fungujú. Pred prvým vydaním však chýba nositeľ identity. Pri súbehu sa môže líšiť názov či dôkaz spoločného pôvodu série. | Nezávislé zápisy dobre škálujú, ale náprava spoločných údajov vyžaduje register série alebo duplikáciu. Register s vlastným životným cyklom je už druhý kontrakt. |
| 4. Vydanie ako EOS história záznamu | Verzia registra nedokazuje vydanie vlastníkom návrhu ani presnú sadu podkladov. Ponuka, BOM či kontrola by záviseli od archívu prevádzkových opráv. | Každá oprava metadát by pôsobila ako technická zmena; nezávislá súbežná platnosť nemá bezpečný význam. Rozpor s CDR-0025. |

Prijatý je model 2: stabilná položka a technické vydanie sú dva samostatné korene agregátov. Vydanie má vlastnú stabilnú, adresovateľnú EOS identitu a vlastný dôkazový základ. Odkazuje na práve jednu stabilnú položku; nie je jej vnorenou históriou. Zmena položky nesmie kaskádovo aktualizovať ani vymazať vydania.

## 10. Predpis materiálu

„Má byť z materiálu X“ je požiadavka vydania. Material označuje materiálový význam, nie rozsah prípustných náhrad. Samotný odkaz na Material je vhodný cieľ pre jednoduchý predpis, ale bez kontextu nehovorí, či ide o povinný materiál, alternatívu alebo skutočne použitý materiál. PropertyRecord je tvrdenie, nie príkaz. Vo v1 je materiálový predpis súčasťou presného technického základu vydania, nie povinným PropertyRecord. Samostatný štruktúrovaný MaterialRequirement zostáva možným budúcim kontraktom, ak ho bude vyžadovať konkrétny priechod zákazkou. Forma nakúpenej zásoby, katalógové číslo dodávateľa a skutočná šarža/tavba patria do nákupu alebo vykonania, nie do identity dielu.

## 11. Dokumentové vydania

Vydanie môže byť založené na schválenom modeli a špecifikácii bez výkresu. Môže vyberať z viacerých dokumentov; jedno vydanie výkresu môže podporiť viac technických vydaní aj dielov. Pre v1 netreba koreň DrawingRelease: postačí preukázateľne zachovaný externý podklad s vydavateľom alebo technickou autoritou, identitou dokumentu či podkladu, konkrétnym vydaním a podľa potreby aj použitou časťou alebo rozsahom. Odkaz musí určovať spôsob, ako neskôr získať alebo overiť rovnaký obsah. Samotná URL, meniteľný súbor, číslo bez vydavateľa ani hash bez dostupného obsahu nestačia. Bez dostatočného podkladu neuvoľniť; nevyžadujeme konkrétny typ archívu. Správa dokumentov, distribúcia a revízny workflow ostávajú samostatnou budúcou témou.

## 12. Variant a následníctvo

| Rozdiel | Predvolený záver a hranica |
| --- | --- |
| Ľavý / pravý diel | B: nová stabilná identita, ak si stranu vyberá zákazník. |
| Materiál; nominálny rozmer; tolerancia | Pre každý: B pri samostatnom výbere alternatívy; C pri zmene existujúceho predpisu. A (nové vydanie toho istého dielu) až pri doloženej kontinuite. |
| Povrch; tepelné spracovanie; iná funkčná požiadavka pri rovnakej geometrii | Pre každý: C bez znalosti účelu, B pri odlíšených funkčných vyhotoveniach, A pri potvrdenom technickom následníkovi toho istého dielu. |
| Iba iný zákaznícky obchodný kód | Ani A ani B: alias, ak je nezmenená definícia a väzba doložená; inak C. |

Variant nepotrebuje samostatnú entitu. A → B → C v rámci jedného dielu je história vydaní, nie postupné nahradenie troch dielov. Neodvodzovať supersedes z dátumu. Prípadná explicitná, smerová väzba medzi vydaniami potrebuje rozsah, dôkaz a čas; opačnú možno vyhľadať, neudržiavať duplicitne. Nahradenie **dielu** iným dielom je samostatné rozhodnutie o použiteľnosti. Neprenášať automaticky Material.replaces/replacedBy. Odvodenie a alternatíva (derivedFrom, alternativeTo) neznamenajú náhradu ani schválenú zámenu; tieto vzťahy a ich serializáciu odložiť.

## 13. Pôvod a dôkaz

Koreň dielu preukazuje existenciu a kontinuitu identity, vlastníka označenia alebo potvrdené mapovanie. Koreň vydania musí samostatne preukázať autoritu uvoľnenia **aj presný obsah**. Použiť existujúci význam SourceLink → SourceReference, lokalizáciu a triedu zdroja podľa tvrdenia; neprideľovať triedu len podľa prípony dokumentu. Dôkaz názvu dielu nie je dôkazom tolerancie. Pre technické uvoľnenie nestačí prázdny zoznam, neurčitý zdroj ani administratívny createdBy. Nie je potrebný nový typ zdroja len preto, že podklad je externý.

## 14. Klasifikácie a tvrdenia

**EngineeringItem v1:** vlastníctvo voliteľného `Classification[]` je prijaté iba pre stabilné zaradenie samotnej položky naprieč vydaniami. Klasifikácia neurčuje identitu: jej zmena sama nerozhoduje o pridelení nového EIT. Kontinuita sa posudzuje podľa CDR-0025 a §7. Klasifikácia nenesie požiadavky jedného vydania, rozmery, tolerancie, materiálový predpis, revíziu výkresu, životný cyklus vydania, identitu variantu, zaradenie zákazkovej položky, výrobnú spôsobilosť ani údaje operácie.

Vlastníctvo `PropertyRecord[]` je pre EngineeringItem v1 zamietnuté. Technický predpis konkrétneho vydania nepatrí na stabilnú položku len preto, že existuje `PropertyRecord`. Rozsah EngineeringRelease sa týmto rozhodnutím nemení.

## 15. Dopyt a ponuka

Dopytový riadok môže dočasne evidovať nerozpoznaný externý podklad. Potvrdený `RequestLine` musí odkazovať na presné technické vydanie (diel z neho vyplýva), podklad, množstvo, jednotku a schválené odchýlky. Ak nesie oba identifikátory, musia označovať tú istú dvojicu. Vydaný `QuotationLine` musí odkazovať na **nemenný obraz tejto požiadavky**, nie na editovateľný riadok. Samotný diel nestačí; ani samotné vydanie neobsahuje množstvo či zákazkovú výnimku. Ponuka z roku 2026 musí aj neskôr vrátiť pôvodný základ a výnimky, nie aktuálne vydanie. Nové nacenenie nevytláča históriu.

## 16. Výroba, kontrola a BOM

Job vyberie potvrdenú požiadavku a presné vydanie; Operation plánuje či vykonáva krok konkrétnej zákazky. ManufacturingProcess zostáva opakovateľná metóda a Machine individuálny fyzický zdroj. Výrobný postup nedefinuje automaticky identitu dielu. Inspection porovná konkrétny kus s kritériom z vydania a prípadnou výnimkou; Observation zostáva nezávislý dôkaz, nie požiadavka. Vydaná BOM musí vedieť spätne určiť komponent a zvolené prípustné vydanie pre pozíciu; nové vydanie komponentu neprepíše starú zostavu. Toto sú skúšky dohľadateľnosti, nie návrhy ďalších kontraktov.

## 17. Identifikátory

**PI-0004: CLOSED / Accepted.** Pred zápisom nebol vo vetve ani jeden výskyt prefixu EIT alebo ERL: kontrola zahŕňala register EOS-003 (Active, Candidate, Deferred), centrálne `$defs`, schémy, fixtures, dokumentáciu aj kód. Trojpísmenový prefix so štyrmi číslicami zodpovedá existujúcej konvencii nezávislých entít. [EOS-003 §2](../governance/EOS-003_Identification_and_Versioning.md) rezervuje obe rodiny ako Candidate. Prijatý formát nie je aktiváciou dátového kontraktu.

| Rodina | Presný formát | Čo identita zachováva |
| --- | --- | --- |
| EngineeringItem | `EIT-xxxx` · `^EIT-[0-9]{4}$` | Jedna stabilná položka naprieč všetkými vydaniami. Nové vydanie, premenovanie ani samotné prečíslovanie externého výkresu EIT nemenia. Samostatný variant potvrdený technickou autoritou dostáva nový EIT; pri nejasnosti sa identita neodvodzuje. |
| EngineeringRelease | `ERL-xxxx` · `^ERL-[0-9]{4}$` | Jedno autorizované vydanie presne jedného EngineeringItem. Zmena záväzného technického základu po uvoľnení vyžaduje nový ERL. Starý ERL sa nepoužije na iný obsah a zostáva adresovateľný. |

Číslo výkresu, zákaznícke číslo dielu ani dodávateľské číslo dielu nie sú EIT. Externé označenia revízií ako `A`, `B` či `02` nie sú ERL: dvaja vydavatelia môžu rovnakým štítkom označiť rozličné vydania. Tieto údaje môžu byť kvalifikované externé odkazy, aliasy alebo označenia; nenahrádzajú identitu EOS.

## 18. Názvy

**PI-0005: CLOSED / Accepted.** Autoritatívne doménové názvy sú `EngineeringItem` a `EngineeringRelease`.

- **EngineeringItem** je jedna stabilná, opakovane špecifikovateľná technická položka naprieč jej riadenými vydaniami. Nie je to fyzický kus, zákazková položka, SKU, výkres ani jeho vydanie, rodina dielov, polotovar či výrobná operácia. Lokalizované používateľské pomenovanie „Diel“ nemení doménovú identitu.
- **EngineeringRelease** je jedno presné, autorizované technické vydanie jedného EngineeringItem. Jeho uvoľnený technický základ je nemenný a historicky adresovateľný. Nie je to EOS `recordVersion`, EOS `revision`, DrawingRevision, výkres ani história editácií záznamu.

Kardinalita: **EngineeringItem 1 → 0..N EngineeringRelease**. Položka môže existovať pred prvým vydaním. Každé vydanie je samostatný koreň agregátu a odkazuje na práve jednu položku; nie je jej vlastneným potomkom.

## 19. Minimálne v1: obsah, nie JSON

### Záväzný zoznam polí EngineeringItem v1: FROZEN

| Stav | Presné názvy polí |
| --- | --- |
| REQUIRED | `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `createdAt`, `createdBy`, `updatedAt`, `updatedBy`, `sourceLinks`, `changeSummary`, `name` |
| OPTIONAL | `description` (administratívny opis), `classifications` (stabilné zaradenie podľa §14) |

Zoznam je uzavretý. `sourceLinks` je povinné pole s dôkazmi pre stabilnú identitu a záznam EngineeringItem. Samo nepreukazuje technické požiadavky vydania, revíziu výkresu, materiálový predpis, zameniteľnosť ani výrobnú spôsobilosť. Povinnosť poľa sa nesmie zameniť za nové pravidlo neprázdnosti mimo existujúcich pravidiel životného cyklu EOS.

**EXCLUDED FROM v1:** `notes`, `properties`, `engineeringReleaseIds`, `releases` a iné spätné vlastníctvo vydaní; externé aliasy a identita podľa čísla výkresu; materiál, rozmery, tolerancie, povrch a tepelné spracovanie ako požiadavky vydania; údaje výrobného procesu, operácie alebo stroja, množstvo, cena, kalkulácia nákladov, zásoby a BOM. Voliteľné polia iných entít sa nededia.

### Porovnanie rozsahu položky a vydania

R = povinné; O = voliteľné; D = odložené; X = nepatrí sem. Pre EngineeringItem je záväzný presný zoznam vyššie. Stĺpec technického vydania ostáva koncepčný.

| Obsah | Stabilná položka | Technické vydanie |
| --- | --- | --- |
| Vlastné id, spoločné metadáta | R | R. schemaVersion, recordVersion, revision, status, createdAt/By, updatedAt/By, sourceLinks, changeSummary podľa existujúceho vzoru; nie náhrada doménovej autorizácie. |
| Názov; opis | R názov, O administratívny opis | O opis vydanej definície; ak má technický význam, patrí do nemenného základu. |
| Odkaz na stabilný diel | X vlastný spätný zoznam vydaní | R presne jeden. |
| Autorita a okamih uvoľnenia | X | R doložené; nemusia sa duplikovať, ak sú jednoznačne rozlíšiteľné v zachovanom doklade. |
| Presný technický základ, vydania podkladov a rozsah | X | R aspoň jeden dostatočný nemenný základ; výkres sám je O. SourceLink bez jednoznačného vydania nepostačuje. |
| Označenie technickej revízie | X | O prevzatý štítok; vlastná identita vydania je R aj bez štítka. |
| Začiatok účinnosti | X | O doložený, nie automaticky deň vydania. Podrobné pravidlá použiteľnosti D. |
| Materiálový predpis; rozmer/geometria; tolerancia; povrch; spracovanie | X | D ako samostatné štruktúrované polia; existujúce platné požiadavky nemožno vynechať zo záväzného podkladu. |
| Classification; PropertyRecord | O stabilná klasifikácia; X vlastníctvo PropertyRecord vo v1 | D oboje. |
| Voľné poznámky | X vo v1 | D. Nepoužiť ako náhradu záväzného podkladu. |
| Množstvo, jednotka zákazky, cena, zásoba, skutočná výroba | X | X; patria používateľom vydania. |

## 20. Skúška prípadu 001

Interný podklad A: 48 kusov púzdier, mapovanie položky aj vydania **UNKNOWN**. Externý podklad B: tri samostatné výkresové odkazy na riadkoch po 16 kusov; ku každému osobitne uchovať vlastný podklad. To ešte neznamená tri potvrdené identity alebo rovnakú revíziu ako v A. Doložiť treba vydavateľa, konkrétne vydanie, pozíciu, oprávnené mapovanie variantu a rozdelenie požadovaného množstva. Pred potvrdením nevytvárať domnelé diely ani vydania len pre úspešné spárovanie. Anonymizovaný príklad je nenormatívny.

## 21. Zistenia

| ID | Priorita | Stav |
| --- | --- | --- |
| SPER-0001 | Critical | **CLOSED / Accepted.** Dva samostatné korene; položka môže predchádzať prvému vydaniu (§5, §9). |
| SPER-0002 | Critical | **CLOSED / Accepted.** Autorizovaným uvoľnením sa technický základ zmrazí. Zmena záväznej požiadavky alebo podkladu vyžaduje nové vydanie. Auditovaná oprava mimo tohto základu nesmie meniť jeho význam ani historické odkazy. EOS `recordVersion` a `revision` označujú verziu a revíziu záznamu, nie technické vydanie (§8). |
| SPER-0003 | High | **CLOSED / Accepted for v1.** Presne doložený externý podklad postačuje bez samostatného systému správy dokumentov. Materiálový predpis ostáva v technickom základe; budúci štruktúrovaný kontrakt nie je vylúčený (§10–11). |
| SPER-0004 | Medium | **CLOSED / Accepted.** PI-0004 a PI-0005 sú uzavreté po kontrole kolízií; definície, formáty ID a hranice externých označení sú v §17–18. |
| SPER-0005 | Medium | **CLOSED / Accepted.** Súbežná platnosť nie je náhrada. Novšie vydanie automaticky neruší ani nenahrádza staršie. Rozsah náhrady alebo zameniteľnosti musí byť výslovne doložený. Ani stiahnutie vydania nemení historické odkazy (§8, §12). |

## 22. Prijaté doménové hranice

Dva korene, jeden nemenný technický základ pri uvoľnení, samostatné dôkazy identity a obsahu. Kontrola tvaru môže neskôr použiť existujúce schémy a spoločný testovací profil ADR-0017. Existencia cieľa, zhoda rozsahu, história nemennosti a oprávnenie vlastníka nie sú kontrolami samotnej JSON Schema. EOS-006/007 nedokazujú existenciu archívu ani úspešné presadenie týchto budúcich pravidiel.

## 23. Poradie budúcej implementácie

Odporúčané poradie: **EngineeringItem v1 → integračné uzatvorenie EngineeringItem → EngineeringRelease v1 → integračné uzatvorenie EngineeringRelease**. Tým možno pri overovaní odkazu vydania používať už overenú identitu položky. Samotná položka ešte nestačí na vydanie dohľadateľnej ponuky. Žiadny z týchto implementačných krokov sa týmto rozhodnutím nezačal.

## 24. Rozhodnutia používateľa

Všetky zistenia sú uzavreté podľa §21, SPER-0003 iba pre v1. Schválenie názvov a rodín nenahrádza samostatné poverenie na implementáciu.

## 25. Pripravenosť

EngineeringItem v1: READY FOR IMPLEMENTATION. PR #11 priniesol prijatý slovník a zmrazenú maticu §19; používateľ poveril implementáciou iba EngineeringItem.

## 26. História zmien

| Verzia | Revízia | Zmena |
| --- | --- | --- |
| 0.1 | 0 | Prvé porovnanie vlastníctva, technického uvoľnenia a podkladov pre budúci kontrakt. |
| 0.1 | 1 | Zapísané prijatie SPER-0001/0002, SPER-0003 pre v1 a rozlíšenie súbežnej platnosti a náhrady v SPER-0005. PI-0004/0005 zostávajú otvorené. |
| 0.1 | 2 | Po kontrole kolízií prijaté názvy a rodiny ID; PI-0004, PI-0005 a SPER-0004 uzavreté. Doplnené integračné uzatvorenie po každom budúcom kontrakte. |
| 0.1 | 3 | Zmrazených 12 povinných a 2 voliteľné polia EngineeringItem v1; prijaté stabilné klasifikácie, zamietnuté properties a vylúčené notes. Slovníkové zosúladenie bez implementácie a bez aktivácie EIT/ERL. |
| 0.1 | 4 | Zaznamenaná pripravenosť EngineeringItem na implementáciu bez zmeny polí alebo identity. |

READY FOR IMPLEMENTATION
