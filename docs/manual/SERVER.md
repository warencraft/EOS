# EOS na serveri – návod

EOS UI beží na serveri pod používateľom `eos` a otvoríte ho súkromne cez Tailscale ([ADR-0025](../../adr/ADR-0025_Quotes_orders_and_Gmail_in_EOS_UI_on_server.md)). Verejne na internete nie je.

## 1. Balíky a Tailscale (ako root)

```bash
apt update
apt install -y git python3-venv curl
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up
```

`tailscale up` vypíše odkaz. Otvor ho v prehliadači a prihlás sa do Tailscale účtu, ktorý budete používať obaja. V [admin konzole Tailscale](https://login.tailscale.com/admin/dns) zapni **MagicDNS** a **HTTPS Certificates**.

Názov servera v Tailnete zistíš príkazom:

```bash
tailscale status --json | python3 -c "import json,sys; print(json.load(sys.stdin)['Self']['DNSName'].rstrip('.'))"
```

Vypíše plný názov, napr. `vps.tail1234.ts.net`.

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

Nahraď `vps.tail1234.ts.net` názvom z kroku 1.

```bash
cat > /etc/systemd/system/eos-ui.service <<'UNIT'
[Unit]
Description=EOS UI
After=network-online.target

[Service]
User=eos
WorkingDirectory=/home/eos/eos
Environment=EOS_ALLOWED_HOSTS=vps.tail1234.ts.net
ExecStart=/home/eos/eos/.venv/bin/python -m scripts.web --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now eos-ui
systemctl status eos-ui --no-pager
```

## 4. Sprístupnenie v Tailnete (ako root)

```bash
tailscale serve --bg 8000
tailscale serve status
```

EOS potom otvoríš na `https://vps.tail1234.ts.net` z počítača alebo mobilu, na ktorom beží Tailscale s tým istým účtom. Brat si nainštaluje aplikáciu Tailscale a prihlási sa do rovnakého Tailnetu (pozvánka v admin konzole → Users → Invite).

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

```bash
mkdir -p /home/eos/zalohy && chown eos: /home/eos/zalohy
echo '15 2 * * * eos tar -czf /home/eos/zalohy/intake-$(date +\%F).tar.gz -C /home/eos/eos intake && find /home/eos/zalohy -name "intake-*.tar.gz" -mtime +30 -delete' > /etc/cron.d/eos-zaloha
```

Záloha je na tom istom serveri. Kópiu mimo servera rob pravidelne (napr. `scp` na vlastný počítač); obsahuje dôverné údaje zákaziek.

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
EOS_CLAUDE_MODEL=MODEL_Z_CLAUDE_CONSOLE
```

V drop-in použi formát `Environment="NÁZOV=hodnota"` v sekcii `[Service]`.
Nahraď príkladové adresy skutočnými loginmi. Do `EOS_MAIL_SENDERS` zahrň iba osoby,
ktoré majú odosielať zo spoločnej Gmail schránky. Prázdny zoznam funkciu vypína.

Pre chat nainštaluj existujúce voliteľné závislosti `.[ui,ai]` a nastav
`LoadCredential=anthropic_key:/cesta/k/suboru-s-api-klucom` v sekcii `[Service]`.
Súbor kľúča ulož mimo gitu, s prístupom pre správcu servera. Alternatívou je
`ANTHROPIC_API_KEY` v chránenom environment súbore. Vyber model dostupný vo svojom API
workspace a nastav v ňom rozpočet. EOS číta model z `EOS_CLAUDE_MODEL`.
Po zmene systemd konfigurácie použi `sudo systemctl daemon-reload` a
`sudo systemctl restart eos-ui`.

Z účtu povoleného v Tailscale otvor skúšobnú ponuku so svojou testovacou adresou,
v náhľade skontroluj konkrétnu správu a potvrď odoslanie. Na VPS musí byť dostupný
odchádzajúci TCP port 465 na `smtp.gmail.com`. Over aj otvorenie vlastného rozhovoru
na oboch povolených účtoch. História sa ukladá do `intake/_eos/chat/`.
Ak služba počas odoslania spadne, v `intake/_eos/prevadzka/mail-attempts/` ostane
záznam pokusu. Pred opakovaním over v Gmaile, či prijal správu s daným Message-ID.

Ak bol proces násilne ukončený počas odpovede, po zastavení služby môže správca
odstrániť prázdny adresár `.request` v priečinku príslušného používateľa chatu.

### Pracovný chat a osobný Gmail

Claude je vpravo v celom EOS. Na mobile otvára panel tlačidlo **Claude**.
Použi rovnaký Tailscale účet na mobile aj na počítači, aby mal EOS prístup k tým
istým uloženým rozhovorom. Návrh z panelu ide do **Stav → Pre Robina** až po
odoslaní formulára. Text rozhovoru sa na nástenku automaticky neprikladá.

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
