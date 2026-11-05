---
name: eos-write-tests
description: Ako písať a meniť testy a fixtúry v EOS, aby sa nerozrastali a neduplikovali. Použi vždy pred pridaním testu, fixtúry alebo neplatného prípadu, aj pri novej entite.
---

# Písanie testov v EOS

Cieľ: **najmenej testov, ktoré chránia najviac pravidiel.** Testy sa v minulosti rozrástli na 671 súborov fixtúr a 130 KB v jednom súbore (pozri ADR-0017). Tento skill zabraňuje, aby sa to zopakovalo.

## 0. Najprv zisti, čo už existuje

Pred napísaním testu odpovedz na otázky:

1. **Pokrýva to už spoločný test?** `tests/test_entity_profiles.py` overuje pre každú entitu: uzavretú schému, centrálne ID, common metadata, presnú množinu polí, minimálnu fixtúru, root `sourceLinks` pri Review/Approved, index, všetky platné a neplatné fixtúry a generované negatívne prípady (chýbajúce alebo `null` povinné pole, zlý prefix ID, prázdny `name`, neznáme pole, koreň typu pole). **Tieto veci znova nepíš.**
2. **Je to len nový neplatný vstup?** Potom je to **riadok v tabuľke**, nie nový test (časť 2).
3. **Existuje podobný test inde?** `grep -rn "<pole alebo errorCode>" tests/`. Rozšír existujúci test cez `subTest`, nevytváraj kópiu.

## 1. Kam čo patrí

| Čo testuješ | Kam |
| --- | --- |
| nová entita, spoločné kritériá | riadok v `ENTITY_PROFILES` v `tests/test_entity_profiles.py` |
| neplatný záznam (zlá hodnota, chýbajúce pole, odložené pole) | riadok v `tests/fixtures/invalid-cases/<family>.json` (ADR-0017) |
| platný príklad kontraktu | `tests/fixtures/valid/<directory>/<family>-<name>-valid.json` |
| pravidlo **iba pre jednu entitu** (napr. CDR výnimka) | `tests/test_<entity>_validation.py` |
| validačný engine, `$ref`, formáty | `tests/test_validation_core.py` |
| knowledge core, katalógy | príslušný `test_knowledge_core_*.py`, `test_catalog_*.py` |
| spoločné konštanty a pomocné funkcie | `tests/validation_support.py` (nie kópia v každom súbore) |

Nový testovací súbor vytvor iba pre novú oblasť. Pridaj ho do tabuľky v `tests/README.md`.

## 2. Neplatné prípady = riadky tabuľky

```json
{"name": "id-lowercase", "base": "minimal-draft", "ops": [["set", "/id", "mac-9001"]]}
```

- Jeden prípad = **jeden dôvod zlyhania.** Ak meníš dve veci naraz, sú to dva riadky.
- `base` je vždy najmenšia platná fixtúra, ktorá stačí (`minimal-draft`).
- Pole, ktoré CDR odkladá, patrí do bloku `deferred`, nie ako ručný prípad.
- `record` (celý záznam) použi iba pre malé value objects alebo koreň typu pole.
- **Nikdy** nevytváraj samostatné `*-invalid.json` súbory.

## 3. Platné fixtúry

- Iba tie, ktoré ukazujú **odlišný tvar** kontraktu (minimálna, plná, s viacerými claims…). Nie varianty, ktoré sa líšia len hodnotou.
- Spoločný test vyžaduje `<family>-minimal-draft-valid.json` a `<family>-populated-source-links-valid.json`.
- Hodnoty sú **fiktívne a netechnické**: ID z rozsahu `-9xxx`, názvy typu „Fiktívny stroj A“. Žiadne reálne materiály, normy, rozmery, časy ani ceny.

## 4. Ako písať samotný test

- **Testuj správanie cez verejné API** (`EosValidator.validate`, `validate_with_context`), nie vnútorné funkcie.
- **Over presný výsledok:** `errorCode` a `path`, prípadne `recordId` a `referencedId`. Nie iba `assertFalse(result.ok)`.
- **Matice cez `subTest`:** stavy × politiky, flagy, viac fixtúr. Nie päť kópií tej istej metódy.
- **Názov hovorí pravidlo:** `test_context_missing_property_keeps_nested_path_and_machine_id`, nie `test_case_7`.
- **Docstring alebo komentár odkazuje na zdroj pravidla:** `# CDR-0021 §64.8`.
- Netestuj text schémy (napr. presný reťazec `$ref`), ak to už robí spoločný test alebo to nie je architektonické pravidlo.
- **Nepridávaj nové kontroly presného počtu súborov** (`assertEqual(len(glob), 63)`). Pri každej zmene sa musia ručne prepisovať. Existujúce ponechaj a pri zmene ich uprav.

## 5. Každý nový test musí vedieť zlyhať

Pred commitom dočasne pokaz to, čo test chráni (zmeň pravidlo vo validátore alebo hodnotu vo fixtúre), a over, že test **zlyhá**. Potom zmenu vráť. Test, ktorý nikdy nezlyhá, je zbytočný.

## 6. Nikdy

- neoslabuj test ani schému, aby testy prešli,
- nemaž ani nepreskakuj (`skip`) existujúce testy bez dôvodu zapísaného v CDR alebo ADR,
- nekopíruj pomocné funkcie a konštanty medzi súbormi (patria do `validation_support.py`),
- nepridávaj `pytest`, `hypothesis` ani inú testovaciu knižnicu (TECH_STACK.md).

## 7. Strážne limity

Ak niečo z tohto platí, **zastav sa a navrhni zjednodušenie** skôr, než budeš pokračovať:

- testovací súbor presiahne ~25 KB alebo ~600 riadkov,
- jedna entita má viac ako ~10 platných fixtúr,
- nový test opakuje viac ako 5 riadkov z iného testu,
- nová entita potrebuje vo vlastnom súbore viac ako ~15 testov (väčšinu má pokryť `ENTITY_PROFILES`).

## 8. Na záver

1. Spusti celú sadu (`eos-run-tests`).
2. Aktuálne počty: `python scripts/project_status.py`. Ak sa zmenili, aktualizuj `tests/README.md` a `CHANGELOG.md`.
3. V hlásení uveď: koľko testov a prípadov pribudlo, kam a prečo; ktoré veci pokryl spoločný test a preto sa nepísali.
