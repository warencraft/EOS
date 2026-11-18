# ADR-0023 - Webová aplikácia EOS Zákazky na claude.ai

**Status:** Superseded by ADR-0025  
**Date:** 2026-11-18  
**Decided by:** Software Architect (IT strana projektu); doménové body 2 a 3 rozhoduje Chief Engineering Knowledge Architect  

## Context

Od 17. 11. 2026 existuje prototyp **EOS Zákazky**, webová stránka (artifact) na claude.ai. Beží mimo repozitára a mimo etáp `TECH_STACK.md`. Prihlásený používateľ ju otvorí v prehliadači a pracuje cez svoje Claude predplatné a svoje konektory. Prototyp vznikol v chate na požiadavku Software Architecta, bez ADR. Toto ADR ho dodatočne pomenúva a určuje jeho hranice.

Čo prototyp robí:

| Časť | Funkcia | Kde sú dáta |
| --- | --- | --- |
| Ponuky | Nájde dopyty v Gmaile, Claude z e-mailu vytiahne zákazníka a položky, odpoveď uloží ako koncept v Gmaile. Odosiela človek. | databáza artifactu na claude.ai, Gmail používateľa |
| Objednávky | Z prijatej ponuky: výrobky, materiál so stavom a dodávateľom, operácie so strojom, termín. | databáza artifactu |
| Sklad | Položky, množstvo, miesto, minimum. | databáza artifactu |
| Dodávatelia | 11 overených dodávateľov, vyhľadanie materiálu odkazom na ich web, text dopytu. | databáza artifactu |
| Knowledge base | Kontext pre Clauda: pravidlá nacenenia, referenčné zákazky, súhrn EOS. | databáza artifactu |
| EOS repozitár | Kópia 172 textových súborov z commitu `84d6ed7` na čítanie. | súbory artifactu |
| Asistent | Chat, ktorý číta všetko vyššie. Nič nemení. | odpovede Clauda, história per používateľ |

Súčasne repozitár od ADR-0021 a ADR-0022 obsahuje **lokálne UI** (`python -m scripts.web`). Vie zakladať zákazky, ukázať výkresy, importovať excelovú kalkuláciu a robiť kalkuláciu bez Excelu. Obe aplikácie pracujú so zákazkou a hrozí, že sa rozídu.

Prototyp tiež naráža na ADR-0019 a na otázku 8 v `docs/handoff/2026-11-04_otazky.md` („ktoré dáta sú citlivé a nesmú ísť do žiadnej AI ani na GitHub“). Na otázku 8 zatiaľ neprišla odpoveď. Ponuky z Gmailu pritom posielajú text e-mailov zákazníkov Claudovi a ukladajú mená zákazníkov, položky a ceny na claude.ai.

## Decision

Návrh. Každý bod treba potvrdiť alebo zmeniť.

1. **Rozdelenie úloh medzi aplikácie.**
   - Lokálne UI zostáva miestom pre **kalkuláciu**: import šablóny, operácie, materiál, nákup, sadzba, história zmien.
   - EOS Zákazky preberá to, čo lokálne UI nevie: **Gmail (dopyt → koncept odpovede), objednávky, sklad, dodávateľov a asistenta**.
   - Cena do ponuky v EOS Zákazky sa preberá z kalkulácie z lokálneho UI (zatiaľ ručne). Ceny navrhnuté Claudom z knowledge base sú iba návrh.
2. **Citlivé údaje (rozhoduje Marco).** Jedna z možností nižšie musí byť prijatá **pred** prvým použitím Ponúk na reálnom e-maile:
   - **A.** Zákazníci, položky a ceny smú byť v EOS Zákazky a smú ísť Claudovi. Platí iba pre účty bratov, artifact sa nezdieľa verejným odkazom.
   - **B.** Do Clauda a do EOS Zákazky idú iba dopyty, ktoré Marco pri e-maile výslovne povolí. Ide o obdobu `aiProcessingAllowed` z ADR-0019; prototyp by dostal prepínač pri každom vlákne.
   - **C.** Ponuky z Gmailu sa nepoužívajú. EOS Zákazky ostáva pri sklade, dodávateľoch a asistentovi nad EOS.
3. **Zdroj pravdy (rozhoduje Marco).** Databáza artifactu **nie je** zdroj pravdy pre znalosti EOS (materiály, procesy, stroje, sadzby). Tie zostávajú v JSON v gite podľa ADR-0002 a ADR-0018. Knowledge base v EOS Zákazky je pracovný kontext; hodnoty v nej majú zdroj N/L/P/V a prevezmú sa do EOS až cez schválené kontrakty. Prevádzkové údaje (objednávky, sklad, stav nákupu) môžu mať zdroj pravdy v EOS Zákazky, kým EOS nemá entitu Job a etapu B.
4. **Kópia repozitára** sa obnovuje na požiadanie („aktualizuj EOS“). Nikdy neobsahuje `intake/` okrem README.
5. **Technický rámec prototypu.** Jedna HTML stránka bez frameworku; schopnosti claude.ai: databáza (`db`), používateľ (`user`), Claude (`sample`) a konektor Gmail (`mcp`: iba `search_threads`, `get_thread`, `create_draft`). Odosielanie e-mailov stránka nemá a nedostane bez nového ADR.

## Alternatives Considered

| Možnosť | Posúdenie |
| --- | --- |
| Zrušiť prototyp a všetko robiť v lokálnom UI | Zachová etapy, ale Gmail, práca z prehliadača bez spúšťania Pythonu a asistent nad celým EOS by čakali na etapy D a E. Marco by stratil to, čo už funguje. |
| Presunúť všetko do EOS Zákazky, lokálne UI zrušiť | Kalkulácia, import šablóny a testy sú v lokálnom UI hotové a overené na V949, CP 289 a V795. Prepis do artifactu by ich zopakoval bez testov a mimo gitu. |
| Nechať obe bez rozdelenia | Rýchle, ale dve miesta pre tú istú zákazku a cenu. Presne tento stav popisuje dokument „EOS – čo je zle“ pri Exceli. |

## Consequences

- Marco a Robino vedia, ktorá aplikácia slúži na čo.
- Citlivé údaje majú výslovné pravidlo ešte pred prvým reálnym dopytom.
- Kým nie je Job a etapa B, objednávky a sklad žijú mimo gitu, bez testov a bez histórie verzií.
- `TECH_STACK.md` dostane poznámku, že EOS Zákazky je prototyp mimo etáp, a odkaz na toto ADR.

## Risks

- **Rozchod údajov.** Cena v ponuke sa môže líšiť od kalkulácie v lokálnom UI. Opatrenie: ponuka uvádza, z ktorej kalkulácie je cena; neskôr prenos.
- **Kópia repozitára zastará** a asistent odpovie podľa starého stavu. Opatrenie: záložka a súhrn v knowledge base ukazujú commit a dátum.
- **Návrh Clauda sa vezme ako hotová cena.** Opatrenie: navrhnuté ceny sú označené ako návrh a nesú zdroj z knowledge base; bez záznamu v knowledge base Claude cenu nedoplní.
- **Zdieľanie artifactu.** Ak sa stránka zdieľa verejným odkazom, údaje v databáze uvidí každý prihlásený s odkazom. Opatrenie: zdieľať iba konkrétnym ľuďom.
- **Prototyp bez testov.** Chyby v stránke neodhalí CI. Opatrenie: kritické výpočty (kalkulácia) ostávajú v lokálnom UI s testami.

## Related Documents

- `adr/ADR-0019_Keep_real_job_intake_outside_git.md`
- `adr/ADR-0021_Local_UI_v0_and_working_calculation.md`, `adr/ADR-0022_Job_entry_in_UI_and_status_board.md`
- `adr/ADR-0018_Define_target_technology_stack.md`, `TECH_STACK.md`
- `adr/ADR-0024_Supplier_price_search_with_Claude_API.md`
- `docs/handoff/2026-11-04_otazky.md` (otázka 8)
- EOS Zákazky: https://claude.ai/artifact/Tk9ZVjT5vWPkV5JNxFz1Xg (prístup iba pre pozvaných)

## Review Date

Pri návrhu entity Job, pri prechode do etapy B alebo 2027-01-31, podľa toho, čo nastane skôr.
