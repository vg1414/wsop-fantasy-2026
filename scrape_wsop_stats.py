import requests
from bs4 import BeautifulSoup
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
import certifi

os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

import firebase_admin
from firebase_admin import credentials, firestore

sys.stdout.reconfigure(encoding="utf-8")

# WSOP.com-URL per spelare (slug eller numeriskt ID)
PLAYER_URLS = {
    "David Peters":           "david-peters",
    "Josh Arieh":             "joshua-arieh",
    "Viktor Blom":            "viktor-blom",
    "Ryutaro Suzuki":         "ryutaro-suzuki",
    "Matt Glantz":            "matthew-barry-glantz",
    "Eli Elezra":             "eli-elezra",
    "Mike Matusow":           "15818236",
    "Ben Lamb":               "ben-lamb",
    "Jason Koon":             "jason-koon",
    "Erik Seidel":            "erik-seidel",
    "Isaac Haxton":           "isaac-blum-haxton",
    "Adam Hendrix":           "12472530",
    "Phil Hellmuth":          "phil-hellmuth",
    "Philip Sternheimer":     "philip-richard-sternheimer",
    "Andrew Lichtenberger":   "andrew-lichtenberger",
    "Sam Soverel":            "sam-wolcott-soverel",
    "Alex Foxen":             "william-foxen",
    "Jon Turner":             "jon-turner",
    "Chris Hunichen":         "christopher-brian-hunichen",
    "Stephen Chidwick":       "stephen-james-chidwick",
    "Stephen Song":           "stephen-song",
    "John Riordan":           "john-riordan",
    "Joao Simao Peres":       "joao-simao",
    "Shaun Deeb":             "shaun-kristopher-deeb",
    "Kevin Yun Lam Choi":    "1188864",
    "Anson Tsang":            "yan-shing-tsang",
    "Jim Collopy":            "james-collopy",
    "Lawrence Brandt":        "lawrence-brandt",
    "Nick Guagenti":          "nick-guagenti",
    "Klemens Roiter":         "838282",
    "Andrew Ostapchenko":     "3717014",
    "Brock Wilson":           "brock-wilson",
    "Joey Weissman":          "joey-marc-weissman",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def parse_number(text):
    if not text:
        return 0
    cleaned = re.sub(r"[^\d]", "", text)
    return int(cleaned) if cleaned else 0

def scrape_player(name, slug):
    url = f"https://www.wsop.com/players/{slug}/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print(f"  FEL {name}: HTTP {r.status_code}")
            return None
        soup = BeautifulSoup(r.text, "html.parser")

        stats = {"bracelets": 0, "final_tables": 0, "cashes": 0, "earnings": 0}

        # Hitta stat-block: label + värde-par
        # WSOP.com använder typiskt <li> eller <div> med label+value
        text = soup.get_text(" ", strip=True)

        # Försök hitta siffrorna via regex på sidtexten
        # Mönster: "Bracelets N Final Tables N Cashes N Total Earnings $N"
        b = re.search(r"Bracelets\s+(\d+)", text)
        ft = re.search(r"Final Tables\s+(\d+)", text)
        c = re.search(r"Cashes\s+([\d,]+)", text)
        e = re.search(r"Total Earnings\s+\$([\d,]+)", text)

        if b:  stats["bracelets"]    = parse_number(b.group(1))
        if ft: stats["final_tables"] = parse_number(ft.group(1))
        if c:  stats["cashes"]       = parse_number(c.group(1))
        if e:  stats["earnings"]     = parse_number(e.group(1))

        print(f"  OK {name}: {stats['bracelets']}B / {stats['final_tables']}FT / {stats['cashes']}C / ${stats['earnings']:,}")
        return stats

    except Exception as ex:
        print(f"  FEL {name}: {ex}")
        return None

def init_firebase():
    sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if sa_json:
        cred = credentials.Certificate(json.loads(sa_json))
    else:
        key_path = r"C:\Users\David\.firebase-keys\wsop-54e15-firebase-adminsdk.json"
        cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()

print("=== Scrapar WSOP-stats ===")
player_stats = {}

for name, slug in PLAYER_URLS.items():
    stats = scrape_player(name, slug)
    if stats:
        player_stats[name] = stats
    time.sleep(1.2)

print(f"\nHämtade {len(player_stats)}/{len(PLAYER_URLS)} spelare")

print("Sparar till Firestore...")
db = init_firebase()
db.collection("wsop_stats").document("latest").set({
    "players": player_stats,
    "updated": datetime.now(timezone.utc).isoformat(),
})
print("Klart!")
