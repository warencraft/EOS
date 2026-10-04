# BACKLOG

## Nasledujúce: Phase 0.2C.1-prep - Material Entity Pre-design Review

- Preskúmať autoritatívne hranice entity `Material`, jej aggregate ownership, lifecycle, identitu, PropertyRecord, Classification, Condition a source traceability bez implementácie schémy.
- Určiť najmenší bezpečný kontrakt a validačné hranice pre následný samostatný implementačný míľnik.

## Ďalšie otvorené položky

- Definovať rodičovský lifecycle kontext pre povinnosť neprázdnych `sourceLinks` vo vnorenom PropertyRecord.
- Navrhnúť budúci requirement/tolerance kontrakt pre výrobné, konštrukčné, rozmerové, geometrické a akceptačné tolerancie; finálny názov, prefix a implementácia zatiaľ nie sú prijaté.
- Definovať minimálnu štruktúru záznamu zákazky.
- Pripraviť šablóny dokumentov `FRM`.
- Pred rozšírením MeasurementQuality stabilizovať význam `accuracy`, declared error, repeatability a reproducibility.
- Pre Observation vyriešiť PROJECT/EXPERIMENT scope, všeobecné alebo nečíselné výsledky, korekcie a supersession, identitu aktéra, prílohy a verifikáciu dôkazu.
- Pre Unit Catalog odložiť quantity kind, dimension model, conversion model, aliases a reálnu katalógovú populáciu.
- Pre Condition Type Catalog odložiť evaluation-mode policy, jednotkové obmedzenia, multiplicitu a logické kombinácie.
- Pre Property Catalog odložiť canonical unit, required Conditions, condition multiplicity, MeasurementQuality policy, classifications, aliases/equivalence a reálnu property populáciu.
- Pre Classification Catalog odložiť classification systems, external codes, hierarchy, aliases/localization, equivalence a applicability.
- Pre runtime odložiť všeobecný entity resolver, referenčnú integritu entít, persistence a načítanie reálnych katalógových dát.

## Dokončené položky

- Dokončená a integračne skontrolovaná `Phase 0.2B.1 - Knowledge Core Contracts` so siedmimi schémami: `Quantity`, `ValueRange`, `MeasurementQuality`, `Condition`, `Classification`, `PropertyRecord` a `Observation`.
- Dokončená `Phase 0.2B.2 - Knowledge Catalogs` so štyrmi katalógovými kontraktmi: Unit Catalog, Condition Type Catalog, Property Catalog a Classification Catalog.
- Zavedené immutable `CatalogRegistry` a explicitný `ValidationContext` pre UNT, CND, PRP a CLS bez persistence alebo reálnych katalógových dát.
- Oddelené runtime vrstvy `reference_integrity` pre existenciu a typ od `catalog_validation` pre lifecycle a kompatibilitu.
- Integrované katalógové pravidlá pre PropertyRecord, Observation, Condition a Classification; closure baseline obsahuje 214 úspešných testov.
- Vytvorená samostatná schéma `DocumentRecord`, ktorá odlišuje verziu riadeného dokumentu od verzií registračného záznamu.
- Zavedená aplikačná validácia významových pravidiel `sourceLinks` v dostupnom lifecycle kontexte.
- Zavedené pravidlá formátu identifikátorov z `EOS-003` Revision 2 cez centrálne JSON Schema referencie.
- Zavedené a spustené unittest testy dátových kontraktov; Knowledge Core closure baseline obsahovala 122 testov.
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
