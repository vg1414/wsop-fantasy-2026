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
SWEAT_URL = "https://www.25kfantasy.com/process/sweat"

SWEAT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.25kfantasy.com/sweat",
    "Origin": "https://www.25kfantasy.com",
}

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
    chip_url = event_url.rstrip("/") + "/chip-counts/"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        }
        resp = requests.get(chip_url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None
        match = re.search(r'Players Left[^0-9]*(\d[\d,]*)', resp.text)
        if match:
            return int(match.group(1).replace(",", ""))
    except Exception as e:
        print(f"  Kunde inte hämta players_left från {chip_url}: {e}")
    return None

def fetch_sweat_ranks():
    """Hämtar chip-rank per fantasy-spelare från 25kfantasy sweat-API.
    Returnerar dict: spelarnamn (lowercase) -> {"rank": "5/7", "event": "Event #37: ..."}
    """
    ranks = {}
    try:
        # Steg 1: hämta aktiva events
        r = requests.post(SWEAT_URL, headers=SWEAT_HEADERS, json={"q": "sweat_events"}, timeout=15)
        if r.status_code != 200:
            print(f"  sweat_events HTTP {r.status_code}")
            return ranks
        data = r.json()
        events = data.get("data", {}).get("events", [])
        print(f"  Aktiva sweat-events: {len(events)}")

        # Steg 2: för varje event, hämta rank per spelare
        for ev in events:
            event_id = ev.get("id")
            event_name = ev.get("name", "")
            print(f"  Hämtar sweat_by_event för {event_name} (id={event_id})...")
            r2 = requests.post(SWEAT_URL, headers=SWEAT_HEADERS, json={"q": "sweat_by_event", "event_id": str(event_id)}, timeout=15)
            if r2.status_code != 200:
                print(f"    HTTP {r2.status_code}")
                continue
            html = r2.json().get("data", {}).get("results", "")

            # Parsa tabellrader: Rank | Player | Team | Chips | BB | Bonus | Points
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
            for row in rows:
                tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
                tds_clean = [re.sub(r'<[^>]+>', '', td).strip() for td in tds]
                if len(tds_clean) < 2:
                    continue
                # Första cellen är rank (t.ex. "5 / 7"), andra är spelarnamn
                rank_str = tds_clean[0]
                player_cell = tds_clean[1]
                if not re.match(r'^\d+\s*/\s*\d+$', rank_str):
                    continue
                # Normalisera till "5/7"
                rank_normalized = re.sub(r'\s*/\s*', '/', rank_str)
                # BB är kolumn 4 (index 4), formatet är "15.6 BB"
                bb_str = None
                if len(tds_clean) > 4:
                    bb_raw = tds_clean[4]
                    m = re.search(r'([\d.]+)\s*BB', bb_raw, re.IGNORECASE)
                    if m:
                        bb_str = m.group(1) + " BB"
                # Matcha spelarnamn mot våra fantasy-spelare
                player_lower = player_cell.lower()
                for fp_lower, fp_canon in FANTASY_PLAYERS_LOWER.items():
                    if fp_lower in player_lower:
                        ranks[fp_canon.lower()] = {"rank": rank_normalized, "event": event_name, "bb": bb_str}
                        print(f"    {fp_canon}: {rank_normalized} {bb_str or ''} ({event_name})")
                        break
    except Exception as e:
        print(f"  Fel i fetch_sweat_ranks: {e}")
    return ranks

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
        latest_action = status.get("latestActionDate", "")

        if event_url and not event_url.startswith("http"):
            event_url = "https://www.pokernews.com" + event_url

        record = {
            "name": canonical,
            "status": widget_type,
            "tournament": tournament_title,
            "event": event_title,
            "event_url": event_url,
            "latest_action": latest_action,
        }

        existing = best_by_name.get(canonical)
        if not existing:
            best_by_name[canonical] = record
        else:
            new_playing = widget_type == "currentlyPlaying"
            old_playing = existing["status"] == "currentlyPlaying"
            if new_playing and not old_playing:
                best_by_name[canonical] = record
            elif old_playing and not new_playing:
                if (latest_action or "") > (existing["latest_action"] or ""):
                    best_by_name[canonical] = record
            else:
                if (latest_action or "") > (existing["latest_action"] or ""):
                    best_by_name[canonical] = record

    results = list(best_by_name.values())

    # Bygg lookup eventnummer -> kanonisk PokerNews-titel, så alla spelare i
    # samma event visar exakt samma eventnamn oavsett om datan kom från
    # PokerNews My Stable eller 25kfantasy sweat (som namnger events olika).
    canonical_event_by_num = {}
    for p in results:
        m = re.search(r'Event\s*#(\d+)', p.get("event") or "", re.IGNORECASE)
        if m:
            canonical_event_by_num[int(m.group(1))] = p["event"]

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

    # Lookup eventnummer -> players_left, så vi kan sätta rätt players_left
    # även för spelare vars event byts av sweat-fallbacken nedan (annars
    # hänger de kvar med players_left från sitt gamla/felaktiga event).
    players_left_by_event_num = {}
    for p in results:
        if p.get("players_left") is None:
            continue
        m = re.search(r'Event\s*#(\d+)', p.get("event") or "", re.IGNORECASE)
        if m:
            players_left_by_event_num[int(m.group(1))] = p["players_left"]

    # Hämta chip-rank från 25kfantasy sweat-API
    print("Hämtar chip-rank från 25kfantasy...")
    sweat_ranks = fetch_sweat_ranks()
    for p in results:
        sweat = sweat_ranks.get(p["name"].lower())
        p["chip_rank"] = sweat["rank"] if sweat else None
        p["bb"] = sweat["bb"] if sweat else None

    # Om en spelare visas som currentlyPlaying men inte längre finns i sweats
    # chip-count-data har han fått poäng på 25kfantasy och är därmed bustad —
    # sweat är den färskare källan, PokerNews my-stable hinner ofta inte
    # uppdatera status i tid.
    for p in results:
        if p["status"] != "currentlyPlaying":
            continue
        if p["name"].lower() in sweat_ranks:
            continue
        print(f"  Bustad enligt sweat (saknas i chip-count-data): {p['name']}")
        p["status"] = "busted"
        p["players_left"] = None

    def canonical_event_name(sweat_event_name):
        m = re.search(r'Event\s*#(\d+)', sweat_event_name or "", re.IGNORECASE)
        if m:
            canon_name = canonical_event_by_num.get(int(m.group(1)))
            if canon_name:
                return canon_name
        return sweat_event_name

    def players_left_for_event(event_name):
        m = re.search(r'Event\s*#(\d+)', event_name or "", re.IGNORECASE)
        return players_left_by_event_num.get(int(m.group(1))) if m else None

    # Fallback: spelare som syns i sweat men inte som currentlyPlaying i PokerNews
    playing_names = {p["name"].lower() for p in results if p["status"] == "currentlyPlaying"}
    for name_lower, sweat in sweat_ranks.items():
        if name_lower not in playing_names:
            canon = FANTASY_PLAYERS_LOWER.get(name_lower)
            if not canon:
                continue
            event_name = canonical_event_name(sweat["event"])
            players_left = players_left_for_event(event_name)
            # Kolla om spelaren finns i results men med fel status
            existing = best_by_name.get(canon)
            if existing:
                existing["status"] = "currentlyPlaying"
                existing["chip_rank"] = sweat["rank"]
                existing["bb"] = sweat["bb"]
                existing["event"] = event_name
                existing["players_left"] = players_left
                print(f"  Fallback (sweat→playing): {canon} ({sweat['rank']} i {event_name}, players_left={players_left})")
            else:
                # Spelaren saknas helt — skapa en minimal post
                new_record = {
                    "name": canon,
                    "status": "currentlyPlaying",
                    "tournament": "WSOP 2026",
                    "event": event_name,
                    "event_url": "",
                    "latest_action": "",
                    "players_left": players_left,
                    "chip_rank": sweat["rank"],
                    "bb": sweat["bb"],
                }
                results.append(new_record)
                print(f"  Fallback (sweat→ny post): {canon} ({sweat['rank']} i {event_name}, players_left={players_left})")

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
        print(f"  {p['name']}: players_left={p.get('players_left')} chip_rank={p.get('chip_rank')}")

if __name__ == "__main__":
    main()
