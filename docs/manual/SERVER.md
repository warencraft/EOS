# EOS na serveri – návod

EOS UI beží na serveri pod používateľom `eos` a otvoríte ho súkromne cez Tailscale ([ADR-0025](../../adr/ADR-0025_Quotes_orders_and_Gmail_in_EOS_UI_on_server.md)). Verejne na internete nie je.

> **Dôležité.** Väčšina stránok EOS (zákazky, výkresy, ponuky, Gmail koncepty, nástenka) nemá vlastné prihlásenie. Kto sa dostane do vášho Tailnetu, vidí ich. Chat a odosielanie e-mailov kontrolujú identitu z Tailscale (ADR-0026). Preto platí:
>
> 1. **každý má vlastný Tailscale účet** (nie jeden spoločný),
> 2. v Tailnete sú iba vaše zariadenia a pravidlá prístupu pustia k serveru iba port 443 (krok 4),
> 3. na verejnej IP servera nie je otvorený žiaden TCP port, ani SSH (krok 1a).
>
> Podrobné zdôvodnenie: [`docs/handoff/2026-11-18_server-bezpecnost.md`](../handoff/2026-11-18_server-bezpecnost.md).

## 1. Balíky a Tailscale (ako root)

```bash
apt update
apt install -y git python3-venv curl
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up
```

`tailscale up` vypíše odkaz. Otvor ho v prehliadači a prihlás sa **svojím** Tailscale účtom (správca Tailnetu). Brat sa neprihlasuje rovnakým účtom: pozveš ho ako samostatného používateľa (krok 4). Inak by EOS nerozlíšil, kto píše do chatu alebo kto odosiela e-mail. V [admin konzole Tailscale](https://login.tailscale.com/admin/dns) zapni **MagicDNS** a **HTTPS Certificates**.

Názov servera v Tailnete zistíš príkazom:

```bash
tailscale status --json | python3 -c "import json,sys; print(json.load(sys.stdin)['Self']['DNSName'].rstrip('.'))"
```

Vypíše plný názov, napr. `vps.tail1234.ts.net`.

## 1a. Spevnenie servera (ako root)

Rob to **pred** tým, ako na server prenesieš údaje zákaziek. Postup predpokladá Ubuntu 24.04 alebo Debian 12.

**Účet u poskytovateľa servera:** dvojstupňové overenie (aplikácia alebo bezpečnostný kľúč, nie SMS). Automatické snapshoty vypni alebo nech sú šifrované, lebo snapshot je kópia celého disku vrátane zákaziek. Ak poskytovateľ ponúka cloud firewall, nastav v ňom rovnaké pravidlá ako nižšie.

**Používateľ `eos`** bez práv správcu:

```bash
adduser --disabled-password --gecos "" eos
```

**Automatické bezpečnostné aktualizácie:**

```bash
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

**SSH iba kľúčom.** Najprv over, že sa prihlásiš kľúčom, a až potom vypni heslá:

```bash
cat > /etc/ssh/sshd_config.d/10-eos.conf <<'SSH'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
SSH
sshd -t && systemctl reload ssh
```

Na server sa potom prihlasuj ako svoj bežný používateľ so `sudo`, nie ako `root`.

**Firewall: zvonka nič, SSH iba cez Tailscale.** Skôr než zatvoríš verejný port 22, over z iného počítača v Tailnete, že funguje `ssh <tvoj-uzivatel>@vps.tail1234.ts.net`. Keby sa niečo pokazilo, ostáva webová konzola poskytovateľa.

```bash
apt install -y ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow in on tailscale0 to any port 22 proto tcp
ufw allow 41641/udp          # priame spojenie Tailscale (bez neho ide pomalšie cez relé)
ufw enable
ufw status verbose
```

`tailscale serve` (krok 4) beží vo vnútri Tailscale, preto port 443 vo firewalle otvárať netreba.

**Skúška:** z počítača **mimo** Tailnetu `nmap -Pn <verejná-IP-servera>` nesmie ukázať žiaden otvorený TCP port.

## 2. EOS (ako používateľ eos)

```bash
su - eos
cd ~/eos
git fetch origin
git checkout main && git pull
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[ui,import,ai]'
.venv/bin/python -m unittest discover -s tests
```

Testy majú skončiť `OK`. Ak `python3 -m venv` hlási `ensurepip is not available`, doinštaluj ako root `apt install -y python3-venv` a venv vytvor znova.

## 3. Služba, ktorá beží stále (ako root)

Nahraď `vps.tail1234.ts.net` názvom z kroku 1. Služba beží v obmedzenom režime (sandbox): zapisovať smie iba do `intake/`, na nástenku `status/` a do svojej konfigurácie Gmailu. Zvyšok systému vidí iba na čítanie.

```bash
mkdir -p /home/eos/.config/eos && chown -R eos: /home/eos/.config && chmod 700 /home/eos/.config/eos
mkdir -p /home/eos/eos/intake && chown eos: /home/eos/eos/intake && chmod 700 /home/eos/eos/intake
cat > /etc/systemd/system/eos-ui.service <<'UNIT'
[Unit]
Description=EOS UI
After=network-online.target tailscaled.service

[Service]
User=eos
Group=eos
WorkingDirectory=/home/eos/eos
Environment=EOS_ALLOWED_HOSTS=vps.tail1234.ts.net
Environment=PYTHONDONTWRITEBYTECODE=1
ExecStart=/home/eos/eos/.venv/bin/python -m scripts.web --port 8000
Restart=on-failure
UMask=0077

# sandbox
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/home/eos/eos/intake /home/eos/eos/status /home/eos/.config/eos
PrivateTmp=yes
PrivateDevices=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectKernelLogs=yes
ProtectControlGroups=yes
ProtectClock=yes
ProtectHostname=yes
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
RestrictNamespaces=yes
RestrictSUIDSGID=yes
LockPersonality=yes
SystemCallArchitectures=native
CapabilityBoundingSet=
MemoryMax=1G

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now eos-ui
systemctl status eos-ui --no-pager
systemd-analyze security eos-ui --no-pager | tail -1
```

Posledný riadok má ukázať hodnotenie `OK` alebo lepšie. Ak služba po zmene nenaštartuje, `journalctl -u eos-ui -n 50` ukáže, kam chcela zapisovať. Cestu doplň do `ReadWritePaths`, neruš celý sandbox.

## 4. Sprístupnenie v Tailnete (ako root)

```bash
tailscale serve --bg 8000
tailscale serve status
```

**Nikdy `tailscale funnel`.** Funnel by EOS zverejnil na internete pre každého, kto pozná adresu.

EOS potom otvoríš na `https://vps.tail1234.ts.net` z počítača alebo mobilu, na ktorom beží Tailscale s tvojím účtom. Brata pozvi ako samostatného používateľa (admin konzola → Users → Invite). Prihlási sa **svojím** Google alebo iným účtom a nainštaluje si aplikáciu Tailscale.

**Pravidlá prístupu** (admin konzola → Access controls). Server označ tagom `tag:eos` (Machines → server → Edit ACL tags) a pravidlá nastav tak, aby brat smel iba na port 443 servera a ty aj na SSH:

```json
{
  "tagOwners": {"tag:eos": ["tvoj-login@example.org"]},
  "grants": [
    {"src": ["brat-login@example.org"], "dst": ["tag:eos"], "ip": ["tcp:443"]},
    {"src": ["tvoj-login@example.org"], "dst": ["tag:eos"], "ip": ["tcp:443", "tcp:22"]}
  ]
}
```

Loginy nahraď skutočnými. Rovnaké loginy patria do `EOS_CHAT_USERS` a `EOS_MAIL_SENDERS` (časť „Odoslanie ponúk a Claude rozhovory“). V nastaveniach zapni **Device approval**, aby sa nové zariadenie nepridalo bez tvojho súhlasu. Pre server vypni **Key expiry**, pre notebooky a mobily ho nechaj zapnutý.

**Skúška:** z mobilu bez Tailscale sa adresa nenačíta. Z bratovho zariadenia sa EOS načíta, ale `ssh` na server nie.

## 5. Gmail

V EOS otvor **Ponuky → Pripojiť Gmail**, zadaj e-mail a heslo aplikácie. Postup, ako ho získať, je priamo na stránke. Pripojenie robí vlastník Gmailu sám. Heslo sa uloží iba na serveri v `/home/eos/.config/eos/gmail.json`.

## 6. Prenos údajov z EOS Zákazky (claude.ai)

Súbor exportu skopíruj na server (napr. cez `scp` v Tailnete) a naimportuj:

```bash
su - eos
cd ~/eos
.venv/bin/python -m scripts.prevadzka import ~/eos-zakazky-export.json
```

Opakovaný import existujúce záznamy nemení; `--prepisat` ich prepíše.

## 7. Aktualizácia

```bash
su - eos -c 'cd ~/eos && git pull && .venv/bin/python -m pip install -e ".[ui,import,ai]"'
systemctl restart eos-ui
```

## 8. Záloha (ako root, raz denne)

Záloha obsahuje dôverné údaje zákaziek a rozhovory s Claudom. Preto je **šifrovaná** a uložená **mimo** poskytovateľa servera. Kópia na tom istom serveri nepomôže, keď server zmizne.

Postup s nástrojom `restic` (balík systému, nie závislosť EOS). Cieľ `RESTIC_REPOSITORY` je úložisko mimo servera, napr. `sftp:zaloha@iny-pocitac:/eos` alebo S3 bucket u iného poskytovateľa.

```bash
apt install -y restic
install -d -m 700 /root/.eos-zaloha
cat > /root/.eos-zaloha/env <<'ENV'
RESTIC_REPOSITORY=sftp:zaloha@iny-pocitac:/eos
RESTIC_PASSWORD_FILE=/root/.eos-zaloha/heslo
ENV
openssl rand -base64 32 > /root/.eos-zaloha/heslo
chmod 600 /root/.eos-zaloha/env /root/.eos-zaloha/heslo
set -a; . /root/.eos-zaloha/env; set +a; restic init
echo '15 2 * * * root set -a; . /root/.eos-zaloha/env; set +a; restic backup -q /home/eos/eos/intake /home/eos/.config/eos && restic forget -q --keep-daily 14 --keep-monthly 6 --prune' > /etc/cron.d/eos-zaloha
```

**Heslo zálohy** (`/root/.eos-zaloha/heslo`) si hneď ulož aj do svojho správcu hesiel. Bez neho sa záloha nedá obnoviť.

Ak si predtým používal zálohu cez `tar` do `/home/eos/zalohy`, staré nešifrované súbory po prvej úspešnej záloze `restic` zmaž (`rm -r /home/eos/zalohy`). Pre cieľ `sftp:` potrebuje `root` SSH kľúč k cieľovému počítaču.

**Raz za mesiac skúšobná obnova** do dočasného priečinka: `restic restore latest --target /tmp/skuska-obnovy` a kontrola, že sa súbory dajú otvoriť. Potom `/tmp/skuska-obnovy` zmaž.

## Riešenie problémov

| Príznak | Príčina a riešenie |
| --- | --- |
| „Požiadavka z inej stránky bola odmietnutá“ | `EOS_ALLOWED_HOSTS` v službe nesedí s adresou v prehliadači. Oprav a `systemctl restart eos-ui`. |
| Stránka sa neotvorí | `systemctl status eos-ui`, `journalctl -u eos-ui -n 50`, `tailscale serve status`. |
| Gmail: prihlásenie zlyhalo | Heslo aplikácie (nie heslo účtu), zapnuté dvojstupňové overenie a IMAP v nastaveniach Gmailu. |

## Odoslanie ponúk a Claude rozhovory

Funkcie podľa ADR-0026 sa zapínajú až nastavením služieb a zoznamov e-mailov. Použi
prihlasovacie adresy, ktoré Tailscale Serve posiela v `Tailscale-User-Login`.
Z backendu nechaj prístup iba cez `127.0.0.1`, pred EOS musí byť priamo
súkromný Tailscale Serve. Pri štarte cez `python -m scripts.web` je spracovanie
forwarded hlavičiek v Uvicorne vypnuté. Pri vlastnom štartovacom príkaze nastav
`--no-proxy-headers`.

Do existujúceho environment súboru služby alebo systemd drop-in doplň:

```ini
EOS_SERVE_ORIGIN=https://vps.example-tailnet.ts.net
EOS_MAIL_SENDERS=majitel@example.org,brat@example.org
EOS_CHAT_USERS=majitel@example.org,brat@example.org
EOS_NASTENKA_AUTORI=majitel@example.org:robino,brat@example.org:marco
EOS_CLAUDE_MODEL=MODEL_Z_CLAUDE_CONSOLE
```

V drop-in použi formát `Environment="NÁZOV=hodnota"` v sekcii `[Service]`.
Nahraď príkladové adresy skutočnými loginmi. Do `EOS_MAIL_SENDERS` zahrň iba osoby,
ktoré majú odosielať zo spoločnej Gmail schránky. Prázdny zoznam funkciu vypína.

Pre chat nainštaluj existujúce voliteľné závislosti `.[ui,ai]`. Firemný API kľúč
ulož **zašifrovaný** cez `systemd-creds` (systemd 250 a novší, Ubuntu 24.04 aj Debian 12 ho majú).
Kľúč zadáš z klávesnice, takže neostane v histórii príkazov ani v čitateľnom súbore:

```bash
mkdir -p /etc/credstore.encrypted
systemd-ask-password -n "Claude API kľúč:" | systemd-creds encrypt --name=anthropic_key - /etc/credstore.encrypted/anthropic_key
```

A v sekcii `[Service]` služby (drop-in) doplň `LoadCredentialEncrypted=anthropic_key`. EOS si kľúč
prečíta z `$CREDENTIALS_DIRECTORY/anthropic_key`. Nepoužívaj `ANTHROPIC_API_KEY` v environment súbore:
premenné prostredia vidí každý proces služby a ľahko sa dostanú do logu.

V Claude Console daj kľúču **samostatný workspace** (napr. `EOS`) s **mesačným limitom výdavkov**
a upozornením pri polovici limitu. EOS zatiaľ nemá vlastný limit na používateľa, takže limit vo workspace
je jediná poistka proti nečakanému účtu. Vyber model dostupný v tomto workspace. EOS ho číta
z `EOS_CLAUDE_MODEL`. Pri podozrení na únik kľúč v Console zmaž, vytvor nový, zopakuj
`systemd-creds encrypt` a `systemctl restart eos-ui`.

**Heslo aplikácie Gmailu** (`/home/eos/.config/eos/`) dáva plný prístup k schránke vrátane odosielania.
Je to najcitlivejší údaj na serveri. Leží na disku v čitateľnej podobe s právami 0600. Chráni ho
iba samostatný používateľ `eos`, sandbox služby a SSH iba cez Tailscale. Pri podozrení na prevzatie servera
heslo hneď zruš v Google účte (Zabezpečenie → Heslá aplikácií).
Po zmene systemd konfigurácie použi `sudo systemctl daemon-reload` a
`sudo systemctl restart eos-ui`.

Z účtu povoleného v Tailscale otvor skúšobnú ponuku so svojou testovacou adresou,
v náhľade skontroluj konkrétnu správu a potvrď odoslanie. Na VPS musí byť dostupný
odchádzajúci TCP port 465 na `smtp.gmail.com`. Over aj otvorenie vlastného rozhovoru
na oboch povolených účtoch. História sa ukladá do `intake/_eos/chat/`.
Ak služba počas odoslania spadne, v `intake/_eos/prevadzka/mail-attempts/` ostane
záznam pokusu. Pred opakovaním over v Gmaile, či prijal správu s daným Message-ID.

Ak bol proces násilne ukončený počas odpovede, ostane v priečinku používateľa chatu
zámok `.request`. EOS ho po 5 minútach považuje za opustený a pri ďalšej správe ho nahradí.
Ručne ho mazať netreba.

### Pracovný chat a osobný Gmail

Claude je vpravo v celom EOS. Na mobile otvára panel tlačidlo **Claude**.
Použi rovnaký Tailscale účet na mobile aj na počítači, aby mal EOS prístup k tým
istým uloženým rozhovorom. Návrh z panelu ide do **Stav → Pre Robina** až po
odoslaní formulára. Text rozhovoru sa na nástenku automaticky neprikladá.
Autor návrhu sa určí podľa `EOS_NASTENKA_AUTORI` (Tailscale login → `marco` alebo `robino`).
Účet, ktorý v zozname nie je, návrh neodošle a dostane chybu 403.

Na osobné schránky nastav `EOS_GMAIL_USERS` na povolené Tailscale účty. Každý si
potom v **Ponuky → Gmail** pripojí svoju schránku. Zdieľaná konfigurácia sa v tomto
režime nepoužíva. Pripojenia sa ukladajú vedľa nej do podpriečinka `accounts/`.
Pre režim iba s konceptmi nastav `EOS_MAIL_SENDERS=`. Existujúce ponuky z Gmailu
bez záznamu o zdrojovej schránke ostanú prístupné, ale ich pôvodné vlákno sa
v osobnom režime nepripojí automaticky. Nové importy si príslušnosť pamätajú.

Claude v EOS dokáže pripraviť aj návrh dodávateľa. Skús napríklad
„Pridaj dodávateľa Ukážkové náradie, kategória Nástroje, dodáva meradlá“.
V chate otvor **Skontrolovať dodávateľa** a vo formulári potvrď **Uložiť**.
Návrh je viditeľný iba v tvojom rozhovore. Uložený dodávateľ je v spoločnom zozname EOS.

V **Zákazky → Nová zákazka** môže inžinier načítať objednávky zo svojej
pripojenej schránky. Vyberie vlákno, skontroluje predvyplnené údaje a založí
zákazku. EOS preberá predmet a odosielateľa a vyplní ďalšie hodnoty, ak ich
správa uvádza na označených riadkoch. Potvrdené údaje aj pôvodný text uloží
do súboru v podkladoch zákazky. Prílohy z e-mailu ukáže podľa názvu, výkresy
sa nahrávajú ručne. Rovnaká schránka a vlákno smerujú na už založenú zákazku.
Načítanie prebieha na výslovný pokyn v rozhraní.
