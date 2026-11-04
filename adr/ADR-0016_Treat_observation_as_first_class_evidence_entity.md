# ADR-0016 - Treat Observation as First-Class Evidence Entity

**Status:** Accepted  
**Date:** 2026-08-01  

## Title

Treat Observation as First-Class Evidence Entity

## Context

EOS potrebuje pred začatím `Phase 0.2B.1 - Knowledge Core Contracts` uzavrieť hranicu medzi dôkazom, tvrdením, odvodeným výsledkom a rozhodnutím.

RFC-0001, RFC-0002 a RFC-0003 už navrhujú `Observation` ako first-class evidence entity so stabilným `OBS-xxxxxx`, vlastným lifecycle, auditom a väzbou na zdroje. `EOS-010_Architecture_Readiness_Review.md` označuje potvrdenie `Observation` ako first-class evidence entity za high blocker pred začatím `0.2B.1`.

Bez tohto rozhodnutia hrozí, že jednotlivé merania, kontroly, snímky, výstupy nástrojov alebo skúšobné výsledky budú zamieňané s autoritatívnymi vlastnosťami, rozhodnutiami, odporúčaniami, kalkulačnými výstupmi alebo workflow udalosťami.

## Decision

EOS prijíma `Observation` ako first-class evidence entity.

`Observation` reprezentuje objektívne zaznamenaný fakt o tom, čo bolo pozorované, namerané, zachytené, skontrolované alebo vyprodukované kontrolovaným zdrojom v konkrétnom kontexte.

`Observation` je dôkaz.

`Observation` nie je:

- tvrdenie,
- interpretácia,
- odporúčanie,
- rozhodnutie,
- odvodený výsledok,
- obchodná logika,
- výpočet,
- workflow krok.

`Observation` musí obsahovať iba dôkazový záznam a jeho kontext. Nesmie obsahovať záver, schválenie, odmietnutie, business logiku ani kalkulačný algoritmus.

## Observation Scope

`Observation` môže predstavovať napríklad:

- meranie,
- vizuálne zistenie,
- výsledok kontroly,
- výsledok skúšky,
- výsledok laboratória,
- fotografiu alebo odkaz na fotografiu,
- výstup CAD analýzy ako zaznamenaný výstup nástroja, nie ako automaticky prijatý záver,
- výsledok CMM ako zaznamenaný výstup merania,
- výstup snímača,
- výstup stroja,
- výstup normovej skúšky,
- výsledok NDT,
- výsledok metalografie,
- výsledok tvrdosti,
- iný kontrolovaný dôkazový záznam so zdrojom, časom a kontextom.

Tieto príklady neurčujú žiadne konkrétne technické hodnoty. Uvádzajú iba typy dôkazových záznamov.

`Observation` nesmie predstavovať:

- schválenie,
- odmietnutie,
- výber,
- odporúčanie,
- business rozhodnutie,
- výpočet ceny,
- výpočet času,
- technologické rozhodnutie,
- automatické povýšenie na autoritatívnu vlastnosť.

## Distinction Between Core Concepts

### Observation

`Observation` je first-class evidence entity.

Význam:

- zaznamenáva, čo bolo pozorované alebo zachytené,
- má stabilné `OBS-xxxxxx`,
- má vlastný lifecycle a audit,
- je referencovateľná z viacerých tvrdení alebo rozhodnutí,
- je source-backed evidence,
- po vzniku sa nesmie ticho prepisovať,
- sama nerozhoduje a sama neinterpretuje význam pre celý svet.

Autoritatívny princíp: `Observation` predstavuje pravdu o tom, čo bolo pozorované, nie pravdu o svete.

### Claim

`Claim` je tvrdenie.

Význam:

- vyjadruje, čo EOS alebo autor záznamu tvrdí o objekte, vlastnosti, stave, zdroji alebo interpretácii,
- môže byť uložené napríklad cez `PropertyRecord` alebo budúci explicitnejší claim model,
- môže byť podložené jednou alebo viacerými `Observation`,
- môže byť podložené aj inými evidence väzbami podľa schválených pravidiel,
- potrebuje `verificationStatus` a `sourceLinks`, ak obsahuje overiteľné technické, výrobné, dodávateľské alebo obchodné tvrdenie.

`Observation` sama o sebe nie je `Claim`. Claim môže interpretovať alebo použiť observation, ale nesmie tvrdiť viac, než podporujú jeho zdroje a rozhodnutia.

Kardinalita:

- `Claim` môže mať `0..N` `Observation`.
- `Observation` môže podporovať `0..N` `Claim`.

Hodnota `0` pri claim znamená, že tvrdenie môže byť v `Draft`, môže byť podložené iným typom evidence alebo môže čakať na doplnenie observation podľa lifecycle pravidiel. Neznamená to automatické schválenie bez zdroja.

### Decision

`Decision` rozhoduje.

Význam:

- prijíma, odmieta alebo podmienene prijíma evidence, claim, derived result alebo odporúčanie,
- môže používať `Observation`,
- môže používať `Claim`,
- môže používať `Derived Result`,
- môže používať engineer approval alebo schválený rozhodovací mechanizmus,
- musí byť auditovateľné, ak ovplyvňuje autoritatívne dáta, quotation výstup alebo manufacturing výstup.

`Observation` nikdy nerozhoduje. `Claim` sám nerozhoduje. `Derived Result` sám nerozhoduje.

### Derived Result

`Derived Result` je odvodený výsledok.

Vzniká napríklad:

- výpočtom,
- algoritmom,
- interpretáciou,
- kombináciou viacerých `Observation`,
- kombináciou `Claim`,
- kombináciou `Property`,
- porovnaním,
- modelom,
- pravidlom,
- AI návrhom.

`Derived Result` nie je zdrojová observation. Môže byť reprodukovateľný, auditovateľný a použiteľný ako vstup do `Decision`, ale nesmie automaticky prepísať source-backed claim ani autoritatívny `PropertyRecord`.

## Evidence, Knowledge, Decision And Workflow

### Evidence

`Evidence` je dôkazový podklad. Patrí sem najmä `Observation`, `SourceReference`, `SourceLink`, snapshot vstupov alebo iný schválený dôkazový artefakt.

Evidence odpovedá na otázku: z čoho vieme, že niečo bolo pozorované alebo zaznamenané?

Evidence nie je automaticky knowledge. Evidence môže podporovať knowledge, ale prijatie významu vyžaduje claim, verification alebo decision podľa kontextu.

### Knowledge

`Knowledge` je riadene evidovaná inžinierska znalosť s významom, identitou, zdrojovou väzbou, lifecycle a auditom.

Knowledge odpovedá na otázku: čo EOS v danom rozsahu považuje za riadenú znalosť?

Knowledge nie je decision. Schválená znalosť môže byť výsledkom rozhodnutia, ale samotný znalostný záznam nemá byť workflow akt schválenia.

### Decision

`Decision` je auditovateľný akt prijatia, odmietnutia alebo podmieneného prijatia.

Decision odpovedá na otázku: čo bolo na základe evidence, claim alebo derived result rozhodnuté?

Decision môže meniť stav alebo použiteľnosť znalosti podľa schváleného mechanizmu. Nemá byť nahradené samotnou observation ani derived result.

### Workflow

`Workflow` je postup, proces alebo sekvencia krokov, ktorými sa evidence, knowledge alebo decision vytvára, kontroluje alebo používa.

Workflow odpovedá na otázku: ako sa práca vykonáva?

Evidence layer nie je workflow, pretože dôkazový záznam má ostať stabilný nezávisle od toho, cez aký proces bol prijatý, skontrolovaný alebo použitý. Workflow môže vytvoriť alebo použiť observation, ale nesmie meniť jej dôkazový význam.

## Authoritative Rules

`Observation`:

- je immutable po vzniku dôkazového záznamu,
- sa neprepisuje tichou úpravou,
- pri novom meraní alebo novom zistení vzniká nová `Observation`,
- musí byť auditovateľná,
- musí byť referencovateľná,
- musí mať stabilné `OBS-xxxxxx`,
- musí mať dohľadateľný zdroj alebo zdrojový kontext,
- je source-backed evidence,
- môže byť použitá vo viacerých `Claim`,
- môže podporovať viacero tvrdení bez toho, aby ich sama vytvorila,
- nesmie byť odvodená,
- nesmie automaticky meniť `PropertyRecord`,
- nesmie automaticky meniť knowledge entity,
- nesmie obsahovať business rozhodnutie,
- nesmie obsahovať kalkulačný algoritmus,
- nesmie obsahovať technologické rozhodnutie.

Ak sa zistí chyba v observation, preferované riešenie je:

- vytvoriť novú opravujúcu observation,
- označiť pôvodnú observation ako spornú, superseded alebo nahradenú podľa budúceho lifecycle pravidla,
- zachovať auditnú stopu pôvodného záznamu,
- nevykonať tichý prepis pôvodného dôkazu.

Ak sa mení iba neúmyselná technická chyba v metadátach, zmena musí byť auditovaná cez `revision`, `changeSummary` alebo ekvivalentný korekčný mechanizmus. Nesmie zmeniť pôvodne pozorovaný dôkazový význam.

## Source-Backed Evidence

First-class `Observation` musí mať jasný pôvod.

Zdrojový kontext môže byť napríklad:

- `SourceReference` na merací protokol,
- `SourceReference` na skúšobný záznam,
- `SourceReference` na fotografiu,
- `SourceReference` na súbor výstupu stroja,
- `SourceReference` na laboratórny report,
- `SourceReference` na normovú skúšku,
- interný auditovateľný zdrojový záznam,
- iný schválený zdrojový artefakt.

Konkrétne použitie zdroja sa vyjadruje cez `SourceLink`. Interpretácia zdroja patrí do `SourceLink`, `Claim` alebo `Decision`, nie do samotnej `SourceReference`.

## Relationship To Aggregate Boundaries

`Observation` je samostatná entita a môže byť aggregate root, ak má globálne `OBS-xxxxxx` a vlastný lifecycle.

Iný aggregate root, napríklad `Material`, `Machine`, `ManufacturingProcess`, `Supplier` alebo `Job`, nesmie vlastniť first-class `Observation` ako vnorený objekt. Môže ju iba referencovať stabilným ID.

Job-local alebo embedded observation-like records môžu existovať iba ako samostatne pomenované vnorené záznamy bez globálneho `OBS` ID. Nesmú sa označovať ako first-class `Observation`.

## Rejected Alternatives

### 1. Observation = Measurement

Odmietnuté, pretože measurement je iba jeden typ observation. Observation musí pokryť aj vizuálne zistenie, kontrolu, skúšku, fotografiu, výstup stroja alebo iný dôkazový záznam.

### 2. Observation = Claim

Odmietnuté, pretože observation zaznamenáva dôkaz, zatiaľ čo claim vyjadruje tvrdenie. Jedna observation môže podporiť viac claims a jeden claim môže byť podporený viacerými observations.

### 3. Observation = Decision

Odmietnuté, pretože observation nerozhoduje. Decision je auditovateľný akt prijatia, odmietnutia alebo podmieneného prijatia.

### 4. Observation = Property

Odmietnuté, pretože observation je konkrétny dôkazový záznam v kontexte. Property alebo `PropertyRecord` predstavuje tvrdenie alebo znalostný význam vlastnosti.

### 5. Observation = Derived Result

Odmietnuté, pretože derived result vzniká výpočtom, interpretáciou alebo kombináciou vstupov. Observation nesmie byť odvodená; zaznamenáva zdrojový dôkazový fakt.

### 6. Observation = Workflow Event

Odmietnuté, pretože workflow event opisuje krok procesu. Observation opisuje dôkazový obsah a jeho kontext, nezávisle od konkrétneho procesu použitia.

### 7. Observation = Log Entry

Odmietnuté, pretože log entry je technický záznam systému. Observation je doménový evidence objekt s identitou, auditom a zdrojovou väzbou.

### 8. Observation = Database Record

Odmietnuté, pretože database record je spôsob uloženia. Observation musí mať rovnaký význam v JSON súbore, PostgreSQL, graph DB, API alebo inom budúcom úložisku.

## Consequences

Pozitívne dôsledky:

- EOS má jasný základ dôveryhodnosti Engineering Knowledge Layer.
- Merania, kontroly, skúšky a iné dôkazové záznamy sú citovateľné cez stabilné `OBS` ID.
- Viac tvrdení môže používať rovnaký dôkaz bez duplicity.
- Jedno tvrdenie môže byť podporené viacerými dôkazmi.
- `Observation`, `Claim`, `Decision` a `Derived Result` zostávajú oddelené.
- Budúce AI, quotation a manufacturing vrstvy môžu používať evidence bez toho, aby sa výstup modelu zamenil za zdrojovú znalosť.

Nevýhody:

- Model pridáva samostatnú entitu a tým aj dodatočný lifecycle, referencie a validáciu.
- Jednoduché prípady, ktoré by sa dali zapísať ako vnorená poznámka, môžu vyžadovať viac explicitnej štruktúry.
- Prefix `OBS-xxxxxx` musí byť doplnený do `EOS-003` pred implementáciou schémy.

Riziká:

- Ak sa observation začne používať ako claim, systém bude predčasne povyšovať dôkaz na znalosť.
- Ak sa observation začne používať ako decision, stratí sa audit schválenia.
- Ak sa derived result zapíše ako observation, výpočtový alebo interpretačný výstup sa bude tváriť ako zdrojový dôkaz.
- Ak sa observation bude ticho editovať, stratí sa dôveryhodnosť auditnej histórie.
- Ak embedded observation records dostanú globálne `OBS` ID bez vlastného lifecycle, vznikne konflikt aggregate boundaries.

## Compliance and Validation

Budúce schémy a aplikačná validácia majú overovať:

- stabilný formát `OBS-xxxxxx` po aktualizácii `EOS-003`,
- povinnú identitu first-class observation,
- oddelenie observation od claim, decision a derived result,
- prítomnosť source-backed evidence podľa lifecycle stavu,
- auditovateľnosť zmeny alebo korekcie,
- zákaz tichého prepisu dôkazového významu,
- referenčnú integritu observation references,
- že aggregate root nevlastní inú first-class observation ako vnorený objekt.

Toto ADR nevytvára JSON schému, validačný kód ani aplikačnú implementáciu.

## Open Follow-up Actions

- Aktualizovať `EOS-003` o prefix `OBS-xxxxxx` a ďalšie required prefixy pred `0.2B.1`.
- Formálne prijať RFC-0001, RFC-0002 a RFC-0003 alebo ich explicitne schváliť ako vstup pre implementáciu.
- Vytvoriť `Knowledge Core Contracts` až po splnení closure podmienok.
- Vytvoriť `Observation.schema.json` až vo fáze schém, nie v tomto ADR.
- Rozhodnúť, či `Decision` zostáva boundary koncept alebo dostane samostatný stored kontrakt.
- Neskôr spresniť korekčný lifecycle pre chybné, superseded alebo disputed observations.

## Related Documents

- `docs/governance/EOS-004_Core_Data_Model.md`
- `docs/governance/EOS-008_Architecture_Baseline.md`
- `docs/governance/EOS-009_Architecture_Closure_Plan.md`
- `docs/governance/EOS-010_Architecture_Readiness_Review.md`
- `docs/rfc/RFC-0001_Engineering_Property_Model.md`
- `docs/rfc/RFC-0002_Engineering_Object_Taxonomy.md`
- `docs/rfc/RFC-0003_EOS_Engineering_Glossary.md`
- `adr/ADR-0015_Establish_engineering_knowledge_layer.md`

## Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-08-01 | 0.1 | 0 | Codex | Initial accepted ADR treating Observation as first-class evidence entity |

## Review Date

2026-08-15
