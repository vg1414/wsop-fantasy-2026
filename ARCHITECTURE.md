# WSOP Fantasy – Teknisk arkitektur och guide för framtida år

> Senast uppdaterad 2026-07-28. Använd den här filen för att snabbt förstå projektet i en ny chatt,
> eller för att sätta upp en ny säsong med nya lag och ett nytt schema.

---

## Snabböversikt

| Komponent | Teknologi | Syfte |
|-----------|-----------|-------|
| `index.html` | HTML + Vanilla JS | Hela UI:t – 5 flikar, realtid via Firestore, hamburgermeny på mobil |
| `scrape_scores.py` | Python 3 | Hämtar poäng från 25kfantasy.com → Firestore |
| `scrape_pokernews.py` | Python 3 | Hämtar live-status från PokerNews → Firestore |
| `.github/workflows/update-scores.yml` | GitHub Actions | Kör scrapers var 30 min under WSOP-tid |
| Firebase Firestore | NoSQL-moln-DB | Mellanlagrar all data, klienten lyssnar i realtid |
| GitHub Pages | Statisk hosting | Serverar index.html, ingen backend behövs |

---

## Hur data flödar

```
25kfantasy.com  ──► scrape_scores.py ──┐
                                       ├──► Firestore ──► index.html (browser)
pokernews.com   ──► scrape_pokernews.py┘

GitHub Actions kör scrape_scores + scrape_pokernews var 30 min under WSOP
```

1. GitHub Actions triggar scrapers på schema (eller manuellt)
2. Scrapers hämtar data från externa sajter och skriver till Firestore
3. Klientens `onSnapshot()`-lyssnare tar emot data direkt — inga sidladdningar behövs

---

## Filstruktur

```
WSOP Fantasy/
├── .github/workflows/
│   └── update-scores.yml      ← Kör var 30 min (scrape_scores + scrape_pokernews)
├── assets/images/
│   ├── bracelet.png           ← WSOP-bracelet-bild (inline i text)
│   ├── favicon.png            ← Favicon + PWA-ikon (browser, iPhone, Android)
│   ├── logo.png               ← Logotyp i headern
│   └── World-Series-of-Poker-WSOP*.jpg
├── .gitignore                 ← Skyddar Firebase-nycklar och lokala engångsskript från commits
├── ARCHITECTURE.md            ← Den här filen
├── CHANGELOG.md               ← Versionslogg
├── README.md                  ← Projektbeskrivning
├── index.html                 ← Hela appen (~3600 rader)
├── manifest.json               ← PWA-manifest (namn, ikon, tema-färg för "Lägg till på hemskärm")
├── scrape_pokernews.py        ← Live-status-scraper
└── scrape_scores.py           ← Huvud-scraper (poäng)
```

> **Borttagna engångsskript:** `seed_wsop_stats.py`, `scrape_wsop_stats.py` och workflowet
> `seed-stats.yml` togs bort 2026-07-01 efter att Lag-statistik-fliken (som de seedade data till)
> togs bort ur `index.html` 2026-06-26. De finns kvar i git-historiken om de behövs som referens.
>
> `backfill_entrants.py` finns lokalt men är avsiktligt gitignoread — ett engångsskript för att
> fylla i saknade `entrants`-värden i `score_history/all`, inte en del av den löpande driften.

---

## index.html – struktur och viktiga delar

Filen är ett enda HTML-dokument med inbäddad CSS och JavaScript. Inga externa beroenden
utom Firebase SDK och Google Fonts.

### Flikar (5 st)

| Tab-id | Namn | Innehåll |
|--------|------|----------|
| `tab-overview` | Översikt | Ställning + lagkort |
| `tab-schedule` | Schema | 100 WSOP-events med status och cashes |
| `tab-history` | Historik | Alla cashes per datum |
| `tab-calculator` | Poängberäknare | Hypotetisk poängkalkyl |
| `tab-live` | Live | Spelare vid bord just nu |

> En sjätte flik, "Lag-statistik" (historiska karriärmeriter per lag), togs bort 2026-06-26.
> Se avsnittet "Borttagen funktion: Lag-statistik" längre ner. Ett dött spår finns kvar i
> `TAB_LABELS`-objektet i JS (`metrics: 'Lag-statistik'`) utan motsvarande flik eller innehåll —
> ofarligt men kan städas bort vid tillfälle.

### Navigation (mobil vs desktop)

- **Desktop (>640px):** Flikrad (`<nav class="tab-bar">`) visas
- **Mobil (≤640px):** Flikraden döljs, `<div class="hamburger-bar">` visas istället
  - Knapp: ☰ MENY med guldglimmer-animation vid sidladdning (10 pulser)
  - Klick öppnar panel från höger som glider in via CSS-transition
  - ☰-ikonen roterar 90° medan menyn är öppen
  - Klick utanför (overlay) stänger menyn

### JavaScript-dataobjekt (ändra varje år)

**`SALARY`** (rad ~2033)
```js
const SALARY = {
  "David Peters": 15,
  "Josh Arieh": 30,
  // ... alla spelare med salary-värde
};
```
Används för "bästa värdespel"-beräkning.

**`TEAMS`** (rad ~2046)
```js
const TEAMS = [
  { owner: "Ante",    players: ["David Peters", "Josh Arieh", ...] },
  { owner: "Majscht", players: [...] },
  { owner: "Olle",    players: [...] },
  { owner: "Hasse",   players: [...] },
  { owner: "Dawod",   players: [...] },
];
```
Index 0–4 matchar CSS-variablerna `--team-0` t.o.m. `--team-4` (blå, orange, grön, lila, guld).
En spelare kan ingå i flera lag — hanteras automatiskt.

**`WSOP_EVENTS`** (rad ~2084)
```js
const WSOP_EVENTS = [
  { n: 1, name: "Mini Mystery Millions", buyin: "$550", start: "2026-05-26", end: "2026-05-30" },
  // ... 100 events
];
```

### Firebase-konfiguration
```js
const firebaseConfig = {
  apiKey: "AIzaSyB-6b-MFxeFlmijA5K-guDNTXeEHSNdpj8",
  projectId: "wsop-54e15",
};
```
API-nyckeln är publik och säker att ha i koden — Firestore Rules styr skrivrättigheter.

### Poängsystem

| Placering | Baspoäng |
|-----------|----------|
| 1:a | 50 |
| 2:a | 45 |
| 3:e | 40 |
| 4:e | 35 |
| 5:e | 30 |
| 6:e | 25 |
| 7:e | 20 |
| 8:e | 15 |
| 9:e | 10 |
| 10–18:e | 5 |
| 19:e+ | 1 |

**Multiplier (buy-in):**
- `< $1 000` → 0.5×
- `$1 000–$4 999` → 1.0×
- `$5 000–$9 999` → 1.5×
- `$10 000+` → 2.0×
- Undantag: Event #82 (Main Event) och Event #60 ($50k Poker Players Championship) → 3.0×

**Fältbonus:** `min(floor(entrants / 100), 100)` – delas ut till spelare som placerat inom ITM-gränsen (topp 15% av fältet, avrundat uppåt).

**Bracelet-bonus:** +25 poäng vid seger (placering = 1)

**Formel:** `(baspoäng + fältbonus) × multiplier + bracelet-bonus`

> Formeln är implementerad två gånger i `index.html` (samma logik, separata funktioner):
> en gång för huvudappens poängberäkning (`_getMultiplier`, rad ~2257) och en gång för
> Poängkalkylator-fliken (`getMultiplier`, rad ~3365).

---

## Borttagen funktion: Lag-statistik

En sjätte flik, "Lag-statistik", visade karriärmeriter per lag (WSOP-vinster, cashes, armband,
final tables) som stapeldiagram. Den togs bort ur `index.html` 2026-06-26 (commit `9c93a54`,
oavsiktligt som en bieffekt i en commit vars meddelande bara nämnde en UI-justering). Relaterade
engångsskript (`seed_wsop_stats.py`, `scrape_wsop_stats.py`, workflowet `seed-stats.yml`) togs bort
separat 2026-07-01 eftersom de bara seedade data till den nu borttagna fliken.

All kod finns kvar i git-historiken (`git show e452982` för när fliken lades till) om funktionen
ska återinföras. Kort sammanfattning för den händelsen:

- Statistiken var hardkodad i `seed_wsop_stats.py` (`PLAYER_STATS`-dict) och seedades manuellt
  till Firestore (`wsop_stats/latest`) via en `Run workflow`-trigger, en gång per säsong
- Anledningen till manuell seeding istället för scraping: wsop.com renderar statistik via
  JavaScript, så enkel HTML-scraping med requests/BeautifulSoup returnerade alltid noll

---

## scrape_scores.py

**Datakälla:** `https://www.25kfantasy.com`

Hämtar från tre undersidor:
1. `/players/` – totalpoäng per spelare
2. `/all-scores/` – alla individuella cashes
3. `/events` – eventstatus

**Output till Firestore (`scores/latest`):**
```json
{
  "updated": "2026-06-24T12:30:00Z",
  "players": { "David Peters": 0, "Josh Arieh": 155 },
  "player_urls": { "David Peters": "https://..." },
  "events": [
    {
      "date": "May 28, 2026",
      "player": "Brock Wilson",
      "event": "Event #2",
      "event_url": "https://...",
      "points": 2,
      "placement": 0,
      "entrants": 1234
    }
  ],
  "event_statuses": { "1": "completed", "2": "live" },
  "itm_events": [2, 5, 8],
  "event_entrants": { "1": 2145, "2": 1876 }
}
```

**OBS om händelsehistorik:** 25kfantasy.com trunkerar gamla events på `/all-scores/`. Därför finns en
separat persistent samling `score_history/all` som aldrig skrivs över — scriptet slår ihop nya events
med befintliga vid varje körning. `scores/latest` uppdateras alltid med den fullständiga historiken.

**Deduplicering:** Sker på `(player, event_number)` — event-numret extraheras ur URL eller eventnamn.
Dubbelposter med kortare ("Event #47") och fullständigt namn slås ihop och bevarar den längre varianten.

---

## scrape_pokernews.py

**Datakälla:** `https://www.pokernews.com/api/my-stable` + `https://www.25kfantasy.com/process/sweat`

Kräver inloggade session-cookies för PokerNews (lagras som GitHub Secret).

**Output till Firestore (`live_status/latest`):**
```json
{
  "updated": "2026-06-24T12:30:00Z",
  "players": [
    {
      "name": "David Peters",
      "status": "currentlyPlaying",
      "event": "Event #60 — $50k Poker Players Championship",
      "event_url": "https://pokernews.com/...",
      "place": "42",
      "total_players": "185",
      "players_left": 28,
      "chip_rank": "5/7",
      "bb": 114.0
    }
  ]
}
```

**Statusvärden:** `currentlyPlaying` / `busted` / `finished`

**Final table-logik:** `players_left < 10` → FT-badge visas i UI

**BB-visning:** Hämtas från 25kfantasy sweat-API och visas på live-fliken

---

## GitHub Actions

### update-scores.yml (automatisk)

**Schema:** Var 30:e minut under WSOP-tid
- UTC 18:00–23:59 och 00:00–11:59 (= ca 20:00–13:00 svensk tid)

Kör i ordning:
1. `scrape_scores.py`
2. `scrape_pokernews.py`

### Secrets som måste finnas i repo-inställningarna

| Secret | Innehåll |
|--------|----------|
| `FIREBASE_SERVICE_ACCOUNT` | Service account JSON (hela filen som sträng) |
| `POKERNEWS_COOKIES` | Session-cookies från PokerNews |

---

## Firebase / Firestore

**Projekt-ID:** `wsop-54e15`

**Samlingar:**
| Samling | Skrivs av | Innehåll |
|---------|-----------|----------|
| `scores/latest` | `scrape_scores.py` | Poäng, events (fullständig historik), ställning |
| `score_history/all` | `scrape_scores.py` | Persistent händelsehistorik — ackumuleras, skrivs aldrig över |
| `live_status/latest` | `scrape_pokernews.py` | Spelares live-status |
| `wsop_stats/latest` | *(borttaget skript)* | Historisk karriärstatistik — data finns kvar i Firestore men skrivs inte längre; ingen läsare finns sedan Lag-statistik-fliken togs bort |

**Service account-nyckel (lokal):**
`C:\Users\David\.firebase-keys\wsop-54e15-firebase-adminsdk.json`
(utanför repot, skyddas av .gitignore)

**OBS:** Firebase Admin SDK har ett SSL-problem på Windows lokalt. Kör alltid via GitHub Actions.

**Firestore Console:**
`https://console.firebase.google.com/project/wsop-54e15/firestore`

---

## GitHub Pages

**Repo:** `https://github.com/vg1414/wsop-fantasy-2026`
**Live URL:** `https://vg1414.github.io/wsop-fantasy-2026`

Pages serverar `index.html` direkt från `main`-branchen. Ingen byggprocess — det räcker att pusha filen.

---

## Att göra inför en ny säsong

### 1. Skapa nytt repo (rekommenderat)
- Kopiera filerna till ett nytt repo, t.ex. `wsop-fantasy-2027`
- Aktivera GitHub Pages i repo-inställningarna

### 2. Uppdatera lag och spelare i `index.html`
- Redigera `TEAMS`: byt spelarnamn och lagnamn
- Uppdatera `SALARY` med nya spelares salary-värden
- Kontrollera att spelarnamnen matchar exakt mot 25kfantasy.com:s stavning

### 3. Uppdatera WSOP_EVENTS i `index.html`
- Hämta årets events från wsop.com eller pokernews.com
- Uppdatera event-nummer, namn, buy-in, datum
- Kontrollera vilka events som ska ha 3× multiplier (Main Event + ev. $50k PC)

### 4. Uppdatera spelarlistan i scrapers
- `FANTASY_PLAYERS`-listan i `scrape_scores.py` och `scrape_pokernews.py`
- Namnen måste matcha 25kfantasy.com:s stavning

### 5. Förnya PokerNews-cookies
- Logga in på pokernews.com
- Kopiera session-cookies via DevTools → Application → Cookies
- Uppdatera GitHub Secret `POKERNEWS_COOKIES`

### 6. Uppdatera GitHub Actions-schemat
- Justera cron-uttrycken i `update-scores.yml` efter årets WSOP-datum
- WSOP 2026: maj–juli

### 7. Ny Firebase (valfritt)
- Skapa nytt projekt på console.firebase.google.com
- Byt `projectId` och `apiKey` i `index.html`
- Generera ny service account och uppdatera GitHub Secret `FIREBASE_SERVICE_ACCOUNT`

---

## Design och stil

- **Tema:** WSOP-inspirerat, mörkt (svart `#0a0a0a`, guld `#c9982b`, vit text)
- **Typsnitt:** Cinzel (rubriker/logga), Oswald (UI-text) – båda från Google Fonts
- **Lagfärger:** CSS-variabler `--team-0` t.o.m. `--team-4`

| Variable | Hex | Lag |
|----------|-----|-----|
| `--team-0` | `#4a9eff` | Ante (blå) |
| `--team-1` | `#e07b39` | Majscht (orange) |
| `--team-2` | `#7ec86a` | Olle (grön) |
| `--team-3` | `#c97de0` | Hasse (lila) |
| `--team-4` | `#e8b84b` | Dawod (guld/gul) |

- **Mobilanpassning:** Hamburgermeny på ≤640px, flexbox-stacking, responsiv typografi
- **Signatur:** "Made by: David Hefner" i footern

---

## Felsökning – vanliga problem

| Problem | Trolig orsak | Lösning |
|---------|-------------|---------|
| Inga live-uppdateringar i UI | Firestore-lyssning brusten | Ladda om sidan; kolla browser console |
| Scraper hittar inga poäng | 25kfantasy.com ändrat HTML-struktur | Granska `/players/`-sidan och uppdatera BeautifulSoup-selektorer |
| PokerNews-scraper misslyckas | Cookies har gått ut | Förnya `POKERNEWS_COOKIES` i GitHub Secrets |
| GitHub Actions kör inte | Cron-tid matchar inte WSOP-perioden | Uppdatera cron-uttrycket i `update-scores.yml` |
| Spelare saknas i datan | Namnmatchning felaktig | Kontrollera stavning mot 25kfantasy.com |
| SSL-fel lokalt | Windows certifi-problem | Kör via GitHub Actions istället (fungerar alltid) |
| Modal visar fel poäng | `score_history/all` saknas eller är tom | Kör `scrape_scores.py` manuellt — den bygger upp historiken automatiskt |
| Spelarmodal öppnas inte vid klick | Spelarnamn innehåller citattecken som bryts i onclick | Kontrollera att `JSON.stringify(name).replace(/"/g,'&quot;')` används |
