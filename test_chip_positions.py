"""
Testscript: hämtar chip-counts-sidor från PokerNews och försöker hitta
fantasy-spelares individuella placering i rankinglistan.
Ändrar ingenting — bara loggar vad vi hittar.
"""
import requests
import re

FANTASY_PLAYERS = [
    "David Peters", "Josh Arieh", "Viktor Blom", "Ryutaro Suzuki",
    "Matt Glantz", "Eli Elezra", "Mike Matusow", "Ben Lamb",
    "Jason Koon", "Erik Seidel", "Isaac Haxton", "Adam Hendrix",
    "Phil Hellmuth", "Philip Sternheimer", "Andrew Lichtenberger",
    "Sam Soverel", "Alex Foxen", "Jon Turner", "Chris Hunichen",
    "Stephen Chidwick", "Stephen Song", "John Riordan", "Joao Simao Peres",
    "Shaun Deeb", "Kevin Yun Lam Choi", "Anson Tsang", "Jim Collopy",
    "Lawrence Brandt", "Nick Guagenti", "Klemens Roiter",
    "Andrew Ostapchenko", "Brock Wilson", "Joey Weissman"
]

FANTASY_PLAYERS_LOWER = {p.lower(): p for p in FANTASY_PLAYERS}
FANTASY_PLAYERS_LOWER["kevin choi"] = "Kevin Yun Lam Choi"
FANTASY_PLAYERS_LOWER["joao simao"] = "Joao Simao Peres"

# Event-URLs för spelare som var currentlyPlaying i senaste körningen
TEST_URLS = [
    "https://www.pokernews.com/tours/wsop/2026-wsop/event-27-10000-dealers-choice-championship/",
    "https://www.pokernews.com/tours/wsop/2026-wsop/event-18-monster-stack/",
    "https://www.pokernews.com/tours/wsop/2026-wsop/event-24-high-roller/",
    "https://www.pokernews.com/tours/wsop/2026-wsop/event-25-500-freezeout/",
    "https://www.pokernews.com/tours/wsop/2026-wsop/event-26-2000-no-limit-holdem/",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
}

def fetch_chip_positions(event_url):
    chip_url = event_url.rstrip("/") + "/chip-counts/"
    print(f"\n=== {chip_url} ===")
    try:
        resp = requests.get(chip_url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code}")
            return
        html = resp.text

        # players_left
        m = re.search(r'Players Left[^0-9]*(\d[\d,]*)', html)
        players_left = int(m.group(1).replace(",", "")) if m else None
        print(f"  players_left: {players_left}")

        # Försök 1: Leta efter rankade rader med nummer + spelarnamn
        # Mönster: <td>4</td>...<td>Matt Glantz</td> eller liknande
        # Hämta alla textnoder nära varandra
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
        print(f"  Antal <tr>-rader: {len(rows)}")

        found_any = False
        for i, row in enumerate(rows):
            text = re.sub(r'<[^>]+>', ' ', row)
            text_clean = ' '.join(text.split())
            name_lower = text_clean.lower()

            for fp_lower, fp_canon in FANTASY_PLAYERS_LOWER.items():
                if fp_lower in name_lower:
                    # Visa rå HTML så vi ser exakt <td>-strukturen
                    print(f"  HITTAD: {fp_canon}")
                    print(f"    text: {text_clean[:150]}")
                    # Hitta alla <td>-celler
                    tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
                    tds_clean = [re.sub(r'<[^>]+>', '', td).strip() for td in tds]
                    print(f"    <td>-celler: {tds_clean}")
                    found_any = True

        if not found_any:
            print("  Ingen fantasy-spelare hittad")
            # Visa rå HTML för de första 3 datarader
            data_rows = [r for r in rows if '<td' in r][:3]
            for i, row in enumerate(data_rows):
                tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
                tds_clean = [re.sub(r'<[^>]+>', '', td).strip() for td in tds]
                print(f"  exempelrad {i}: {tds_clean}")

    except Exception as e:
        print(f"  FEL: {e}")

for url in TEST_URLS:
    fetch_chip_positions(url)

print("\n=== KLAR ===")
