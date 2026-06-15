# WSOP Fantasy – Gängets liga

En realtids-webbapp för fem vänner att följa sin WSOP Pick 8 Fantasy-liga under World Series of Poker.

## Funktioner
- Ställningstabell med ranking baserat på totalpoäng
- Lagkort med alla 8 spelare per lag, individuella poäng och bracelet-vinster
- Poänghistorik grupperad per datum
- Live-flik som visar spelare vid borden i realtid (chip counts, spelare kvar)
- Schema med alla 100 WSOP bracelet-events och status (pågår/avslutat/kommande)
- Poängkalkylator för att beräkna hypotetiska poäng
- Statistik: toppspelare, bästa värdespel, bästa enskilda prestation

## Lag (2026)
- Ante
- Majscht
- Olle
- Hasse
- Dawod

## Tekniskt
- Statisk HTML-sida på GitHub Pages (ingen backend)
- Python-scrapers hämtar data från 25kfantasy.com och PokerNews
- Data sparas till Firebase Firestore (realtidsdatabas)
- GitHub Actions kör scrapers var 30:e minut under WSOP-tid
- index.html lyssnar på Firestore via onSnapshot (live-uppdateringar utan sidladdning)

## Dokumentation
Se [ARCHITECTURE.md](ARCHITECTURE.md) för fullständig teknisk dokumentation och guide för att återanvända projektet nästa år.
