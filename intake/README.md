# intake - príjem podkladov reálnej zákazky

Lokálny priečinok na podklady reálnych zákaziek: výkresy, 3D modely, dopyt, ponuka, objednávka, výrobné podklady, merania a korešpondencia. **Git ho ignoruje** (okrem tohto súboru), takže sa podklady nedostanú na GitHub. Pravidlá sú v ADR-0019.

Podklady tu **nie sú zdrojom pravdy EOS**. Znalosť z nich vznikne až prevodom na záznamy so SourceReference a klasifikáciou N/L/P/V, keď bude navrhnutá entita Job (CDR Job) a projekt prejde do etapy B (TECH_STACK.md).

## Štruktúra jednej zákazky

```
intake/
  JOB-2026-0001/
    manifest.json     súpis súborov (vytvorí a udržiava skript)
    vykresy/          výkresy (PDF, DWG, DXF)            → drawing
    modely/           3D modely (STEP, IGES)             → model
    dopyt/            dopyt zákazníka                    → inquiry
    ponuka/           naša cenová ponuka                 → quote
    objednavka/       objednávka                         → order
    vyroba/           postup, časy, plán                 → production
    merania/          meracie protokoly                  → measurement
    korespondencia/   e-maily a poznámky                 → correspondence
    ine/              všetko ostatné                     → other
```

`JOB-2026-0001` je predbežné označenie vo formáte ID zákazky (ADR-0008). Význam ID potvrdí až CDR Job.

## Postup

Z koreňa repozitára (`python` = Python z `.venv`):

1. Založ zákazku:

   ```
   python scripts/job_intake.py new JOB-2026-0001 --title "Krátky názov" --by Marco
   ```

2. Nakopíruj súbory do podpriečinkov podľa druhu.
3. Zapíš ich do manifestu (doplní kontrolný súčet, veľkosť a kategóriu podľa podpriečinka):

   ```
   python scripts/job_intake.py scan intake/JOB-2026-0001
   ```

4. V `manifest.json` doplň pri každom súbore `sourceClass` (N/L/P/V podľa EOS-000), prípadne `documentRevision` a `description`. Pri zákazke skontroluj `confidentiality` a `aiProcessingAllowed`.
5. Over:

   ```
   python scripts/job_intake.py check
   ```

   Chyba = chýbajúci, zmenený alebo nezapísaný súbor, neplatný manifest, súbor zákazky v gite. Upozornenie = súbor bez `sourceClass`.

Po každej zmene súborov zopakuj `scan` a `check`.

## Pravidlá

- Podklady sa **nikdy necommitujú** a nenahrávajú na GitHub. `check` hlási chybu, ak by sa súbor z `intake/` dostal do gitu.
- `aiProcessingAllowed` je predvolene `false`. AI agent obsah súborov nečíta, kým ho vlastník zákazky výslovne nepovolí v manifeste aj v zadaní.
- `confidentiality`: `internal`, `confidential` (predvolené), `restricted`.
- Zálohu priečinka rieš mimo gitu (napr. firemné úložisko).
- Údaje zo zákazky sa do `data/`, fixtúr ani dokumentácie neprepisujú bez zdroja a klasifikácie (AGENTS.md, TECH_STACK.md §5).
