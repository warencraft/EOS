# ADR-0014 - Establish RFC Governance Lifecycle

**Status:** Accepted  
**Date:** 2026-07-25  

## Title

Establish RFC Governance Lifecycle

## Context

EOS používa RFC dokumenty na návrh znalostných modelov, architektonických smerov, dátových kontraktov a systematických scope rozhodnutí pred implementáciou.

Po revíziách RFC-0001, RFC-0002 a RFC-0003 vznikol stav, v ktorom sú RFC dokumenty pripravené na governance uzatvorenie, ale samotný lifecycle RFC ešte nie je autoritatívne definovaný v ADR. Tento stav bol označený ako blocker `CRC-0009` a ako podmienka `ARR-001` v `EOS-010_Architecture_Readiness_Review.md`.

Bez explicitného RFC lifecycle hrozí, že dokument v stave `Draft` alebo `Review` bude použitý ako záväzný architektonický kontrakt, alebo že prijaté RFC bude neskôr obsahovo zmenené tichou editáciou bez revízie, review a auditu.

## Decision

EOS zavádza autoritatívny lifecycle pre RFC dokumenty.

RFC dokumenty používajú tieto lifecycle stavy:

- `Draft`
- `Review`
- `Accepted`
- `Rejected`
- `Superseded`
- `Deprecated`
- `Archived`

RFC v stave `Accepted` je autoritatívny pre definovaný scope a implementácia sa naň môže záväzne odvolávať.

RFC v stave `Draft` alebo `Review` nesmie byť použité ako Accepted architecture contract.

Prijatie RFC-0001, RFC-0002 a RFC-0003 sa nevykonáva automaticky týmto ADR. Ich prijatie musí prebehnúť samostatným následným governance krokom po splnení podmienok definovaných v `EOS-010`.

## Lifecycle States

### Draft

`Draft` je návrh vo vývoji.

Význam:

- môže sa významne meniť,
- slúži na tvorbu a diskusiu,
- nie je autoritatívnym podkladom pre implementáciu,
- nesmie byť použitý ako záväzný kontrakt.

### Review

`Review` znamená, že návrh je pripravený na odbornú kontrolu.

Význam:

- významové zmeny sú stále povolené,
- dokument čaká na posúdenie architektom, vlastníkom znalostí alebo governance procesom,
- nesmie byť použitý ako Accepted architecture contract,
- môže slúžiť ako vstup do review reportu alebo readiness review.

### Accepted

`Accepted` znamená, že návrh je prijatý ako autoritatívny pre definovaný scope.

Význam:

- implementácia sa na RFC môže záväzne odvolávať,
- význam sa nesmie meniť tichou editáciou,
- zmeny musia byť riadené cez revision, version, nové review alebo superseding RFC,
- Accepted RFC nesmie kolidovať s Accepted ADR alebo governance dokumentmi.

### Rejected

`Rejected` znamená, že návrh bol posúdený a neprijatý.

Význam:

- nesmie byť používaný ako architektonický základ,
- zostáva zachovaný pre audit rozhodnutia,
- môže byť zdrojom poučenia alebo rejected alternative pre budúce rozhodnutia.

### Superseded

`Superseded` znamená, že RFC bolo nahradené novším RFC alebo rozhodnutím.

Význam:

- nový dokument preberá autoritatívny význam,
- pôvodný dokument už nie je platný pre novú implementáciu,
- pôvodný dokument zostáva zachovaný pre audit a históriu,
- musí uvádzať náhradu alebo odkaz na superseding rozhodnutie.

### Deprecated

`Deprecated` znamená, že RFC alebo jeho časť môže byť dočasne podporovaná, ale neodporúča sa na nové použitie.

Význam:

- nové použitie je zakázané alebo neodporúčané podľa uvedeného dôvodu,
- musí existovať plán náhrady alebo odstránenia,
- musí byť uvedené prechodné obdobie alebo podmienka ukončenia podpory.

### Archived

`Archived` znamená, že RFC je historický dokument mimo aktívneho lifecycle.

Význam:

- nesmie riadiť novú implementáciu,
- zostáva dostupné pre audit,
- nemá sa obsahovo upravovať okrem jednoznačne označených archivačných metadát.

## State Transitions

Povolené prechody:

| From | To | Meaning |
| --- | --- | --- |
| `Draft` | `Review` | Návrh je pripravený na odbornú kontrolu |
| `Review` | `Draft` | Review odhalilo potrebu zásadného prepracovania |
| `Review` | `Accepted` | Návrh splnil acceptance criteria |
| `Review` | `Rejected` | Návrh bol posúdený a neprijatý |
| `Accepted` | `Superseded` | Novší RFC alebo governance rozhodnutie preberá autoritatívny význam |
| `Accepted` | `Deprecated` | Návrh je dočasne podporovaný, ale neodporúča sa na nové použitie |
| `Deprecated` | `Superseded` | Náhrada preberá autoritatívny význam |
| `Rejected` | `Archived` | Zamietnutý návrh sa ponechá iba historicky |
| `Superseded` | `Archived` | Nahradený dokument sa presunie mimo aktívneho lifecycle |
| `Deprecated` | `Archived` | Dočasne podporovaný dokument sa vyradí z aktívneho lifecycle |

Zakázané prechody:

- `Draft` -> `Accepted`
- `Draft` -> `Superseded`
- `Draft` -> `Deprecated`
- `Rejected` -> `Accepted`
- `Archived` -> `Accepted`

Priamy prechod, ktorý obchádza review, je zakázaný. Výnimka je možná iba explicitným ADR alebo samostatným governance rozhodnutím, ktoré vysvetlí dôvod, scope a auditnú stopu.

## Acceptance Criteria

RFC môže prejsť do `Accepted` iba vtedy, keď:

- má ukončený odborný review,
- nemá otvorené Critical alebo High blockery pre svoj scope,
- je terminologicky konzistentné s Accepted glossary a governance,
- nekoliduje s Accepted ADR,
- má aktualizovanú Change History,
- má identifikované závislosti,
- má určený implementačný scope,
- má vyriešené alebo explicitne deferred otvorené otázky,
- potrebné identifikátory a prefixy sú governance schválené,
- existuje explicitný záznam o prijatí.

Pre RFC-0001, RFC-0002 a RFC-0003 platí, že ich prijatie sa vykoná samostatným následným governance krokom. Vytvorenie ADR-0014 ich neoznačuje ako `Accepted`.

## Revision and Version Rules

`Revision` sa zvyšuje pri obsahovej zmene v rámci tej istej verzie.

`Version` sa zvyšuje pri významnej zmene kompatibility alebo scope.

Zmena `Status` sa musí zaznamenať v Change History.

Accepted RFC sa nesmie obsahovo meniť bez:

- novej `Revision` a návratu do `Review`, ak ide o meaningful change v rámci rovnakého scope,
- alebo novej `Version` alebo superseding RFC, ak ide o breaking architectural change alebo zásadnú zmenu scope.

Historická prijatá verzia musí zostať auditovateľná.

Žiadne pravidlo v tomto ADR neumožňuje prepísať Accepted význam bez review.

## Relationship to ADR and Governance Documents

Priorita autoritatívnych artefaktov v EOS je:

1. Governance documents
2. Accepted ADR
3. Accepted RFC
4. Implementation contracts and documentation

Pravidlá:

- RFC nesmie meniť Accepted ADR.
- Ak RFC odhalí potrebu zmeniť Accepted ADR, najprv musí vzniknúť nový ADR.
- ADR rozhoduje medzi významnými alternatívami.
- RFC opisuje model, kontrakt, návrh alebo systematický scope.
- Governance dokument určuje procesné a projektové pravidlá.
- Implementácia nesmie meniť význam Accepted RFC.

Ak vznikne konflikt medzi Accepted RFC a implementáciou, implementácia sa musí opraviť alebo musí vzniknúť nový RFC alebo ADR podľa povahy zmeny.

## Change Control After Acceptance

### Minor editorial correction

Minor editorial correction je oprava preklepu, formátovania, odkazu alebo zjavne neúmyselnej jazykovej chyby.

Pravidlá:

- nesmie meniť význam,
- musí byť zaznamenaná podľa governance pravidiel,
- nesmie meniť scope, objektový model, povinnosť, identifikátor alebo kontrakt.

### Meaningful change

Meaningful change mení definíciu, scope, povinnosť, objektový model alebo kontrakt v rámci rovnakého významového smeru.

Pravidlá:

- vyžaduje novú `Revision`,
- stav RFC sa musí vrátiť do `Review`,
- implementácia sa nesmie považovať za zosúladenú, kým zmena nie je znovu `Accepted`.

### Breaking architectural change

Breaking architectural change mení kompatibilitu, zásadný scope, identitu objektov, základný lifecycle alebo implementačný kontrakt spôsobom, ktorý môže rozbiť existujúce použitie.

Pravidlá:

- vyžaduje novú `Version` alebo superseding RFC,
- môže vyžadovať ADR,
- musí obsahovať migration alebo compatibility assessment.

## Superseding and Deprecation

`Superseded` sa používa vtedy, keď nový dokument preberá autoritatívny význam pôvodného dokumentu.

Pravidlá pre `Superseded`:

- starý dokument už nie je platný pre novú implementáciu,
- musí uvádzať nový autoritatívny dokument alebo rozhodnutie,
- zostáva zachovaný pre audit.

`Deprecated` sa používa vtedy, keď dokument alebo jeho časť zostáva dočasne platná alebo podporovaná, ale nové použitie je zakázané alebo neodporúčané.

Pravidlá pre `Deprecated`:

- musí uvádzať dôvod deprecácie,
- musí uvádzať náhradu alebo plán náhrady,
- musí uvádzať prechodné obdobie alebo podmienku ukončenia podpory,
- nesmie sa používať ako skrytý spôsob zrušenia bez auditu.

## Rejected Alternatives

### 1. Používať iba Draft a Accepted

Odmietnuté, pretože medzi voľným návrhom a prijatým kontraktom chýba stav odbornej kontroly. Tento model by podporoval predčasné prijatie nedostatočne preskúmaných návrhov.

### 2. Povoliť priame Draft -> Accepted

Odmietnuté, pretože obchádza review, zvyšuje riziko terminologických a architektonických konfliktov a oslabuje audit rozhodovania.

### 3. Riadiť RFC lifecycle iba cez Git branches a pull requests

Odmietnuté, pretože Git workflow eviduje technickú zmenu súboru, ale neurčuje autoritatívny význam dokumentu, jeho governance stav ani podmienky prijatia.

### 4. Považovať RFC po commite automaticky za Accepted

Odmietnuté, pretože commit znamená uloženie artefaktu, nie prijatie architektonického rozhodnutia alebo kontraktu.

### 5. Používať ADR namiesto RFC pre každý návrhový dokument

Odmietnuté, pretože ADR má rozhodovať medzi významnými alternatívami, zatiaľ čo RFC môže opisovať model, scope, kontrakt alebo systematický návrh, ktorý ešte nie je finálnym rozhodnutím.

### 6. Umožniť tiché úpravy Accepted RFC bez novej Revision

Odmietnuté, pretože by stratila auditovateľnosť, spätná dohľadateľnosť a dôvera v Accepted RFC ako implementačný základ.

## Consequences

Pozitívne dôsledky:

- RFC dokumenty majú jasný lifecycle.
- Implementácia vie rozlíšiť návrh od autoritatívneho kontraktu.
- Accepted RFC sú chránené pred tichými významovými zmenami.
- CRC-0009 a ARR-001 majú autoritatívne rozhodnutie.

Negatívne dôsledky:

- Pred prijatím RFC vzniká dodatočný governance krok.
- Niektoré existujúce governance dokumenty budú potrebovať následnú aktualizáciu, aby obsahovali RFC lifecycle a prefixy.
- Implementácia `0.2B.1` musí počkať na formálne prijatie príslušných RFC.

## Compliance and Validation

Budúce kontroly RFC majú overovať:

- povinnú hlavičku RFC,
- povinné pole `Status`,
- povinné pole `Revision`,
- povinnú Change History,
- povolené hodnoty lifecycle,
- nepovolené prechody, najmä `Draft` -> `Accepted`,
- konflikt s Accepted ADR,
- otvorené Critical alebo High blockery pred prechodom do `Accepted`,
- existenciu explicitného záznamu o prijatí.

Toto ADR nevytvára validátor ani JSON schému. Definuje iba budúce validačné požiadavky.

## Open Follow-up Actions

- Aktualizovať `EOS-002` alebo `EOS-003` v samostatnej úlohe, ak sa rozhodne zapisovať RFC lifecycle do governance štandardu.
- Formálne aplikovať lifecycle na RFC-0001, RFC-0002 a RFC-0003.
- Rozhodnúť Accepted stav RFC-0001 až RFC-0003 až po splnení všetkých podmienok `EOS-010`.
- Doplniť `EOS-003` o RFC prefix v samostatnej governance úlohe.
- Neskôr zvážiť automatizovanú kontrolu RFC hlavičiek, lifecycle hodnôt a Change History.

## Related Documents

- `docs/governance/EOS-002_Documentation_Standard.md`
- `docs/governance/EOS-003_Identification_and_Versioning.md`
- `docs/governance/EOS-009_Architecture_Closure_Plan.md`
- `docs/governance/EOS-010_Architecture_Readiness_Review.md`
- `docs/rfc/RFC-0001_Engineering_Property_Model.md`
- `docs/rfc/RFC-0002_Engineering_Object_Taxonomy.md`
- `docs/rfc/RFC-0003_EOS_Engineering_Glossary.md`
- `docs/rfc/RFC-0001-0003_Cross_Consistency_Review.md`

## Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-07-25 | 0.1 | 0 | Codex | Initial accepted ADR establishing RFC governance lifecycle |

## Review Date

2026-08-15
