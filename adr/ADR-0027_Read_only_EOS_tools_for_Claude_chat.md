# ADR-0027 - Nástroje iba na čítanie pre Claude chat v EOS

**Status:** Accepted (Software Architect) pre rozsah bez údajov zákaziek; údaje zákaziek čakajú na rozhodnutia Marca D1–D3
**Date:** 2026-11-19

## Context

Panel Claude z ADR-0026 dostáva iba ručne napísané správy. Plán `docs/handoff/2026-11-18_claude-chat-plan.md` (etapa F2, §5.1–5.4) navrhuje, aby Claude videl stav EOS: pravidlá, ADR, schémy, dokumenty, dodávateľov, sklad, knowledge base a nástenku. Ponuky, objednávky, zákazky, kalkulácie a Gmail obsahujú údaje zákazníkov. O ich odoslaní do Claude API rozhoduje Marco (D1–D3). ADR-0019 bez výslovného povolenia zakazuje posielať obsah `intake/` do AI.

## Decision

- Všetok prístup Clauda k údajom ide cez jednu čistú bránu `scripts/ai/brana.py`. Brána nemá vedľajšie účinky a vracia povolenie alebo dôvod odmietnutia v slovenčine.
- Súbory repozitára: povolené sú iba vybrané súbory v koreni (README, ROADMAP, BACKLOG, CHANGELOG, TECH_STACK, AGENTS, CLAUDE, CONTRIBUTING, pyproject) a priečinky `adr/`, `docs/`, `schemas/`, `scripts/`, `tests/`, `templates/`, `data/`, `calculators/` a `assets/`. Povolené sú iba textové prípony a súbory do 400 kB. Nikdy nie `intake/`, skryté súbory, absolútne cesty, `..` ani symbolické odkazy.
- Prevádzkové záznamy: otvorení sú dodávatelia, sklad, knowledge base a nevyriešené správy nástenky. Knowledge base bez kategórií „Referenčné zákazky“ a „Zákazníci“. Ponuky, objednávky, zákazky, kalkulácie a Gmail brána odmieta s odkazom na čakajúce rozhodnutie.
- Claude dostáva tri nástroje (`scripts/ai/nastroje.py`): `eos_hladaj`, `eos_citaj` a `eos_zaznamy`. Všetky sú iba na čítanie. Zapisovať môže iba človek cez existujúce formuláre (návrh dodávateľa podľa ADR-0026).
- Výsledok nástroja je označený ako dáta, nie pokyny. Systémový prompt `scripts/ai/system_prompt.md` žiada uvádzať zdroje, nevymýšľať hodnoty, označovať odhady ako „Návrh“ a nerozhodovať doménové otázky.
- Najviac 8 krokov s nástrojmi na jednu odpoveď, potom posledná požiadavka bez nástrojov. Paralelné volania sú vypnuté. Panel pod odpoveďou ukáže, čo Claude čítal. Odpoveď sa zobrazuje iba ako text.

## Alternatives Considered

| Možnosť | Dôvod |
| --- | --- |
| Celý repozitár a `intake/` ako kontext | Porušuje ADR-0019 a predbieha rozhodnutia Marca. |
| MCP server pre EOS | Pre jeden panel na jednom serveri je zbytočnou ďalšou službou. Nástroje Messages API stačia. |
| Zápis cez nástroje | Zmeny v EOS majú ostať na človeku; návrh dodávateľa už má potvrdzovací tok. |

## Consequences

Claude môže odpovedať na otázky o pravidlách, schémach, dodávateľoch a sklade s citovaním zdroja. Každý krok s nástrojom zvyšuje cenu odpovede. Pridanie údajov zákaziek je po rozhodnutí Marca zmena brány a nového ADR, nie zmena nástrojov.

## Risks

Do Claude API odchádza obsah repozitára, dodávateľov a skladu; ten neobsahuje údaje zákazníkov, pokiaľ sa nedostanú do knowledge base mimo blokovaných kategórií. Text v záznamoch môže obsahovať pokyny (prompt injection); obrana je označenie výsledku, nástroje bez zápisu a textové zobrazenie. Ceny zo skladu sú interné údaje firmy a idú cez firemný API kľúč.

## Related Documents

- `adr/ADR-0019_Keep_real_job_intake_outside_git.md`
- `adr/ADR-0025_Quotes_orders_and_Gmail_in_EOS_UI_on_server.md`
- `adr/ADR-0026_Confirm_quote_email_and_keep_Claude_sessions_in_EOS.md`
- `docs/handoff/2026-11-18_claude-chat-plan.md`
- `tests/test_chat_nastroje.py`

## Review Date

Po rozhodnutiach Marca D1–D3 alebo po mesiaci používania na serveri.

## Change History

| Dátum | Zmena |
| --- | --- |
| 2026-11-19 | Prijaté pre rozsah bez údajov zákaziek (etapa F2). |
