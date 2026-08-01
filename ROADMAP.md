# ROADMAP

## Fáza 0.1 - Architektúra a riadenie projektu

Cieľ:

- vytvoriť základnú štruktúru repozitára,
- definovať governance dokumenty,
- zaviesť identifikáciu, verziovanie a ADR,
- pripraviť prázdne dátové kontrakty.

Stav: Completed.

## Míľnik 0.1.1 - Governance Alignment

Cieľ:

- jazykovo stabilizovať manifest,
- odstrániť konflikt prefixu `STD`,
- oddeliť interné štandardy EOS od externých normatívnych referencií,
- potvrdiť `SourceReference` ako samostatnú entitu,
- zaviesť `SourceLink`,
- spresniť metadáta entít pred detailnými schémami.

Stav: Completed / Approved.

## Fáza 0.2 - Schémy a validačné pravidlá

Predbežný cieľ:

- dopracovať JSON-kompatibilné schémy,
- pripraviť pravidlá validácie,
- vytvoriť testy štruktúry bez technických hodnôt.

Stav: In progress.

## Fáza 0.2A - Foundation Data Contracts

Cieľ:

- vytvoriť modulárne schémy pre spoločné metadáta, zdroje, normatívne referencie a riadené dokumenty,
- pripraviť minimálnu aplikačnú validačnú vrstvu,
- pridať netechnické testovacie fixtures,
- zdokumentovať rozdiel medzi syntaktickou a významovou validáciou.

Stav: podmienečne schválené, auditované v 0.2A.1.

## Míľnik 0.2A.1 - Validation Capability Audit

Cieľ:

- zdokumentovať reálne schopnosti aktuálnej validačnej vrstvy,
- zaviesť fail-closed správanie pre nepodporované JSON Schema kľúčové slová,
- doplniť auditné testy,
- pripraviť návrh ADR-0013 pre štandardný JSON Schema validátor.

Stav: Completed / Approved.

## Míľnik 0.2A.2 - Standards-Compliant Validator Integration

Cieľ:

- zaviesť `jsonschema` ako štandardný validátor JSON Schema Draft 2020-12,
- ponechať EOS aplikačné pravidlá v internej validačnej vrstve,
- zaviesť jednotný chybový model,
- pripraviť regresné testy pre štandardné JSON Schema schopnosti,
- zdokumentovať runtime dependency postup.

Stav: Completed / Approved.

## Míľnik 0.2B.0 - Governance Finalization

Cieľ:

- uzavrieť architektonickú fázu EOS,
- doplniť required prefixy do `EOS-003`,
- prijať RFC-0001, RFC-0002 a RFC-0003,
- zmeniť Architecture Readiness Verdict na `READY`,
- zmraziť architektúru pred implementáciou Knowledge Core Contracts.

Stav: Completed / Approved.

## Míľnik 0.2B.1 - Knowledge Core Contracts

Cieľ:

- vytvoriť schémy pre minimálne knowledge core kontrakty schválené architektúrou,
- zachovať oddelenie JSON Schema validácie a EOS aplikačnej validácie,
- neprekročiť schválený scope bez ADR alebo RFC.

Predbežný scope:

- `Quantity`,
- `ValueRange`,
- `MeasurementQuality`,
- `Condition`,
- `Classification`,
- `PropertyRecord`,
- `Observation`.

Stav: Next.

## Fáza 0.3 - Prvé prázdne záznamové šablóny

Predbežný cieľ:

- pripraviť šablóny pre materiál, polotovar, proces, stroj, nástroj a zákazku,
- zachovať zdrojovú klasifikáciu a revízie.

Stav: čaká na schválenie.
