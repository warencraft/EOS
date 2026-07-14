# ADR-0001 - Use Markdown for governed documentation

**Status:** Approved  
**Date:** 2026-07-13  

## Context

EOS potrebuje riadenú dokumentáciu, ktorá je čitateľná, ľahko verzovateľná a použiteľná bez špeciálneho softvéru.

## Decision

Riadená projektová dokumentácia EOS sa bude v počiatočných fázach písať vo formáte Markdown.

## Alternatives Considered

- DOCX: vhodný pre formálne výstupy, ale horšie sa verzionuje v Git.
- PDF: vhodný na distribúciu, nie na autoritatívne úpravy.
- Wiki systém: užitočný neskôr, ale v tejto fáze by pridal zbytočnú infraštruktúru.

## Consequences

Dokumenty budú ľahko čitateľné, kontrolovateľné a verzovateľné.

Exporty do PDF alebo DOCX môžu vzniknúť neskôr z autoritatívnych Markdown zdrojov.

## Risks

Markdown nemá natívne riadenie schvaľovania. Tento nedostatok sa bude riešiť stavmi dokumentov, verziami, revíziami a neskôr validačnými nástrojmi.

## Related Documents

- `docs/governance/EOS-000_Development_Manifesto.md`
- `docs/governance/EOS-002_Documentation_Standard.md`

## Review Date

2026-10-01

