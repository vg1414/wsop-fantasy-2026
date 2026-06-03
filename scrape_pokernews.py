import requests
import json
import os
import re
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore

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
FANTASY_PLAYERS_LOWER["joão simão"] = "Joao Simao Peres"
FANTASY_PLAYERS_LOWER["joão simão peres"] = "Joao Simao Peres"

API_URL = "https://www.pokernews.com/api/my-stable"

def fetch_my_stable(cookie_string):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "sv-SE,sv;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.pokernews.com/myplayers/settings/",
        "Cookie": cookie_string,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "DNT": "1",
    }
    resp = requests.get(API_URL, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()

def fetch_players_left(event_url):
    """Hämtar antal spelare kvar från PokerNews chip counts-sida."""
    chip_url = event_url.rstrip("/") + "/chip-counts/"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        }
        resp = requests.get(chip_url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None
        # Leta efter "Players Left" följt av ett tal
        match = re.search(r'Players Left[^0-9]*(\d[\d,]*)', resp.text)
        if match:
            return int(match.group(1).replace(",", ""))
    except Exception as e:
        print(f"  Kunde inte hämta players_left från {chip_url}: {e}")
    return None

def init_firebase():
    sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if not sa_json:
        raise RuntimeError("FIREBASE_SERVICE_ACCOUNT environment variable is not set")
    sa_dict = json.loads(sa_json)
    cred = credentials.Certificate(sa_dict)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    return firestore.client()

def main():
    cookie_string = os.environ.get("POKERNEWS_COOKIES", "").strip()
    if not cookie_string:
        raise RuntimeError("POKERNEWS_COOKIES must be set")

    print("Fetching PokerNews my-stable...")
    players_raw = fetch_my_stable(cookie_string)
    print(f"Got {len(players_raw)} players from PokerNews")

    best_by_name = {}
    for entry in players_raw:
        name = entry.get("title", "")
        canonical = FANTASY_PLAYERS_LOWER.get(name.lower())
        if not canonical:
            continue

        status = entry.get("status") or {}
        widget_type = status.get("widgetType", "")
        tournament_title = status.get("tournamentTitle", "")
        event_title = status.get("title", "")
        event_url = status.get("url", "")
        place = status.get("place", "")
        total_players = status.get("totalPlayers", "")
        latest_action = status.get("latestActionDate", "")

        if event_url and not event_url.startswith("http"):
            event_url = "https://www.pokernews.com" + event_url

        record = {
            "name": canonical,
            "status": widget_type,
            "tournament": tournament_title,
            "event": event_title,
            "event_url": event_url,
            "place": place,
            "total_players": total_players,
            "latest_action": latest_action,
        }

        # Deduplicera: currentlyPlaying vinner om den är nyare; annars senast latest_action
        existing = best_by_name.get(canonical)
        if not existing:
            best_by_name[canonical] = record
        else:
            new_playing = widget_type == "currentlyPlaying"
            old_playing = existing["status"] == "currentlyPlaying"
            if new_playing and not old_playing:
                best_by_name[canonical] = record
            elif old_playing and not new_playing:
                # Ny post är inte playing — byt om den är nyare (spelaren har åkt ut)
                if (latest_action or "") > (existing["latest_action"] or ""):
                    best_by_name[canonical] = record
            else:
                if (latest_action or "") > (existing["latest_action"] or ""):
                    best_by_name[canonical] = record

    results = list(best_by_name.values())

    # Hämta players_left per unik event_url för currentlyPlaying-spelare
    playing_urls = set(
        p["event_url"] for p in results
        if p["status"] == "currentlyPlaying" and p["event_url"]
    )
    players_left_by_url = {}
    for url in playing_urls:
        print(f"Hämtar players_left från {url}...")
        count = fetch_players_left(url)
        players_left_by_url[url] = count
        print(f"  -> {count} spelare kvar")

    for p in results:
        p["players_left"] = players_left_by_url.get(p["event_url"])

    updated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    db = init_firebase()
    db.collection("live_status").document("latest").set({
        "updated": updated,
        "players": results,
    })

    currently_playing = [p for p in results if p["status"] == "currentlyPlaying"]
    print(f"Wrote {len(results)} fantasy players to Firestore")
    print(f"Currently playing: {[p['name'] for p in currently_playing]}")
    for p in currently_playing:
        if p.get("players_left") is not None:
            print(f"  {p['name']}: {p['players_left']} spelare kvar")

if __name__ == "__main__":
    main()
