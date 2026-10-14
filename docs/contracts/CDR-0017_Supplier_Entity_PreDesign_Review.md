# CDR-0017 Supplier Entity Pre-design Review

Project: EOS – Engineering Operating System
Contract Review ID: CDR-0017
Contract: Supplier
Review type: Pre-design
Phase: 0.2C.2-prep
Version: 0.1
Revision: 1
Status: Review
Document basis: Accepted EOS architecture + completed Material entity phase

Aktuálny výsledok: SI-0001 CLOSED; Supplier v1 READY FOR IMPLEMENTATION. Sekcie 1 až 58 zachovávajú pôvodný pre-design a jeho vtedajší blocker. Aktuálne identity rozhodnutie, rozsah v1 a opakované posúdenie pripravenosti sú v sekcii 60; staršie formulácie OPEN/NOT READY sa čítajú ako história Revision 0.

## 1. Purpose

Určiť najmenší bezpečný Supplier profil a odhaliť rozhodnutia, ktoré musia predchádzať jeho serializačnému kontraktu. Review rozlišuje autoritatívne pravidlá od odporúčaní. Prijatie entity Supplier v architektúre samo neurčuje presnú identitu organizácie ani pravidlá jej zmeny.

## 2. Scope

Predmetom sú Supplier význam, SUP identita, právny subjekt a organizácia, prevádzky, roly, naming, provenance, lifecycle, owned values a hranice budúcich obchodných, hodnotiacich a capability modelov. Nevzniká schéma, implementácia, fixture, katalógová položka ani reálny dodávateľský záznam.

## 3. Reviewed Artifacts

Preskúmané vstupy:

- AGENTS.md, EOS-000, EOS-003, EOS-006, EOS-007, EOS-009 a EOS-010;
- Accepted RFC-0001, RFC-0002, RFC-0003 a relevantné Accepted ADR-0015 a ADR-0016;
- CDR-0015 Revision 1, CDR-0016 Revision 1 a Material schema;
- Classification, PropertyRecord, Observation, Classification Catalog Entry a Property Catalog Entry;
- common identifiers, metadata, lifecycle, SourceLink, schema index a existujúci DocumentRecord;
- CatalogRegistry, ValidationContext a explicitná schema/application/catalog dispatch implementácia;
- BACKLOG, ROADMAP, CHANGELOG a schemas/scripts/tests README.

Pre-flight 2026-10-06: vetva `feature/phase-0.2c-knowledge-entities`, tracking `origin/feature/phase-0.2c-knowledge-entities`, HEAD `2c4d8415a35ab9d344c0bb1bb3e4433db0b86cfc`, čistý pracovný strom. Material closure je COMPLETE. Testy: 236 passed, 0 failed, 0 errors, `OK`. Schémy: 21 celkom, 7 Knowledge Core, 4 katalógové, 1 entity (Material). ADR: 17 dokumentov; RFC adresár: 4 dokumenty vrátane cross-review. Supplier ani StockMaterial schéma neexistuje. SUP výskyty vo fixtures sú fiktívne referencie alebo zámerné wrong-prefix prípady, nie Supplier dáta.

## 4. Authoritative Findings

| Zistenie | Stav | Autorita / obmedzenie |
| --- | --- | --- |
| Supplier patrí medzi Knowledge Entities | AUTHORITATIVE | RFC-0002 §2 a ADR-0015 Scope |
| Supplier je Entity a Aggregate Root | AUTHORITATIVE | RFC-0002 §4.6 a §16 |
| Stabilná identita, vlastný lifecycle, verzovanie, root zdroje | AUTHORITATIVE | RFC-0002 §16; ADR-0015 DDD |
| Supplier je obchodný alebo servisný partner | AUTHORITATIVE | RFC-0002 §4.6; RFC-0003 G-0049 |
| SUP má presne štyri číslice | AUTHORITATIVE | EOS-003 SUP Active; identifiers `#/$defs/SUP` |
| Classification môže byť používaný Value Object | AUTHORITATIVE | RFC-0002 §4.6 |
| CommercialObservation a Designation sú konceptuálne možné owned values | AUTHORITATIVE / DEFERRED IMPLEMENTATION | RFC-0002 §4.6; príslušné schémy neexistujú |
| Supplier nesmie vlastniť Observation | AUTHORITATIVE | ADR-0016 Aggregate Boundaries |
| Observation môže mať SUP subjectId | IMPLEMENTED | Observation schema používa centrálny SUP `$ref` |
| SUP mapovanie na právny subjekt, prevádzkovú organizáciu alebo vzťah | OPEN / BLOCKING | Accepted definícia partnera túto granularitu neurčuje |
| Supplier-only PropertyRecord ownership | NOT ESTABLISHED FOR V1 | Supplier zoznam v RFC-0002 §4.6 ho neuvádza; current PropertyRecord je numeric technical claim |
| Address, Site, Contact, Person, ExternalIdentifier kontrakty | DEFERRED | V preskúmaných schémach neexistujú |
| DocumentRecord kontrakt | IMPLEMENTED | `schemas/document-record.schema.json`; predpoklad zadania o jeho neexistencii neplatí |

Nezistený rozpor medzi EOS-003, central SUP pattern a RFC formátom. Zistená je medzera v identity sémantike, nie konflikt formátu alebo dôkaz, že Accepted Supplier Entity je nesprávna.

## 5. Supplier Domain Meaning

Autoritatívne minimum: Supplier je dodávateľ alebo obchodný či servisný partner evidovaný v EOS, samostatne identifikovateľný a auditovateľný. Tento pojem nezahŕňa automaticky všetky externé organizácie.

Odporúčaný v1 význam, ktorý ešte vyžaduje explicitné rozhodnutie: **jedna právne samostatná organizácia evidovaná v dodávateľskej roli**, bez ohľadu na počet jej služieb a prevádzok. Vyberá sa variant A z doménových kandidátov, zúžený na organizáciu ako partnera; B (site), C (account), D/E/F (jediná rola), G (všetky organizácie) a H (samotný vzťah) sa pre identitu v1 neodporúčajú.

Supplier nie je miesto, sklad, značka, ERP účet, objednávka, ponuka, certifikát, kvalifikácia ani zdroj technickej pravdy. Táto odporúčaná právna granularita nie je existujúcim pravidlom EOS a nesmie sa implementovať bez potvrdenia.

## 6. Object Type

Supplier je Knowledge Entity, Entity a Aggregate Root. Má stabilné ID, vlastný lifecycle, revízie, provenance a audit. Iné agregáty ho môžu referencovať; môže vlastniť dohodnuté embedded Value Objects. Nie je Reference Object, Value Object ani Catalog Entry. Rozhodnutie nebolo odvodené kopírovaním Materialu: je priamo v RFC-0002 §4.6 a §16.

## 7. SUP Identifier Semantics

Autoritatívny formát je `SUP-xxxx`, presne štyri numerické číslice: `^SUP-[0-9]{4}$`. Budúce vlastné pole má byť `id`; reference môže používať `supplierId`. Schéma musí reuse-nuť `https://eos.local/schemas/common/identifiers.schema.json#/$defs/SUP`; nesmie vlastniť lokálny regex.

SUP poskytuje internú stabilnú identitu. Nie je VAT, registračné číslo, ERP vendor code, názov ani dôkaz právnej registrácie.

## 8. Supplier Identity Boundary

Presné pravidlo „jeden SUP = jeden subjekt“ ešte nie je autoritatívne uzavreté. Odporúčam jeden SUP pre jednu právne samostatnú organizáciu v dodávateľskej roli, nie SUP pre každý obchodný účet, produkt, rolu, site alebo transakciu.

Zmena zobrazovaného názvu alebo doplnenie role nemení SUP. Rozdielne právne samostatné spoločnosti sa nesmú spojiť iba pre spoločnú značku alebo vlastníka. Ide o odporúčané identity pravidlá čakajúce na rozhodnutie SI-0001 v sekcii 57.

## 9. Legal Entity / Organization Boundary

Accepted „obchodný alebo servisný partner“ povoľuje viac interpretácií. Rozlíšenie právneho subjektu, prevádzkovej organizácie a procurement relationship ovplyvní deduplikáciu, merger, sites aj budúce externé identifikátory. Prázdne `legalName` alebo odložené addresses tento problém neriešia.

Odporúčaný rozhodovací profil:

| Prípad | Odporúčaná identita po schválení |
| --- | --- |
| Jedna spoločnosť, viac závodov | Jeden SUP; závody neskôr v samostatnom site modeli |
| Skupina s viacerými právnymi subjektmi | Samostatný SUP pre každý dodávajúci subjekt; skupina nie je spoločný SUP |
| Distribútor s viacerými pobočkami toho istého subjektu | Jeden SUP; pobočky nie sú nové SUP |
| Výrobca a distribútor ako rôzne spoločnosti | Dva SUP, bez automatickej equivalence |
| Tá istá spoločnosť dodáva materiál aj službu | Jeden SUP, viac priradení rolí |

Pred implementáciou treba potvrdiť aj hranicu pre fyzickú osobu podnikateľa alebo neinkorporovaný servisný subjekt: buď explicitne mimo v1, alebo zahrnutý presným širším counterparty pravidlom. Tento review nevytvára všeobecnú právnu ani osobnú entitu. Odporúčam v1 obmedziť na právne samostatné organizácie a ostatné prípady odložiť; ani toto obmedzenie sa nepovažuje za prijaté.

## 10. Site / Location Boundary

Odporúčanie D: structured locations kompletne odložiť. Headquarters, billing/shipping address, výrobný závod, warehouse a branch office sú odlišné účely alebo prevádzkové objekty; nemožno ich stotožniť s jedným SUP.

Budúci SupplierSite oproti všeobecnému Location zostáva samostatná návrhová otázka. V1 nepridáva `sites` ani voľné address stringy a nevytvára nový prefix.

## 11. Manufacturer Boundary

Manufacturer je možná rola organizácie, nie automaticky samostatný entity typ ani povinná vlastnosť každého Supplieru. Nepridávať `isManufacturer`. Generic klasifikácia môže označiť rolu, ale nepreukazuje, že subjekt vyrobil konkrétny produkt v konkrétnom závode.

## 12. Vendor / Distributor / Service Provider Semantics

Preferovaný EOS názov entity zostáva `Supplier`. Vendor je iba informatívny externý obchodný termín, nie nové autoritatívne synonymum alebo typ. Distributor, Manufacturer, Service Provider a Subcontractor označujú kontextové roly; nemajú tvoriť navzájom výlučný root enum.

Viac generic rolí možno neskôr vyjadriť Classification assignments. Konkrétny subcontract vzťah, produktové zastúpenie alebo výrobná zodpovednosť vyžadujú vlastný relationship/business context. Review nevytvára CLS položky ani taxonómiu rolí.

## 13. Name Model

Odporúčaný jediný povinný názov je `name`: neprázdny kanonický ľudsky čitateľný EOS label. Nie je identita, globálne unikátny názov ani právne overený údaj len preto, že prešiel schémou.

`legalName`, `tradingName`, `shortName` a `displayName` sa pre v1 odkladajú. Aj pri právnej granularite môže name zobraziť evidovaný názov, no nesmie predstierať registrový kontrakt alebo históriu oficiálnych názvov. Jurisdikčné naming pravidlá sa nevymýšľajú.

## 14. External / Legal Identifiers

Registration number, VAT, tax ID, DUNS a ERP vendor code patria do konkrétneho scheme/jurisdiction/system contextu. Samostatné nešpecifikované stringy by umožnili nejednoznačnú deduplikáciu.

V1 ich odloží. Budúci ExternalIdentifier môže riešiť scheme, issuer/jurisdiction, value, platnosť a provenance; nejde o hotový kontrakt. SUP sa externým identifikátorom nenahrádza.

## 15. Root Provenance

Root `sourceLinks` má byť required common metadata kolekcia. Podporuje existenciu, identitu a definíciu Supplieru. Draft môže mať `[]`; Review/Approved s takýmito overiteľnými tvrdeniami vyžaduje neprázdnu provenance cez existujúci EOS application helper.

SourceLink pre identitu nepreukazuje kvalifikáciu, capability, cenu, lead time ani rating. Nevzniká SupplierSource. Existenciu SRC cieľa runtime bez príslušného resolvera nesmie predstierať.

## 16. Lifecycle

Odporúčanie: reuse common RecordStatus a common entity metadata. `Approved` znamená schválený EOS záznam, nie approved vendor. `Archived` neznamená právny zánik organizácie.

Commercial active/blocked, právny active/inactive a kvalifikovaný dodávateľ sú samostatné budúce doménové stavy, ktoré sa nesmú ukladať do root `status`.

## 17. Supplier Qualification Boundary

Root `approved`, `approvalStatus` a `qualificationStatus` sa odmietajú. Kvalifikácia môže byť viazaná na materiál, proces, závod, customer context, rozsah certifikácie a dátum.

Budúci qualification/assessment/workflow model musí evidovať scope, dôkaz a rozhodnutie. Presný objekt a jeho ownership nie sú týmto review ustanovené. Generic Classification ani root Approved sa nesmú použiť ako náhrada qualification.

## 18. Classification Relationship

Odporúčam voliteľné `classifications: Classification[]`, ktoré povoľuje RFC-0002 §4.6. Supplier vlastní assignments, nie Classification Catalog Entries. Pole môže byť prázdne, viacnásobné; poradie nemá prioritu. Bez novej multiplicity policy nezavádzať uniqueness pravidlo.

Assignment provenance zostáva v Classification.sourceLinks; root provenance ju nenahrádza. Runtime vie CLS existenciu a lifecycle, ale nevie applicability pre Supplier. Tento rozdiel musí zostať explicitný: úspešná catalog validation nepreukazuje správnosť role, qualification ani capability.

## 19. PropertyRecord Relationship

Odporúčanie pre v1: žiadne `properties`. RFC-0002 Supplier ownership neustanovuje technické PropertyRecord claims a implementovaný kontrakt je numeric technical property model. Materiálový vzor sa nekopíruje automaticky.

Lead time, rating, MOQ, payment terms a capacity sa týmto poľom nesmú premeniť na univerzálny business key/value register. Budúce presne definované technické capability claims môžu reuse-nuť Knowledge Core v inom prijatom modeli; nejde o zákaz všetkých budúcich Supplier-related claims.

## 20. Observation Relationship

Observation.subjectId už povoľuje centrálny SUP `$ref`. Platný fixture `observation-one-condition-valid.json` používa fiktívny SUP subject. Overuje tvar, nie existenciu Supplieru ani obchodný význam merania.

Supplier nebude obsahovať `observations` ani `observationIds`. Observation je samostatný Aggregate Root; vyhľadávanie podľa subjectId je budúca repository/query zodpovednosť. Súčasný numeric Observation profil nie je všeobecný performance-history alebo commercial payload.

## 21. Address Model

V preskúmaných schémach nie je Address, Location, PostalAddress ani ContactAddress kontrakt. V1 môže existovať bez structured address, pretože jeho minimum je evidencia identity, nie nákupný alebo dodací workflow.

Adresy sa nebudú ukladať do `notes` ako autoritatívna náhrada budúcej štruktúry. Odloženie adresy však neodstraňuje blokujúcu otázku, aký subjekt SUP identifikuje.

## 22. Contact Information

Email, phone a contacts sa odložia: môžu patriť osobám, rolám, pobočkám alebo účelom komunikácie a mať časovú platnosť. Root contactName/contactEmail/contactPhone by tento kontext stratil.

Aj jednoduchý `website` sa pre najmenší v1 profil odloží. URI nie je identita organizácie; skupina alebo značka môže zdieľať web. Webový dokument použitý ako dôkaz možno evidovať existujúcou SourceReference/SourceLink cestou, bez nového communication modelu.

## 23. Contact Person / Privacy Boundary

Neexistuje Contact/Person kontrakt vhodný na reuse. Osobné kontakty potrebujú vlastné pravidlá identity, rolí, platnosti, prístupu a správy údajov. Toto je návrhová požiadavka, nie výklad právnych povinností.

V1 nebude obsahovať osoby ani ich kontaktné údaje. Nie je potrebné zavádzať osobnú entitu iba preto, aby mohol existovať Supplier Draft.

## 24. Material Relationship

Supplier a generic Material sú nezávislé aggregate roots. V1 nepridáva `materialIds` a Material nedostane `supplierIds`. Dodávanie konkrétneho materiálu patrí budúcemu StockMaterial/product/offer alebo relationship contextu, nie dvojici synchronizovaných root arrays.

## 25. StockMaterial Relationship

RFC-0002 §4.6 povoľuje Supplier referencovať StockMaterial, ale nevyžaduje spätný zoznam vo v1. RFC-0003 G-0049 dáva príklad dodávateľa referencovaného zo StockMaterial.

Odporúčanie: budúci StockMaterial alebo obchodný záznam referencuje SUP v presne definovanom kontexte. Kardinalita sa určí pri jeho návrhu. Supplier nevlastní StockMaterial aggregate ani jeho geometriu, grade, inventory alebo cenu; `stockMaterialIds` sa do v1 nepridá.

## 26. ManufacturingProcess Relationship

V1 nemá `processIds`, `capabilities` ani `services`. Capability sa môže líšiť podľa verzie procesu, materiálu, rozmerov, tolerancií, kapacity, času a závodu. Zoznam procesov by neoprávnene naznačil univerzálnu schopnosť.

Budúci sourced capability/relationship model môže referencovať Supplier a ManufacturingProcess s potrebným contextom. Review neurčuje jeho schému alebo Aggregate Root kategóriu.

## 27. Machine / CuttingTool Boundary

Supplier nesmie vlastniť Machine ani CuttingTool aggregate roots. V1 nebude ukladať machineIds, toolIds ani tool recommendations. Vlastníctvo zariadenia, jeho prevádzkovanie a predaj nástroja sú odlišné budúce vzťahy; obchodný sortiment nie je technická capability.

## 28. Commercial Offer Boundary

Price, currency, validity interval, quantity breaks, MOQ, delivery time, payment terms, Incoterms a shipping cost patria do budúceho offer/procurement/quotation modelu so svojím contextom a provenance. V1 ich neobsahuje.

Accepted CommercialObservation môže byť embedded časové obchodné zistenie, ale nemá implementovaný kontrakt a podľa RFC-0001 §4.10 nie je cena, ponuka ani právny záväzok. Preto sa teraz nevnára a neskôr sa nesmie zameniť s CommercialOffer.

## 29. Lead Time Boundary

Root `leadTime` sa odmieta. Význam závisí od predmetu dodávky, množstva, procesu, miesta, začiatku a konca časového intervalu aj dátumu zistenia. Budúci ponukový alebo výkonnostný záznam musí tento context definovať.

## 30. Pricing Boundary

`price`, `hourlyRate`, `materialMarkup` a `pricePerKg` nepatria do identity Supplieru. Odmietajú sa ako root fields. Pricing/costing model musí neskôr niesť predmet, jednotku, menu, časovú platnosť, podmienky a zdroj; v tomto review sa nenavrhuje.

## 31. Supplier Capability

Capability znamená tvrdenie o schopnosti vykonať konkrétny proces alebo dodať výsledok za určených podmienok. Samotný názov služby alebo CLS rola nestačí.

Knowledge Core poskytuje hodnoty, intervaly, Conditions a provenance, ale ešte netvorí úplný Supplier Capability kontrakt vrátane identity subjektu/site, scope a schvaľovania. Capability sa preto odloží a nevynúti do PropertyRecord[] ani free-text arrays.

## 32. Certifications

V1 nemá `certifications`. Certifikácia potrebuje issuing body, scope, identifikátor, časovú platnosť, subjekt/site a zdrojový dokument; uncontrolled string array tieto väzby stráca.

Budúci sourced certification/qualification model musí odlíšiť existenciu dokumentu od aktuálnej platnosti a applicability. DocumentRecord je možné reuse-nuť pre evidenciu dokumentu, ale sám nepreukazuje certifikáciu Supplieru.

## 33. Document Relationship

Oprava vstupného predpokladu: DocumentRecord už existuje v `schemas/document-record.schema.json` a je registrovaný v indexe. Nejde iba o plánovanú entitu.

Napriek tomu Supplier v1 nemá `documentIds`: chýba dohodnutý vzťah, role dokumentu, kardinalita a entity resolution. SourceLink používa SRC referenciu, nie DocumentRecord ID, a nemožno doň vložiť ľubovoľný dokumentový identifikátor. Supplier nevlastní DocumentRecord aggregate.

## 34. Supplier Rating / Assessment

Rating a score sú hodnotenia s metodikou, vstupmi, časovým oknom a scope. Nepridávať root `rating`, deliveryRating ani preferredSupplierScore.

Budúci Assessment/Derived Result môže vyhodnotiť evidence; Decision môže zachytiť prijatie. Číselná Observation sama nie je definitívnym Supplier ratingom ani schválením dodávateľa.

## 35. Performance History

Nevnárať neobmedzené performance history arrays. Budúce udalosti, zákazky, objednávky, observations a hodnotenia majú svoje auditné hranice. Supplier root sa nesmie automaticky meniť pri každom novom meraní.

## 36. Notes / Description

Odporúčam voliteľné `description` a common `notes` pre stručné vysvetlenie evidovaného subjektu a záznamu. Description má byť neprázdny string, ak je prítomný; notes reuse-nú common definíciu.

Ani jedno pole nesmie byť náhradou adresy, kontaktu, právneho identifikátora, qualification, capability, certifikácie alebo obchodných podmienok. JSON Schema nemôže spoľahlivo vynútiť význam voľného textu; kontrola patrí autorovaniu a review.

## 37. Replacement / Supersession

RFC-0002 §4.6 povoľuje nahradenie a supersede. Odporúčam však pre Supplier v1 `replaces` a `replacedBy` odložiť: presný rozdiel medzi náhradou duplicitného záznamu a nástupníckou organizáciou závisí od nevyriešenej identity.

Po uzavretí identity môže samostatné rozhodnutie zaviesť iba record replacement cez SUP refs. Nemá automaticky znamenať právne nástupníctvo, equivalence, transfer zmlúv alebo migráciu evidence. Common metadata voliteľné replacement polia nezaväzujú každý entity profil ich publikovať.

## 38. Corporate Relationship Boundary

Premenovanie zachováva identitu iba pri nezmenenom subjekte. Akvizícia mení vlastníctvo, nie nutne SUP. Merger a successor legal entity môžu meniť subjekt; parent/subsidiary je vzťah, nie replacement.

Žiadnu z týchto operácií nemožno bezpečne automatizovať z názvu. V1 neobsahuje corporate graph, parentSupplierId ani merger history. Tieto pravidlá sa musia neskôr previazať s prijatou identity granularitou.

## 39. External System Mapping

`externalId`, `supplierCode` a `vendorCode` bez systému a schémy sa odmietajú ako v1 shortcuts. Jeden Supplier môže mať viac externých účtov; jeden externý systém môže evidovať site namiesto právneho subjektu.

Mapping patrí do budúceho scheme-aware ExternalIdentifier/integration modelu s provenance a pravidlami reconciliation. Nemá meniť SUP identitu.

## 40. Multi-role Organizations

Jedna organizácia môže byť výrobca, distribútor, materiálový dodávateľ aj subcontractor súčasne. Odporúčaný model B umožňuje viac Classification assignments a nemá povinný supplierType enum.

Rola sama nesmie vytvárať ďalšie SUP ID pre tú istú identitu. Zmena role sa nesmie zameniť so zmenou organizácie; ide o súčasť identity rozhodnutia pred implementáciou.

## 41. Root Verification Status

Nepridávať root `verificationStatus`. RecordStatus riadi záznam, SourceLink má vlastný verification status a budúce claims či assessments budú mať vlastnú sémantiku overenia. Root Approved nesmie certifikovať všetky downstream tvrdenia.

## 42. Minimum Useful Supplier

Po uzavretí identity je najmenší užitočný Draft: common required metadata, `id`, neprázdny `name` a `sourceLinks` (môžu byť prázdne v Draft). Address, externý identifikátor, Classification alebo Contact nemusia byť povinné pre inkrementálne autorovanie.

Samotný label nie je dôkaz skutočnej identity. Review/Approved musí mať provenance a ľudské overenie, že ide o správny subjekt podľa prijatej identity policy. Tento minimum profil zatiaľ nie je autorizáciou implementovať alebo onboardovať reálne subjekty.

## 43. Candidate Models

| Kandidát | Posúdenie |
| --- | --- |
| A: common metadata + id + name + sourceLinks | Malý a rozšíriteľný; bezpečné minimum po uzavretí identity, ale bez riadených kategórií |
| B: A + optional classifications | Odporúčaný jeden v1 model; opiera sa o RFC-0002 a existujúci Classification kontrakt, nevyžaduje role enum |
| C: A + legalName | Nevyrieši právnu granularitu a pridáva druhý názov bez naming policy; odložiť |
| D: generic Organization/relationship model | V Accepted architektúre sa teraz nevyžaduje; nepridávať nový entity framework |

Žiadny kandidát sám nerieši otázku, čo SUP identifikuje. Rovnaký JSON tvar môže skryť nekompatibilné identity modely.

## 44. Recommended v1 Model

Odporúčam **B**, s voliteľnými description a notes, po výslovnom uzavretí SI-0001. Základom má byť jedna právne samostatná organizácia v dodávateľskej roli; toto je návrh rozhodnutia, nie nové Accepted pravidlo.

Povinné: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `createdAt`, `createdBy`, `updatedAt`, `updatedBy`, `sourceLinks`, `changeSummary`, `name`.

Voliteľné: `description`, `classifications`, `notes`. Žiadne ďalšie root fields. SUP a metadata cez existujúce `$ref`, Classification cez existujúci kontrakt; uzavretý objekt. V1 neobsahuje replacement links ani PropertyRecord.

## 45. Field Inventory

Hodnotenia NOW opisujú výlučne odporúčaný profil po odstránení blockeru, nie aktuálne povolenie implementácie. DEFER znamená možný budúci model; REJECT znamená neprípustné root použitie alebo shortcut v tomto profile.

| Pole | Stav | Dôvod |
| --- | --- | --- |
| id | REQUIRED NOW | Stabilná SUP identita cez centrálnu definíciu |
| common metadata | REQUIRED NOW | Schema/record version, revision, audit, lifecycle, changeSummary |
| name | REQUIRED NOW | EOS label, nie unique/legal identity |
| legalName | DEFER | Naming a právna identita vyžadujú policy |
| tradingName | DEFER | Alias/Designation semantics |
| description | OPTIONAL NOW | Ľudské vysvetlenie subjektu |
| classifications | OPTIONAL NOW | Existujúce owned assignments, bez applicability garancie |
| properties | REJECT | Žiadny universal business PropertyRecord register |
| sourceLinks | REQUIRED NOW | Root identity provenance; obsah podmienený lifecycle |
| notes | OPTIONAL NOW | Common notes, nie náhrada odložených dát |
| website | DEFER | Communication údaj, nie identita |
| email | DEFER | Kontakt potrebuje účel, rolu a platnosť |
| phone | DEFER | Kontakt potrebuje context |
| contacts | DEFER | Chýba Contact kontrakt |
| addresses | DEFER | Chýba address a účelový model |
| sites | DEFER | Samostatná location/site identita |
| registrationNumber | DEFER | Scheme/jurisdiction-aware identifikácia |
| taxId | DEFER | Scheme/jurisdiction-aware identifikácia |
| vatNumber | DEFER | Nie nešpecifikovaný root string |
| externalIdentifiers | DEFER | Chýba riadený ExternalIdentifier kontrakt |
| supplierCode | REJECT | Nešpecifikovaný systémový shortcut |
| qualificationStatus | REJECT | Contextual qualification patrí inde |
| approved | REJECT | Nesprávny globálny boolean |
| certifications | DEFER | Scope, čas a dôkaz potrebujú samostatný model |
| capabilities | DEFER | Chýba Supplier capability context |
| processIds | REJECT | Pole ID nesmie predstierať capability |
| materialIds | REJECT | Bez bidirectional root arrays |
| stockMaterialIds | REJECT | Žiadny root inventory alebo sortiment index |
| machineIds | REJECT | Samostatné aggregate/vzťahy |
| rating | REJECT | Časové hodnotenie, nie identity attribute |
| leadTime | REJECT | Predmetovo a časovo závislá hodnota |
| price | REJECT | Offer/costing context |
| paymentTerms | REJECT | Obchodný vzťah alebo ponuka |
| replaces | DEFER | Najprv identity a record replacement policy |
| replacedBy | DEFER | Najprv identity a record replacement policy |
| verificationStatus | REJECT | Root lifecycle nie je claim verification |
| observations / observationIds | REJECT | Samostatný evidence aggregate |

CONDITIONALLY REQUIRED: neprázdny obsah required `sourceLinks` pri Review/Approved s overiteľným identity tvrdením. Žiadne ďalšie podmienene povinné root pole sa nenavrhuje.

## 46. Aggregate Ownership Matrix

| Objekt | Klasifikácia pre Supplier v1 | Hranica |
| --- | --- | --- |
| Classification | OWNED EMBEDDED VALUE | Assignment, nie katalogový záznam |
| PropertyRecord | REJECTED | Nie súčasť Supplier v1 |
| Observation | SEPARATE AGGREGATE | SUP subject referencia zvonka |
| Address | DEFERRED | Bez ad-hoc štruktúry |
| Site | DEFERRED | Budúca samostatná identita nerozhodnutá |
| Contact | DEFERRED | Roly a platnosť neuzavreté |
| Person | DEFERRED | Identity/prístup/data policy |
| Material | SEPARATE AGGREGATE | Bez root ID arrays |
| StockMaterial | SEPARATE AGGREGATE | Budúci referenčný context, žiadne vlastníctvo |
| ManufacturingProcess | SEPARATE AGGREGATE | Capability vzťah až neskôr |
| Machine | SEPARATE AGGREGATE | Žiadne embedding |
| CuttingTool | SEPARATE AGGREGATE | Žiadne embedding/sortiment |
| Certification | DEFERRED | Kategória a scope model neuzavreté |
| SupplierAssessment | DEFERRED | Budúci hodnotiaci model |
| CommercialOffer | DEFERRED | Samostatný obchodný context, kategória zatiaľ neurčená |
| DocumentRecord | SEPARATE AGGREGATE | Existujúci kontrakt, Supplier väzba deferred |
| SourceReference | REFERENCED | Iba cez SourceLink, nevlastní sa |

## 47. Provenance Matrix

| Vlastník provenance | Čo podporuje | Čo nepreukazuje |
| --- | --- | --- |
| Supplier root | Existenciu, identitu a definíciu partnera | Všetky ceny, schopnosti a certifikácie |
| Classification assignment | Konkrétne zaradenie/rolu | Kvalifikáciu pre konkrétny proces |
| Budúca Certification | Rozsah a platnosť certifikačného tvrdenia | Všeobecnú použiteľnosť všetkých služieb |
| Budúca Capability | Presne scoped capability claim | Neobmedzenú univerzálnu schopnosť |
| Budúci Assessment | Hodnotenie, metódu a vstupy | Nadčasovú pravdu o Supplierovi |
| Budúca Offer | Konkrétne obchodné tvrdenie/podmienky | Identitu všetkých obchodných vzťahov |
| Observation | Pozorovaný dôkaz | Automatické schválenie claim alebo Supplieru |

## 48. Validation Responsibility

| Vrstva | Budúca zodpovednosť a limit |
| --- | --- |
| JSON Schema | Uzavretý Supplier tvar, required fields, SUP `$ref`, local typy a nested Classification |
| EOS application | SourceLinks podľa lifecycle a výslovne schválené lokálne invarianty; nepredstiera rozpoznanie právnej identity |
| Nested Knowledge Core | Existing Classification štruktúra a SourceLink reuse |
| Reference integrity | CLS existencia/type cez CatalogRegistry; SUP/SRC/Document existenciu všeobecný resolver zatiaľ neoveruje |
| Catalog validation | CLS lifecycle; nie Supplier applicability ani qualification |
| Workflow/governance | Schválenie identity a záznamu; qualification samostatne |
| Persistence | Uniqueness SUP, history/revisions, konkurentné zmeny; zatiaľ neimplementované |

Návrh nevyžaduje nové chybové kategórie ani novú validačnú vrstvu. Contract-only úspech sa nesmie označiť ako úplná referenčná alebo business validácia.

## 49. Entity Resolver Requirement

Pre navrhnutý profil B nie je generic entity resolver potrebný. Existujúci CatalogRegistry postačuje pre explicitnú CLS validáciu; nie je entity resolver pre SUP, MAT ani dokumenty. Replacement references sú deferred.

Skutočná existencia subjektu a deduplikácia pred onboardingom sa nesmú simulovať validitou prefixu. Ide o samostatné budúce runtime/governance schopnosti.

## 50. Supplier vs SourceReference

Supplier eviduje partnera; SourceReference eviduje autoritatívny zdroj. Dodávateľ môže byť pôvodcom dokumentu, ale SUP ID nenahrádza SRC citáciu. Informácia získaná od Supplieru potrebuje SourceReference a SourceLink s podporovaným tvrdením, klasifikáciou a overením podľa existujúceho modelu.

## 51. Supplier vs Customer

Supplier je rola partnera v EOS doméne, nie univerzálny register všetkých organizácií. Tá istá organizácia môže neskôr vystupovať ako customer alebo partner, čo vytvára riziko duplicitnej identity naprieč rolovými entitami.

V1 nepridáva customer polia ani Organization entitu. Budúce zjednotenie identity musí zachovať historické SUP referencie a explicitné mappings; rovnaký názov nie je dôkaz zhody.

## 52. Organization Abstraction Risk

Variant A (Supplier ako first-class organizácia v dodávateľskej roli) je v súlade s prijatou Supplier Entity. Variant B (Organization + Supplier role/relationship) môže byť budúca architektúra, ale dnes nie je prijatý a review ho nezavádza.

Riziko migrácie spočíva v tom, že aktuálne široký partner význam dovolí niekomu založiť SUP pre skupinu a inému pre pobočku. Neskoršia Organization abstrakcia to nedokáže bez straty referenčnej jednoznačnosti automaticky opraviť. Preto je SI-0001 skutočný pre-implementation blocker, aj keď JSON profil zostane malý.

## 53. Real Data Boundary

Žiadne reálne Supplier záznamy, firmy, addresses, VAT IDs, weby, emaily, supplier codes ani certifikácie sa nevytvárajú. Existujúce fiktívne SUP referencie v testoch nie sú Supplier populácia.

## 54. Future Real-data Requirements

| Téma | Predpoklad alebo enrichment |
| --- | --- |
| Prijatá identity granularita a deduplication policy | Predpoklad každého reálneho onboardingu |
| Spoľahlivý identity zdroj a overený názov subjektu | Predpoklad Review/Approved identity |
| External registration identifiers | Podľa identity policy a rizika zhody; najprv riadený kontrakt |
| Addresses/sites | Enrichment identity registra; predpoklad site-scoped capability alebo dodacieho použitia |
| Contacts/persons | Enrichment; najprv kontakt a správa údajov |
| Classification/roles | Voliteľný riadený enrichment, nie qualification dôkaz |
| Qualification/certification | Predpoklad tvrdenia o kvalifikácii, nie každej Supplier identity |
| StockMaterial/services/offers | Neskorší obchodný context, nie minimum identity |

V1 kontrakt nemá automaticky znamenať pripravenosť procurement alebo certifikačného workflow.

## 55. Risks

| Priorita | Riziko | Ochrana / ďalší krok |
| --- | --- | --- |
| High / blocking | Partner vs právna organizácia vs site/vzťah | Uzavrieť SI-0001 pred schémou |
| High | Supplier ako ERP catch-all | Uzavretý v1 field list |
| High | Qualification zamieňaná s RecordStatus | Žiadny root approved/qualificationStatus |
| High | PropertyRecord ako business key/value store | `properties` v1 odmietnuť |
| High | Root sourceLinks preukazujú všetky downstream claims | Oddelená provenance matrix |
| Medium | Jediná rola vylučuje multi-role organizácie | Optional multiple Classification, bez enum |
| Medium | Free-text externé ID a nekontrolovaná adresa | Deferred scheme-aware a address kontrakty |
| Medium | Kontakty bez osoby/role/platnosti | Odložiť Contact/Person model |
| Medium | Capability/process array naznačuje univerzálnu schopnosť | Odložiť scoped capability model |
| Medium | Volatilné price/lead time na root | Obchodný/časový model neskôr |
| Medium | Certification string bez scope/expiry/source | Samostatný sourced model |
| High | Vlastnenie StockMaterial/Machine roots | Len budúce explicitné referencie |
| Medium | Bidirectional Material/Supplier zoznamy | Nepridávať root arrays |
| Medium | Duplicita budúcej Organization identity | Stabilná granularita, auditované mappings |
| Medium | Premature real Supplier populácia | Žiadne reálne dáta v tejto fáze |
| Medium | Replacement vydávaný za merger alebo equivalence | Deferred replacement policy |

## 56. Deferred Concepts

Odložené sú legal/trading names a aliases, ExternalIdentifier, Address, Site/Location, Contact/Person, website/communications, qualification, certification, assessment/performance history, Supplier Capability, CommercialObservation serializácia, offers/pricing/lead times, corporate relationships, replacement policy, Organization unification, entity resolver, persistence a real-data onboarding.

Odloženie týchto kontraktov je bezpečné pre úzky identity register až po uzavretí významu SUP; nemôže nahradiť rozhodnutie o identity granularite.

## 57. Implementation Preconditions

### SI-0001: Supplier identity granularity

- Severity: High, blocking Supplier implementation.
- Evidence: RFC-0002 §4.6 definuje obchodného alebo servisného partnera, G-0049 dodávateľa alebo obchodného partnera. Ani jeden neurčuje legal entity / operational organization / procurement relationship granularitu. EOS-003 rieši formát, nie tieto hranice.
- Required decision: potvrdiť jeden primárny subjekt SUP a pravidlá multi-site, group/multiple legal entities, multi-role a continuity pri premenovaní alebo zmene právneho subjektu.
- Recommendation: jeden SUP pre jednu právne samostatnú organizáciu v dodávateľskej roli; prevádzky a účty nie sú nové SUP; ostatné typy counterparty mimo v1, kým nebudú presne definované.
- Resolution route: explicitné doménové rozhodnutie a jeho zachytenie schváleným RFC/ADR postupom podľa architecture freeze, ak vyžaduje rozšírenie alebo zmenu prijatého významu. Nevytvárať nové pravidlo potichu v JSON Schema ani považovať tento Review dokument za Accepted autoritu.

Po uzavretí SI-0001 treba potvrdiť v1 profil B, Classification inclusion, exclusion PropertyRecord, common provenance/lifecycle, deferred addresses/contacts, qualification/capability/commercial boundaries a exclusion replacement refs. Tieto sú konkrétne návrhy review, nie implementácia.

Implementácia môže následne použiť existing common metadata, SUP, SourceLink a Classification bez generic entity resolvera. Nie je potrebné predtým implementovať kompletné ERP, Address, Organization ani Decision.

## 58. Readiness Verdict

Supplier je autoritatívne Entity/Aggregate Root a existujúce kontrakty technicky podporujú úzky model B. SUP formát, metadata, lifecycle a aggregate ownership nie sú sporné. Material zostáva vhodným mechanickým vzorom, nie zdrojom Supplier doménovej identity.

Implementácia teraz nesmie začať: jedna materiálna identity otázka vedie k nekompatibilným významom toho istého SUP a nedá sa bezpečne odložiť na neskoršie rozšírenie polí. Preto nejde o READY WITH CONDITIONS pre už implementovateľný profil. Je potrebné uzavrieť SI-0001 a potom aktualizovať readiness review; Supplier schema, testy a runtime sa zatiaľ nevytvárajú.

## 59. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-10-06 | 0.1 | 0 | Codex | Pre-design Supplier review: autoritatívne SUP a aggregate hranice, navrhnutý minimálny profil B, provenance a ownership matice, deferred domény a blokujúca identity granularita SI-0001. |
| 2026-10-14 | 0.1 | 1 | Codex | Phase 0.2C.2-prep.1: výber právne samostatnej organizácie v dodávateľskej roli, rozlíšenie sites a commercial relationships, uzavretie SI-0001 a opakované posúdenie Supplier v1 bez zmeny Accepted architektúry. |

## 60. Supplier Identity Boundary Decision

### 60.1 Baseline and reconstructed problem

Rozhodnutie vychádza z commitnutého CDR-0017 Revision 0, HEAD `aceaf27dcc4a078da81ae1cbff2baf469f8141fc`. Vetva je `feature/phase-0.2c-knowledge-entities`, tracking `origin/feature/phase-0.2c-knowledge-entities`; vstupný pracovný strom bol čistý.

SI-0001 vznikol preto, že RFC-0002 §4.6 určuje Supplier ako obchodného alebo servisného partnera a G-0049 ako dodávateľa alebo obchodného partnera, ale neurčuje, či SUP patrí právne samostatnej organizácii, prevádzke alebo obchodnému vzťahu. Rovnaká schéma by potom mohla niesť nekompatibilné identity. Dopad sa týka deduplikácie, StockMaterial, sites, capabilities, subcontractingu, procurement, offers, certifikácií, assessments, customers/partners, external mappings a entity relationships.

Pôvodné odporúčanie jednej právne samostatnej organizácie bolo návrhom, nie pravidlom odvodeným z regexu. Tento samostatný rozhodovací míľnik ho preveruje na konkrétnych scenároch a uzatvára pre obmedzený implementačný profil v1.

### 60.2 Candidate comparison

| Kandidát | Výhody | Nevýhody | Rozhodnutie |
| --- | --- | --- | --- |
| A: právne samostatná organizácia v dodávateľskej roli | Stabilita cez názvy, prevádzky, účty a roly; jasný subjekt referencií a provenance | Potrebuje identity dôkaz; site-scoped fakty a account data vyžadujú ďalší context; budúca Organization integrácia | SELECTED pre v1 |
| B: operational organization / establishment / site | Blízko miestnej capability, skladov a certifikačného scope | Neurčitá prevádzková hranica; viac SUP pre jednu právnu organizáciu; duplikované právne údaje a nejednoznačné procurement/accounting mapping | REJECTED ako SUP identita; site koncept zostáva deferred |
| C: commercial relationship / vendor account | Priame napojenie na buyer-specific účty, meny a podmienky | Rôzne účty by vytvárali rôzne SUP pre ten istý subjekt; zmena vzťahu by menila identity evidence; capability a certifikácia sa viažu na nesprávny account objekt | REJECTED ako SUP identita; commercial context zostáva deferred |

Variant A nevyžaduje, aby všetky certifikácie alebo služby platili pre celú organizáciu. Vyžaduje práve opačne, aby budúce scoped tvrdenia neboli odvodené iba z organizačného SUP.

### 60.3 Selected normative identity statement

**V Supplier v1 identifikuje jedno SUP jednu právne samostatnú organizáciu reprezentovanú v EOS v dodávateľskej roli.** Viac prevádzok, rolí, vendor účtov, capabilities alebo offers samo osebe NESMIE vytvoriť ďalšiu SUP identitu. Iná právne samostatná organizácia vyžaduje odlišné SUP; ak pre ňu už SUP existuje, použije sa existujúce ID namiesto nového duplikátu.

SUP NEIDENTIFIKUJE site, pobočku bez samostatnej právnej identity, warehouse, brand, trade name, vendor account, offer, capability, certification, contact, stock item ani commercial relationship. Je internou stabilnou identitou Supplier aggregate, nie všeobecným Organization ID, registračným číslom ani globálnym identifikátorom všetkých rolí v EOS.

Formát zostáva `SUP-xxxx`, presne štyri číslice, centrálne `^SUP-[0-9]{4}$` cez existujúci `$ref`. Pole zostáva `id`. Žiadny nový prefix alebo lokálny regex nevzniká.

### 60.4 Operational legal boundary

Pre v1 je právne samostatná organizácia subjekt, pri ktorom spoľahlivý zdroj potvrdzuje oddelenú organizačnú právnu identitu od iných evidovaných subjektov. Samostatné registračné údaje môžu byť dôkazom, ale samotné odlišné číslo, VAT, adresa, názov alebo interný účet nie sú automatickým algoritmom na založenie nového SUP.

| Prípad | Pravidlo v1 |
| --- | --- |
| Samostatná dcérska právna organizácia | Vlastný SUP, aj keď má spoločného vlastníka alebo značku |
| Pobočka bez samostatnej právnej identity | Nie nové SUP; neskôr site/location context |
| Corporate group | Nie spoločné SUP pre členov; konkrétna samostatná organizácia skupiny môže mať vlastný SUP |
| Trade name / brand | Nemení identity subjektu |
| Internal division | Nevytvára vlastné SUP |
| Fyzická osoba podnikateľ / sole trader | Mimo obmedzeného v1 profilu; nezamieňať s právne samostatnou organizáciou a nevkladať ad-hoc osobné údaje |
| Nejasná právna samostatnosť | Nezakladať nový subjekt ako potvrdenú Supplier identitu; najprv vyriešiť identity dôkaz |

Toto je doménová hranica EOS v1, nie medzinárodná právna taxonómia. Rozšírenie na iné druhy counterparties vyžaduje samostatný návrh. Draft povoľuje inkrementálny zápis a prázdne sourceLinks, ale nie vedomé miešanie site, account a organization významov.

### 60.5 Organization and role

Supplier predstavuje organizáciu konkrétne v dodávateľskej roli. Nie je organizačne neutrálnym registrom všetkých subjektov. Manufacturer, Distributor, Service Provider, Subcontractor a Material Supplier sú súbežné možné roly; Vendor zostáva informatívny obchodný termín.

Pre rovnaký subjekt NESMIE vzniknúť ďalšie SUP iba pre inú rolu. Generic Classification assignments môžu neskôr vyjadrovať kategórie; konkrétna výroba produktu, subcontract vzťah alebo distributor authorization vyžadujú vlastný context a provenance. Jediný povinný role enum sa nezavádza.

Ak organizácia neskôr vystupuje aj ako Customer, toto rozhodnutie nepredpisuje Customer kontrakt ani nové ID. Budúci návrh musí riešiť zdieľanú organizačnú identitu a mappings; nesmie pretypovať SUP na Customer alebo predpokladať zhodu podľa názvu.

### 60.6 Sites, capabilities and certifications

Jedna právne samostatná organizácia môže mať viac plants, warehouses, branches a service locations. Fyzická odlišnosť sama nevytvára ďalšie SUP. SupplierSite alebo Location zostáva budúcim konceptom bez novej schémy či prefixu.

Certifikácia jedného závodu, capability konkrétneho stroja/site alebo skladová dodávka z warehouse sa nesmie povýšiť na organizačne univerzálnu vlastnosť. Budúce capability/certification/stock records budú potrebovať explicitný subject a site/scope/time context. Ak tento model nie je dostupný, v1 taký údaj neserializuje do Supplier root, PropertyRecord, notes ani generic capability array.

### 60.7 Commercial relationship and identifier placement

Vendor code, payment terms, currency, price lists, commercial status, MOQ, delivery terms a buyer-specific account number sú budúce commercial/relationship údaje. Nedefinujú SUP a zmena týchto hodnôt nevytvára novú Supplier identitu.

| Identifier context | Budúce priradenie |
| --- | --- |
| Company registration identity | Organizácia/Supplier profil, so scheme a provenance |
| Establishment/location identifier | Site/location, nie náhradná SUP identita |
| ERP vendor code / buyer account | External system mapping alebo commercial relationship |

Všetky mappings musia rešpektovať skutočný význam externého systému; nemožno z názvu vendor code usúdiť, že identifikuje právny subjekt. ExternalIdentifier sa teraz neimplementuje.

### 60.8 Rename, merger and duplicate scenarios

| Scenár | Identity výsledok | Hranica |
| --- | --- | --- |
| A: rovnaký právny subjekt mení názov | Zachovať SUP; auditovaná zmena záznamu | Continuity musí byť doložená, nie odvodená z podobného názvu |
| B: trade name sa mení | Zachovať SUP | Brand nie je identita |
| C: pobočka sa zatvorí | Zachovať organizačné SUP | Site stav neznamená zánik organizácie |
| D: jedna firma nadobudne druhú | Oba SUP ostávajú, ak oba subjekty právne pokračujú | Acquisition je ownership relationship, nie record replacement |
| E: dve entity sa zlúčia do nového právneho subjektu | Nový subjekt má odlišné SUP; staré referencie a história sa zachovajú | Bez automatického prenesenia kvalifikácií, zmlúv a evidence |
| E doplnenie: jeden pôvodný subjekt právne pokračuje | Jeho SUP pokračuje; druhý sa neprepisuje naň | Skutočnú continuity treba overiť zo zdrojov |
| F: objaví sa duplicitný EOS record pre rovnaký subjekt | Nezakladať tretie SUP; určiť canonical záznam budúcim auditovaným dedup postupom | Bez mazania histórie alebo tichého prepisu existujúcich odkazov |

`replaces`/`replacedBy` môže byť neskôr relevantné pre náhradu duplicitného záznamu, ale nie ako univerzálna reprezentácia merger, acquisition alebo právneho nástupníctva. Vo v1 zostáva odložené, pretože chýba dedup/replacement workflow a resolver. Povolenie supersession v RFC neznamená povinnosť publikovať tieto polia v prvom profile.

### 60.9 Provenance consequences

Supplier.root.sourceLinks podporuje identitu, existenciu a definíciu reprezentovanej organizácie. Automaticky nepreukazuje qualification, capability, certification, commercial terms alebo site attributes. Každé budúce takéto tvrdenie musí mať vlastný scope a zdroj.

Common metadata/source lifecycle zostáva bez zmeny: sourceLinks je required, Draft povoľuje prázdne pole, Review/Approved overiteľnej identity vyžaduje zdroj. Validita source odkazu nie je automatickým dôkazom právnej identity alebo kvalifikácie.

### 60.10 Future Organization risk

Riziko: **MEDIUM**. Supplier ako rolový aggregate môže neskôr zdieľať organizáciu s Customer alebo Partner profilom. Prijatá granularita umožňuje budúce explicitné prepojenie Supplier profilu na Organization bez zmeny významu existujúceho SUP.

Možná migračná zásada, nie nový model: zachovať SUP a historické referencie, vytvoriť overené mappings na budúcu organizačnú identitu a premiestňovať shared identity údaje iba auditovane. Supplier môže zostať supplier-role profilom odkazujúcim na Organization. Nesmie sa vymazať SUP ani odvodiť one-to-one mapping automaticky z názvu.

Budúca duplicita rolových profilov je riaditeľná; deštruktívna duplicita by vznikla najmä miešaním site/account/organization identity. Vybrané pravidlo ju obmedzuje. Organization sa teraz nezavádza a SI-0001 preto nezostáva otvorené pre túto budúcu abstrakciu.

### 60.11 RFC / ADR impact

Výsledok: **A – spresnenie obmedzeného v1 profilu existujúceho Supplier konceptu**. RFC-0002 §4.6 a §16 aj G-0049 ponechávajú Supplier ako obchodného/servisného partnera, Entity a Aggregate Root so SUP. Žiadny Accepted text neurčuje site alebo account ako povinnú SUP granularitu ani nevyžaduje zahrnúť všetky typy counterparties do v1.

Rozhodnutie nemení entity kategóriu, aggregate ownership, lifecycle, provenance, ID formát ani význam iných kontraktov. Vyberá explicitný identity profil v rámci prijatého partner konceptu pre prvú implementáciu, podobne ako Material v1 explicitne obmedzuje širší koncept. Nie je univerzálnou redefiníciou všetkých budúcich Supplier prípadov.

Preto sa nemení Accepted RFC/ADR, governance ani EOS-003. Ak sa neskôr bude meniť význam SUP, povoľovať site/account ako SUP alebo nahrádzať Supplier všeobecným Organization aggregate, už to nebude toto spresnenie a bude potrebný príslušný architektonický proces.

### 60.12 Supplier v1 preconditions re-evaluation

Identity kandidát A a serializačný model B zo sekcie 43 sú rôzne osi rozhodnutia: vyberá sa organizačná identita A a minimal identity + optional Classification profil B.

| Predpoklad | Výsledok pre v1 |
| --- | --- |
| Domain meaning, object type, SUP | Jedna právne samostatná organizácia v dodávateľskej roli; Knowledge Entity/Aggregate Root; central SUP |
| Organization / legal boundary | Definovaná v 60.3–60.4; sole traders mimo v1 |
| Site boundary | Žiadne nové SUP iba pre site; structured sites deferred |
| Manufacturer/vendor/distributor | Viac rolí jednej identity; bez hard-coded type enum |
| Naming | Required neprázdny `name`; nie unique identity; legalName/tradingName deferred |
| Provenance / lifecycle | Required common metadata/sourceLinks; common RecordStatus; nie qualified-vendor status |
| Classification | Optional multiple embedded assignments; CLS existence/lifecycle cez existing context; applicability nevyriešená a nepredstieraná |
| PropertyRecord | V1 neobsahuje `properties`; žiadny business key/value register |
| Address/contact/person/website | Deferred; nie free-text náhrady |
| Qualification/certification/capability | Deferred scoped models; nie root Approved ani boolean |
| Commercial data | Price, leadTime, terms, accounts, offers mimo root |
| Material/StockMaterial/process/tool | Samostatné aggregates/future context; bez root zoznamov a embedding |
| Observation | Môže SUP referencovať; Supplier ju nevlastní |
| Minimum valid Supplier | Common required metadata, SUP `id`, `name`, `sourceLinks`; optional description/classifications/notes |
| Root verificationStatus | Nepridáva sa |
| Replacement | `replaces`/`replacedBy` deferred; žiadne implicitné corporate semantics |
| Resolver | Generic entity resolver nie je predpoklad v1; CLS kontext sa reuse-ne |
| Real data | Budúci samostatný onboarding s identity dôkazom; teraz iba návrh |

Nezostáva ďalšia nejednoznačnosť vyžadujúca nekompatibilné v1 schémy. Odložené kontrakty nie sú skryté optional fields. Pri následnej implementácii sa musí zachovať presný field list sekcie 44, closed shape, central `$ref`, uvedené lifecycle pravidlá a oddelenie schema/application/reference/catalog výsledkov. Žiadna výnimka z obmedzení v1 sa nesmie doplniť ako voľný string alebo catch-all array.

### 60.13 SI-0001 closure and readiness

- Previous state: High, blocking Supplier implementation; NOT READY.
- Final state: **SI-0001 CLOSED**.
- Rationale: Jedna identity granularita bola vybraná po porovnaní A/B/C a preverená na rename, sites, accounts, multi-role, merger, acquisition, duplicate a future Organization scenároch. Corporate a relationship semantics sa neprekrývajú so SUP; otvorené rozšírenia sú explicitne mimo v1.
- Remaining Supplier implementation blockers: **0** pre presne definovaný v1 profil.
- Readiness: **READY FOR IMPLEMENTATION** v samostatnom následnom míľniku, bez začatia implementácie v tomto rozhodnutí.

### 60.14 Verification and unchanged scope

Kompletná existujúca sada: 236 passed, 0 failed, 0 errors. Schémy zostávajú 21, Knowledge Core 7, catalogs 4, entity schemas 1 (iba Material); ADR 17 a RFC dokumenty 4. Supplier schéma neexistuje. Jediná zmena tohto míľnika je CDR-0017 Revision 1. Material, schémy, Python, tests, fixtures, katalógy, Accepted RFC/ADR, governance, BACKLOG, ROADMAP a CHANGELOG zostávajú nezmenené. Nevznikli reálne Supplier dáta.

READY FOR IMPLEMENTATION
