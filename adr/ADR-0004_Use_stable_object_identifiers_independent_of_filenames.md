# ADR-0004 - Use stable object identifiers independent of filenames

**Status:** Approved  
**Date:** 2026-07-13  

## Context

EOS bude obsahovať dokumenty, dátové záznamy, zákazky, kalkulátory a šablóny. Názvy súborov sa môžu meniť, ale odkazy medzi objektmi musia zostať stabilné.

## Decision

Každý riadený objekt bude mať stabilné ID nezávislé od názvu súboru.

Názov súboru má byť čitateľný, ale autoritatívne ID je uložené v dokumente alebo dátovom zázname.

## Alternatives Considered

- Používať iba názvy súborov: jednoduché, ale krehké pri premenovaní.
- Používať iba interné databázové ID: vhodné neskôr, ale predčasné vo fáze 0.1.
- Používať neformálne názvy: nevhodné pre spätnú dohľadateľnosť.

## Consequences

Odkazy medzi dokumentmi a dátami budú stabilnejšie.

Premenovanie súboru nebude znamenať zmenu identity objektu.

## Risks

Je potrebná disciplína pri prideľovaní ID. Pravidlá sú definované v `EOS-003`.

## Related Documents

- `docs/governance/EOS-003_Identification_and_Versioning.md`

## Review Date

2026-10-01

