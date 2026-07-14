# EOS-000 - EOS Development Manifesto

**Project:** EOS - Engineering Operating System  
**Document ID:** EOS-000  
**Version:** 0.1  
**Revision:** 0  
**Status:** Draft  
**Language:** Slovak  
**Author:** Chief Engineering Knowledge Architect + Codex  
**Last update:** 2026-07-13  
**Source classification:** P  

---

## 1. Purpose

Tento dokument definuje filozofiu, pravidla kvality, rozhodovania a vyvoja projektu EOS - Engineering Operating System.

EOS nie je iba dokumentacia. EOS je dlhodoby inziniersky znalostny system pre konstrukciu, vyrobu, technologiu a pripravu cenovych ponuk.

Tento manifest ma byt referencnym dokumentom pre kazde buduce rozhodnutie v projekte.

Ak vznikne pochybnost, ci je nejake riesenie vhodne, rozhodnutie sa porovna s tymto manifestom.

## 2. Mission

Misiou EOS je vytvorit najpraktickejsi inziniersky znalostny system pre realnu strojarensku prax.

EOS ma pomahat odpovedat najma na otazky:

- aky material pouzit,
- aky polotovar zvolit,
- aku vyrobnu technologiu navrhnut,
- ake rizika existuju,
- kolko moze vyroba trvat,
- ake poznamky patria do cenovej ponuky,
- ake normy alebo pravidla sa vztahuju na dany pripad,
- ci uz existovala podobna vyrobna zakazka.

EOS sa ma zlepsovat kazdou dokoncenou zakazkou, kazdym overenym poznatkom a kazdou opravou chybneho predpokladu.

## 3. Identity Of EOS

EOS nie je:

- skolska ucebnica,
- kopia technickych noriem,
- zbierka PDF suborov,
- nahodna databaza internetovych clankov,
- jednorazovy softverovy experiment.

EOS je:

- inziniersky znalostny system,
- vyrobna znalostna databaza,
- podpora pripravy cenovych ponuk,
- prakticka technicka prirucka,
- zaklad pre kalkulacie a automatizaciu,
- system, ktory sa dlhodobo uci z realnej vyroby.

## 4. Roles

### 4.1 Chief Engineering Knowledge Architect

Chief Engineering Knowledge Architect rozhoduje, co ma EOS vediet.

Zodpovednosti:

- definovat inziniersky obsah,
- urcovat priority znalosti,
- schvalovat prakticke pravidla,
- oddelovat normy od odporucani,
- rozhodovat o tom, ktore skusenosti z vyroby maju byt zapisane do systemu.

### 4.2 Software Architect & Engineering Infrastructure Developer

Codex vystupuje ako Software Architect & Engineering Infrastructure Developer.

Zodpovednosti:

- navrhovat technicku architekturu,
- vytvarat strukturu projektu,
- implementovat databazy, kalkulatory, sablony a nastroje,
- dbat na testovatelnost,
- chranit projekt pred technickym dlhom,
- navrhovat riesenia, ktore budu udrzatelne aj po rokoch vyvoja.

## 5. Golden Rules

### Rule 1 - Accuracy Before Quantity

Presnost je vzdy dolezitejsia ako mnozstvo informacii.

EOS nesmie rast sposobom, ktory zvysuje chaos. Menej overenych informacii je hodnotnejsich ako vela nejasnych tvrdeni.

### Rule 2 - Every Engineering Statement Must Be Classified

Kazde technicke tvrdenie musi mat zdrojovu klasifikaciu.

Pouzivaju sa tieto triedy:

- **N** - Standard alebo norma,
- **L** - Technicka literatura,
- **P** - Vyrobna alebo inzinierska skusenost,
- **V** - Overene realnou vyrobou.

Ziadna technicka informacia nema byt v EOS uvedena bez klasifikacie.

### Rule 3 - Standards And Recommendations Must Never Be Mixed

Normy, zakonne poziadavky a zavazne pravidla musia byt jasne oddelene od odporucani.

Odporucanie moze byt velmi hodnotne, ale nesmie sa tvarit ako norma.

### Rule 4 - EOS Is Never Final

Ziadny dokument v EOS nie je definitivny.

Kazdy dokument, databazovy zaznam, kalkulator a metodika musi byt pripraveny na reviziu.

### Rule 5 - Real Production Has The Highest Learning Value

Poznatok overeny realnou vyrobou ma mimoriadnu hodnotu.

Ak sa rozdiel medzi teoriou a realnou vyrobou opakuje, EOS musi tento rozdiel zachytit.

## 6. Quality Principles

EOS musi byt navrhnuty ako profesionalny inziniersky system, nie ako osobne poznamky.

Kazdy dokument alebo zaznam ma mat:

- jednoznacne ID,
- verziu,
- reviziu,
- stav,
- autora alebo zdroj,
- datum poslednej aktualizacie,
- referencie,
- zdrojovu klasifikaciu.

Informacie sa nemaju duplikovat. Ak jedna informacia patri do materialovej karty, nema sa kopirovat do kazdej metodiky. Ma sa na nu odkazovat.

## 7. Architecture Principles

Architektura ma prednost pred rychlou implementaciou.

Projekt musi byt modularny:

- dokumentacia,
- databazy,
- kalkulatory,
- sablony,
- skripty,
- exporty,
- testy.

Kazdy modul musi byt navrhnuty tak, aby mohol existovat samostatne, ale zaroven bol prepojitelny s ostatnymi modulmi.

Na zaciatku sa data mozu ukladat v JSON suboroch. Struktura vsak musi byt navrhnuta tak, aby bol neskor mozny prechod na SQLite alebo PostgreSQL.

## 8. Data Principles

Databazy su jadrom EOS.

Kalkulatory a automatizacia nesmu obsahovat napevno zapisane inzinierske hodnoty, ak tieto hodnoty patria do databazy.

Priklad:

- hustota materialu patri do materialovej databazy,
- dostupny rozmer polotovaru patri do databazy polotovarov,
- vykon stroja patri do databazy strojov,
- realny vyrobny cas patri do zaznamu zakazky.

Kod ma pocitat. Databazy maju niesť znalosti.

## 9. Documentation Principles

Dokumentacia EOS ma byt prakticka, nie akademicka.

Dobry dokument v EOS:

- pomoze urobit rozhodnutie,
- jasne povie, co je norma a co je odporucanie,
- obsahuje zdrojovu klasifikaciu,
- odkazuje na suvisiace zaznamy,
- je pripraveny na buducu reviziu.

Dokument nema byt dlhsi, nez je potrebne. Ma byt presny, pouzitelny a udrzatelny.

## 10. Decision Principles

Pri rozhodovani v EOS sa pouziva toto poradie:

1. Bezpecnost a technicka spravnost.
2. Norma alebo zavazna poziadavka.
3. Overena realna vyroba.
4. Inzinierska a vyrobna skusenost.
5. Technicka literatura.
6. Efektivita implementacie.

Ak je rychle riesenie v rozpore s buducou udrzatelnostou systemu, prednost ma udrzatelnost.

## 11. Development Strategy

EOS sa bude vyvijat postupne.

Priorita vyvoja:

1. Architektura.
2. Zakladna dokumentacia.
3. Databazove struktury.
4. Sablony a formularove zaznamy.
5. Kalkulatory.
6. Automatizacia.
7. Pokrocile vyhodnocovanie historickych zakazok.

Implementacia nesmie predbiehat pochopenie struktury znalosti.

## 12. Future Vision

EOS ma casom podporovat:

- citanie a analyzu technickych vykresov,
- navrh vyrobnych technologii,
- vyber vhodneho polotovaru,
- odhad vyrobneho casu,
- odhad ceny,
- generovanie poznamok do cenovej ponuky,
- vyhladavanie podobnych historickych zakazok,
- tvorbu vyrobnych postupov,
- export PDF dokumentacie,
- export Excel cenovych ponuk,
- tvorbu technickych reportov.

Tieto schopnosti su dlhodoby ciel. Nemaju byt implementovane skor, nez vznikne spolahlivy zaklad.

## 13. Definition Of Done

Praca v EOS sa povazuje za dokoncenu iba vtedy, ked:

- ma jasne ID,
- ma definovany ucel,
- ma zdrojovu klasifikaciu,
- je ulozena v spravnom module,
- nezdvojuje existujuce informacie,
- je prepojitelna s ostatnymi castami systemu,
- je pripravena na reviziu,
- pri vypoctoch je testovatelna.

## 14. First Official Decision

Prve oficialne rozhodnutie projektu EOS je:

**EOS sa bude budovat ako profesionalny Engineering Operating System, nie ako zbierka dokumentov.**

Dokumentacia je iba jedna cast systemu.

Databazy, kalkulatory, zaznamy realnych zakazok, sablony a automatizacia su rovnako dolezite casti celku.

## 15. Closing Statement

EOS ma vznikat pomaly, presne a systematicky.

Kvalita ma prednost pred rychlostou.

Architektura ma prednost pred improvizaciou.

Realna vyroba ma prednost pred teoretickymi predpokladmi.

Kazda dobra zakazka ma EOS zlepsit.

Kazda chyba ma EOS naucit.

Kazda revizia ma EOS spravit presnejsim.

