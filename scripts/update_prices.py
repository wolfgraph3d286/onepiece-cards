"""Download One Piece TCG card prices from optcgapi.com and write data/prices.json.

Runs daily on GitHub Actions (see .github/workflows/update-prices.yml),
or by hand:  python scripts/update_prices.py
Uses only the Python standard library.
"""
import json
import pathlib
import time
import urllib.request
from datetime import date

API = "https://optcgapi.com/api/"
ENDPOINTS = ["allSetCards/", "allSTCards/"]
UA = "OnePieceCollection/1.0"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "prices.json"


def fetch(path):
    req = urllib.request.Request(API + path, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    rows = []
    for ep in ENDPOINTS:
        for c in fetch(ep):
            name = c.get("card_name") or ""
            rows.append({
                "k": f'{c.get("card_image_id")}~{c.get("set_id")}|{name}',
                "c": c.get("card_set_id"),
                "n": name,
                "s": c.get("set_name"),
                "r": c.get("rarity"),
                "p": c.get("market_price"),
                "d": c.get("date_scraped"),
                "i": c.get("card_image"),
            })
        time.sleep(1)
    if len(rows) < 1000:
        raise SystemExit(f"Only {len(rows)} cards came back; keeping the old file.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = {"updated": date.today().isoformat(), "source": "optcgapi.com", "cards": rows}
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(rows)} cards to {OUT}")


if __name__ == "__main__":
    main()
