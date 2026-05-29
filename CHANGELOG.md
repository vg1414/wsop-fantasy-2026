# CHANGELOG

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
