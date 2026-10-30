# WSOP Fantasy – Gängets liga

En realtids-webbapp för fem vänner att följa sin WSOP Pick 8 Fantasy-liga under World Series of Poker.

## Funktioner

- **Översikt** – Ställningstabell med ranking och lagkort med alla 8 spelare, poäng, bracelet-vinster och ITM-badges
- **Schema** – Alla 100 WSOP bracelet-events med status (pågår/avslutat/kommande), klickbara för att se cashes
- **Historik** – Poänghistorik grupperad per datum
- **Poängkalkylator** – Beräkna hypotetiska poäng för en placering i valfritt event
- **Live** – Spelare vid borden i realtid med chip counts, antal spelare kvar och BB-visning

### Små roliga detaljer

- **Pilar upp/ner** i ställningen visar hur placeringen ändrats jämfört med dagen innan
- **Vänd lagkortet**: tryck på ett lagkort så vänds det och visar nyckeltal (cashes, armband, i pengarna, snitt per cash, bästa spelare, största cash)
- **Armband**: tryck på en armbandsikon så skjuts guldkonfetti ut och en ruta visar vilket event armbandet vanns i
- **Skimmer**: rader som fått nya poäng sedan förra uppdateringen lyser upp i guld en stund
- **Kortlek**: medan datan laddas blandas en liten kortlek
- **Vattenstämplar**: lagens spelkortssymbol ligger svagt bakom rubriken i modalerna (inte längre bakom namnen i ställningen eller på lagkorten)
- **Dra ner för att uppdatera** (mobil): en pokermark snurrar och samma uppdatering som knappen startas

## Navigation

På **desktop** visas flikarna som en flytande rad med ikoner längst upp. På **mobil** blir samma rad en flytande bottenmeny med ikoner. En glasmarkering glider till den flik man väljer, och innehållet glider in från rätt håll.

## Design

"Svart & guld": nästan svart bakgrund med varmt guldsken och en aning rött (WSOP:s egna färger) och kort av frostat glas. Rubriken är guldfärgad WSOP med glödande spelkortssymboler. Typsnitten är Oswald i rubriken och Outfit eller Plus Jakarta Sans i övrigt. Det finns mycket animationer: poäng som räknar upp, kort som glider in ett i taget, fjädrande knappar, mjuk utfällning i schemat och ett glanssvep över ledaren. Menyn har färglösa konturikoner. Modalerna (lag/spelare) kan svepas ner för att stängas på mobilen.

## Lag (2026)

| Lag | Färg |
|-----|------|
| Ante | Blå |
| Majscht | Orange |
| Olle | Mintgrön |
| Hasse | Rosa |
| Dawod | Gul |

Färgerna är valda så att de går att skilja åt även för den som är färgblind.

## Tekniskt

- Statisk HTML-sida på GitHub Pages (ingen backend)
- Python-scrapers hämtar data från 25kfantasy.com och PokerNews
- Data sparas till Firebase Firestore (realtidsdatabas)
- GitHub Actions kör scrapers var 30:e minut under WSOP-tid (pausat sedan 2026-08-25, körs nu bara när någon öppnar sidan, trycker "Uppdatera" eller drar ner på mobilen)
- `index.html` lyssnar på Firestore via `onSnapshot` (live-uppdateringar utan sidladdning)

## Dokumentation

Se [ARCHITECTURE.md](ARCHITECTURE.md) för fullständig teknisk dokumentation och guide för att återanvända projektet nästa år.
