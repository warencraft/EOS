# BACKLOG

## Nasledujúce: Phase 0.2B.2 - Knowledge Catalogs

- Navrhnúť Unit Catalog a zaviesť kontrolu existencie a použiteľnosti `UNT-xxxxxx` bez pridania reálnych jednotkových záznamov.
- Navrhnúť Condition Type Catalog vrátane povolenej hodnotovej formy a rodiny cieľovej referencie pre každý `CND-xxxxxx`; vyriešiť duplicity a rozpory podmienok v aplikačnej validácii.
- Navrhnúť Property Catalog a zaviesť kontrolu existencie a použiteľnosti `PRP-xxxxxx`, povoleného typu hodnoty, jednotkovej a rozmerovej kompatibility a požadovaných podmienok.
- Navrhnúť Classification Catalog a zaviesť kontrolu existencie, použiteľnosti, systému, hierarchie a kompatibility `CLS-xxxxxx` s rodičom.
- Pri klasifikáciách rozlíšiť zdroj definície katalógovej položky od dôkazu zaradenia rodiča a podľa katalógového pôvodu vynucovať relevantné `sourceLinks` podľa RFC-0001 §4.6.
- Zaviesť katalógovo uvedomelú referenčnú integritu. Formát identifikátora zostáva výlučne schémovou validáciou; existencia, stav a kompatibilita cieľa patria do `reference_integrity`.
- Doplniť integračné fixtures a testy katalógovej existencie, lifecycle a kompatibility bez zavedenia reálnych technických znalostí.

## Ďalšie otvorené položky

- Definovať rodičovský lifecycle kontext pre povinnosť neprázdnych `sourceLinks` vo vnorenom PropertyRecord.
- Navrhnúť budúci requirement/tolerance kontrakt pre výrobné, konštrukčné, rozmerové, geometrické a akceptačné tolerancie; finálny názov, prefix a implementácia zatiaľ nie sú prijaté.
- Definovať minimálnu štruktúru záznamu zákazky.
- Pripraviť šablóny dokumentov `FRM`.
- Pred rozšírením MeasurementQuality stabilizovať význam `accuracy`, declared error, repeatability a reproducibility.
- Pre Observation vyriešiť PROJECT/EXPERIMENT scope, všeobecné alebo nečíselné výsledky, korekcie a supersession, identitu aktéra, prílohy a verifikáciu dôkazu.

## Dokončené položky

- Dokončená a integračne skontrolovaná `Phase 0.2B.1 - Knowledge Core Contracts` so siedmimi schémami: `Quantity`, `ValueRange`, `MeasurementQuality`, `Condition`, `Classification`, `PropertyRecord` a `Observation`.
- Vytvorená samostatná schéma `DocumentRecord`, ktorá odlišuje verziu riadeného dokumentu od verzií registračného záznamu.
- Zavedená aplikačná validácia významových pravidiel `sourceLinks` v dostupnom lifecycle kontexte.
- Zavedené pravidlá formátu identifikátorov z `EOS-003` Revision 2 cez centrálne JSON Schema referencie.
- Zavedené a spustené unittest testy dátových kontraktov; closure baseline obsahuje 122 testov.
- Rozhodnutý presný minimálny scope `0.2B.1`.
- Uzavretá architektonická fáza EOS.
- Prijaté RFC-0001, RFC-0002 a RFC-0003.
- Doplnené required prefixy v `EOS-003` Revision 2.
- Architecture Readiness Verdict zmenený na `READY`.

## Odložené položky

- Kalkulačky.
- Používateľské rozhranie.
- Import alebo čítanie výkresov.
- Databázový server.
- Automatické odhady času alebo ceny.
- Stored `Decision` contract.
- First-class `Relationship` object.
- Všeobecný `Event` object.
