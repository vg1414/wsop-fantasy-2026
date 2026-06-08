"""
Testscript: anropar 25kfantasy.com/process/sweat utan inloggning.
Ändrar ingenting — bara loggar svaret.
"""
import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.25kfantasy.com/sweat",
    "Origin": "https://www.25kfantasy.com",
}

URL = "https://www.25kfantasy.com/process/sweat"

# Steg 1: hämta aktiva events
print("=== sweat_events ===")
r = requests.post(URL, headers=HEADERS, json={"q": "sweat_events"}, timeout=15)
print(f"HTTP {r.status_code}")
print(r.text[:2000])

# Steg 2: om vi fick events, testa sweat_by_event med event_id 1331 (Event #24)
print("\n=== sweat_by_event (event_id=1331) ===")
r2 = requests.post(URL, headers=HEADERS, json={"q": "sweat_by_event", "event_id": "1331"}, timeout=15)
print(f"HTTP {r2.status_code}")
print(r2.text[:3000])
