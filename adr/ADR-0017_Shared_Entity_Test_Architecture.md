# ADR-0017 - Shared Entity Test Architecture

**Status:** Accepted  
**Date:** 2026-11-05  
**Document basis:** Internal governance decision (schválené používateľom)

## Kontext

Na `origin/main` pri `af7cb9e` sú najvyšší súbor aj najvyššia citácia ADR-0018. Číslo 0017 nie je voľná poradová voľba: skill `eos-write-tests` a handoff zo 4. novembra ho výslovne spájajú s konsolidáciou testov. V dostupnej histórii všetkých vetiev chýba súbor ADR-0017, spoločný profil, modul pomôcok aj adresár tabuliek; publikované hlavy oboch PR ukazujú na už preverené commity. ADR-0019 by ponechalo existujúce odkazy nevyriešené. Toto je nový návrh pod rezervovaným číslom, nie obnovenie údajne schváleného textu.

## Problém a východiskové meranie

Na Windows, Python 3.12.14, jsonschema 4.26.0 a referencing 0.37.0: 290 metód prešlo, 0 failures/errors/skipped. Štyri moduly: `test_validation.py` 196, `test_catalog_validation.py` 42, `test_supplier_validation.py` 25, `test_manufacturing_process_validation.py` 27. Najväčší je prvý: 2 514 riadkov, 131 972 bajtov pracovnej kópie. Z 804 JSON fixtures je 132 platných, 671 neplatných a jedna kontextová (najväčšia: `catalog-context/fictional-catalog-context.json`, 10 166 bajtov). Počet 671 neoznačuje všetky fixtures.

| Rodina | Platné | Neplatné |
| --- | ---: | ---: |
| DocumentRecord / NormReference / SourceReference | po 1 | po 0 |
| Quantity | 5 | 12 |
| ValueRange | 8 | 20 |
| MeasurementQuality | 10 | 29 |
| Condition | 7 | 31 |
| Classification | 4 | 26 |
| PropertyRecord | 10 | 40 |
| Observation | 10 | 45 |
| Unit Catalog | 8 | 31 |
| Condition Type Catalog | 8 | 38 |
| Property Catalog | 11 | 44 |
| Classification Catalog | 9 | 34 |
| Material | 16 | 42 |
| Supplier | 12 | 131 |
| ManufacturingProcess | 11 | 148 |

Supplier a ManufacturingProcess majú 22 rovnakých názvov testovacích metód, nie nutne 22 identických záruk. Oba moduly napríklad iterujú súbory, kontrolujú uzavretosť, common metadata, required polia, cestu chýbajúceho sourceLinks, odmietnutie odložených polí a index bez kolekcie. Material má príbuzné kontroly MAT, metadát, indexu a fixtures v test_validation; kontextové testy aj v test_catalog_validation.

Po porovnaní dekódovaných objektov so svojou platnou minimálnou fixture má 129/131 SUP a 146/148 TEC presne **jeden odlišný koreňový kľúč** (pridaný, chýbajúci alebo zmenený; zmena vnútri poľa sa ráta raz). Nie je to dôkaz jediného diagnostického dôvodu. Konkrétne 97 SUP a 125 TEC názvov obsahuje `deferred-`: napríklad pridanie TEC poľa `abrasive` má byť jedinou príčinou additionalProperties. Material má podľa toho istého porovnania 0/42; jeho prípady sa nesmú hromadne premenovať na rovnakú mutáciu. Chýbajúce/null polia, chybný prefix, koreň typu pole, prázdny name a neznáme pole budú explicitné spoločné pravidlá; samotný počet starých súborov nedokazuje pokrytie každého z nich v každej rodine.

## Rozhodnutie

Ponechať unittest, subTest a jsonschema. Pre **existujúce entity** zaviesť malý explicitný profil, deterministické záporné prípady a zdieľané načítanie vstupov. Očakávanie je nezávislé od testovanej schémy: najmä povolené polia sa nesmú odvodiť z aktuálneho obsahu schémy, lebo potom by test akceptoval aj chybnú zmenu.

## Rozsah

Rozhodnutie je prierezové pre testy; nemení testovací framework, produkčné schémy, validátor, katalógové ani Machine významy. Žiadne nové závislosti, reálne dáta, persistence ani UI. Meranie ostatných rodín nie je automatické povolenie migrovať ich.

## Model ENTITY_PROFILES

V budúcom `tests/test_entity_profiles.py` stačí slovník podľa mena rodiny. Riadok deklaruje family, schemaPath/schemaId, idFamily, required, allowed, názvy minimal/populated fixtures, owned, invalidTable a indexDef, prípadne očakávanú indexovú kolekciu. Názvy ciest možno odvodiť jedinou čitateľnou konvenciou: pre rodinu F je schéma `schemas/entities/F.schema.json`, URI má základ `https://eos.local/schemas/`; platné sú `tests/fixtures/valid/entities/F-{minimal-draft,populated-source-links}-valid.json`, tabuľka `tests/fixtures/invalid-cases/F.json`. Bez dedičnosti profilov, pluginov a dynamického generovania tried.

Nezávislá spoločná množina R: id, schemaVersion, recordVersion, revision, status, createdAt, createdBy, updatedAt, updatedBy, sourceLinks, changeSummary, name. Allowed = required plus presne uvedené voliteľné polia:

| F / ID | Required | Voliteľné | Owned | Index: definícia / kolekcia |
| --- | --- | --- | --- | --- |
| material / MAT | R | description, notes, properties, classifications, replaces, replacedBy | PropertyRecord, Classification | material / materials |
| supplier / SUP | R | description, notes, classifications | Classification | supplier / žiadna |
| manufacturing-process / TEC | R + description | notes, classifications | Classification | manufacturingProcess / žiadna |

Spoločný test overí Draft 2020-12, uzavretosť, centrálny ID odkaz aj správanie nesprávneho prefixu, common metadata, presné množiny polí a index. Spustí minimum i populated a všetky ďalšie platné tvary; vykoná tabuľky a generované prípady pre každé missing/null required, prázdny name, zlý prefix, neznáme pole a koreň typu pole. V matici Draft/Review/Approved overí prázdne/neprázdne root sourceLinks, pôvodné varianty príznaku a presnú početnosť diagnostiky. Required description sa netestuje ako univerzálne pravidlo. Odkaz na owned typ neimplikuje jeho doménovú kompatibilitu.

## Spoločný validation_support

SUP a TEC dnes opakujú ROOT/BASE/INDEX/VALID/INVALID, funkciu fixture(name), načítanie fictional-catalog-context, vytvorenie EosValidator a takmer zhodnú assert_valid. Spoločné s Material/katalógmi sú aj URI a cesty. Do `tests/validation_support.py` presunúť iba časti použité aspoň dvoma testami/modulmi: cesty, načítanie novej kópie JSON podľa rodiny, prípravu fiktívneho kontextu pre kontextové testy. Validator vytvárať priamo, ak by helper iba premenoval konštruktor. Lokálne ponechať doménové assertions a runner mutácií, kým druhý nezávislý konzument nepotrebuje totožnú logiku. Žiadny globálny meniteľný záznam ani skryté očakávania.

## Tabuľkové neplatné prípady

Navrhovaný dátový príklad, nie nový súbor:

```json
{
  "cases": [
    {"name":"lowercase-id","base":"minimal-draft","ops":[["set","/id","sup-9001"]],
     "expect":{"errorCode":"schema_validation.pattern","path":"$.id"}}
  ],
  "deferred": ["exampleExcludedField"]
}
```

Každý názov musí byť v rodine jedinečný. Base označuje menovanú, najprv overenú platnú fixture. Na čerstvej kópii stačí `set` (nastaví alebo pridá kľúč) a `remove` (iba existujúci kľúč). Absolútna cesta používa JSON Pointer s dekódovaním ~0/~1; rodič musí existovať, index poľa musí byť existujúci nezáporný index. Žiadne wildcardy, implicitné vytváranie vetiev, append ani všeobecný JSON Patch. Neplatný názov, base, cesta alebo operácia je chyba testovacích dát, nie úspešne odmietnutý záznam.

Jeden prípad mení jedno pravidlo. Primárny test overí očakávaný errorCode aj **výstupnú EOS cestu**, nie iba `ok == False`; pri samostatnom porušení aj početnosť. Ak jeden vstup nutne produkuje viac správ, zachovať explicitný očakávaný zoznam v špecifickom teste, neschovávať druhú chybu. Koreň typu pole generovať priamo ako `[]` s očakávaním type na koreňovej ceste. Každý názov v deferred vygeneruje jeden prípad s jediným novým poľom, očakáva additionalProperties na konkrétnej ceste a po odstránení poľa opäť platný základ. Len skutočné odložené polia z daného CDR; ukážkový názov vyššie nie je rozhodnutie o poli.

## Platné fixtures

Ponechať minimálny Draft a populated-source záznam, ďalšie len pre odlišný tvar, napr. viac vnorených tvrdení. Opakovanie hodnôt riešiť subTest. Zachovať fiktívne vstupy; najprv mapovať aj staré pozitívne prípady.

## Špecifické testy

Nepresúvať do profilu Material replacement a vnorené PRP/UNT/CND, odlišnosť koreňových a vnorených zdrojov, Observation subject ani CLS lifecycle/warning politiky bez dôkazu ekvivalencie. Používať verejné validate/validate_with_context; zachovať category, severity, path, recordId, referencedId, početnosť a pozitívne kontroly tam, kde ich vyžaduje pôvodná záruka.

## Migrácia

1. Až po explicitnom prijatí pripraviť spoločný runner, východiskovú mapu pokrytia a minimálne fixtures; stará sada ďalej beží.
2. Pilot Supplier: Classification a root provenance bez PropertyRecord a replacement. Má 131 záporných prípadov, takže prínos aj ekvivalenciu možno zmerať; TEC by na pilot pridal required description a väčšiu sadu. Spustiť staré aj nové prípady na tej istej revízii produkčného kódu.
3. Po prijatí dôkazov migrovať ManufacturingProcess (povinný description, discovery bez kolekcie) a nakoniec Material (indexová kolekcia, replacement, kompozícia tvrdení). Každú rodinu preskúmať oddelene. Zachovať existujúce verejné správanie bez úprav schém/validátora kvôli migrácii.
4. Až po overení všetkých troch rodín, zjednotení návodov a samostatnom zadaní uvoľniť Machine. Tento Draft nič z toho neaktivuje.

## Vyradenie a ekvivalencia

V migračnom PR uchovať verziovanú mapu: stará cesta/metóda a konkrétny subprípad → nové stabilné ID (rodina + názov pravidla/riadku a vstup) → očakávané diagnostiky alebo úspech → výsledok súbežného behu a odkaz na skúšku citlivosti daného pravidla. Viac starých prípadov môže mať jeden cieľ len pri zdôvodnenej totožnosti záruky. Nuly v stĺpci „nenamapované“ sú podmienkou vymazania starých fixtures rodiny. Pri nenahraditeľnom komplexnom vstupe zachovať vstup a špecifický test; súbory nemažú počty ani podobnosť názvu.

## Skúška citlivosti

Dočasne narušiť chránené pravidlo alebo jednu kópiu vstupu, spustiť pomenovaný test, zaznamenať očakávané zlyhanie konkrétneho subTest. Ihneď vrátiť **iba vlastnú** dočasnú úpravu, skontrolovať diff a spustiť celú sadu. Nepoužiť reset/clean a necommitovať zámernú poruchu. Pozitívny výsledok bez preukázaného negatívneho signálu nestačí pre nový mechanizmus.

## Počet metód a prípadov

Uvádzať oddelene skutočné unittest methods run, failures/errors/skipped a počet vykonaných pomenovaných generovaných a tabuľkových prípadov podľa rodiny. Súbor tabuľky nie je jeden prípad; počet definovaných riadkov nie je počet vykonaných. SubTest nepridáva samostatnú unittest metódu. Pokles metód je dôvod vyšetrovať, nie dôkaz parity. Zámerný pokles pripustiť až po schválenom mapovaní, rovnakých alebo silnejších assertions a oboch zelených behoch; v CHANGELOG uviesť staré/nové metódy, prípady a dôvod. Spresniť eos-run-tests pri migrácii, nie potichu znížiť baseline.

## Vplyv na project_status a návody

`scripts/project_status.py` na tejto revízii neexistuje: dnes nepočíta testy, fixtures, schémy, referencie ani ADR/RFC. Nie je potrebný na rozhodnutie ani na pilot. Ak neskôr vznikne, oddeliť fyzické súbory, prípady odvodené z profilov/tabuliek a výsledky skutočného test runu. Pri migrácii zosúladiť tests/README, eos-schema-change a eos-write-tests s dodanými cestami: README dnes opisuje samostatné invalid fixtures, skilly už odkazujú na chýbajúci profil, validation_support, invalid-cases a rozdelené moduly. Overiť každý odkaz vrátane project_status a „Nová entita“; nepredpisovať neexistujúci skript ani nevytvárať súbor iba kvôli odkazu. Historické výsledky nemazať.

## Zvažované alternatívy

| Možnosť | Posúdenie |
| --- | --- |
| Nechať plné súbory a per-entity testy | Ľahko sa čítajú samostatne, ale 222 deferred fixtures len pre dve entity kopíruje prevažne nezmenený základ. Ponechať len tam, kde tvar nesie vlastný význam. |
| Profily + tabuľkové prípady | Opakované záruky sú identifikovateľné, rozdiely MAT/SUP/TEC sa zmestia do jedného riadka na rodinu. Náklady: malý deterministický runner a kontrola samotných testovacích dát. Odporúčaná voľba. |
| Externý parametrizačný/property-based framework | Poskytuje generovanie vstupov, ale neprináša mapu starých záruk; unittest.subTest stačí bez novej závislosti. |
| Všeobecný meta-framework alebo big-bang prepis | Menej mechanického kódu, ale skryté očakávania alebo jediná chybná slučka môžu zakryť celú rodinu. Ťažšie určiť, ktorý krok stratil coverage. |

## Dôsledky a riziká

Menej kópií, nie menej kontrol. Cena je jednorazové mapovanie a dočasné dvojité behy. Chybný generátor môže ignorovať prázdnu tabuľku, duplikát či neznámu operáciu: kontrolovať jedinečnosť a očakávaný vykonaný súbor ID oproti mape, chybnú konfiguráciu odmietnuť. Nepresúvať špecifickú sémantiku do generátora. Chyba migrácie nie je dôvod oslabiť validator. Zodpovednosť za prijatie ADR zostáva používateľovi.

## Bezpečný návrat

Pri chýbajúcom mapovaní, odlišnej diagnostike alebo nevysvetlenom poklese zastaviť rodinu, zachovať staré testy ako autoritatívnu regresiu a opraviť iba návrh migrácie. Pred ďalšou rodinou vyžadovať samostatný overiteľný krok. Po zlúčení možno vrátiť konkrétny migračný commit štandardným review bez prepisu histórie.

## Súvisiace dokumenty

EOS-000/001/002/003/006/007; ADR-0013 a ADR-0018; AGENTS.md a TECH_STACK.md; tests/README.md; projektové skilly eos-adr, eos-write-tests, eos-schema-change, eos-run-tests, eos-governance-check a eos-git-publish; CDR-0016/0018/0020/0021. Pre pôvod odkazu na číslo pozri docs/handoff/2026-11-04_ai-guardrails.md.

## Termín review

2026-11-05: predložené na rozhodnutie používateľa; znova posúdiť po pilote Supplier pred odstránením jeho starých fixtures.

## Change History

| Dátum | Revízia | Zmena |
| --- | --- | --- |
| 2026-11-05 | 0 | Prvý Draft na základe merania af7cb9e; žiadna migrácia ani implementácia. |
| 2026-11-05 | 1 | Používateľ prijal rozhodnutie a povolil implementáciu spoločnej infraštruktúry. Kontrola pilotu pred vyradením starých fixtures zostáva povinná. |
| 2026-11-06 | 2 | Lokálne uzavretie migrácie troch entít podľa [CDR-0022](../docs/contracts/CDR-0022_ADR-0017_Shared_Test_Architecture_Closure_Review.md); Accepted rozhodnutie sa nemení. |
