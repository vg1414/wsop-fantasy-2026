# CHANGELOG

## 2026-07-10
- Fix: garanterade poäng ("Låst" i Live-fliken) visade fel/för lite (t.ex. Suzuki visade 1p istället för 48p) eftersom vår egen uträkning saknade antal anmälda (entrants) för events som PokerNews inte hunnit publicera resultat för. Läser nu av 25kfantasys egna "Locked PTS"-kolumn direkt (snabbare uppdaterad än PokerNews) och faller tillbaka på vår egen formel med entrants från 25kfantasy om deras poängkolumn saknas
- Fix: ITM-events kunde missas i appen om PokerNews cash-sida inte hunnit uppdateras. 25kfantasys sweat-lista (som flaggar events som "(ITM)") används nu som extra källa och slås ihop med PokerNews-baserad ITM-detektering

## 2026-07-09
- Fix: Main Event (#82) och andra stora fält visade felaktigt alla spelare som bustade fast de fortfarande spelade på PokerNews. 25kfantasys sweat listar events innan de är ITM, men chip-count-tabellen är tom tills ITM faktiskt nås — ett event räknas nu bara som "ITM enligt sweat" om dess tabell faktiskt innehöll minst en rankad rad, inte bara för att eventet syns i sweat_events

## 2026-07-04
- Fix: spelare som bustat kunde hänga kvar i "Spelar just nu" i Live-fliken om PokerNews My Stable inte hunnit uppdatera status. Scrapern sätter nu status till "busted" när en spelare som tidigare var currentlyPlaying inte längre finns i 25kfantasys chip-count-data (dvs. han har fått poäng och är klar)
- Fix: föregående busted-fix var för aggressiv och flaggade felaktigt spelare med stackar kvar (t.ex. vidare till dag 2) som bustade, eftersom 25kfantasys sweat bara trackar events som nått ITM. Busted-flaggan sätts nu bara om spelarens event faktiskt är ITM enligt sweat men han saknas i det eventets chip-count-tabell — events som inte är ITM ännu lämnas orörda

## 2026-07-03
- Uppdatera-knappen visar nu "✓ Klar" i grönt (istället för "✓ Uppdaterad") när uppdateringen är klar, innan den går tillbaka till "Uppdatera"
- Live-fliken: BB (Big Blinds-antal) fick en egen kolumn istället för att klippas av på slutet av spelarraden. På desktop placerad mellan spelarnamn och live-pricken, på mobil syns den alltid intill live-pricken
- Fix: spelare som fångas via sweat-fallback (aktiva i 25kfantasy men inte som "currentlyPlaying" i PokerNews My Stable) fick fel eventnamn kvar från gammal PokerNews-data. Eventnamnet skrivs nu alltid över med sweat-datans event, så chip_rank/BB och eventnamn hör ihop.
- Fix: eventnamn normaliseras nu mot PokerNews kanoniska titel (via eventnummer) för spelare som kommer in via 25kfantasy sweat-fallback, så alla spelare i samma event visar exakt samma eventnamn (tidigare kunde 25kfantasys eget namnformat, t.ex. med "— X left (ITM)" inbakat, avvika från PokerNews-titeln)
- Uppdatera-knappen visar nu verklig status: väntar på att Firestore-datan faktiskt ändras (inte bara en fast 30s-timer) innan den visar "Uppdaterad", med en 2-minuters fallback om det tar längre tid
- Live-fliken: spelare i samma event grupperas nu ihop i listan istället för att sorteras enbart på players_left oberoende av event
- Fix: entrants (deltagarantal) för ett event kunde bli fel eftersom PokerNews tagit bort HTML-inputen #event-entrants på vissa sidor. Scrapern faller nu tillbaka på att läsa "Total Entries: N" i klartext
- Fix: players_left för spelare som fångas via 25kfantasy sweat-fallback (t.ex. spelare PokerNews My Stable inte listar som spelande) hängde kvar med värdet från spelarens gamla/felaktiga event istället för att räknas om för det korrekta eventet. Gav fel "X kvar"-siffra och fel gruppering i Live-fliken (t.ex. Jon Turner visade 12 kvar i Event #83 istället för korrekta 227)
- Live-fliken: spelare inom samma event sorteras nu på faktisk placering (chip_rank), inte bara på players_left (som är samma tal för alla i eventet). Spelare utan känd placering grupperas per fantasy-lag istället

## 2026-07-01
- Bättre kontrast på alla datum/tidsstämplar (statusrad, uppdatera-knapp, datumrubriker i historik/spelarmodal/schema, "Fantasy · 2026" i headern) för läsbarhet i solljus på mobil
- Bättre kontrast på flikarna i menyn (Översikt, Schema, Historik, Poängberäknare, Live)

## 2026-06-25 (uppdatering 4)
- Modal: turneringsnamn är nu klickbar länk till 25kfantasy.com-sidan för respektive event (samma fönster)

## 2026-06-25 (uppdatering 3)
- Spelarmodal: öppnas nu från live-fliken, lagmodalen och statistik-fliken (alla spelarknappar)
- Lagmodal: spelarnamn klickbara, armband visas efter lagnamnet
- Lagmodal: spelarnamns utseende återställt efter knapp-konvertering

## 2026-06-25 (uppdatering 2)
- Modal: scroll-position återställs alltid till toppen när en ny modal öppnas

## 2026-06-25
- Ställning: poäng räknas upp med cubic-ease-animation vid laddning
- Modal: graderad färgskala på poäng (guld ≥100p → grönt 1p, glidande)
- Modal: spelarnamn klickbara i lagkorten öppnar spelarens egna resultatmodal
- Spelarmodal: visar värde i parentes efter namn, armband efter namnet
- Buggfix: `JSON.stringify` med dubbla citattecken bröt onclick-attribut för spelarknappar

## 2026-06-24
- Ny flik "Lag-statistik" med historiska WSOP-karriärmeriter per lag (vinster, cashes, armband, final tables) som stapeldiagram med lagfärger
- Lagnamn i statistik-fliken visas i respektive lags färg
- Fotnot i statistik-fliken: "Statistiken avser karriärmeriter t.o.m. innan WSOP 2026"
- Nytt skript `seed_wsop_stats.py` med hardkodad statistik för alla 33 spelare (hämtad från wsop.com)
- Nytt GitHub Actions-workflow `seed-stats.yml` för manuell seeding av historisk statistik
- Hamburgermeny på mobil (≤640px): flikraden ersätts av ☰ MENY-knapp med panel som glider in från höger
- Hamburgerknapp: guldglimmer-animation vid sidladdning (10 pulser), ikon roterar 90° när menyn är öppen
- Live-flik: borttagen redundant "Uppdaterad"-rad (visas redan i statusbaren)
- Dokumentation: ARCHITECTURE.md och README.md uppdaterade med allt nytt

## 2026-06-15
- Fix: multiplier-bugg där events med $50k+ buy-in (t.ex. #29 $50k, #36 $100k, #41 $250k) felaktigt fick 3x istället för 2x — nu får alla $10k+-events 2x, och 3x gäller enbart #82 (Main Event) och #60 (Poker Players Championship)

## 2026-06-08
- Översikt: antal ITM (cashes) visas inom parantes efter spelarens poäng i lagkorten, t.ex. "61 (1)"
- Live: chip-rank visas nu för ITM-spelare (t.ex. "5/7") från 25kfantasy sweat-API; för övriga spelas fortfarande "X kvar" baserat på players_left
- Scraper: scrape_pokernews.py hämtar nu chip_rank per spelare via 25kfantasy.com/process/sweat

## 2026-06-05
- Översikt: ITM-badge visas nu även bredvid spelares namn i lagkorten (precis som på live-sidan), när spelaren är in the money och inte på finalbord
- Översikt: spelarpoängen i lagkorten följer nu lagets färg (blå, orange, grön, lila, guld) istället för att alltid vara grön

## 2026-06-04
- Dokumentation: skapade ARCHITECTURE.md med fullständig teknisk guide, dataflöden, poängsystem och checklista inför nya säsonger
- README.md: uppdaterades att reflektera nuvarande funktioner (5 flikar, Firestore-arkitektur)

## 2026-06-03
- Live: FT-badge (guldglödande) visas efter spelarnamn och lagnamn i ställningen när en spelare är på finalbord (<10 spelare kvar)
- Scraper: hämtar nu "players_left" från PokerNews chip counts-sida per aktiv turnering

## 2026-06-01
- Schema: fix för spelare med dubbla Firebase-poster (t.ex. Joao Simao Peres) – väljer nu posten med event_url istället för alltid första träffen


- GitHub Actions triggas automatiskt vid sidladdning (inte bara via knapp)

## 2026-05-31 (uppdatering 3)
- Ställning: 🥇 visas efter ägarnamnet för varje bracelet-vinst (placement = 1) i laget

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
