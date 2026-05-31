# CHANGELOG

## 2026-05-31 (uppdatering 2)
- Schema: "Event #N" har nu samma färg som turneringsnamnet (vit/guld/dämpad beroende på status)
- Schema: buy-in kolumn är nu riktigt högerkantsanpassad i grid
- Schema: teamfärgprickar visas direkt efter spelarnamnet i expanderade events
- Schema: event-statuser (avslutad/pågår/kommande) hämtas nu från 25kfantasy.com/events via scraper

## 2026-05-31
- Ny flik "Schema" med alla 100 WSOP 2026 bracelet events (datum och buy-in)
- Events som pågår visas i guld, avslutade dämpas med lägre opacity
- Klicka på ett event för att expandera och se vilka av våra spelare som cashat
- Grön blinkande prick på events där en spelare är live just nu
- Färgprickar per lag på varje event (samma färger som övriga flikar)
- Legend med lagfärger på Schema-fliken

## 2026-05-29
- Mobilfixar: status-bar staplas vertikalt (text + knapp) istället för att klämmas i grid
- Live-fliken: spelarnamn och turneringsnamn staplas nu i en rak kolumn på mobil
- Live-fliken: spelarnamn klipps inte längre av på desktop (bredare namnkolumn)
- Flik-knappar (Översikt, Poänghistorik, Live): större och tydligare text på mobil
- Mobilläsbarhet: höjt font-size på alla element som var för små (status-bar, section-labels, live-event, live-legend, mm)

## 2026-05-29 (Firebase-integration)
- Bytte datakälla från scores.json (GitHub Actions commit) till Firestore realtidsdatabas
- scrape_scores.py skriver nu direkt till Firestore istället för lokal fil
- index.html använder Firestore SDK med onSnapshot (live-uppdateringar utan polling)
- GitHub Actions workflow optimerad: kör bara under WSOP-tid (20:00–13:00 svensk tid)
- Service account-nyckel hanteras säkert via GitHub Secret (FIREBASE_SERVICE_ACCOUNT)
- Lade till .gitignore som skyddar mot att nycklar råkar committas

## 2026-05-29 (spelarlista)
- Lade till ny sektion "Spelare" – alla unika spelare sorterade efter poäng (högst först)
- Varje spelare visar vilka lag de ingår i som små taggar (spelare kan delas mellan lag)

## 2026-05-29 (redesign)
- Fullständig WSOP-inspirerad redesign: grön felt-bakgrund, guld-typografi, Cinzel-font, kortsymboler, bracelet-dekoration
- Förbättrad mobilanpassning
- Subtexten "Gängets liga — Pick 8" borttagen från headern

## 2026-05-29 (uppdatering)
- Korrigerade lagtilldelning: Ante→Arieh, Majscht→Hellmuth, Olle→Chidwick, Hasse→Deeb, Dawod→Guagenti

## 2026-05-29
- Projektet skapat
- index.html med standings och lag-kort
- scrape_scores.py som hämtar poäng från 25kfantasy.com
- GitHub Actions workflow som uppdaterar scores.json var 30:e minut
