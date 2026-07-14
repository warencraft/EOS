# EOS-005 - Inžiniersky pracovný tok

**Project:** EOS - Engineering Operating System  
**Document ID:** EOS-005  
**Version:** 0.1  
**Revision:** 1  
**Status:** Draft  
**Author:** Chief Engineering Knowledge Architect + Codex  
**Last update:** 2026-07-13  
**Document basis:** Internal governance decision  

---

## 1. Účel

Tento dokument definuje počiatočný pracovný tok od prijatia podkladov po aktualizáciu EOS. Neobsahuje automatické výpočty ani konkrétne technické hodnoty.

## 2. Všeobecné stavy procesu

Možné stavy kroku:

- `Not started`,
- `In progress`,
- `Waiting for input`,
- `Blocked`,
- `Completed`,
- `Rejected`.

## 3. Kroky workflow

### 3.1 Prijatie podkladov

Vstupy: výkresy, modely, špecifikácie, požiadavky zákazníka.

Výstupy: zoznam prijatých podkladov.

Zodpovednosť: obchod alebo technická príprava.

Validácia: kontrola čitateľnosti a identifikácie podkladov.

Dôvod zastavenia: chýbajúce alebo nečitateľné podklady.

### 3.2 Registrácia zákazky

Vstupy: prijaté podklady a interný kontext.

Výstupy: záznam `Job` s ID `JOB-yyyy-xxxx`.

Zodpovednosť: technická príprava.

Validácia: jedinečné ID, základný názov a stav.

Dôvod zastavenia: nemožnosť priradiť jednoznačnú zákazku.

### 3.3 Kontrola úplnosti výkresu

Vstupy: výkresová dokumentácia a požiadavky.

Výstupy: zoznam chýbajúcich alebo nejasných informácií.

Zodpovednosť: konštruktér alebo technológ.

Validácia: kontrola potrebných informácií pre rozbor.

Dôvod zastavenia: kritická neúplnosť výkresu.

### 3.4 Technický rozbor

Vstupy: výkres, požiadavky, dostupné znalosti EOS.

Výstupy: technické poznámky, predpoklady, riziká.

Zodpovednosť: technológ alebo konštruktér.

Validácia: oddelenie faktov, predpokladov a odporúčaní.

Dôvod zastavenia: konflikt požiadaviek alebo technická nejasnosť.

### 3.5 Výber materiálu a polotovaru

Vstupy: požiadavky zákazky, materiálové špecifikácie, dostupné záznamy.

Výstupy: návrh `Material` a `StockMaterial`.

Zodpovednosť: technológ.

Validácia: zdrojová klasifikácia a dohľadateľnosť.

Dôvod zastavenia: neoverený alebo nejasný materiál.

### 3.6 Návrh technologického postupu

Vstupy: technický rozbor, materiál, polotovar, procesné možnosti.

Výstupy: zoznam `JobOperation`.

Zodpovednosť: technológ.

Validácia: každá operácia má proces, poradie a účel.

Dôvod zastavenia: chýbajúca technológia alebo výrobná schopnosť.

### 3.7 Odhad času

Vstupy: operácie, historické dáta, skúsenosť, budúce kalkulátory.

Výstupy: plánované `TimeRecord` záznamy.

Zodpovednosť: technológ alebo kalkulant.

Validácia: odhad musí mať zdroj, typ a väzbu cez `SourceLink`.

Dôvod zastavenia: nedostatok zdrojov pre zodpovedný odhad.

### 3.8 Identifikácia rizík

Vstupy: technický rozbor, operácie, materiál, skúsenosti.

Výstupy: záznamy `Risk`.

Zodpovednosť: technológ, konštruktér alebo kalkulant.

Validácia: riziko má popis, typ a stav.

Dôvod zastavenia: neriešené kritické riziko.

### 3.9 Tvorba cenovej ponuky

Vstupy: technický postup, odhady, riziká, poznámky.

Výstupy: návrh ponuky a `QuotationNote`.

Zodpovednosť: kalkulant alebo obchod.

Validácia: poznámky majú dôvod, zdroj a väzbu cez `SourceLink`.

Dôvod zastavenia: chýbajúce schválenie alebo nejasné riziko.

### 3.10 Výroba

Vstupy: schválená zákazka, výrobný postup, podklady.

Výstupy: vyrobený diel alebo zostava, výrobné poznámky.

Zodpovednosť: výroba.

Validácia: postup a zmeny sú zaznamenané.

Dôvod zastavenia: technický problém, chýbajúci materiál alebo nezhoda.

### 3.11 Záznam skutočných časov

Vstupy: výrobná realita a operácie.

Výstupy: skutočné `TimeRecord` záznamy.

Zodpovednosť: výroba alebo technológ.

Validácia: čas je naviazaný na operáciu a má zdroj.

Dôvod zastavenia: nemožnosť priradiť čas ku konkrétnej operácii.

### 3.12 Kontrola výsledku

Vstupy: vyrobený diel, požiadavky, kontrolné záznamy.

Výstupy: výsledok kontroly a prípadné nezhody.

Zodpovednosť: kontrola kvality alebo zodpovedná rola.

Validácia: výsledok je dohľadateľný.

Dôvod zastavenia: nezhoda alebo chýbajúce kontrolné údaje.

### 3.13 Lessons learned

Vstupy: rozdiely medzi plánom a realitou, problémy, úspešné postupy.

Výstupy: poučenia klasifikované ako `P` alebo `V`.

Zodpovednosť: technológ a Chief Engineering Knowledge Architect.

Validácia: poznatok je konkrétny, dohľadateľný a nezamieňa sa s normou.

Dôvod zastavenia: nemožnosť overiť záver.

### 3.14 Aktualizácia EOS

Vstupy: lessons learned, overené záznamy, schválené zmeny.

Výstupy: aktualizované dokumenty, dáta alebo backlog.

Zodpovednosť: Chief Engineering Knowledge Architect + Codex.

Validácia: súlad s `EOS-000`, ID, zdroje a revízie.

Dôvod zastavenia: chýbajúce schválenie alebo potreba ADR.

## 4. Súvisiace dokumenty

- `EOS-000_Development_Manifesto.md`
- `EOS-004_Core_Data_Model.md`
- `EOS-002_Documentation_Standard.md`

## 5. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-07-13 | 0.1 | 0 | Chief Engineering Knowledge Architect + Codex | Initial draft |
| 2026-07-13 | 0.1 | 1 | Codex | Governance Alignment 0.1.1: zosúladenie workflow s `Document basis` a väzbou technických tvrdení cez `SourceLink` |
