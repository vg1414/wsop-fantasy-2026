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

def scrape_totals(player_lookup):
    scores = {p: 0 for p in PLAYERS}
    try:
        res = requests.get("https://www.25kfantasy.com/players/", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                name_norm = normalize(cells[0].get_text(strip=True))
                if name_norm in player_lookup:
                    try:
                        scores[player_lookup[name_norm]] = int(cells[1].get_text(strip=True))
                    except ValueError:
                        pass
    except Exception as e:
        print(f"Error scraping players page: {e}")
    return scores

def scrape_events(player_lookup):
    """
    Returns list of dicts: { date, player, event, points }
    Only entries where player is in our PLAYERS list.
    Ordered newest date first.
    """
    events = []
    try:
        res = requests.get("https://www.25kfantasy.com/all-scores/", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")

        for table in soup.find_all("table"):
            # Date is in the <th> inside <thead>
            th = table.find("th")
            if not th:
                continue
            date_str = th.get_text(strip=True)  # e.g. "May 29, 2026"

            for row in table.find_all("tr"):
                td = row.find("td")
                if not td:
                    continue

                links = td.find_all("a")
                if len(links) < 2:
                    continue

                player_name = links[0].get_text(strip=True)
                event_name = links[1].get_text(strip=True)

                pts_span = td.find("span", class_="fw-bolder")
                if not pts_span:
                    continue

                pts_text = pts_span.get_text(strip=True)  # "13 points" or "1 point"
                try:
                    pts = int(pts_text.split()[0])
                except (ValueError, IndexError):
                    continue

                name_norm = normalize(player_name)
                if name_norm in player_lookup:
                    events.append({
                        "date": date_str,
                        "player": player_lookup[name_norm],
                        "event": event_name,
                        "points": pts
                    })

    except Exception as e:
        print(f"Error scraping all-scores page: {e}")

    return events

def main():
    player_lookup = {normalize(p): p for p in PLAYERS}

    scores = scrape_totals(player_lookup)
    events = scrape_events(player_lookup)

    # Fallback: if totals page missed someone, sum from events
    for entry in events:
        p = entry["player"]
        if scores.get(p, 0) == 0 and entry["points"] > 0:
            scores[p] = scores.get(p, 0) + entry["points"]

    output = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "players": scores,
        "events": events
    }

    with open("scores.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Done. Players with points: { {k:v for k,v in scores.items() if v > 0} }")
    print(f"Event entries for our players: {len(events)}")

if __name__ == "__main__":
    main()
