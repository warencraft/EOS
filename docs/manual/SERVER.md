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
