import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore

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

BASE_URL = "https://www.25kfantasy.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def normalize(name):
    return name.lower().strip()

def player_slug(name):
    return name.lower().replace(" ", "-")

def scrape_totals(player_lookup):
    scores = {p: 0 for p in PLAYERS}
    try:
        res = requests.get(f"{BASE_URL}/players/", headers=HEADERS, timeout=15)
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
    events = []
    try:
        res = requests.get(f"{BASE_URL}/all-scores/", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")

        for table in soup.find_all("table"):
            th = table.find("th")
            if not th:
                continue
            date_str = th.get_text(strip=True)

            for row in table.find_all("tr"):
                td = row.find("td")
                if not td:
                    continue

                links = td.find_all("a")
                if len(links) < 2:
                    continue

                player_name = links[0].get_text(strip=True)
                player_href = links[0].get("href", "")
                event_name = links[1].get_text(strip=True)
                event_href = links[1].get("href", "")

                pts_span = td.find("span", class_="fw-bolder")
                if not pts_span:
                    continue

                pts_text = pts_span.get_text(strip=True)
                try:
                    pts = int(pts_text.split()[0])
                except (ValueError, IndexError):
                    continue

                # Try to find placement (e.g. "1st", "2nd", "3rd", "4th")
                placement = ""
                full_text = td.get_text(" ", strip=True)
                place_match = re.search(r'\b(\d+(?:st|nd|rd|th))\b', full_text)
                if place_match:
                    placement = place_match.group(1)

                name_norm = normalize(player_name)
                if name_norm in player_lookup:
                    canonical_name = player_lookup[name_norm]
                    event_url = BASE_URL + event_href if event_href.startswith("/") else event_href
                    player_url = BASE_URL + player_href if player_href.startswith("/") else player_href

                    events.append({
                        "date": date_str,
                        "player": canonical_name,
                        "player_url": player_url,
                        "event": event_name,
                        "event_url": event_url,
                        "points": pts,
                        "placement": placement
                    })

    except Exception as e:
        print(f"Error scraping all-scores page: {e}")

    return events

def build_player_urls(player_lookup):
    """Build profile URLs for all players based on slug pattern."""
    urls = {}
    for norm, canonical in player_lookup.items():
        slug = player_slug(canonical)
        urls[canonical] = f"{BASE_URL}/players/player-profile/{slug}/"
    return urls

def init_firebase():
    sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if not sa_json:
        raise RuntimeError("FIREBASE_SERVICE_ACCOUNT environment variable is not set")
    sa_dict = json.loads(sa_json)
    cred = credentials.Certificate(sa_dict)
    firebase_admin.initialize_app(cred)
    return firestore.client()

def main():
    player_lookup = {normalize(p): p for p in PLAYERS}

    scores = scrape_totals(player_lookup)
    events = scrape_events(player_lookup)
    player_urls = build_player_urls(player_lookup)

    # Fallback: if totals page missed someone, sum from events
    for entry in events:
        p = entry["player"]
        if scores.get(p, 0) == 0 and entry["points"] > 0:
            scores[p] = scores.get(p, 0) + entry["points"]

    updated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    db = init_firebase()
    doc_ref = db.collection("scores").document("latest")
    doc_ref.set({
        "updated": updated,
        "players": scores,
        "player_urls": player_urls,
        "events": events
    })

    print(f"Wrote to Firestore. Updated: {updated}")
    print(f"Players with points: { {k:v for k,v in scores.items() if v > 0} }")
    print(f"Event entries for our players: {len(events)}")

if __name__ == "__main__":
    main()
