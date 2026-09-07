# BACKLOG

## Otvorené položky

- Začať `Phase 0.2B.1 - Knowledge Core Contracts`.
- Navrhnúť prvú verziu JSON schém pre schválený minimálny scope `0.2B.1`: `Quantity`, `ValueRange`, `MeasurementQuality`, `Condition`, `Classification`, `PropertyRecord` a `Observation`.
- Navrhnúť samostatnú schému `DocumentRecord`, ktorá oddelí verziu riadeného dokumentu od `schemaVersion`, `recordVersion` a `revision` registračného záznamu.
- Navrhnúť aplikačnú validačnú vrstvu pre významové pravidlá `sourceLinks`, ktoré nevie plne overiť samotná JSON Schema.
- V `Phase 0.2B.2` zaviesť pre Classification kontrolu existencie a použiteľnosti CLS položky, systému a kompatibility s rodičom; podľa katalógového pôvodu vynucovať neprázdne a relevantné `sourceLinks` pri klasifikáciách z externého systému, normy alebo dokumentu podľa RFC-0001 §4.6. Rozlíšiť zdroj definície kategórie od dôkazu zaradenia rodiča; dovtedy sa kontroluje iba štruktúra a pôvod sa neodhaduje.
- Definovať pravidlá validácie nových ID formátov z `EOS-003` Revision 2.
- Navrhnúť budúci requirement/tolerance kontrakt pre výrobné, konštrukčné, rozmerové, geometrické a akceptačné tolerancie; finálny názov, prefix a implementácia zatiaľ nie sú prijaté.
- Definovať minimálnu štruktúru záznamu zákazky.
- Rozhodnúť, kedy sa začnú používať testy dátových kontraktov.
- Pripraviť šablóny dokumentov `FRM`.

## Dokončené položky

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
