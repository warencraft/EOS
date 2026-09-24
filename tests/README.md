# tests

## Míľnik 0.2B.2.4 - Classification Catalog v1

Classification Catalog Entry má 9 platných a 34 neplatných fiktívnych fixtures v priečinkoch `fixtures/valid/catalogs/` a `fixtures/invalid/catalogs/`. Nepredstavujú reálne classifications, externé klasifikačné systémy ani autoritatívnu populáciu katalógu.

Štrnásť nových unittest testov overuje Draft 2020-12 schému, centrálny CLS a common metadata refs, SourceLink, povinný name a description, zámernú neunikátnosť name, lifecycle/provenance pri priamej aj indexovej validácii, replacement CLS odkazy, odmietnutie system/code/hierarchy/alias/equivalence/applicability polí a registráciu v schema indexe.

Kompletná sada má 182 testov. Úspešná validácia katalógovej položky nepotvrdzuje existenciu alebo použiteľnosť CLS cieľa ani kompatibilitu embedded Classification s rodičom. Spustenie z koreňa projektu:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Míľnik 0.2B.2.3 - Property Catalog v1

Property Catalog Entry má 11 platných a 44 neplatných fiktívnych fixtures v priečinkoch `fixtures/valid/catalogs/` a `fixtures/invalid/catalogs/`. Nepredstavujú reálne properties, jednotky, condition types ani autoritatívnu populáciu katalógu.

Šestnásť nových unittest testov overuje Draft 2020-12 schému, centrálne PRP/UNT/CND a common metadata refs, SourceLink, povinný name a description, uzavretý a unikátny `allowedValueTypes`, povinný UNT allow-list, voliteľný CND allow-list, lifecycle/provenance pri priamej aj indexovej validácii, replacement PRP odkazy, odmietnutie deferred polí a registráciu v schema indexe.

Kompletná sada má 168 testov. Úspešná validácia katalógovej položky nepotvrdzuje existenciu PRP, UNT alebo CND cieľa ani kompatibilitu PropertyRecord/Observation s katalógovou policy. Spustenie z koreňa projektu:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Míľnik 0.2B.2.2 - Condition Type Catalog v1

Condition Type Catalog Entry má 8 platných a 38 neplatných fiktívnych fixtures v priečinkoch `fixtures/valid/catalogs/` a `fixtures/invalid/catalogs/`. Nepredstavujú reálne typy podmienok ani autoritatívnu populáciu katalógu.

Pätnásť nových unittest testov overuje Draft 2020-12 schému, centrálny CND a common metadata refs, SourceLink, povinný name, uzavretý a unikátny `allowedValueForms`, podmienenú reference-prefix policy, jej presnú zhodu s aktuálnym Condition reference unionom, lifecycle/provenance pri priamej aj indexovej validácii, replacement CND odkazy, odmietnutie deferred polí a schema index.

Kompletná sada má 152 testov. Úspešná validácia katalógovej položky nepotvrdzuje existenciu CND alebo reference targetu a validácia Condition ešte nepoužíva katalógovú kompatibilitu. Spustenie z koreňa projektu:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Míľnik 0.2B.2.1 - Unit Catalog v1

Unit Catalog Entry má 8 platných a 31 neplatných fiktívnych fixtures v priečinkoch `fixtures/valid/catalogs/` a `fixtures/invalid/catalogs/`. Nepredstavujú reálne jednotky ani autoritatívnu populáciu katalógu.

Pätnásť nových unittest testov overuje Draft 2020-12 schému, centrálny UNT a property-level common metadata refs, SourceLink, povinný name a symbol, zámernú neunikátnosť symbolu, existujúci lifecycle, source pravidlo pri priamej aj indexovej validácii, replacement UNT formát, odmietnutie root verificationStatus a všetkých deferred polí a registráciu v schema indexe.

Kompletná sada má 137 testov. Unit Catalog v1 nekontroluje existenciu UNT záznamov, symbolové kolízie, replacement cykly, quantity-kind alebo dimension kompatibilitu ani konverzie. Spustenie z koreňa projektu:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Míľnik 0.2B.1.7 - Observation Contract

Observation má 10 platných a 45 neplatných fiktívnych fixtures v Knowledge Core priečinkoch. Pätnásť nových `unittest` testov overuje Draft 2020-12 schému, centrálny OBS a PRP formát, všetkých osem povolených subject ID rodín, GLOBAL/JOB podmienky, Quantity/ValueRange discriminator, odmietnutie PropertyRecord a arbitrary payloadu, povinný `observedAt`, spoločné metadata a registráciu v schema indexe.

Regresie dokazujú, že obrátený ValueRange, záporná MeasurementQuality uncertainty, nulová resolution a významové pravidlá ValueRange vo vnorenom Condition sa zachytia aj v Observation s úplnou cestou. `sourceLinks` je povinné pole; prázdny Draft prejde, kým Review/Approved bez zdroja vracia `application_validation.source_links_required`.

Úspešná validácia nepotvrdzuje existenciu subject, JOB, PRP ani katalógovú kompatibilitu. Nekontroluje persistence immutability, evidence promotion ani Decision workflow. Po korektívnom uzatvorení 0.2B.1 má kompletná sada 122 testov. Suite-level preflight pri chýbajúcom `jsonschema` alebo `referencing` skončí chybou a nenulovým návratovým kódom, nie úspešným preskočením testov.

Formát `sourceReferenceId` kontroluje iba JSON Schema. Platne formátovaný, ale nevyriešený SRC identifikátor zostáva platný, kým 0.2B.2 nezavedie skutočný resolver záznamov; budúca kontrola existencie musí používať kategóriu `reference_integrity`. Spustenie z koreňa projektu:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Míľnik 0.2B.1.6 - PropertyRecord Contract

Testy používajú `unittest` a existujúci EOS validátor. PropertyRecord má 10 platných a 40 neplatných fiktívnych fixtures v Knowledge Core priečinkoch. Pokrytie overuje centrálny PRP `$ref`, povinný discriminator `valueType`, presne jednu vetvu `quantity` alebo `valueRange`, všetky znovupoužité kontrakty, štyri VerificationStatus stavy, povinné ale potenciálne prázdne `sourceLinks`, viac podmienok a odmietnutie deferred, identity a lifecycle polí.

Kritické regresie dokazujú, že obrátené hranice ValueRange, záporná MeasurementQuality uncertainty a nulová resolution zostávajú aplikačnými chybami aj pri vnorení v PropertyRecord, s úplnou cestou k poľu. Kompozičná kontrola pokrýva aj ValueRange vo vnorenom Condition. Schema a aplikačné chyby zostávajú rozlíšiteľné.

Platný PRP alebo UNT formát nepotvrdzuje existenciu katalógovej položky ani kompatibilitu. Kontextová povinnosť neprázdnych zdrojov, Property Catalog pravidlá a Decision workflow nie sú predmetom týchto testov.

Kompletná sada má 105 testov. Spustenie z koreňa projektu:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Míľnik 0.2B.1.5 - Classification Contract

Testy používajú `unittest` a existujúci EOS validátor. Nové fixtures majú názvy `classification-*-valid.json` a `classification-*-invalid.json` v príslušných `tests/fixtures/valid/knowledge-core/` a `tests/fixtures/invalid/knowledge-core/` priečinkoch. Obsahujú iba fiktívne CLS a SRC identifikátory, nie reálne katalógové či zdrojové záznamy.

Pokrytie zahŕňa 4 platné a 26 neplatných fixtures, centrálny CLS `$ref`, znovupoužitie SourceLink, povinné `classificationId`, voliteľné a prázdne `sourceLinks`, viac zdrojov a zachovanie existujúceho pravidla bez unikátnosti. Neplatné fixtures sa kontrolujú podľa očakávaného schema error kódu a presnej cesty. Testy odmietajú metadáta, lifecycle, koreňový `verificationStatus`, `evaluationMode`, poznámky, voľný text a ostatné nepovolené polia; overujú vnorené chyby cez index, viac chýb naraz a rozlíšenie existujúcej kategórie `reference_integrity`.

Úspech Classification testov potvrdzuje štruktúru. Existencia a použiteľnosť CLS cieľa, externý pôvod a z neho vyplývajúca povinnosť `sourceLinks` sa ešte nekontrolujú; katalógová validácia je odložená do `0.2B.2`. Aj platný odkaz bez zdrojov môže byť po zavedení katalógu sémanticky neplatný. Test neprítomnosti odhadu pôvodu dokumentuje toto obmedzenie, nie jeho budúcu platnosť.

Kompletná sada má 92 testov vrátane pôvodných 80 testov a regresií Quantity, ValueRange, MeasurementQuality a Condition. Spustenie z koreňa projektu:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Míľnik 0.2B.1.4 - Condition Contract

Testy pre `Condition` používajú iba `unittest` a existujúcu validačnú vrstvu.

Platné a neplatné fixture sú v:

- `tests/fixtures/valid/knowledge-core/`
- `tests/fixtures/invalid/knowledge-core/`

Pokrytie zahŕňa:

- povinné `conditionTypeId` vo formáte `CND-xxxxxx`,
- povinné `evaluationMode` s hodnotami `mandatory`, `limiting`, `descriptive`, `recommended` a `contextual`,
- presne jednu hodnotovú formu z `quantity`, `valueRange`, `textValue`, `booleanValue` alebo `referenceId`,
- notes-only objekt ako neplatný,
- vnorené `Quantity` a `ValueRange` cez `$ref`,
- neprázdne `textValue` a `referenceId`,
- obmedzenie `referenceId` na existujúce centrálne podporované EOS identifikátory,
- zákaz entity metadát, lifecycle polí, `sourceLinks`, `verificationStatus` a `propertyId`,
- presné cesty k vnoreným chybám,
- dostupnosť `Condition` cez centrálny schema index,
- regresiu `Quantity`, `ValueRange` a `MeasurementQuality`.

Pre `Condition` nebolo pridané nové aplikačné pravidlo; kontraktové pravidlá tohto míľnika sú pokryté JSON Schema Draft 2020-12.

## Míľnik 0.2B.1.3 - MeasurementQuality Contract

Testy pre `MeasurementQuality` používajú iba `unittest` a existujúcu validačnú vrstvu.

Platné a neplatné fixture sú v:

- `tests/fixtures/valid/knowledge-core/`
- `tests/fixtures/invalid/knowledge-core/`

Pokrytie zahŕňa:

- `uncertainty`, nulovú `uncertainty`, `resolution` a `confidenceLevel`,
- hranice `confidenceLevel` 0 a 1,
- kombinácie štruktúrovaných polí a voliteľné `notes`,
- empty object a notes-only objekt ako neplatné,
- zápornú neistotu cez aplikačnú validáciu,
- nulové a záporné rozlíšenie cez aplikačnú validáciu,
- neplatné vnorené `Quantity`,
- presné cesty k vnoreným chybám,
- zákaz metadát, lifecycle polí, `sourceLinks`, `verificationStatus`,
- zákaz tolerančných polí a odložených polí `accuracy`, `repeatability`, `reproducibility`,
- rozlíšenie `schema_validation` a `application_validation`,
- dostupnosť `MeasurementQuality` cez centrálny schema index.

## Míľnik 0.2B.1.2 - ValueRange Contract

Testy pre `ValueRange` používajú iba `unittest` a existujúcu validačnú vrstvu.

Platné a neplatné fixture sú v rovnakých Knowledge Core priečinkoch ako `Quantity`:

- `tests/fixtures/valid/knowledge-core/`
- `tests/fixtures/invalid/knowledge-core/`

Pokrytie zahŕňa:

- uzavretý, otvorený a polootvorený rozsah,
- jednostranne ohraničené rozsahy,
- rovnaké hranice,
- zápornú až kladnú fiktívnu hodnotu,
- voliteľné `notes`,
- chýbajúci `unitId`,
- chýbajúce obe hranice,
- obrátené hranice cez aplikačnú validáciu,
- inkluzivitu bez príslušnej hranice,
- nesprávne typy hraníc,
- neplatný `UNT` identifikátor,
- `additionalProperties: false`,
- zákaz entity metadát, `sourceLinks`, `tolerance` a `uncertainty`,
- rozlíšenie `schema_validation` a `application_validation`,
- dostupnosť `ValueRange` cez centrálny schema index.

## Míľnik 0.2B.1.1 - Quantity Contract

Testy pre `Quantity` používajú iba `unittest` a existujúcu validačnú vrstvu.

Platné fixture sú v:

- `tests/fixtures/valid/knowledge-core/`

Neplatné fixture sú v:

- `tests/fixtures/invalid/knowledge-core/`

Pokrytie zahŕňa:

- platné celé číslo,
- platné desatinné číslo,
- platnú zápornú hodnotu,
- platnú nulu,
- platné voliteľné `notes`,
- chýbajúce povinné polia,
- nesprávny typ `value`,
- neplatný prefix `unitId`,
- malé písmená v prefixe `unitId`,
- neúplné nulové doplnenie `unitId`,
- `additionalProperties: false`,
- zákaz metadát entity vo value objecte,
- viac chýb v jednom zázname,
- presné cesty k chybným poliam,
- dostupnosť `Quantity` cez centrálny schema index.

Tento priečinok je určený pre budúce testy schém, dátových kontraktov a kalkulačných modulov.

Vo fáze 0.2A obsahuje testy základných dátových kontraktov.

Používa sa `unittest` zo štandardnej knižnice Pythonu. Projekt zatiaľ neprechádza na `pytest`.

Fixtures sú fiktívne a netechnické. Nesmú obsahovať reálne materiálové hodnoty, normové tabuľky, výrobné časy, ceny ani rezné podmienky.

Phase 0.2A.1 dopĺňa auditné testy pre:

- lokálne `$ref`,
- povinné polia,
- enumy,
- regex patterny,
- `additionalProperties: false`,
- neplatné dátumy a verzie,
- vnorený `SourceLink`,
- nepodporované JSON Schema kľúčové slová,
- viac chýb v jednom zázname,
- presné cesty k chybným poliam.

## Lokálne spustenie testov

V koreňovom priečinku projektu:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -m unittest discover -s tests -p "test_*.py" -v
```

Ak `jsonschema` nie je nainštalované, integračné testy validácie sú blokované. Takýto stav sa nesmie považovať za úspešný testovací beh.
