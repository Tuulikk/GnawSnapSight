# GnawSnapSight

Ett minimalistiskt verktyg för agenter att "se" applikationer.

## Funktioner
- Starta en applikation och vänta på att den laddar.
- Ta en screenshot av det aktiva fönstret (renare än hela skärmen).
- Skicka bilden till Ollama för automatisk beskrivning (Vision).
- **Verifiering av fönstertitel:** Använd vision-modellen för att bekräfta att rätt fönster har fångats, med automatisk retry om fokus missades.
- **Flexibel prompt:** Ställ specifika frågor om UI:t ("Finns det felmeddelanden?", "Beskriv layouten på knapparna").

## Krav
- `spectacle` (KDE skärmbildsverktyg)
- `python3` + `requests`
- (Valfritt) `ollama` med en vision-modell (t.ex. `llama3.2-vision:11b` eller `llava`)

## Användning

### Grundläggande analys med verifiering
Starta kalkylatorn och säkerställ att det är rätt fönster som beskrivs:
```bash
./gnawsnapsight.py --launch "kcalc" --expect-title "Kcalc" --describe
```

### Specifika frågor (Refaktorisering / Datautvinning)
Fråga efter specifik information i gränssnittet:
```bash
./gnawsnapsight.py --launch "kcalc" --prompt "What is the background color of the numeric buttons?"
```

## Argument
- `--launch <cmd>`: Kommando för att starta applikationen.
- `--delay <sek>`: Väntetid innan screenshot tas (default: 2.0).
- `--describe`: Utför en standardanalys av fönstret.
- `--prompt "<text>"`: Ställ en specifik fråga till vision-modellen.
- `--expect-title "<titel>"`: Verifiera att fönstret innehåller denna titel via vision-modellen.
- `--model <namn>`: Ollama-modell (default: `llama3.2-vision:11b`).
- `--output <fil>`: Filnamn för screenshot (default: `snap.png`).
- `--ollama-url <url>`: URL till Ollama API (default: `http://localhost:11434`).
