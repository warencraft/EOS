# EOS-002 - Dokumentačný štandard

**Project:** EOS - Engineering Operating System  
**Document ID:** EOS-002  
**Version:** 0.1  
**Revision:** 1  
**Status:** Draft  
**Author:** Chief Engineering Knowledge Architect + Codex  
**Last update:** 2026-07-13  
**Document basis:** Internal governance decision  

---

## 1. Účel

Tento dokument definuje pravidlá tvorby, údržby a citovania dokumentácie v EOS.

## 2. Povinná hlavička dokumentu

Každý riadený dokument musí obsahovať hlavičku:

```markdown
# DOCUMENT-ID - Názov dokumentu

**Project:** EOS - Engineering Operating System
**Document ID:** DOCUMENT-ID
**Version:** 0.1
**Revision:** 0
**Status:** Draft
**Author:** meno alebo rola
**Last update:** YYYY-MM-DD
**Document basis:** Internal governance decision
```

Povinné polia:

- `Document ID`,
- názov,
- verzia,
- revízia,
- stav,
- autor alebo rola,
- dátum poslednej aktualizácie,
- pôvod dokumentu alebo spôsob vzniku dokumentu.

## 3. Document basis a zdrojová klasifikácia

Pole `Document basis` popisuje pôvod riadeného dokumentu alebo dôvod jeho existencie.

Governance dokumenty používajú:

```markdown
**Document basis:** Internal governance decision
```

Technické triedy `N`, `L`, `P` a `V` sa nepoužívajú na označenie governance dokumentu ako celku. Používajú sa na klasifikáciu technických tvrdení, zdrojov a dôkazov v dokumentoch alebo dátových záznamoch.

## 4. Technické zdrojové klasifikácie

Používajú sa tieto triedy:

- **N** - externá norma, štandard alebo záväzný technický predpis,
- **L** - technická literatúra,
- **P** - výrobná alebo inžinierska skúsenosť,
- **V** - poznatok overený reálnou výrobou.

Ak dokument obsahuje viac typov tvrdení, musí pri konkrétnych tvrdeniach uvádzať príslušnú klasifikáciu.

## 5. Citovanie zdrojov

### 5.1 Externá norma alebo štandard

Citácia externej normy alebo štandardu musí používať referenciu typu `NRM-xxxx` a musí uvádzať minimálne:

- označenie normy,
- názov alebo predmet,
- vydanie alebo rok, ak je známy,
- rozsah použitia v dokumente,
- poznámku, či ide o citáciu alebo interpretáciu.

Bez prístupu k presnému zneniu normy sa nesmie uvádzať záväzné technické tvrdenie.

### 5.2 Technická literatúra

Citácia literatúry musí uvádzať:

- autora alebo organizáciu,
- názov zdroja,
- vydanie alebo dátum,
- kapitolu, stranu alebo inú lokalizáciu, ak je dostupná,
- spôsob použitia informácie.

### 5.3 Reálna zákazka

Citácia zákazky musí používať ID `JOB-yyyy-xxxx`.

Citácia musí uvádzať:

- ID zákazky,
- typ poznatku,
- či bol poznatok overený,
- prípadné obmedzenie použiteľnosti.

Citácia zákazky nesmie odhaliť citlivé obchodné údaje, ak na to nie je schválenie.

## 6. Väzba na zdroj

Technické tvrdenie má byť napojené na autoritatívny `SourceReference` cez `SourceLink`.

`SourceLink` má umožniť uviesť:

- `sourceReferenceId`,
- `sourceClass`,
- podporované tvrdenie alebo pole,
- typ použitia zdroja,
- lokalizáciu v zdroji,
- poznámku k interpretácii,
- stav overenia.

## 7. Typy tvrdení

Každé významné technické tvrdenie má byť označiteľné ako:

- **Fakt** - tvrdenie podložené zdrojom.
- **Predpoklad** - pracovná úvaha, ktorá ešte nie je overená.
- **Odporúčanie** - praktický návrh alebo preferovaný postup.
- **Otvorená otázka** - bod, ktorý vyžaduje rozhodnutie alebo overenie.

Odporúčanie sa nesmie zapisovať ako norma.

## 8. História zmien

Každý riadený dokument má obsahovať časť `Change History`.

Odporúčaná štruktúra:

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| YYYY-MM-DD | 0.1 | 0 | Role | Initial draft |

## 9. Jazyk a kódovanie

Používateľské a projektové dokumenty sa píšu po slovensky s diakritikou.

Súbory sa ukladajú v UTF-8.

Programové identifikátory, názvy JSON polí, názvy tried a technické názvy v schémach sa píšu po anglicky.

## 10. Tabuľky, jednotky, čísla a označenia

Tabuľky sa používajú iba vtedy, keď zlepšujú čitateľnosť.

Jednotky sa zapisujú vždy pri hodnote. Vo fáze 0.1 sa konkrétne technické hodnoty nezapisujú.

Desatinné čísla v dátových súboroch musia byť kompatibilné s JSON.

Materiálové označenia sa nesmú normalizovať ručne bez zdroja. Každé označenie musí mať jasný pôvod a kontext.

## 11. Jedno autoritatívne miesto

Každá informácia má mať jedno autoritatívne miesto.

Príklady princípu:

- opis pravidla patrí do dokumentácie,
- hodnota alebo vlastnosť patrí do dátového záznamu,
- formát dát patrí do schémy,
- pôvod zdroja patrí do `SourceReference`,
- použitie zdroja pri tvrdení patrí do `SourceLink`,
- rozhodnutie patrí do ADR.

Duplicitné kopírovanie informácií je zakázané, ak nie je výslovne odôvodnené.

## 12. Súvisiace dokumenty

- `EOS-000_Development_Manifesto.md`
- `EOS-003_Identification_and_Versioning.md`
- `ADR-0001_Use_Markdown_for_governed_documentation.md`

## 13. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-07-13 | 0.1 | 0 | Chief Engineering Knowledge Architect + Codex | Initial draft |
| 2026-07-13 | 0.1 | 1 | Codex | Governance Alignment 0.1.1: oddelenie `Document basis` od technických zdrojových klasifikácií a doplnenie pravidiel pre `SourceLink` |
