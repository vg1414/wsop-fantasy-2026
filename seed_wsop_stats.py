"""
Seed WSOP historical stats to Firestore.
Data collected manually from wsop.com 2026-06-24.
Run: python seed_wsop_stats.py
"""
import json, os, sys, certifi
from datetime import datetime, timezone

os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

import firebase_admin
from firebase_admin import credentials, firestore

sys.stdout.reconfigure(encoding="utf-8")

PLAYER_STATS = {
    "David Peters":         {"bracelets": 4,  "final_tables": 69,  "cashes": 307, "earnings": 15532103},
    "Josh Arieh":           {"bracelets": 7,  "final_tables": 49,  "cashes": 192, "earnings": 13255283},
    "Viktor Blom":          {"bracelets": 0,  "final_tables": 9,   "cashes": 46,  "earnings": 4774563},
    "Ryutaro Suzuki":       {"bracelets": 2,  "final_tables": 5,   "cashes": 38,  "earnings": 1107460},
    "Matt Glantz":          {"bracelets": 0,  "final_tables": 23,  "cashes": 125, "earnings": 4493987},
    "Eli Elezra":           {"bracelets": 5,  "final_tables": 27,  "cashes": 92,  "earnings": 4612486},
    "Mike Matusow":         {"bracelets": 4,  "final_tables": 35,  "cashes": 143, "earnings": 7312896},
    "Ben Lamb":             {"bracelets": 2,  "final_tables": 24,  "cashes": 61,  "earnings": 12815731},
    "Jason Koon":           {"bracelets": 2,  "final_tables": 25,  "cashes": 94,  "earnings": 14769935},
    "Erik Seidel":          {"bracelets": 10, "final_tables": 73,  "cashes": 232, "earnings": 14138756},
    "Isaac Haxton":         {"bracelets": 1,  "final_tables": 22,  "cashes": 72,  "earnings": 12108144},
    "Adam Hendrix":         {"bracelets": 0,  "final_tables": 40,  "cashes": 248, "earnings": 6585857},
    "Phil Hellmuth":        {"bracelets": 17, "final_tables": 92,  "cashes": 249, "earnings": 20105893},
    "Philip Sternheimer":   {"bracelets": 1,  "final_tables": 12,  "cashes": 49,  "earnings": 6581370},
    "Andrew Lichtenberger": {"bracelets": 1,  "final_tables": 45,  "cashes": 176, "earnings": 12314652},
    "Sam Soverel":          {"bracelets": 4,  "final_tables": 25,  "cashes": 70,  "earnings": 11654654},
    "Alex Foxen":           {"bracelets": 4,  "final_tables": 82,  "cashes": 323, "earnings": 29672557},
    "Jon Turner":           {"bracelets": 0,  "final_tables": 32,  "cashes": 201, "earnings": 2550772},
    "Chris Hunichen":       {"bracelets": 1,  "final_tables": 23,  "cashes": 180, "earnings": 13056597},
    "Stephen Chidwick":     {"bracelets": 2,  "final_tables": 36,  "cashes": 138, "earnings": 17351396},
    "Stephen Song":         {"bracelets": 1,  "final_tables": 46,  "cashes": 191, "earnings": 6767247},
    "John Riordan":         {"bracelets": 2,  "final_tables": 49,  "cashes": 195, "earnings": 2752374},
    "Joao Simao Peres":     {"bracelets": 4,  "final_tables": 18,  "cashes": 270, "earnings": 9683975},
    "Shaun Deeb":           {"bracelets": 8,  "final_tables": 57,  "cashes": 260, "earnings": 14711713},
    "Kevin Yun Lam Choi":  {"bracelets": 0,  "final_tables": 1,   "cashes": 28,  "earnings": 47788},
    "Anson Tsang":          {"bracelets": 2,  "final_tables": 11,  "cashes": 114, "earnings": 1424803},
    "Jim Collopy":          {"bracelets": 3,  "final_tables": 34,  "cashes": 280, "earnings": 6275422},
    "Lawrence Brandt":      {"bracelets": 2,  "final_tables": 8,   "cashes": 76,  "earnings": 1357865},
    "Nick Guagenti":        {"bracelets": 2,  "final_tables": 15,  "cashes": 79,  "earnings": 1411252},
    "Klemens Roiter":       {"bracelets": 1,  "final_tables": 8,   "cashes": 86,  "earnings": 5130773},
    "Andrew Ostapchenko":   {"bracelets": 1,  "final_tables": 24,  "cashes": 115, "earnings": 4348333},
    "Brock Wilson":         {"bracelets": 0,  "final_tables": 48,  "cashes": 284, "earnings": 4557005},
    "Joey Weissman":        {"bracelets": 1,  "final_tables": 17,  "cashes": 192, "earnings": 4686257},
}

def init_firebase():
    sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if sa_json:
        cred = credentials.Certificate(json.loads(sa_json))
    else:
        key_path = r"C:\Users\David\.firebase-keys\wsop-54e15-firebase-adminsdk.json"
        cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()

print("Ansluter till Firestore...")
db = init_firebase()
db.collection("wsop_stats").document("latest").set({
    "players": PLAYER_STATS,
    "updated": datetime.now(timezone.utc).isoformat(),
})
print(f"Klart! {len(PLAYER_STATS)} spelare sparade till Firestore.")
