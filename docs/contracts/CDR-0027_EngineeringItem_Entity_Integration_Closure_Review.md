# CDR-0027: Integračné uzatvorenie EngineeringItem v1

Project: EOS – Engineering Operating System\
Contract Review ID: CDR-0027\
Review type: Integračné uzatvorenie\
Version: 0.1\
Revision: 0\
Status: Review\
Document basis: RFC-0003 G-0082, CDR-0025 a [zmrazený kontrakt CDR-0026 §19](CDR-0026_Stable_Part_and_Engineering_Release_PreDesign_Review.md)

## Rozsah a identita

Posudzovaný je implementovaný kontrakt, nie správnosť alebo pôvod skutočných dielov. Základ: čistý main po PR #11, 2cfb93f. Jeden EIT označuje jednu opakovane špecifikovateľnú položku naprieč jej riadenými vydaniami. Premenovanie, nové vydanie a autoritatívne potvrdené prečíslovanie výkresu identitu samy nemenia. Samostatne vyberateľný variant dostáva inú identitu podľa technickej autority; validátor kontinuitu neodhaduje.

## Kontrakt a registrácia

| Kontrola | Výsledok |
| --- | --- |
| Tvar | Draft 2020-12, uzavretý koreň. Povinné: id, schemaVersion, recordVersion, revision, status, createdAt, createdBy, updatedAt, updatedBy, sourceLinks, changeSummary, name. Voliteľné: description a classifications. |
| Identifikátor | Centrálna definícia EIT s formátom ^EIT-[0-9]{4}$; schéma ju referencuje. Nová definícia nemení žiadnu existujúcu množinu povolených subjektov Observation. |
| Objaviteľnosť | schemas/entities/engineering-item.schema.json, v indexe $defs.engineeringItem. Bez novej koreňovej kolekcie. |
| Agregát | EngineeringItem môže existovať bez vydania. Nepatrí mu iný koreň. EngineeringRelease bude odkazovať na položku, nie naopak. |
| Pôvod | Povinné sourceLinks dokladá evidenciu a identitu položky. Draft pripúšťa prázdny zoznam, Review/Approved vyžaduje koreňový zdroj. Zdroj vnoreného zaradenia ho nenahrádza. |
| Zaradenie | Iba Classification[] pre stabilné zaradenie. Zmena klasifikácie sama neurčuje nový EIT. Pri poskytnutom katalógovom kontexte sa použije spoločná kontrola existencie a stavu CLS; bez kontextu sa existencia nepredstiera. |
| Hranice | Diel nie je fyzický kus ani výkres. Číslo výkresu, číslo dielu u zákazníka či dodávateľa ani SKU nie sú EIT. Žiadna heuristika ani register aliasov. |
| Vylúčenia | Bez properties, notes, spätných odkazov na vydania, technického predpisu, zásob, ceny a výrobných krokov. Žiadny prechod k PropertyRecord, PRP, UNT ani CND. |

V produkcii pribudla len schéma entity, centrálne ID, odkaz v indexe a registrácia do existujúcich ciest pre pôvod a klasifikácie. Pravidlá existujúcich entít, životný cyklus katalógu a závislosti sa nezmenili.

## Dôkazy

Profil ADR-0017 deklaruje očakávania nezávisle od schémy. Dve fiktívne fixtures v tests/fixtures/valid/entities pokrývajú minimum a záznam s opisom, klasifikáciou a koreňovým pôvodom. Spoločný runner vytvorí pre EngineeringItem **60** negatívnych prípadov (29 generovaných, 6 jednotlivých mutácií vstupu, 25 vylúčených polí). Pomenované prípady deferred-properties a deferred-releases chránia hranicu medzi stabilnou identitou a technickým vydaním.

Tri metódy pre EngineeringItem: matica stavov CLS (zdieľaná s existujúcimi entitami), viaceré zaradenia s nevyriešeným druhým odkazom a nezávislosť koreňového dôkazu od dôkazu zaradenia. Spoločný profil navyše overuje pôvod pri oboch hodnotách príznaku tvrdení aj bez neho. DEFAULT pripúšťa Approved, Deprecated varuje; AUTHORING navyše pripúšťa Draft a Review. Archived je odmietnuté v oboch režimoch.

| Scenár | Presná diagnostika (kód; cesta; recordId; referencedId; severity) |
| --- | --- |
| Druhé zaradenie nenájdené | reference_integrity.reference_not_found; $.classifications[1].classificationId; EIT-9002; CLS-999999; error. Presne jedna chyba, bez následnej chyby stavu. |
| Deprecated pri prvom zaradení | catalog_validation.deprecated_reference; $.classifications[0].classificationId; EIT-9001; CLS-980001; warning. Výsledok zostáva platný. |
| Chýba zdroj identity pri doloženom zaradení | application_validation.source_links_required; $.sourceLinks; EIT-9002; null; error. |

Mutačná skúška pracovala výhradne v pamäti s novým validátorom pre každú zmenu. Test nezávislého profilu odhalil odstránenie povinného name a výmenu EIT za MAC. Test negatívnych prípadov odhalil osobitne povolenie properties a releases. Test druhého chýbajúceho CLS odhalil osobitne poškodenú cestu, stratu recordId a stratu referencedId. **7/7 odhalených ako zlyhanie asercie**, bez ponechania mutácie na disku.

Východisková sada: 284/284; 24 schém a 230 odkazov. Výsledok po implementácii: **287/287**, 0 failures, 0 errors, 0 skipped; **25/25** schém prešlo kontrolou Draft202012Validator.check_schema, **243/243** odkazov vyriešených v registrovanom kontexte vlastniacej schémy. Python 3.12.14, jsonschema 4.26.0, referencing 0.37.0.

## Governance a rozhodnutie

1. PASS: iba fiktívne, netechnické fixtures; prípad 001 zostal neautoritatívny.
2. PASS: identita podľa prijatého CDR, nie podľa odhadu alebo výrobnej normy.
3. PASS: dve platné fixtures, žiadne výrobné podklady.
4. PASS: centrálne EIT, jediný význam; ID a história CDR evidované.
5. PASS: správny modul, bez nového mechanizmu validácie.
6. PASS: opätovné použitie metadát, klasifikácie a spoločného testovacieho profilu.
7. PASS: UTF-8, dokumentácia po slovensky, identifikátory po anglicky.
8. PASS: závislosti a technologický rámec nezmenené.
9. PASS: úplná regresia a mutačné skúšky podľa výsledkov vyššie.
10. PASS: implementácia už prijatých rozhodnutí; žiadna odchýlka od ADR-0012/0017 ani nové architektonické rozhodnutie.
11. PASS: plánovanie rozlišuje lokálne dokončenie a publikáciu.
12. PASS: EngineeringRelease nezačal; ERL zostáva Candidate, bez produkčnej definície alebo záznamu.

**EngineeringItem v1 COMPLETE lokálne, čaká na publikovanie.** Až na základe tohto uzatvorenia prechádza EIT z Candidate na Active podľa EOS-003. Technické vydanie, správa výkresov, externé identifikátory, materiálové požiadavky, operácie a BOM ostávajú mimo rozsahu.

## História zmien

| Verzia | Revízia | Zmena |
| --- | --- | --- |
| 0.1 | 0 | Prvé lokálne integračné uzatvorenie EngineeringItem v1. |
