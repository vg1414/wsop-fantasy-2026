# WSOP Fantasy 2026 – Gängets liga

En enkel webbsida för att följa fem vänners WSOP Pick 8 Fantasy-lag under WSOP 2026.

## Funktioner
- Ställningstabell med ranking baserat på totalpoäng
- Alla 5 lags spelare listade med individuella poäng
- Poäng hämtas automatiskt från 25kfantasy.com var 30:e minut via GitHub Actions
- Visar senaste uppdateringstid

## Lag
- Dawod
- Olle
- Ante
- Majscht
- Hasse

## Tekniskt
- Statisk HTML-sida på GitHub Pages
- Python-script scraper poäng och sparar till `scores.json`
- GitHub Actions kör scriptet var 30:e minut
