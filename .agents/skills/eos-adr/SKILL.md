---
name: eos-adr
description: Kedy a ako napísať Architecture Decision Record (ADR) v EOS. Použi pri zmene architektúry, závislostí, formátov, pravidiel identifikácie alebo technologického rámca.
---

# ADR v EOS

## Kedy je ADR povinné

- nová alebo odstránená závislosť, nástroj alebo framework (TECH_STACK.md),
- zmena formátu dát, schém, identifikátorov alebo verziovania,
- nový modul alebo zmena povolených závislostí medzi modulmi (EOS-001 §4),
- zmena úložiska (napr. SQLite), testovacieho frameworku alebo validátora,
- akákoľvek odchýlka od Accepted ADR.

Ak si nie si istý, opýtaj sa používateľa a ADR navrhni.

## Postup

1. Zisti najvyššie použité číslo ADR. Pozri `adr/` aj odkazy v repozitári (`grep -rho "ADR-[0-9]\{4\}" . | sort -u | tail`), lebo niektoré ADR môžu byť citované skôr, než majú súbor.
2. Skopíruj `adr/ADR-0000_Template.md` do `adr/ADR-NNNN_<Anglický_názov_s_podčiarkovníkmi>.md`.
3. Vyplň Context, Decision, Alternatives Considered (najlepšie tabuľkou ako v ADR-0013), Consequences, Risks, Related Documents a Review Date. Píš po slovensky.
4. `Status: Draft`. Na Accepted ho mení **iba používateľ**.
5. Ak ADR nahrádza staré, staré ADR nemaž. Doplň do neho odkaz „Superseded by ADR-NNNN“.
6. Doplň odkaz na ADR do dokumentov, ktorých sa týka (TECH_STACK.md, EOS-001…), a záznam do `CHANGELOG.md`.

Implementácia, ktorá od ADR závisí, začína až po jeho schválení.
