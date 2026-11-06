# CDR-0023 Machine Entity Integration Closure Review

Project: EOS – Engineering Operating System
Contract Review ID: CDR-0023
Review: Machine Entity v1
Review type: Closure
Phase: 0.2C.4
Version: 0.1
Revision: 0
Status: Review
Document basis: Accepted EOS architecture, CDR-0021 Revision 1 a integračné dôkazy

## Rozsah a východisko

Overený je výlučne profil C podľa [CDR-0021 §64](CDR-0021_Machine_Entity_PreDesign_Review.md). MI-0001 zostáva CLOSED. ADR-0017 určuje spoločné testy; CDR-0022 uzavrel infraštruktúrny predpoklad. Číslo 0023 bolo voľné po 0022. Čistá baseline cd926e90b951a66a2c4e3afa65acf7635293f481 obsahuje opravu 045acef. Pred prenosom: 277 úspešných metód, 23 platných schém, 215 rozlíšených odkazov.

## Posúdenie kontraktu

| Kritérium | Výsledok a hranica dôkazu |
| --- | --- |
| Identita | PASS. Jeden MAC-xxxx označuje jednu fyzickú výrobnú alebo kontrolnú jednotku. ID používa centrálnu definíciu MAC, bez lokálneho regexu. Názov nie je identita. |
| Kontinuita | Premenovanie, premiestnenie, zmena vlastníka, výmena vretena alebo riadiacej jednotky, pridaná os a doložená prestavba či rekonštrukcia toho istého stroja nemenia MAC. Iný fyzický kus vyžaduje nový MAC aj pri rovnakom názve a umiestnení. Nejasná kontinuita a duplicity vyžadujú riadené rozhodnutie; validátor ho nerobí. |
| Tvar | PASS. Uzavretá schéma s povinnými id, schemaVersion, recordVersion, revision, status, createdAt, createdBy, updatedAt, updatedBy, sourceLinks, changeSummary, name. Voliteľné sú len description, classifications, properties a notes. Name a prítomný description sú neprázdne reťazce. Index sprístupňuje $defs.machine, nepridáva kolekciu machines. |
| Špecifikácie | PASS. PropertyRecord je tvrdenie o konkrétnej jednotke. Katalógová kontrola overuje PRP, UNT, CND, povolený typ hodnoty, jednotku, podmienky a lifecycle. Neznáma referencia nemá vyvolať závislé chyby o kompatibilite. |
| Kategória a dôkaz | PASS. Classification používa CLS; overené sú obe politiky, päť stavov a upozornenie Deprecated. Observation môže odkazovať na MAC cez existujúci subjectId. Pozorovanie nie je vnorenou vlastnosťou a kategória nepreukazuje schopnosť. |
| Zdroje | PASS. Draft môže mať prázdne root sourceLinks, Review/Approved nie. Odkaz na úrovni jednotky nedokazuje pôvod ani použiteľnosť jednotlivého tvrdenia; vnorený zdroj nenahrádza koreňový. Pred schválením zostáva vecná kontrola zdroja špecifikácie manuálna. |
| Vylúčenia | PASS. Bez modelu, capability, Operation, WorkCenter, nastavení stroja, stavu výroby, údržby, kalibrácie, času či sadzieb. Žiadne priame zoznamy podporovaných procesov, materiálov a nástrojov. Žiadne reálne technické údaje. |

## Integračné dôkazy

- Prvá Machine regresia po prenose WIP: obrátené hranice v druhovo správnom vnorenom ValueRange vrátili jedinú chybu application_validation.value_range_reversed_bounds na $.properties[0].valueRange.minValue; recordId MAC-9001, severity error, referencedId None. Oprava z PR #7 funguje bez osobitnej diagnostiky pre Machine. Regresia MAT-9001 z PR #7 ostala v sade.
- Runtime iba registruje Machine pre existujúcu koreňovú provenance a vnorené PropertyRecord/Classification. Nezmenili sa pravidlá, verejné API, závislosti ani existujúce schémy znalostných entít.
- Dve fiktívne fixtures: minimálny Draft a Review s koreňovým zdrojom, klasifikáciou a tvrdením s vlastným zdrojom. Spoločný profil vykonal 107 negatívnych prípadov (1 explicitný, 76 deferred, 30 generovaných alebo zložených). Cielený beh: 10/10 metód (7 Machine a 3 spoločné).
- Šesť dočasných porúch bolo odhalených očakávanými testami: chybné required, zamenená rodina MAC, povolené machineCapability, poškodená cesta vnoreného rozsahu, strata MAC recordId a strata referencedId pri nenájdenom PRP. Zásahy boli obmedzené na pamäť testovacieho procesu.
- Plná sada: 284 passed, 0 failures, 0 errors, 0 skipped. Draft202012Validator.check_schema: 24/24; lokálne aj medzisúborové $ref: 230/230. Python 3.12.14, jsonschema 4.26.0, referencing 0.37.0.

## Záver

Žiadny otvorený blokér pre obmedzený kontrakt v1. Výsledok lokálneho integračného review: **Phase 0.2C.4 Machine Entity v1 COMPLETE**. Neznamená to schválenie reálneho onboardingu, výpočtu capability ani povolenie ďalšej fázy. Zmeny čakajú na používateľské review pred publikovaním.

## Change History

| Dátum | Revízia | Zmena |
| --- | --- | --- |
| 2026-11-06 | 0 | Overenie identity, vlastníctva, provenance, diagnostiky a registrácie po reintegrácii s PR #7. |
