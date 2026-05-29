import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone

PLAYERS = [
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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def normalize(name):
    return name.lower().strip()

def scrape_25k():
    scores = {p: 0 for p in PLAYERS}
    player_lookup = {normalize(p): p for p in PLAYERS}

    try:
        res = requests.get("https://www.25kfantasy.com/players/", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")

        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                name_cell = cells[0].get_text(strip=True)
                score_cell = cells[1].get_text(strip=True)

                name_norm = normalize(name_cell)
                if name_norm in player_lookup:
                    try:
                        scores[player_lookup[name_norm]] = int(score_cell)
                    except ValueError:
                        pass
    except Exception as e:
        print(f"Error scraping players page: {e}")

    # Also check all-scores page for more complete data
    try:
        res2 = requests.get("https://www.25kfantasy.com/all-scores/", headers=HEADERS, timeout=15)
        soup2 = BeautifulSoup(res2.text, "html.parser")

        for row in soup2.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                name_cell = cells[0].get_text(strip=True)
                score_cell = cells[1].get_text(strip=True)

                name_norm = normalize(name_cell)
                if name_norm in player_lookup:
                    try:
                        val = int(score_cell)
                        canon = player_lookup[name_norm]
                        if val > scores[canon]:
                            scores[canon] = val
                    except ValueError:
                        pass
    except Exception as e:
        print(f"Error scraping all-scores page: {e}")

    return scores

def main():
    scores = scrape_25k()

    output = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "players": scores
    }

    with open("scores.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    total = sum(scores.values())
    scorers = {k: v for k, v in scores.items() if v > 0}
    print(f"Done. Total points across all players: {total}")
    print(f"Players with points: {scorers}")

if __name__ == "__main__":
    main()
