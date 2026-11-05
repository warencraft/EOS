---
name: eos-git-publish
description: Uloží hotovú prácu do gitu a pošle ju na GitHub ako pull request (vetva, commit, push, PR). Použi, keď používateľ povie „ulož to“, „commitni“, „pushni“, „pošli to na GitHub“, „sprav PR/MR“ alebo keď je fáza hotová a otestovaná.
---

# Uloženie a odoslanie zmien (commit → push → pull request)

Používateľ nie je programátor a git nepozná. Všetky kroky urobíš za neho. Vysvetľuj ich jednoduchou slovenčinou, bez git žargónu, a pred odoslaním si vypýtaj jedno jasné potvrdenie.

Repozitár: `https://github.com/warencraft/EOS`, hlavná vetva `main`.
Pozn.: na GitHube sa „merge request“ (MR) volá **pull request** (PR). Ide o to isté.

## Pravidlá, ktoré sa nikdy neporušujú

- **Nikdy necommituj priamo do `main`.** Vždy pracuj vo vetve.
- **Nikdy** nepoužívaj `git push --force`, `git reset --hard`, `git rebase` na zdieľané vetvy, `git clean` ani mazanie vetiev bez výslovného súhlasu.
- **Nikdy** necommituj `.venv/`, `.env`, `exports/` (okrem README), heslá, tokeny ani reálne citlivé dáta (ceny, zákazníci).
- **Nikdy** nezlučuj (merge) PR sám. Merge robí používateľ na GitHube, prípadne na jeho výslovný pokyn.
- Ak niečo nečakane zlyhá (konflikt, odmietnutý push, chyba prihlásenia), **zastav sa a vysvetli**. Neopravuj to „silou“.

## Postup

### 1. Zisti stav

```bash
git status --short
git branch --show-current
git remote -v
git fetch origin
```

Ak priečinok nie je git repozitár alebo chýba `origin`, zastav sa a povedz to.

### 2. Vetva

Ak si na `main`, vytvor novú vetvu **ešte pred commitom** (necommitnuté zmeny sa prenesú):

```bash
git switch -c <typ>/<krátky-popis>
```

| Typ | Kedy | Príklad |
| --- | --- | --- |
| `feature/` | nová entita, schéma, funkcia | `feature/0.2c4-machine` |
| `review/` | CDR, RFC, posudok | `review/0.2c4-machine-closure` |
| `fix/` | oprava chyby alebo nálezu | `fix/0.2c3-close-1` |
| `docs/` | iba dokumentácia | `docs/index-update` |
| `tools/` | skripty, CI, tooling | `tools/export-viewer` |

Názov: malé písmená, bez diakritiky a medzier, slová spoj pomlčkou.

Ak už si vo vetve, ktorá patrí k tejto práci, zostaň v nej.

### 3. Kontroly pred uložením

1. Spusti skill `eos-run-tests`. Ak testy neprejdú, **necommituj**. Povedz používateľovi, čo zlyhalo.
2. Prejdi skill `eos-governance-check`.
3. Pozri, čo sa mení: `git status --short` a `git diff --stat`. Over, že tam nie sú súbory, ktoré tam nepatria (pozri pravidlá vyššie).

### 4. Potvrdenie od používateľa

Napíš krátke zhrnutie po slovensky, napríklad:

> Pripravil som na odoslanie:
> - nová schéma Stroj (`schemas/entities/machine.schema.json`),
> - 25 nových testov, všetkých 315 prechádza,
> - aktualizovaný ROADMAP, BACKLOG a CHANGELOG.
>
> Uložím to do vetvy `feature/0.2c4-machine` a vytvorím na GitHube žiadosť o zlúčenie (pull request). Môžem?

Pokračuj až po súhlase.

### 5. Commit

```bash
git add <konkrétne súbory alebo priečinky>
git commit -F <dočasný súbor so správou>
```

Ak sú všetky zmeny v `git status` v poriadku, môžeš použiť `git add -A`.

Formát správy (po slovensky, prvý riadok najviac ~72 znakov):

```
[<fáza>] <Čo sa urobilo>

- <hlavná zmena 1>
- <hlavná zmena 2>
- Testy: <N> passed, 0 failures/errors/skipped

Ref: <CDR-xxxx / ADR-xxxx, ak existuje>
```

Príklad: `[0.2C.4] Machine v1: schéma, fixtúry a testy`

Ak práca nepatrí k fáze, použi typ: `[docs]`, `[tools]`, `[fix]`.

Ak commit zlyhá, pretože git nepozná meno alebo e-mail, zastav sa a požiadaj používateľa o jednorazové nastavenie (pozri `docs/manual/GIT_TAHAK.md`, časť „Prvé nastavenie“).

### 6. Push

```bash
git push -u origin <vetva>
```

- **Chyba prihlásenia** (`Authentication failed`, `403`, `could not read Username`): zastav sa. Povedz používateľovi, aby spustil `gh auth login` (návod v `docs/manual/GIT_TAHAK.md`).
- **Odmietnutý push** (`rejected`, `non-fast-forward`): na GitHube je novšia verzia vetvy. Zastav sa a vysvetli to. Nič neprepisuj.

### 7. Pull request

Ak je k dispozícii GitHub CLI (`gh --version`):

```bash
gh pr create --base main --head <vetva> --title "<prvý riadok commitu>" --body-file <dočasný súbor>
```

Telo PR (po slovensky):

```markdown
## Čo sa mení
- …

## Prečo
Fáza <fáza> podľa <CDR-xxxx / zadania>.

## Testy
<N> passed, 0 failures/errors/skipped (Python <verzia>, jsonschema <verzia>)

## Kontrola EOS
- [x] bez reálnych technických hodnôt
- [x] zdrojová klasifikácia
- [x] ROADMAP / BACKLOG / CHANGELOG / docs/INDEX.md aktualizované
- [ ] potrebné ADR: <áno – ADR-xxxx / nie>

## Čo nie je súčasťou
- <odložené veci podľa CDR>
```

Ak `gh` nie je nainštalované, daj používateľovi tento odkaz. PR otvorí na GitHube jedným klikom:

```
https://github.com/warencraft/EOS/compare/main...<vetva>?expand=1
```

### 8. Záver pre používateľa

Povedz jednoducho:

> Hotovo. Zmeny sú na GitHube ako pull request: <odkaz>.
> Pozri si ich tam (záložka „Files changed“). Keď súhlasíš, klikni na zelené tlačidlo **Merge pull request**. Potom mi napíš a ja si stiahnem aktuálny stav.

### 9. Po zlúčení (keď to používateľ potvrdí)

```bash
git switch main
git pull origin main
git branch -d <vetva>
```

`-d` (malé d) zmaže iba lokálnu vetvu, ktorá už je zlúčená. Ak git odmietne, vetva zlúčená nie je, takže ju nemaž.
