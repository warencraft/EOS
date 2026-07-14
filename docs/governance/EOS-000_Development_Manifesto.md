# EOS-000 - EOS Development Manifesto

**Project:** EOS - Engineering Operating System  
**Document ID:** EOS-000  
**Version:** 0.1  
**Revision:** 1  
**Status:** Draft  
**Language:** Slovak  
**Author:** Chief Engineering Knowledge Architect + Codex  
**Last update:** 2026-07-13  
**Document basis:** Internal governance decision  

---

## 1. Účel

Tento dokument definuje filozofiu, pravidlá kvality, rozhodovania a vývoja projektu EOS - Engineering Operating System.

EOS nie je iba dokumentácia. EOS je dlhodobý inžiniersky znalostný systém pre konštrukciu, výrobu, technológiu a prípravu cenových ponúk.

Tento manifest má byť referenčným dokumentom pre každé budúce rozhodnutie v projekte.

Ak vznikne pochybnosť, či je nejaké riešenie vhodné, rozhodnutie sa porovná s týmto manifestom.

## 2. Misia

Misiou EOS je vytvoriť najpraktickejší inžiniersky znalostný systém pre reálnu strojársku prax.

EOS má pomáhať odpovedať najmä na otázky:

- aký materiál použiť,
- aký polotovar zvoliť,
- akú výrobnú technológiu navrhnúť,
- aké riziká existujú,
- koľko môže výroba trvať,
- aké poznámky patria do cenovej ponuky,
- aké normy alebo pravidlá sa vzťahujú na daný prípad,
- či už existovala podobná výrobná zákazka.

EOS sa má zlepšovať každou dokončenou zákazkou, každým overeným poznatkom a každou opravou chybného predpokladu.

## 3. Identita EOS

EOS nie je:

- školská učebnica,
- kópia technických noriem,
- zbierka PDF súborov,
- náhodná databáza internetových článkov,
- jednorazový softvérový experiment.

EOS je:

- inžiniersky znalostný systém,
- výrobná znalostná databáza,
- podpora prípravy cenových ponúk,
- praktická technická príručka,
- základ pre kalkulácie a automatizáciu,
- systém, ktorý sa dlhodobo učí z reálnej výroby.

## 4. Roly

### 4.1 Chief Engineering Knowledge Architect

Chief Engineering Knowledge Architect rozhoduje, čo má EOS vedieť.

Zodpovednosti:

- definovať inžiniersky obsah,
- určovať priority znalostí,
- schvaľovať praktické pravidlá,
- oddeľovať normy od odporúčaní,
- rozhodovať o tom, ktoré skúsenosti z výroby majú byť zapísané do systému.

### 4.2 Software Architect & Engineering Infrastructure Developer

Codex vystupuje ako Software Architect & Engineering Infrastructure Developer.

Zodpovednosti:

- navrhovať technickú architektúru,
- vytvárať štruktúru projektu,
- implementovať databázy, kalkulátory, šablóny a nástroje,
- dbať na testovateľnosť,
- chrániť projekt pred technickým dlhom,
- navrhovať riešenia, ktoré budú udržateľné aj po rokoch vývoja.

## 5. Zlaté pravidlá

### Pravidlo 1 - Presnosť pred množstvom

Presnosť je vždy dôležitejšia ako množstvo informácií.

EOS nesmie rásť spôsobom, ktorý zvyšuje chaos. Menej overených informácií je hodnotnejších ako veľa nejasných tvrdení.

### Pravidlo 2 - Každé technické tvrdenie musí byť klasifikované

Každé technické tvrdenie musí mať zdrojovú klasifikáciu.

Používajú sa tieto triedy:

- **N** - norma, štandard alebo záväzný technický predpis,
- **L** - technická literatúra,
- **P** - výrobná alebo inžinierska skúsenosť,
- **V** - overené reálnou výrobou.

Žiadna technická informácia nemá byť v EOS uvedená bez klasifikácie.

### Pravidlo 3 - Normy a odporúčania sa nesmú miešať

Normy, zákonné požiadavky a záväzné pravidlá musia byť jasne oddelené od odporúčaní.

Odporúčanie môže byť veľmi hodnotné, ale nesmie sa tváriť ako norma.

### Pravidlo 4 - EOS nikdy nie je finálny

Žiadny dokument v EOS nie je definitívny.

Každý dokument, databázový záznam, kalkulátor a metodika musí byť pripravený na revíziu.

### Pravidlo 5 - Reálna výroba má najvyššiu hodnotu učenia

Poznatok overený reálnou výrobou má mimoriadnu hodnotu.

Ak sa rozdiel medzi teóriou a reálnou výrobou opakuje, EOS musí tento rozdiel zachytiť.

## 6. Princípy kvality

EOS musí byť navrhnutý ako profesionálny inžiniersky systém, nie ako osobné poznámky.

Každý dokument alebo záznam má mať:

- jednoznačné ID,
- verziu,
- revíziu,
- stav,
- autora alebo zdroj,
- dátum poslednej aktualizácie,
- referencie,
- zdrojovú klasifikáciu, ak obsahuje technické tvrdenia.

Informácie sa nemajú duplikovať. Ak jedna informácia patrí do materiálovej karty, nemá sa kopírovať do každej metodiky. Má sa na ňu odkazovať.

## 7. Architektonické princípy

Architektúra má prednosť pred rýchlou implementáciou.

Projekt musí byť modulárny:

- dokumentácia,
- databázy,
- kalkulátory,
- šablóny,
- skripty,
- exporty,
- testy.

Každý modul musí byť navrhnutý tak, aby mohol existovať samostatne, ale zároveň bol prepojiteľný s ostatnými modulmi.

Na začiatku sa dáta môžu ukladať v JSON súboroch. Štruktúra však musí byť navrhnutá tak, aby bol neskôr možný prechod na SQLite alebo PostgreSQL.

## 8. Dátové princípy

Databázy sú jadrom EOS.

Kalkulátory a automatizácia nesmú obsahovať napevno zapísané inžinierske hodnoty, ak tieto hodnoty patria do databázy.

Príklad:

- hustota materiálu patrí do materiálovej databázy,
- dostupný rozmer polotovaru patrí do databázy polotovarov,
- výkon stroja patrí do databázy strojov,
- reálny výrobný čas patrí do záznamu zákazky.

Kód má počítať. Databázy majú niesť znalosti.

## 9. Princípy dokumentácie

Dokumentácia EOS má byť praktická, nie akademická.

Dobrý dokument v EOS:

- pomôže urobiť rozhodnutie,
- jasne povie, čo je norma a čo je odporúčanie,
- obsahuje zdrojovú klasifikáciu pri technických tvrdeniach,
- odkazuje na súvisiace záznamy,
- je pripravený na budúcu revíziu.

Dokument nemá byť dlhší, než je potrebné. Má byť presný, použiteľný a udržateľný.

## 10. Princípy rozhodovania

Pri rozhodovaní v EOS sa používa toto poradie:

1. Bezpečnosť a technická správnosť.
2. Norma alebo záväzná požiadavka.
3. Overená reálna výroba.
4. Inžinierska a výrobná skúsenosť.
5. Technická literatúra.
6. Efektivita implementácie.

Ak je rýchle riešenie v rozpore s budúcou udržateľnosťou systému, prednosť má udržateľnosť.

## 11. Stratégia vývoja

EOS sa bude vyvíjať postupne.

Priorita vývoja:

1. Architektúra.
2. Základná dokumentácia.
3. Databázové štruktúry.
4. Šablóny a formulárové záznamy.
5. Kalkulátory.
6. Automatizácia.
7. Pokročilé vyhodnocovanie historických zákaziek.

Implementácia nesmie predbiehať pochopenie štruktúry znalostí.

## 12. Budúca vízia

EOS má časom podporovať:

- čítanie a analýzu technických výkresov,
- návrh výrobných technológií,
- výber vhodného polotovaru,
- odhad výrobného času,
- odhad ceny,
- generovanie poznámok do cenovej ponuky,
- vyhľadávanie podobných historických zákaziek,
- tvorbu výrobných postupov,
- export PDF dokumentácie,
- export Excel cenových ponúk,
- tvorbu technických reportov.

Tieto schopnosti sú dlhodobý cieľ. Nemajú byť implementované skôr, než vznikne spoľahlivý základ.

## 13. Definition Of Done

Práca v EOS sa považuje za dokončenú iba vtedy, keď:

- má jasné ID,
- má definovaný účel,
- má zdrojovú klasifikáciu, ak obsahuje technické tvrdenia,
- je uložená v správnom module,
- nezdvojuje existujúce informácie,
- je prepojiteľná s ostatnými časťami systému,
- je pripravená na revíziu,
- pri výpočtoch je testovateľná.

## 14. Prvé oficiálne rozhodnutie

Prvé oficiálne rozhodnutie projektu EOS je:

**EOS sa bude budovať ako profesionálny Engineering Operating System, nie ako zbierka dokumentov.**

Dokumentácia je iba jedna časť systému.

Databázy, kalkulátory, záznamy reálnych zákaziek, šablóny a automatizácia sú rovnako dôležité časti celku.

## 15. Záverečné vyhlásenie

EOS má vznikať pomaly, presne a systematicky.

Kvalita má prednosť pred rýchlosťou.

Architektúra má prednosť pred improvizáciou.

Reálna výroba má prednosť pred teoretickými predpokladmi.

Každá dobrá zákazka má EOS zlepšiť.

Každá chyba má EOS naučiť.

Každá revízia má EOS spraviť presnejším.

## 16. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-07-13 | 0.1 | 0 | Chief Engineering Knowledge Architect + Codex | Initial draft |
| 2026-07-13 | 0.1 | 1 | Codex | Jazyková normalizácia do slovenčiny s plnou diakritikou bez zmeny významu |

