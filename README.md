# GnawSnapSight

Ett minimalistiskt verktyg för agenter att "se" applikationer.

## Funktioner
- Starta en applikation och vänta på att den laddar.
- Ta en screenshot av det aktiva fönstret (renare än hela skärmen).
- Skicka bilden till Ollama för automatisk beskrivning (Vision).
- **Flexibel prompt:** Ställ specifika frågor om UI:t ("Finns det felmeddelanden?", "Beskriv layouten på knapparna").

## Krav
- `spectacle` (KDE skärmbildsverktyg)
- `python3` + `requests`
- (Valfritt) `ollama` med en vision-modell (t.ex. `llama3.2-vision:11b` eller `llava`)

## Användning

### Grundläggande analys
Starta kalkylatorn och få en allmän beskrivning:
```bash
./gnawsnapsight.py --launch "kcalc" --delay 3 --describe
```

### Specifika frågor (Refaktorisering / Datautvinning)
Fråga efter specifik information i gränssnittet:
```bash
./gnawsnapsight.py --launch "kcalc" --delay 3 --prompt "What is the background color of the numeric buttons?"
```

```bash
./gnawsnapsight.py --delay 0 --prompt "Is there an error message visible in this window? If yes, what does it say?"
```

## Argument
- `--launch <cmd>`: Kommando för att starta applikationen.
- `--delay <sek>`: Väntetid innan screenshot tas (default: 2.0).
- `--describe`: Utför en standardanalys av fönstret.
- `--prompt "<text>"`: Ställ en specifik fråga till vision-modellen (implicerar `--describe`).
- `--model <namn>`: Ollama-modell (default: `llama3.2-vision:11b`).
- `--output <fil>`: Filnamn för screenshot (default: `snap.png`).