import requests
import json
import os
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

API_URL = "https://www.pokernews.com/api/my-stable"

def fetch_my_stable(xpid, xpkey):
    cookies = {
        "_xpid": xpid,
        "_xpkey": xpkey,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Referer": "https://www.pokernews.com/myplayers/settings/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    resp = requests.get(API_URL, cookies=cookies, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()

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
    xpid = os.environ.get("POKERNEWS_XPID")
    xpkey = os.environ.get("POKERNEWS_XPKEY")
    if not xpid or not xpkey:
        raise RuntimeError("POKERNEWS_XPID and POKERNEWS_XPKEY must be set")

    print("Fetching PokerNews my-stable...")
    players_raw = fetch_my_stable(xpid, xpkey)
    print(f"Got {len(players_raw)} players from PokerNews")

    results = []
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

        results.append({
            "name": canonical,
            "status": widget_type,
            "tournament": tournament_title,
            "event": event_title,
            "event_url": event_url,
            "place": place,
            "total_players": total_players,
            "latest_action": latest_action,
        })

    updated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    db = init_firebase()
    db.collection("live_status").document("latest").set({
        "updated": updated,
        "players": results,
    })

    currently_playing = [p for p in results if p["status"] == "currentlyPlaying"]
    print(f"Wrote {len(results)} fantasy players to Firestore")
    print(f"Currently playing: {[p['name'] for p in currently_playing]}")

if __name__ == "__main__":
    main()
