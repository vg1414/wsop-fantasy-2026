import requests
from bs4 import BeautifulSoup
import json
import os
import re
import sys
from datetime import datetime, timezone
import certifi

os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

import firebase_admin
from firebase_admin import credentials, firestore
import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account

# Fix Windows terminal encoding for special characters
sys.stdout.reconfigure(encoding="utf-8")

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
        res = requests.get(f"{BASE_URL}/players/", headers=HEADERS, timeout=15, verify=False)
        soup = BeautifulSoup(res.text, "html.parser")
        # Find the table and detect column indices from headers
        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            if "player" not in headers or "score" not in headers:
                continue
            player_i = headers.index("player")
            score_i = headers.index("score")
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) <= max(player_i, score_i):
                    continue
                name_norm = normalize(cells[player_i].get_text(strip=True))
                if name_norm in player_lookup:
                    try:
                        scores[player_lookup[name_norm]] = int(cells[score_i].get_text(strip=True))
                    except ValueError:
                        pass
    except Exception as e:
        print(f"Error scraping players page: {e}")
    return scores

def scrape_events(player_lookup):
    events = []
    try:
        res = requests.get(f"{BASE_URL}/all-scores/", headers=HEADERS, timeout=15, verify=False)
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
                        "placement": 0
                    })

    except Exception as e:
        print(f"Error scraping all-scores page: {e}")

    return events

def scrape_event_details(event_urls):
    """For each unique event URL, fetch entrants and per-player placement.
    Returns dict {url: {"entrants": int, "placements": {player_name: int}}}"""
    cache = {}
    for url in set(event_urls):
        if not url:
            continue
        try:
            res = requests.get(url, headers=HEADERS, timeout=15, verify=False)
            soup = BeautifulSoup(res.text, "html.parser")

            inp = soup.find("input", {"id": "event-entrants"})
            entrants = int(inp["value"]) if inp and inp.get("value") else 0

            placements = {}
            for table in soup.find_all("table"):
                headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
                if "place" in headers and "player" in headers:
                    place_i = headers.index("place")
                    player_i = headers.index("player")
                    for row in table.find_all("tr"):
                        cells = row.find_all("td")
                        if len(cells) > max(place_i, player_i):
                            place = cells[place_i].get_text(strip=True)
                            player = cells[player_i].get_text(strip=True)
                            if place.isdigit():
                                placements[normalize(player)] = int(place)
                    break

            cache[url] = {"entrants": entrants, "placements": placements, "has_cashes": len(placements) > 0}
            print(f"  {url} -> {entrants} entrants, {len(placements)} placements")
        except Exception as e:
            print(f"  Could not fetch event details for {url}: {e}")
            cache[url] = {"entrants": 0, "placements": {}, "has_cashes": False}
    return cache

def scrape_event_statuses():
    """Fetch event statuses from 25kfantasy.com/events.
    Returns (statuses, live_event_urls) where:
      statuses: dict {event_num: status}  ('completed'/'live'/'upcoming')
      live_event_urls: dict {event_num: url} for events currently live
    """
    statuses = {}
    live_event_urls = {}
    try:
        res = requests.get(f"{BASE_URL}/events", headers=HEADERS, timeout=15, verify=False)
        soup = BeautifulSoup(res.text, "html.parser")
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            row_text = row.get_text(" ", strip=True)
            m = re.search(r'Event\s*#(\d+)', row_text, re.IGNORECASE)
            if not m:
                continue
            num = int(m.group(1))
            # Status is in the last cell
            status_text = cells[-1].get_text(strip=True).lower()
            if "event completed" in status_text:
                statuses[num] = "completed"
            elif "tracking live" in status_text:
                statuses[num] = "live"
                # Grab the event URL from the first link in the row
                link = row.find("a", href=True)
                if link:
                    href = link["href"]
                    url = BASE_URL + href if href.startswith("/") else href
                    live_event_urls[num] = url
            elif "not yet tracking" in status_text:
                statuses[num] = "upcoming"
        print(f"Event statuses: {len(statuses)} found, "
              f"{sum(1 for s in statuses.values() if s == 'completed')} completed, "
              f"{sum(1 for s in statuses.values() if s == 'live')} live")
    except Exception as e:
        print(f"Error scraping event statuses: {e}")
    return statuses, live_event_urls

def build_player_urls(player_lookup):
    """Build profile URLs for all players based on slug pattern."""
    urls = {}
    for norm, canonical in player_lookup.items():
        slug = player_slug(canonical)
        urls[canonical] = f"{BASE_URL}/players/player-profile/{slug}/"
    return urls

def scrape_cash_counts(player_urls):
    """Hämtar antal cashes per spelare från deras profilsida."""
    counts = {}
    for player, url in player_urls.items():
        try:
            res = requests.get(url, headers=HEADERS, timeout=15, verify=False)
            soup = BeautifulSoup(res.text, "html.parser")
            # Letar efter "X cashes" eller antal rader i cash-tabellen
            cash_count = 0
            for table in soup.find_all("table"):
                headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
                if "score" in headers and ("event" in headers or "placement" in "".join(headers)):
                    cash_count = len([r for r in table.find_all("tr") if r.find("td")])
                    break
            counts[player] = cash_count
            if cash_count > 0:
                print(f"  {player}: {cash_count} cashes")
        except Exception as e:
            print(f"  Kunde inte hämta profil för {player}: {e}")
            counts[player] = 0
    return counts

FIRESTORE_PROJECT = "wsop-54e15"
FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{FIRESTORE_PROJECT}/databases/(default)/documents/scores/latest"
FIRESTORE_SCOPES = ["https://www.googleapis.com/auth/datastore"]

def get_firebase_token():
    sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if sa_json:
        sa_dict = json.loads(sa_json)
        cred = service_account.Credentials.from_service_account_info(sa_dict, scopes=FIRESTORE_SCOPES)
    else:
        key_path = r"C:\Users\David\.firebase-keys\wsop-54e15-firebase-adminsdk.json"
        if not os.path.exists(key_path):
            raise RuntimeError("Ingen Firebase-nyckel hittades (varken env-variabel eller lokal fil)")
        cred = service_account.Credentials.from_service_account_file(key_path, scopes=FIRESTORE_SCOPES)
    session = requests.Session()
    session.verify = False
    auth_req = google.auth.transport.requests.Request(session=session)
    cred.refresh(auth_req)
    return cred.token

def to_firestore_value(v):
    if isinstance(v, str):   return {"stringValue": v}
    if isinstance(v, bool):  return {"booleanValue": v}
    if isinstance(v, int):   return {"integerValue": str(v)}
    if isinstance(v, float): return {"doubleValue": v}
    if v is None:            return {"nullValue": None}
    if isinstance(v, list):  return {"arrayValue": {"values": [to_firestore_value(i) for i in v]}}
    if isinstance(v, dict):  return {"mapValue": {"fields": {k: to_firestore_value(val) for k, val in v.items()}}}
    return {"stringValue": str(v)}

def write_to_firestore(data):
    token = get_firebase_token()
    fields = {k: to_firestore_value(v) for k, v in data.items()}
    res = requests.patch(
        FIRESTORE_URL,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"fields": fields},
        verify=certifi.where(),
        timeout=30,
    )
    res.raise_for_status()
    return res.json()

def main():
    player_lookup = {normalize(p): p for p in PLAYERS}

    scores = scrape_totals(player_lookup)
    events = scrape_events(player_lookup)
    player_urls = build_player_urls(player_lookup)

    # Fetch entrants + placements per unique event URL
    print("Fetching entrants and placements per event...")
    event_details = scrape_event_details([e["event_url"] for e in events])
    # Build set of event numbers where at least one player has cashed (bubble burst)
    itm_event_nums = set()
    for ev in events:
        details = event_details.get(ev["event_url"], {})
        ev["entrants"] = details.get("entrants", 0)
        ev["placement"] = details.get("placements", {}).get(normalize(ev["player"]), 0)
        if details.get("has_cashes"):
            m = ev["event"] and re.search(r'Event\s*#(\d+)', ev["event"], re.IGNORECASE)
            if m:
                itm_event_nums.add(int(m.group(1)))

    # Fallback: if totals page missed someone, sum from events
    for entry in events:
        p = entry["player"]
        if scores.get(p, 0) == 0 and entry["points"] > 0:
            scores[p] = scores.get(p, 0) + entry["points"]

    # Fetch event statuses (completed / live / upcoming) + URLs for live events
    print("Fetching event statuses...")
    event_statuses_raw, live_event_urls = scrape_event_statuses()
    event_statuses = {str(k): v for k, v in event_statuses_raw.items()}

    # Build event_entrants from already-fetched event details
    event_entrants = {}
    for ev in events:
        m = ev["event"] and re.search(r'Event\s*#(\d+)', ev["event"], re.IGNORECASE)
        if m and ev.get("entrants", 0) > 0:
            event_entrants[int(m.group(1))] = ev["entrants"]

    # Check all live events for cashes (bubble burst detection) + grab entrants
    print("Checking live events for ITM (bubble burst)...")
    live_event_nums = [k for k, v in event_statuses_raw.items() if v == "live"]
    print(f"  Live event nums from statuses: {live_event_nums}")
    live_check_urls = {n: f"{BASE_URL}/events/wsop-event/2026-event-{n}/" for n in live_event_nums}
    print(f"  Checking URLs: {list(live_check_urls.values())}")
    live_details = scrape_event_details(list(live_check_urls.values()))
    for evN, url in live_check_urls.items():
        d = live_details.get(url, {})
        if d.get("has_cashes"):
            itm_event_nums.add(evN)
        if d.get("entrants", 0) > 0:
            event_entrants[evN] = d["entrants"]
    print(f"ITM events: {sorted(itm_event_nums)}")
    print(f"Event entrants: { {k:v for k,v in sorted(event_entrants.items())} }")

    print("Hämtar antal cashes från spelarprofilsidor...")
    cash_counts = scrape_cash_counts(player_urls)

    updated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    write_to_firestore({
        "updated": updated,
        "players": scores,
        "player_urls": player_urls,
        "events": events,
        "event_statuses": event_statuses,
        "itm_events": sorted(itm_event_nums),
        "event_entrants": event_entrants,
        "cash_counts": cash_counts,
    })

    print(f"Wrote to Firestore. Updated: {updated}")
    print(f"Players with points: { {k:v for k,v in scores.items() if v > 0} }")
    print(f"Event entries for our players: {len(events)}")

if __name__ == "__main__":
    main()
