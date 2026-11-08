---
name: eos-write-tests
description: Ako písať a meniť testy a fixtúry v EOS podľa ADR-0017 (spoločný profil entít, tabuľky neplatných prípadov s presnou diagnostikou). Použi vždy pred pridaním testu, fixtúry alebo neplatného prípadu, aj pri novej entite.
---

# Testy a fixtúry v EOS (ADR-0017)

Platí `adr/ADR-0017_Shared_Entity_Test_Architecture.md` a uzavretie migrácie v CDR-0022. Vzor pre novú entitu: Machine (CDR-0023) a EngineeringItem (CDR-0027).

## 0. Najprv sa opýtaj

1. **Pokrýva to už spoločný profil?** `tests/test_entity_profiles.py` overuje pre každú entitu tvar schémy, povinné a voliteľné polia, centrálne ID, index, platné fixtúry, root provenance a negatívne prípady. Ak áno, nepíš nový test.
2. **Je to len nový neplatný vstup?** Potom je to **riadok v tabuľke** `tests/fixtures/invalid-cases/<family>.json`, nie nový test.
3. **Existuje podobný test inde?** `grep -rn "<pole alebo errorCode>" tests/`. Rozšír existujúci test cez `subTest`, nevytváraj kópiu.

## 1. Kam čo patrí

| Čo testuješ | Kam |
| --- | --- |
| spoločné kritériá entity | riadok v `ENTITY_PROFILES` v `tests/test_entity_profiles.py` |
| neplatný vstup s jedným dôvodom zlyhania | riadok v `cases` v `tests/fixtures/invalid-cases/<family>.json` |
| pole, ktoré CDR odkladá alebo zakazuje | názov poľa v zozname `deferred` tej istej tabuľky |
| platný príklad odlišného tvaru | `tests/fixtures/valid/entities/<family>-<case>-valid.json` + názov v `validCases` profilu |
| CLS lifecycle, nenájdené referencie, nezávislosť root a claim zdrojov | zdedené kontroly z `tests/owned_claim_checks.py` (`OwnedClassificationChecks`, `OwnedClaimChecks`) |
| pravidlo iba pre jednu entitu (výnimka z CDR) | `tests/test_<entity>_validation.py` |
| kontextová validácia voči katalógom | `tests/test_catalog_validation.py` |
| jadro validátora, knowledge core, katalógové schémy, referencie | existujúce testy v `tests/test_validation.py`; nový súbor iba pre novú oblasť |
| cesty a načítanie fixtúr | `tests/validation_support.py` (`entity_fixture`, `load_json`), nie kópia v každom súbore |
| nástroj na príjem zákazky | `tests/test_job_intake.py` (iba fiktívne súbory v dočasnom priečinku) |

## 2. Riadok v `ENTITY_PROFILES`

```python
"machine": {
    "validCases": ["minimal-draft", "populated-source-links"],
    "idFamily": "MAC", "required": COMMON | {"name"},
    "optional": {"description", "notes", "properties", "classifications"},
    "owned": {"properties": "property-record", "classifications": "classification"},
    "indexDef": "machine", "collection": None, "deferredValue": "fictional",
},
```

- `required` a `optional` sa berú presne z CDR (zmrazený zoznam polí), nie zo schémy. Profil je nezávislé očakávanie, ktoré schému kontroluje.
- `validCases` = presný zoznam platných fixtúr rodiny. Každá musí existovať a prejsť validáciou.
- `owned`: pole → vnorený kontrakt (`property-record`, `classification`).
- `deferredValue` = hodnota pre všetky odložené polia; `deferredValues` iba pre polia s inou hodnotou.
- `caseBase` iba výnimočne (Material, `legacy-draft`); nová entita ho nepoužíva.

## 3. Tabuľka neplatných prípadov

```json
{
  "cases": [
    {"name":"eit-too-short","base":"minimal-draft","ops":[["set","/id","EIT-901"]],"expect":{"errorCode":"schema_validation.pattern","path":"$.id"}}
  ],
  "deferred": ["properties", "notes", "releases"]
}
```

- Kľúče tabuľky sú presne `cases` a `deferred`; `cases` nesmie byť prázdne.
- Každý riadok má **presne jednu** operáciu: `["set", "/json/pointer", hodnota]` alebo `["remove", "/json/pointer"]`. Viac zmien = viac riadkov.
- Každý riadok má `expect` s **jedným** `errorCode` a `path`. Runner porovná presnú množinu diagnostík (kód, cesta, recordId, referencedId, severity, kategória), nie iba to, že validácia zlyhala.
- `base` je názov platnej fixtúry tej istej rodiny (`minimal-draft`, `populated-source-links`…).
- **Negeneruj ručne** to, čo runner vytvára sám pre každú entitu: `missing-<pole>` a `<pole>-null` pre každé povinné pole, `name-empty`, `generic-wrong-family`, `generic-unknown`, `array`, `empty-object`, pri `properties` aj `invalid-property-record`.
- Zložený vstup s viacerými diagnostikami nepatrí do tabuľky; ak je potrebný pre všetky entity, doplní sa do `negative_cases` v `test_entity_profiles.py`.
- **Nikdy** nevytváraj samostatné `*-invalid.json` súbory.

## 4. Platné fixtúry

- Povinné sú `<family>-minimal-draft-valid.json` (iba povinné polia) a `<family>-populated-source-links-valid.json` (root zdroj, prípadne klasifikácia a tvrdenie s vlastným zdrojom).
- Ďalšie iba pre **odlišný tvar** kontraktu, nie pre inú hodnotu. Machine aj EngineeringItem majú iba tieto dve.
- Hodnoty sú **fiktívne a netechnické**: ID z rozsahu `-9xxx` a `-98xxxx`, žiadne reálne materiály, normy, rozmery, časy ani ceny.

## 5. Vlastný test entity

```python
class MachineValidationTests(OwnedClaimChecks, unittest.TestCase):
    family = "machine"
    uri = BASE + "entities/machine.schema.json"
    claim_fixture = "populated-source-links"
```

- Zdeď `OwnedClassificationChecks` (iba klasifikácie) alebo `OwnedClaimChecks` (klasifikácie a PropertyRecord). Nepíš tieto kontroly znova.
- Pridaj iba pravidlá špecifické pre entitu z CDR. Docstring triedy odkazuje na CDR (`"""CDR-0021: …"""`).
- Over presnú diagnostiku cez `diagnostics(result)`: `(errorCode, path, recordId, referencedId, severity)`. Nie iba `assertFalse(result.ok)`.
- Matice cez `subTest` (stavy × politiky, viac vstupov), nie kópie metód.
- Testuj cez verejné API (`EosValidator.validate`, `validate_with_context`, `validate_json_file`).

## 6. Skúšky citlivosti (povinné)

Každý nový alebo zmenený test musí vedieť zlyhať. Pred dokončením:

1. Dočasne, **iba v pamäti testovacieho procesu**, vnes poruchu, ktorú má test zachytiť (napr. povol odložené pole, zmeň prefix ID, poškoď vnorenú cestu, strať `recordId`).
2. Over, že zlyhá **konkrétny subTest**, nie chyba spustenia.
3. Poruchu odstráň a spusti čistú sadu.
4. Zapíš do CDR tabuľku `| # | Vnesená porucha | Pozorovaný signál |` (vzor: CDR-0022, CDR-0027).

## 7. Nikdy

- neoslabuj test ani schému, aby testy prešli,
- neodvodzuj očakávania z výstupu testovanej schémy; berú sa z CDR,
- nemaž ani nepreskakuj (`skip`) testy bez dôvodu zapísaného v CDR alebo ADR,
- nekopíruj pomocné funkcie a konštanty medzi súbormi,
- nepridávaj `pytest`, `hypothesis` ani inú testovaciu knižnicu (TECH_STACK.md),
- nepridávaj kontroly presného počtu súborov (`assertEqual(len(glob), 63)`).

## 8. Strážne limity

Zastav sa a navrhni zjednodušenie, ak:

- vlastný test entity má viac ako ~10 metód (väčšinu má pokryť profil a zdedené kontroly),
- entita potrebuje viac ako ~3 platné fixtúry,
- nový test opakuje viac ako 5 riadkov z iného testu.

## 9. Na záver

1. Spusti celú sadu (`eos-run-tests`). Počet testov ber z výstupu `Ran N tests`.
2. Nový počet a skúšky citlivosti zapíš do CDR, sekcie v `tests/README.md` (formát: tabuľka `Súbor | Overenie`) a `CHANGELOG.md`.
3. V hlásení uveď: koľko metód a negatívnych prípadov pribudlo, čo pokryl spoločný profil a preto sa nepísalo.
