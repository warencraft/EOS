# Git ťahák pre EOS

Krátky návod, ako dostať zmeny na GitHub. Najjednoduchšie je povedať AI agentovi **„ulož to a pošli na GitHub“**. Postup za teba urobí skill `eos-git-publish`. Tento ťahák je pre prípad, keď to chceš urobiť sám alebo pochopiť, čo agent robí.

## Ako to funguje (v skratke)

- **`main`** je hlavná, „čistá“ verzia projektu.
- **Vetva (branch)** je tvoja pracovná kópia na jednu úlohu. Nič nepokazíš, `main` zostane bez zmeny.
- **Commit** je uložená verzia s popisom, čo sa zmenilo.
- **Push** pošle tvoje commity na GitHub.
- **Pull request (PR)** je žiadosť „zlúč moju vetvu do `main`“. Na GitHube vidíš všetky zmeny a jedným tlačidlom ich zlúčiš. (V GitLabe sa to volá merge request, MR.)

```
main ──●────────────────●── (po zlúčení)
        \              /
vetva    ●──●──●──────●   ← tu pracuješ, potom pull request
```

## Prvé nastavenie (iba raz na počítači)

**Windows (PowerShell):**

```powershell
winget install --id Git.Git -e
winget install --id GitHub.cli -e
git config --global user.name "Tvoje Meno"
git config --global user.email "tvoj@email.sk"
gh auth login
```

**macOS:**

```bash
brew install git gh
git config --global user.name "Tvoje Meno"
git config --global user.email "tvoj@email.sk"
gh auth login
```

Pri `gh auth login` vyber: **GitHub.com → HTTPS → Yes → Login with a web browser**. Skopíruj kód, potvrď ho v prehliadači a je hotovo.

## Bežná práca: 5 krokov

V priečinku projektu EOS:

```bash
# 1. aktuálny stav z GitHubu
git switch main
git pull

# 2. nová vetva na úlohu
git switch -c feature/0.2c4-machine

#    ... pracuješ (ty alebo agent) ...

# 3. ulož zmeny
git add -A
git commit -m "[0.2C.4] Machine v1: schéma, fixtúry a testy"

# 4. pošli na GitHub
git push -u origin feature/0.2c4-machine

# 5. vytvor pull request
gh pr create --fill --base main
```

Potom otvor PR na GitHube, pozri si záložku **Files changed** a klikni na **Merge pull request**.

Po zlúčení:

```bash
git switch main
git pull
git branch -d feature/0.2c4-machine
```

## Užitočné príkazy

| Príkaz | Čo urobí |
| --- | --- |
| `git status` | čo je zmenené a v ktorej vetve si |
| `git log --oneline -10` | posledných 10 commitov |
| `git diff` | čo presne sa zmenilo (ešte neuložené) |
| `gh pr list` | otvorené pull requesty |
| `gh pr view --web` | otvorí PR aktuálnej vetvy v prehliadači |

## Keď niečo nejde

| Hlásenie | Čo to znamená | Čo urobiť |
| --- | --- | --- |
| `Please tell me who you are` | git nepozná tvoje meno | spusti dva `git config` príkazy z prvého nastavenia |
| `Authentication failed` / `403` | nie si prihlásený na GitHub | `gh auth login` |
| `rejected … non-fast-forward` | na GitHube je novšia verzia | nič neprepisuj, opýtaj sa agenta alebo brata |
| `CONFLICT` | dve zmeny v tom istom mieste | nič nemaž, opýtaj sa agenta alebo brata |
| `Your local changes would be overwritten` | máš neuložené zmeny | najprv ich commitni do vetvy |

**Nikdy nepoužívaj** `--force`, `reset --hard` ani `clean`, kým presne nevieš, čo robia. Môžu nenávratne zmazať prácu.
