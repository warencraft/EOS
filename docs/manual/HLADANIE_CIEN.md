# Vyhľadanie cien u dodávateľov – návod

Nástroj nájde k položkám materiálu ceny na weboch dodávateľov a vráti **návrh** s odkazom, citátom zo stránky a časom zistenia. Pravidlá sú v [ADR-0024](../../adr/ADR-0024_Supplier_price_search_with_Claude_API.md).

## Príprava (raz)

```bash
cd ~/eos
.venv/bin/python -m pip install -e '.[ai]'
export ANTHROPIC_API_KEY=...        # kľúč z platform.claude.com, nikdy do gitu
```

Kľúč si môžeš dať do `~/.bashrc` alebo do súboru mimo repozitára. Volania API sa platia podľa tokenov a počtu vyhľadaní.

## Vstup

JSON podľa `scripts/ai/cenovy_dopyt.schema.json`. Vzor je v `scripts/ai/priklad_vstup.json`:

```json
{
  "formatVersion": "0.1.0",
  "items": [
    {"id": "P1", "text": "popis položky ako v dopyte dodávateľovi", "quantity": 4, "unit": "ks"}
  ],
  "suppliers": [
    {"id": "dodavatel-a", "name": "Názov dodávateľa", "domain": "eshop.dodavatel.sk"}
  ]
}
```

- `domain` je holá doména bez `https://`. Claude smie hľadať a čítať **iba** na týchto doménach.
- Do vstupu nepatrí zákazník, číslo zákazky ani výkresy; schéma ich odmietne.
- Vstup sa dá pripraviť aj v aplikácii EOS Zákazky: Dodávatelia → Nájsť dodávateľov → **Vstup pre hľadanie cien** (skopíruj JSON do súboru).

## Spustenie

```bash
.venv/bin/python -m scripts.ai.hladanie_cien vstup.json -o navrh.json
```

Voľby: `--model` (predvolene `claude-sonnet-5-5`, alebo premenná `EOS_AI_MODEL`), `--max-searches` a `--max-fetches` (predvolene 10 na jednu požiadavku).

## Výstup

`navrh.json` podľa `scripts/ai/cenovy_navrh.schema.json`. Pri každej položke a dodávateľovi:

| Pole | Význam |
| --- | --- |
| `priceStatus` | `verejna` (cena so stránky), `na_dopyt` (produkt sedí, cena nie je verejná), `nenajdene` |
| `url`, `productName`, `quote` | odkaz na produkt a krátky citát zo stránky na overenie |
| `price`, `currency`, `priceUnit`, `vatIncluded` | cena iba pri `verejna`; DPH iba ak to stránka uvádza |
| `retrievedAt` | kedy sa cena zistila |
| `notes` | čo nástroj vyradil alebo zmenil (napr. odkaz mimo webu dodávateľa) |

## Čo platí

- Všetko je **návrh**. Pred použitím v ponuke otvor odkaz a over produkt (rozmer, materiál, norma) a cenu.
- Ceny za prihlásením alebo „na dopyt“ nástroj nezistí; pošli dopyt.
- Cena z webu nie je znalosť EOS. Ako ju zaradiť (N/L/P/V), rozhoduje Marco.
