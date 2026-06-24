# WSOP Fantasy – Gängets liga

En realtids-webbapp för fem vänner att följa sin WSOP Pick 8 Fantasy-liga under World Series of Poker.

## Funktioner

- **Översikt** – Ställningstabell med ranking och lagkort med alla 8 spelare, poäng, bracelet-vinster och ITM-badges
- **Schema** – Alla 100 WSOP bracelet-events med status (pågår/avslutat/kommande), klickbara för att se cashes
- **Historik** – Poänghistorik grupperad per datum
- **Poängkalkylator** – Beräkna hypotetiska poäng för en placering i valfritt event
- **Live** – Spelare vid borden i realtid med chip counts, antal spelare kvar och BB-visning
- **Lag-statistik** – Historiska WSOP-karriärmeriter per lag (vinster, cashes, armband, final tables) med stapeldiagram

## Navigation

På **desktop** visas alla flikar i en rad längst upp. På **mobil** ersätts flikraden av en hamburgermeny (☰ MENY) som öppnar en panel från höger.

## Lag (2026)

| Lag | Färg |
|-----|------|
| Ante | Blå |
| Majscht | Orange |
| Olle | Grön |
| Hasse | Lila |
| Dawod | Guld/gul |

## Tekniskt

- Statisk HTML-sida på GitHub Pages (ingen backend)
- Python-scrapers hämtar data från 25kfantasy.com och PokerNews
- Data sparas till Firebase Firestore (realtidsdatabas)
- GitHub Actions kör scrapers var 30:e minut under WSOP-tid
- `index.html` lyssnar på Firestore via `onSnapshot` (live-uppdateringar utan sidladdning)

## Dokumentation

Se [ARCHITECTURE.md](ARCHITECTURE.md) för fullständig teknisk dokumentation och guide för att återanvända projektet nästa år.
