# Bezpečné nastavenie servera EOS pre Claude chat (vzdialený server)

**Pre koho:** Robino (Software Architect)  
**Stav:** Návrh, doplnok k `docs/handoff/2026-11-18_claude-chat-plan.md`  
**Dátum:** 2026-11-18, revízia 1: server je vzdialený (VPS, platí Robino), nie Mac  
**Revízia 2 (2026-11-19):** postup na nasadenie je v [`docs/manual/SERVER.md`](../manual/SERVER.md) (cesty `/home/eos/eos`, služba `eos-ui`). Tento dokument vysvetľuje dôvody. Identitu dáva Tailscale (ADR-0026), nie Google prihlásenie, takže §5 platí až pri prípadnom prechode na Google OIDC. Šifrovaný zväzok LUKS (§4.3) zatiaľ nie je v návode a je to odporúčanie, nie povinnosť.  

---

## 0. Krátka odpoveď

**Áno.** Brat sa cez UI EOS prihlási Googlom a chatuje s Claudom. Server volá Anthropic API jedným firemným kľúčom z Claude Console pre všetkých používateľov a to je povolená cesta.

**Na vzdialenom serveri platíš dve veci:** server (mesačne pevne) a spotrebu Clauda (podľa používania). Proti nečakaným účtom sú dva nezávislé limity: vo workspace v Console a pre každého používateľa v EOS (§2, §7).

**Dve veci treba vyriešiť pred spustením:**
1. **V EOS ešte nie je kód pre prihlásenie a chat** (etapy F1 až F3 z plánu). Dnešné UI nemá prihlásenie, takže **na vzdialenom serveri ho bez F1 nespúšťaj ani na skúšku.** Stačilo by jedno nesprávne nastavenie a všetky zákazky by boli na internete.
2. **Dáta zákaziek opustia tvoj počítač.** ADR-0019 počíta s tým, že `intake/` je na jednom počítači. Presun k poskytovateľovi servera je nové rozhodnutie a patrí do ADR. Súhlasiť musí aj Marco ako vlastník obsahu (§4.1).

## 1. Čo chránime a pred kým

| Čo | Prečo je to cenné | Najhorší prípad |
| --- | --- | --- |
| Podklady a kalkulácie zákaziek (`intake/`) | dôverné údaje zákazníkov, ceny | únik ku konkurencii alebo na internet |
| API kľúč Anthropic | platíš z neho ty | niekto ho zneužije a minie peniaze |
| Prístup na server (SSH, účet u poskytovateľa) | kto ho má, má všetko | prevzatie servera, ťažba kryptomien na tvoj účet |
| Tajné hodnoty EOS (relácia, Google client secret) | kto ich má, vie sa vydávať za používateľa | prihlásenie bez Google účtu |
| História chatov | obsahuje dáta zákaziek | rovnaké ako podklady |

**Pred kým sa bránime:**
1. **Automatické skenery z internetu.** Verejný server nájdu do niekoľkých minút. Riešenie: na verejnej adrese nie je otvorený **žiadny** port (§3).
2. **Niekto s cudzím Google účtom.** Riešenie: zoznam povolených e-mailov v EOS (§5).
3. **Ukradnutý notebook brata.** Riešenie: odobratie zariadenia a zrušenie relácií (§9).
4. **Únik účtu u poskytovateľa servera** (heslo, chýbajúce 2FA). Kto ho má, otvorí konzolu servera alebo stiahne snapshot disku. Riešenie: 2FA, šifrovanie dát, tajomstvá mimo snapshotov (§4).
5. **Text v dokumente, ktorý sa snaží zmanipulovať Clauda.** Riešenie: nástroje iba na čítanie, kontrola pri každom volaní, Claude nemá internet (§7).
6. **Chyba v našom kóde.** Riešenie: všetko je predvolene zakázané a test prejde všetky stránky (§6).

```
 internet ──✖  verejná IP servera: firewall zatvorí všetko, aj SSH
 brat ──┐
 ty ────┴─ Tailscale (iba pozvané zariadenia) ─► VPS "eos"
                                                  │ tailscale serve :443 (HTTPS)
                                                  │ 127.0.0.1:8000  uvicorn, používateľ eos, systemd sandbox
                                                  EOS: Google login + zoznam e-mailov + rola v každej trase
                                                  │ brána AI (aiProcessingAllowed, dôvernosť)
                                                  │ nástroje iba na čítanie
                                                  └─► Anthropic API (kľúč zo systemd credentials, limit € v Console)
                                                  /srv/eos/intake  (šifrovaný zväzok, šifrovaná záloha mimo servera)
```

## 2. Vrstva 1: Claude Console a kľúč

1. **Samostatný workspace „EOS“.** Kľúč patrí k workspacu, v ktorom vznikol, a nedá sa presunúť, takže kľúč pre EOS nemá nič spoločné s inými projektmi.
2. **Mesačný limit vo workspace** a upozornenie hlboko pod ním (napr. pri 50 %). Toto je posledná poistka pre tvoju peňaženku, keby zlyhal limit v EOS.
3. **Jeden kľúč = jedno použitie** (`eos-vps`). Nepoužívaj ho v Claude Code ani v skriptoch na svojom počítači.
4. **Rotácia** každé 3 mesiace a hneď pri podozrení.
5. **Na serveri** je kľúč v systemd credentials (§4.4), nie v repozitári, nie v `/srv/eos`, nie v premennej v unit súbore.
6. **Do prehliadača sa kľúč nikdy nedostane.** Prehliadač posiela otázky iba na EOS.

## 3. Vrstva 2: sieť

### 3.1 Odporúčané: Tailscale, verejná IP úplne zatvorená

1. Na VPS nainštaluj Tailscale a pripoj ho s tagom: `tailscale up --advertise-tags=tag:eos --ssh=false`.
2. **Firewall poskytovateľa** (cloud firewall v jeho paneli) **a** `ufw` na serveri:
   - príchodzie: **všetko zakázané**, výnimka iba UDP 41641 (priame spojenie Tailscale; bez nej to ide pomalšie cez relé, ale ide),
   - odchádzajúce: povolené (aktualizácie, Anthropic, Google, Tailscale).
3. **SSH iba cez Tailscale.** `sshd` počúva iba na Tailscale adrese (`ListenAddress 100.x.y.z`), alebo je port 22 zatvorený vo firewalle a pustený iba z rozhrania `tailscale0` (`ufw allow in on tailscale0 to any port 22`). Na verejnej IP potom **nie je vidieť nič.**
4. EOS počúva iba na `127.0.0.1:8000` a `tailscale serve --bg 8000` ho ponúkne ako `https://eos.<tailnet>.ts.net`. Serve sprístupní službu iba v tailnete, s automatickým HTTPS a bez otvoreného portu.
5. **Nikdy `tailscale funnel`.** S Funnel sa k službe dostane ktokoľvek, kto pozná URL. V politike tailnetu nepridávaj atribút `funnel`.
6. **Pravidlá prístupu (grants):** brat smie iba na `tag:eos` port 443. Ty smieš aj na 22.

```json
{
  "tagOwners": {"tag:eos": ["robert@…"]},
  "grants": [
    {"src": ["brat@gmail.com"], "dst": ["tag:eos"], "ip": ["tcp:443"]},
    {"src": ["robert@…"],       "dst": ["tag:eos"], "ip": ["tcp:443", "tcp:22"]}
  ]
}
```

7. Zapni **device approval**. Pre server **vypni key expiry**, aby nevypadol sám od seba, ale pre notebooky ho nechaj zapnutý.
8. Voliteľne: EOS overí aj hlavičku `Tailscale-User-Login` od Serve proti Google e-mailu v relácii. Hlavičke verí iba vtedy, keď požiadavka prišla z `127.0.0.1`.

**Pre brata to znamená:** raz si nainštaluje aplikáciu Tailscale a prihlási sa. Potom už iba otvorí `https://eos.<tailnet>.ts.net`.

### 3.2 Ak brat Tailscale nechce: verejná adresa (neodporúčam)

Vtedy je **jediný zámok prihlásenie v EOS** a server je na internete pre každého skenera. Ak predsa len:
- vlastná doména, reverse proxy **Caddy** (automatické HTTPS), otvorené iba 80/443,
- pred EOS **Cloudflare Access** alebo **oauth2-proxy** s rovnakým zoznamom e-mailov, aby sa neprihlásený človek nedostal ani k prihlasovacej stránke EOS,
- obmedzenie počtu požiadaviek v Caddy, `fail2ban` na neúspešné prihlásenia,
- SSH stále iba cez Tailscale.

Je to viac práce, viac služieb a väčšie riziko. Tailscale je jednoduchší aj bezpečnejší.

## 4. Vrstva 3: server (VPS)

### 4.1 Výber poskytovateľa a miesto dát

| Požiadavka | Prečo |
| --- | --- |
| dátové centrum v **EÚ** (napr. Nemecko, Fínsko, Holandsko) | GDPR, dáta zákazníkov ostanú v EÚ |
| poskytovateľ podpíše **DPA** (zmluvu o spracúvaní údajov) | bude spracúvať dôverné dáta tvojich zákazníkov |
| **cloud firewall** v paneli | druhý firewall nezávislý od servera |
| **2FA** na účet u poskytovateľa (aplikácia alebo bezpečnostný kľúč, nie SMS) | účet u poskytovateľa = plný prístup k serveru |
| zálohy a snapshoty **vypnuté** alebo šifrované | snapshot je kópia celého disku vrátane dát zákaziek |

**Rozhodnutie pre ADR (Robino + Marco):** dáta `intake/` sa presúvajú z tvojho počítača k poskytovateľovi. Marco by mal vedieť, u koho sú a v akej krajine. Je to amendment k ADR-0019 bod 1 a riziko „podklady iba na jednom počítači“.

### 4.2 Základné spevnenie (Ubuntu 24.04 LTS alebo Debian 12)

| # | Nastavenie | Detail |
| --- | --- | --- |
| S1 | aktualizácie | `unattended-upgrades` so zapnutými bezpečnostnými aktualizáciami a automatickým reštartom v noci |
| S2 | SSH | iba kľúče (`PasswordAuthentication no`), `PermitRootLogin no`, `AllowUsers robert`, počúva iba na Tailscale (§3.1) |
| S3 | tvoj účet | `robert` so `sudo`. Kľúč SSH ideálne na hardvérovom kľúči (YubiKey, `ed25519-sk`) alebo aspoň s heslom. |
| S4 | používateľ aplikácie | `eos`: systémový, bez shellu, bez `sudo`, vlastní iba `/srv/eos` |
| S5 | práva | `/srv/eos` `750 eos:eos`, `/srv/eos/intake` `700` |
| S6 | firewall | `ufw default deny incoming`, výnimky z §3.1. K tomu cloud firewall s tými istými pravidlami. |
| S7 | čas | `systemd-timesyncd` zapnutý (platnosť Google tokenov a relácií závisí od presného času) |
| S8 | nepotrebné služby | nič iné na serveri nebeží: žiadna databáza, panel ani FTP |
| S9 | logy | `journald` s obmedzenou veľkosťou. Prístupový log uvicorn vypnutý, EOS má vlastný audit bez obsahu. |

### 4.3 Šifrovanie dát na disku

Pri VPS má disk v rukách poskytovateľ. Odporúčané riešenie: **samostatný šifrovaný zväzok** iba pre dáta.
- Pripojený blokový zväzok (block volume) s **LUKS**, pripojený na `/srv/eos/intake`.
- Po reštarte servera ho odomkneš ručne cez SSH (`cryptsetup open` + `mount`, potom `systemctl start eos`). Heslo **nie je na serveri**.
- Dôsledok: po reštarte (napr. po aktualizácii jadra) je EOS nedostupný, kým ho neodomkneš. Pri dvoch používateľoch je to prijateľné. Automatický reštart pri aktualizáciách potom nastav iba na čas, keď si dostupný, alebo ho vypni a reštartuj ručne raz týždenne.
- Jednoduchšia možnosť je šifrovanie disku od poskytovateľa, ak ho ponúka. Chráni pred stratou disku, ale **nie** pred poskytovateľom ani pred niekým s prístupom k tvojmu účtu u neho.

### 4.4 Tajomstvá: systemd credentials

Na Linuxe nie je Keychain. Tajomstvá sú šifrované súbory, ktoré systemd odovzdá iba službe EOS:

```bash
# raz, ako root; hodnota sa zadá z klávesnice a nezostane v histórii
systemd-ask-password -n "Anthropic kľúč:" | systemd-creds encrypt --name=anthropic_key - /etc/credstore.encrypted/anthropic_key
# rovnako: session_secret, google_client_secret
```

EOS ich číta z `$CREDENTIALS_DIRECTORY/<meno>`. Súbory sú zašifrované kľúčom viazaným na tento server (a TPM, ak ho VPS má), takže samotný snapshot disku ich neprezradí tak ľahko ako `.env`. Nie sú v `/srv/eos`, teda ani v zálohe dát.

### 4.5 Služba EOS (systemd so sandboxom)

`/etc/systemd/system/eos.service`:

```ini
[Unit]
Description=EOS
After=network-online.target tailscaled.service
RequiresMountsFor=/srv/eos/intake

[Service]
User=eos
Group=eos
WorkingDirectory=/srv/eos/app
ExecStart=/srv/eos/app/.venv/bin/python -m uvicorn scripts.web.app:app \
  --host 127.0.0.1 --port 8000 --proxy-headers --forwarded-allow-ips 127.0.0.1 \
  --no-server-header --no-access-log
Environment=EOS_VEREJNA_ADRESA=https://eos.<tailnet>.ts.net
Environment=EOS_INTAKE=/srv/eos/intake
LoadCredentialEncrypted=anthropic_key
LoadCredentialEncrypted=session_secret
LoadCredentialEncrypted=google_client_secret
Restart=on-failure

# sandbox: služba nevidí nič okrem toho, čo potrebuje
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/srv/eos/intake /srv/eos/app/status
PrivateTmp=yes
PrivateDevices=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
RestrictNamespaces=yes
LockPersonality=yes
MemoryDenyWriteExecute=yes
SystemCallArchitectures=native
CapabilityBoundingSet=
UMask=0077
MemoryMax=1G

[Install]
WantedBy=multi-user.target
```

Kontrola: `systemd-analyze security eos` by mal ukázať hodnotenie „OK“ alebo lepšie. `MemoryDenyWriteExecute` môže pri niektorých knižniciach Pythonu robiť problém. Ak služba nenaštartuje, vypni iba toto jedno.

### 4.6 Nasadenie novej verzie

- Server si kód **stiahne** z GitHubu (deploy key iba na čítanie, iba pre tento repozitár). Ty nekopíruješ súbory ručne.
- `git pull` → `pip install -e .[ui,import,ai]` → celá testovacia sada → `systemctl restart eos`. Keď testy neprejdú, reštart sa neurobí.
- `pip-audit` pred každým nasadením.
- `intake/` na serveri **nie je** v repozitári (ADR-0019 platí aj tu) a `.gitignore` sa nemení.

### 4.7 Zálohy

- `restic` (alebo `borg`) **šifrovane** na úložisko mimo poskytovateľa servera, každú noc, z `/srv/eos/intake`.
- Heslo zálohy máš v správcovi hesiel, nie na serveri v čitateľnej podobe (systemd credential pre zálohovaciu službu).
- **Raz za mesiac skúšobná obnova.** Neoverená záloha nie je záloha.

## 5. Vrstva 4: prihlásenie cez Google

### 5.1 Google Cloud Console

1. Nový projekt `eos-prihlasenie`, OAuth klient typu **Web application**.
2. **Authorized redirect URI** iba jedna, presne `https://eos.<tailnet>.ts.net/auth/callback`. Žiadne `http`, žiadne zástupné znaky, žiadne `localhost` v produkčnom klientovi. Na vývoj vytvor samostatného klienta.
3. Scope iba `openid email profile`.
4. **Pozor, dôležité:** Google zoznam „test users“ **nie je zámok.** Keď aplikácia žiada iba základné scope (openid, email, profile), prihlási sa ktorýkoľvek Google používateľ, aj keď nie je v zozname testerov. **Jediný skutočný zoznam povolených je `pouzivatelia.json` v EOS.** Google iba potvrdí, kto to je. O prístupe rozhoduje EOS.
5. Client secret ulož do tajomstiev servera (`google_client_secret`, §4.4), nie do repozitára.

### 5.2 Čo musí EOS overiť (kód F1)

| Kontrola | Prečo |
| --- | --- |
| tok Authorization Code + **PKCE**, náhodný `state` a `nonce` uložené v relácii | proti podvrhnutiu prihlásenia (login CSRF) a opakovaniu tokenu |
| `id_token`: podpis cez Google JWKS, `iss`, `aud` = náš client ID, `exp`, `nonce` | token je naozaj od Google a pre nás |
| `email_verified == true` | Google overil, že e-mail patrí používateľovi |
| identita = **`sub`** (stále ID od Google), e-mail iba na prvé spárovanie v `pouzivatelia.json` | e-mail sa dá zmeniť, `sub` nie |
| e-mail/`sub` je v `pouzivatelia.json`, inak 403 a záznam do auditu | jediný skutočný zámok |
| najviac 10 pokusov o prihlásenie za 10 minút z jednej adresy | proti skúšaniu |

### 5.3 Relácia (cookie)

- Názov `__Host-eos`. Prefix `__Host-` vynúti `Secure`, `Path=/` a zakáže doménu.
- `HttpOnly`, `Secure`, `SameSite=Lax`.
- Platnosť najviac 12 h, odhlásenie po 2 h nečinnosti.
- V cookie je iba ID relácie a `verziaRelacie`. Zmena roly, odobratie používateľa alebo „Odhlásiť všade“ zvýši verziu a staré cookie prestanú platiť.
- Podpisový kľúč relácie (`eos-session`) je náhodných 32 bajtov z `secrets.token_bytes`. Jeho výmena odhlási všetkých, čo je núdzové tlačidlo v §9.

## 6. Vrstva 5: aplikácia EOS

| # | Nastavenie | Detail |
| --- | --- | --- |
| A1 | **Predvolený zákaz** | middleware pustí bez prihlásenia iba `/prihlasenie`, `/auth/*`, `/static/*`. Všetko ostatné, vrátane `/zakazka/*/subor/*` (náhľady PDF), vyžaduje reláciu. |
| A2 | **Test všetkých trás** | test prejde `app.routes` a overí, že každá trasa bez relácie vráti 401 alebo presmerovanie na prihlásenie. Nová trasa bez ochrany test zhodí. |
| A3 | **Oprávnenie v každej trase** | `smie(pouzivatel, akcia, job_ref)` na serveri. Šablóna iba skrýva tlačidlá. |
| A4 | **CSRF token** vo všetkých formulároch a HTMX požiadavkách (`hx-headers`) | dnešná ochrana `iba_z_tejto_aplikacie` počíta s localhostom. Pri ts.net adrese treba token a povolený `Origin` = `EOS_VEREJNA_ADRESA`. |
| A5 | **Bezpečnostné hlavičky** | `Strict-Transport-Security: max-age=31536000`, `Content-Security-Policy: default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `Permissions-Policy: camera=(), microphone=(), geolocation=()` |
| A6 | **Písma z Google Fonts** | `base.html` dnes načítava `fonts.googleapis.com`. Kvôli prísnej CSP a tomu, aby prehliadač brata nehlásil Googlu každé otvorenie EOS, daj písma do `scripts/web/static/` (sú pod licenciou OFL). |
| A7 | **Limity nahrávania** | max. veľkosť súboru (napr. 50 MB) a počet súborov na požiadavku. Kontrolovať aj typ, nielen príponu. |
| A8 | **Chyby bez detailov** | žiadne tracebacky v odpovedi. `/docs`, `/redoc` a `/openapi.json` už sú vypnuté a tak to ostane. |
| A9 | **Lokálny režim** `--lokalne` (bez prihlásenia) | spustí sa iba keď nie je nastavená `EOS_VEREJNA_ADRESA`. Na serveri (systemd) sa nedá zapnúť. |
| A10 | **Závislosti** | `pip-audit` raz mesačne a pred každým nasadením. Verzie pripnuté v `pyproject.toml`. |

## 7. Vrstva 6: Claude

| # | Pravidlo | Prečo |
| --- | --- | --- |
| C1 | **Brána pri každom volaní nástroja**: používateľ má zákazku povolenú, `aiProcessingAllowed: true`, dôvernosť nie je `restricted` (kým Marco nerozhodne inak) | Claude sa nedostane k zákazke, ku ktorej nemá, ani keď ho o to požiada text v dokumente |
| C2 | **Nástroje iba na čítanie**, žiadny zápis, žiadne mazanie | zmanipulovaný Claude nič nepokazí |
| C3 | **Žiadny internet pre Clauda**: nepoužívať web search, web fetch ani code execution na strane API | dáta sa nedajú poslať von |
| C4 | **Odpoveď ako text**: Jinja autoescape, žiadne HTML, obrázky ani automatické odkazy | dáta sa nedajú vyniesť cez URL obrázka v odpovedi |
| C5 | **Limity na otázku**: najviac 8 volaní nástrojov, `max_tokens`, časový limit 60 s | zacyklenie nemíňa peniaze |
| C6 | **Limit € na používateľa v EOS** + limit workspace v Console | dve nezávislé poistky |
| C7 | **Kľúč nikdy v logu**: knižnice `httpx` a `anthropic` majú log na úrovni `WARNING`, chyby sa pred zápisom čistia od hlavičiek | kľúč neunikne cez log alebo hlásenie chyby |
| C8 | **Systémový prompt**: obsah dokumentov sú dáta, nie pokyny; čísla iba s ID zdroja; odhad = „Návrh“ | menej halucinácií a manipulácie, súlad s EOS-001 §8 |

## 8. Vrstva 7: dáta a záznamy

- **Čo odchádza do Anthropicu:** iba výsledky nástrojov, ktoré pustila brána. Anthropic podľa Commercial Terms netrénuje na vstupoch a výstupoch z API. Bežná retencia je krátka. Ak pôjdu do AI aj výkresy, požiadaj o Zero Data Retention.
- **História chatov:** `/srv/eos/intake/_eos/chat/`, mimo gitu, práva iba pre používateľa `eos`. Zmazanie po dobe, ktorú určíš (návrh: 12 mesiacov).
- **Audit:** `intake/_eos/audit/<rok-mesiac>.jsonl`, záznamy sa iba pridávajú. Zapisujú sa prihlásenia, odmietnutia, otázky, nástroje, odmietnutia bránou, tokeny a €. **Bez textu otázok.**
- **Kontrola raz týždenne** (5 minút v `/admin`): neúspešné prihlásenia, odmietnutia bránou, spotreba.

## 9. Keď sa niečo pokazí (núdzový postup)

| Situácia | Čo urobiť hneď | Potom |
| --- | --- | --- |
| podozrenie na únik API kľúča | v Console kľúč **zmaž**, vytvor nový, `systemd-creds encrypt`, `systemctl restart eos` | skontroluj spotrebu v Console a audit |
| bratovi ukradli notebook | v Tailscale **odober zariadenie**, v EOS „Odhlásiť všade“ pre brata | nové zariadenie znova schváľ |
| podozrenie na cudzie prihlásenie do EOS | vymeň `session_secret` (odhlási všetkých), skontroluj audit | vymeň Google client secret |
| chyba v EOS púšťa bez prihlásenia | `tailscale serve reset` a `systemctl stop eos` | oprava, test všetkých stránok (A2), až potom zapnúť |
| podozrenie na prevzatie servera (neznámy proces, vysoké CPU, neznámy SSH kľúč) | v paneli poskytovateľa **vypni sieť servera** alebo ho vypni; vymeň všetky kľúče (Anthropic, Google, SSH, Tailscale) | server **nečisti, ale postav nanovo** zo zálohy dát a z gitu |
| únik účtu u poskytovateľa | zmena hesla + 2FA, kontrola snapshotov a SSH kľúčov v paneli | ako pri prevzatí servera |
| Claude odpovedal z nepovolenej zákazky | vypni chat (`EOS_AI=off`), nechaj si audit a chat | oprava brány + test, ktorý tento prípad zachytí |

## 10. Kontrolný zoznam pred prvým spustením pre brata

**Rozhodnutia**
- [ ] ADR: dáta zákaziek na VPS (amendment ADR-0019), Marco vie, kde dáta sú
- [ ] DPA s poskytovateľom, dátové centrum v EÚ

**Console**
- [ ] workspace `EOS`, kľúč `eos-vps` iba v ňom, mesačný limit a upozornenie

**Poskytovateľ**
- [ ] 2FA na účet, cloud firewall: dnu iba UDP 41641
- [ ] automatické snapshoty vypnuté alebo šifrované

**Server**
- [ ] `unattended-upgrades`, SSH iba kľúče a iba cez Tailscale, `PermitRootLogin no`
- [ ] `ufw default deny incoming`
- [ ] používateľ `eos` bez shellu, `/srv/eos/intake` na LUKS zväzku, práva `700`
- [ ] tajomstvá v `systemd-creds`, žiadny `.env`
- [ ] `eos.service` so sandboxom, `systemd-analyze security eos` je OK
- [ ] šifrovaná záloha mimo poskytovateľa + skúšobná obnova

**Tailscale**
- [ ] `tailscale serve --bg 8000`, **bez Funnel** a bez atribútu `funnel` v politike
- [ ] grants: brat → `tag:eos` iba `tcp:443`
- [ ] device approval zapnuté, key expiry na serveri vypnuté

**Google**
- [ ] Web klient, jediná redirect URI `https://eos.<tailnet>.ts.net/auth/callback`
- [ ] e-mail brata v `pouzivatelia.json` (Google test users nestačia)

**EOS (kód F1–F3)**
- [ ] predvolený zákaz + test všetkých stránok, CSRF, hlavičky, písma lokálne
- [ ] brána, nástroje iba na čítanie, odpoveď ako text, limity €

**Skúška nanečisto**
- [ ] `nmap` na verejnú IP servera z iného počítača neukáže **žiadny** otvorený TCP port
- [ ] z telefónu mimo tailnetu sa ts.net adresa nenačíta
- [ ] cudzí Google účet v tailnete dostane „Nemáte prístup“
- [ ] brat sa prihlási, vidí iba povolené zákazky, Claude odmietne zákazku bez `aiProcessingAllowed`
- [ ] po reštarte servera EOS nenaštartuje, kým neodomkneš zväzok (ak LUKS)
- [ ] v audite sú všetky pokusy

## 11. Čo neodporúčam

- otvorený port 22 alebo 8000 na verejnej IP, `--host 0.0.0.0`,
- `tailscale funnel` alebo verejná adresa bez ďalšieho zámku pred EOS (§3.2),
- `.env` s kľúčmi v `/srv/eos` alebo v repozitári: dostane sa do záloh a snapshotov,
- spúšťať EOS ako `root` alebo pod tvojím účtom so `sudo`,
- Docker s publikovaným portom (`-p 8000:8000`): obchádza `ufw` a port by bol verejný,
- „vyčistiť“ prevzatý server namiesto postavenia nového,
- spoločný Google účet pre teba aj brata: audit by nevedel, kto čo urobil.

## 12. Čo budeš platiť

| Položka | Ako sa platí | Ako to udržať pod kontrolou |
| --- | --- | --- |
| VPS + blokový zväzok | pevne mesačne | malý server stačí; EOS nepotrebuje GPU ani veľa RAM (1–2 vCPU, 2–4 GB RAM) |
| úložisko záloh | podľa objemu | zálohuje sa iba `intake/` |
| Claude API | podľa tokenov | limit vo workspace + limit € na používateľa v EOS; predvolene lacnejší model |
| Tailscale | bezplatný plán stačí pre pár ľudí a zariadení | – |
| Google prihlásenie | zadarmo | – |

Ceny konkrétnych poskytovateľov a modelov sa menia. Over ich pri výbere, do kódu ani do tohto dokumentu ich nedávame.
