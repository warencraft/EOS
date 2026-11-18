# ADR-0026 - Potvrdené odoslanie ponuky a rozhovory s Claudom v EOS

**Status:** Draft
**Date:** 2026-11-18

## Context

ADR-0025 povoľuje čítanie Gmailu a ukladanie konceptov cez IMAP. Používateľ požiadal o potvrdené odosielanie priamo z detailu ponuky a o bočný panel s vlastnými rozhovormi. Tento návrh popisuje implementačnú vetvu a dopĺňa ADR-0025 iba v rozsahu týchto dvoch funkcií.

## Decision

- EOS ponechá koncept cez IMAP a pridá odoslanie cez Gmail SMTP s TLS. Použije existujúcu schránku a heslo aplikácie. Odoslanie vyžaduje náhľad a následný POST s odtlačkom tej istej správy. Existujúce vlákno využije pôvodný identifikátor správy. Po prijatí SMTP sa zapíše existujúci stav `sent`.
- Pred odovzdaním správy SMTP vznikne jedinečný súbor pokusu. Pri neistom výsledku alebo výpadku zabráni ďalšiemu odoslaniu bez ručného overenia v Gmaile. Pri potvrdenom odmietnutí sa odstráni. Záznam pokusu obsahuje identitu odosielajúceho, čas a identifikátor správy.
- Obe funkcie sú predvolene vypnuté. Povolenia pre chat a odosielanie sa nastavujú samostatne podľa loginu overeného v súkromnom Tailscale Serve. EOS overí lokálny zdroj požiadavky, povolený hostiteľ a pri POST aj pôvod stránky. EOS musí počúvať iba na loopbacku, za Tailscale Serve. Hostiteľ a lokálne procesy sú súčasťou dôveryhodnej infraštruktúry.
- Claude používa existujúcu voliteľnú závislosť `.[ai]` a firemný Claude API kľúč na serveri. EOS ukladá históriu do vlastných súborov oddelených podľa identity. API dostáva ručne napísané správy a predchádzajúce správy rozhovoru. Prístup k súborom zákaziek, Gmailu a kalkuláciám sa v tejto etape nepridáva. Návrh sa do textu ponuky prenesie iba kliknutím človeka.
- Voliteľné pole `emailBody` patrí do nástrojovej schémy prevádzkového záznamu. Bez vlastného textu platí doterajšie generovanie. Kontrakty EOS sa nemenia.

- Panel je súčasťou spoločnej šablóny EOS. Navigácia medzi internými stránkami vymieňa obsah vedľa panela. Na mobiloch je panel zbalený a rozhovory sa obnovujú z VPS podľa rovnakého účtu. Návrh zlepšenia je výslovné podanie na existujúcu nástenku pre Robina.
- V osobnom režime `EOS_GMAIL_USERS` má každý povolený účet samostatný súbor pripojenia. EOS pri novom importe zaznamená zdrojovú schránku. Staršie ponuky bez zdrojovej schránky si ju automaticky neprisvoja. Nasadenie pre inžiniera používa koncepty s prázdnym zoznamom `EOS_MAIL_SENDERS`.

- Claude môže pripraviť štruktúrovaný návrh dodávateľa. Vlastník rozhovoru môže návrh načítať do existujúceho formulára. Zápis robí až formulár po potvrdení človekom.

- Používateľ môže z Gmailu vybrať objednávku a založiť zákazku po kontrole predvyplnených údajov. Zdrojový text a potvrdené údaje sa ukladajú cez existujúci príjem podkladov. Pri tomto toku sa Claude API nevolá.

## Alternatives Considered

| Možnosť | Dôvod |
| --- | --- |
| Rýchle odoslanie jedným kliknutím | Dvojkrokové potvrdenie umožňuje skontrolovať príjemcu a obsah. |
| História z webu Claude | Messages API pracuje s históriou dodanou EOS. Pre túto verziu sa používa vlastné úložisko. |
| Google OIDC ako súčasť prvého vydania | Pre tento úzky rozsah sa využíva už nasadená súkromná identita Tailscale. Širší návrh rolí a prístupu k dátam zostáva samostatný. |

## Consequences

Správy odchádzajú zo spoločnej schránky. Širšie pravidlá prístupu k súčasným stránkam EOS tento návrh nemení. Pri používaní chatu vznikajú náklady na API a históriu uloženú na VPS. Rozhovory sú mimo gitu.

## Risks

Pri nejasnom výsledku SMTP treba porovnať identifikátor pokusu s Odoslanými v Gmaile. Z vlastného textu e-mailu môže vzniknúť neaktuálna ponuka, preto musí používateľ pri odoslaní prečítať náhľad. Do chatu sa vkladajú iba údaje, ktoré schvaľujú pravidlá EOS. Kľúč API potrebuje limit vo firemnom workspace.

## Related Documents

- `adr/ADR-0025_Quotes_orders_and_Gmail_in_EOS_UI_on_server.md`
- `adr/ADR-0019_Keep_real_job_intake_outside_git.md`
- `docs/manual/SERVER.md`

## Review Date

Po prvom overení SMTP a Claude API na skúšobnej ponuke na VPS.

## Change History

| Dátum | Zmena |
| --- | --- |
| 2026-11-18 | Prvý návrh pre implementačnú vetvu. |
