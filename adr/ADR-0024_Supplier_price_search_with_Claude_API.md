# ADR-0024 - Vyhľadanie cien u dodávateľov cez Claude API

**Status:** Accepted  
**Date:** 2026-11-18  
**Accepted:** 2026-11-18, Software Architect (zadanie implementácie). Bod 5, zaradenie ceny z webu medzi N/L/P/V, ostáva na rozhodnutí Chief Engineering Knowledge Architecta.  
**Decided by:** Software Architect (IT strana projektu); použitie cien v ponukách rozhoduje Chief Engineering Knowledge Architect  

## Context

Pri ponuke treba zistiť cenu a dostupnosť materiálu a nakupovaných dielov (honované rúry, piestne tyče, ložiská, tesnenia…). Dnes to Marco hľadá ručne na weboch dodávateľov alebo posiela dopyty.

EOS Zákazky (ADR-0023) vie k položke vybrať vhodných dodávateľov a otvoriť vyhľadávanie na ich webe. Weby však čítať nevie, lebo stránka v prehliadači nesmie volať cudzie servery. Skutočné čítanie webov dodávateľov musí bežať na strane servera alebo na počítači.

`TECH_STACK.md` má na AI etapu **E**: `anthropic` SDK v module `ai/`. Etapa E nie je aktívna.

## Decision

Návrh:

1. **Predčasne povoliť úzku časť etapy E:** jeden nástroj na vyhľadanie cien. Ostatné AI funkcie, ako čítanie výkresov, ostávajú v etape E.
2. **Nástroj `scripts/ai/hladanie_cien.py`** (podľa `TECH_STACK.md` §6 patrí kód do `scripts/`, kým nie je schválený presun do `src/eos/`).
   - Vstup: zoznam položiek (text, množstvo, jednotka) a zoznam dodávateľov s webovými doménami (JSON súbor).
   - Volá Claude API s nástrojmi na hľadanie a čítanie webu **obmedzenými na domény dodávateľov zo vstupu**.
   - Výstup: JSON návrh podľa `scripts/ai/cenovy_navrh.schema.json` (nástrojový formát, nie kontrakt EOS, rovnako ako manifest v ADR-0019). Ku každej položke a dodávateľovi: odkaz na stránku produktu, cena, mena, jednotka, či je s DPH, dostupnosť, dátum a čas zistenia, citovaný text zo stránky a stav `navrh`. Keď cena nie je verejná, výstup uvedie „na dopyt“ a odkaz.
   - Príkazový riadok: `python -m scripts.ai.hladanie_cien vstup.json > navrh.json`.
3. **Závislosť `anthropic`** ako voliteľná skupina `.[ai]` v `pyproject.toml`, zapísaná do `TECH_STACK.md`. Jadro a testy bez nej bežia ďalej, AI testy sa preskočia rovnako ako testy UI bez `.[ui]`.
4. **Kľúč API** iba v premennej prostredia `ANTHROPIC_API_KEY`, nikdy v gite. Model sa nastavuje parametrom, nie natvrdo v kóde.
5. **Cena z webu nie je znalosť EOS.** Do ponuky ju môže prevziať iba Marco. Do znalostí EOS vstúpi až po návrhu kontraktu pre cenu (PriceRecord alebo podobne) so zdrojovou klasifikáciou. Zaradenie ceny z webu medzi N/L/P/V rozhoduje Marco.
6. **Bez údajov zákaziek.** Vstup obsahuje iba položky materiálu, nie meno zákazníka, číslo zákazky ani výkresy. Položky z `intake/` sa smú použiť iba pri `aiProcessingAllowed: true` (ADR-0019).
7. **Testy** s náhradným (mock) klientom na fiktívnych dátach: tvar výstupu, obmedzenie domén, správanie bez ceny, chyba API. Bez volania skutočného API v CI.

## Alternatives Considered

| Možnosť | Posúdenie |
| --- | --- |
| Hľadanie priamo zo stránky EOS Zákazky | Nedá sa: prehliadač nepovolí čítať cudzie weby. |
| Vlastný scraper (requests + HTML parser) pre každého dodávateľa | Bez AI, ale pre každý web iný kód, ktorý sa pri zmene webu rozbije. Nové závislosti. Niektoré weby to zakazujú. |
| Cenníky od dodávateľov v súboroch (Excel, PDF) | Najspoľahlivejšie tam, kde ich dodávateľ dá. Doplnok, nie náhrada: importér cenníkov môže byť samostatné ADR. |
| Hľadanie cez Claude v chate na požiadanie | Funguje hneď bez kódu, ale výsledok nie je opakovateľný ani uložený vo formáte, ktorý EOS prečíta. |

## Consequences

- Marco dostane k položkám návrh s odkazmi a cenami tam, kde sú verejné.
- Pribudne voliteľná závislosť a jeden nový priečinok `scripts/ai/`; jadro EOS sa nemení.
- Volania API stoja peniaze podľa počtu položiek a dodávateľov; nástroj vypíše počet volaní.

## Risks

- **Ceny za prihlásením alebo na dopyt.** Časť dodávateľov ukazuje ceny až po prihlásení do zákazníckeho účtu alebo iba na dopyt. Nástroj ich nezistí a uvedie „na dopyt“ s odkazom.
- **Nesprávne priradený produkt** (iný rozmer, iný materiál). Opatrenie: výstup cituje text zo stránky a nesie stav `navrh`.
- **Zastaraná cena.** Opatrenie: každá cena nesie dátum a čas zistenia.
- **Podmienky používania webov.** Niektoré weby zakazujú automatický prístup. Opatrenie: iba domény, ktoré Marco v zozname dodávateľov povolí; nízka frekvencia.
- **Rozsah etapy E sa rozšíri bez rozhodnutia.** Opatrenie: toto ADR povoľuje iba tento nástroj.

## Related Documents

- `adr/ADR-0018_Define_target_technology_stack.md`, `TECH_STACK.md` (§3 etapa E, §6)
- `adr/ADR-0019_Keep_real_job_intake_outside_git.md`
- `adr/ADR-0023_Web_app_for_quotes_orders_and_stock.md`
- `docs/governance/EOS-001_System_Architecture.md` (§8: výstupy AI sú návrh)

## Review Date

Po prvých 10 použitiach na reálnych položkách alebo pri aktivácii etapy E, podľa toho, čo nastane skôr.
