# Metriken-Auswahl – CryptoSim

**Projekt:** CryptoSim (Krypto-Trading-Simulation, Flask + SQLite)  
**Vorlesung:** Software Engineering – Aufgabenblatt 17 (Metriken)  
**Datum:** Mai 2026

---

## Übersicht

Zusätzlich zu den Softwaretest-Metriken (Code-Coverage via `pytest-cov`) messen wir drei weitere Metriken. Alle drei werden mit dem Python-Paket [`radon`](https://radon.readthedocs.io/) berechnet und automatisch in der CI/CD-Pipeline ausgegeben.

| # | Metrik | Tool | Befehl |
|---|--------|------|--------|
| 1 | Zyklomatische Komplexität | `radon cc` | `radon cc . -a -s` |
| 2 | Wartbarkeitsindex (Maintainability Index) | `radon mi` | `radon mi . -s` |
| 3 | Raw Metrics (LOC, Kommentaranteil) | `radon raw` | `radon raw . -s` |

---

## Metrik 1: Zyklomatische Komplexität (Cyclomatic Complexity)

### Was wird gemessen?

Die zyklomatische Komplexität zählt die Anzahl der linear unabhängigen Pfade durch eine Funktion. Für jede Kontrollstruktur (`if`, `elif`, `for`, `while`, `except`, `and`, `or`) wird der Wert um 1 erhöht. Eine Funktion ohne Verzweigung hat den Wert 1.

Radon bewertet das Ergebnis mit Buchstaben:

| Komplexität | Note | Bedeutung |
|-------------|------|-----------|
| 1–5 | A | Einfach, kein Risiko |
| 6–10 | B | Mäßig komplex |
| 11–15 | C | Komplex |
| 16–20 | D | Sehr komplex |
| 21–25 | E | Fehlerhaft |
| 26+ | F | Nicht testbar |

### Warum diese Metrik?

Im Rahmen des Clean-Code-Refactorings (April 2026) wurde `market_service.py` gezielt vereinfacht: Die ursprüngliche `execute_trade`-Methode vermischte Validierung, Datenbankzugriff und Geschäftslogik und wies dadurch eine hohe Komplexität auf. Nach dem IOSP-Refactoring verteilt sich die Logik auf kleine, fokussierte Hilfsmethoden mit je niedriger Komplexität.

Ähnlich ist die `/trade`-Route in `app.py` durch die drei Modi (AMOUNT, EUR, PERCENT) und mehrfache Fehlerbehandlung naturgemäß komplexer – die Metrik hilft, diesen Tradeoff zu dokumentieren und zu begründen, warum dort keine weitere Aufteilung sinnvoll ist (Route-Handler müssen den vollständigen HTTP-Kontext kennen).

Die zyklomatische Komplexität zeigt direkt, welche Teile unseres Projekts gut vereinfacht wurden und wo bewusst Komplexität akzeptiert wird.

### Wie wird sie berechnet?

```bash
radon cc cryptosim/ -a -s
```

`-a` gibt den Durchschnitt aller Funktionen aus, `-s` zeigt die Note (A–F) je Funktion.

---

## Metrik 2: Wartbarkeitsindex (Maintainability Index)

### Was wird gemessen?

Der Wartbarkeitsindex (MI) ist eine zusammengesetzte Metrik, die aus drei Einzelwerten berechnet wird:

```
MI = 171 - 5.2 * ln(V) - 0.23 * CC - 16.2 * ln(LOC)
```

- **V** = Halstead-Volumen (basiert auf Anzahl eindeutiger Operatoren/Operanden)
- **CC** = Zyklomatische Komplexität
- **LOC** = Logische Zeilen Code

Radon normalisiert den Wert auf 0–100 (höher = besser):

| MI-Wert | Bewertung |
|---------|-----------|
| 20–100 | Gut wartbar |
| 10–19 | Mäßig wartbar |
| 0–9 | Schlecht wartbar |

### Warum diese Metrik?

Der Wartbarkeitsindex gibt einen kompakten Gesamteindruck der Codequalität je Datei. Er lohnt sich besonders für unser Projekt, weil das Refactoring (Clean Code, April 2026) gezielt auf Wartbarkeit ausgerichtet war – kürzere Methoden, DRY-Prinzip, einheitliche Abstraktionsebenen. Der MI macht diesen Fortschritt in einer einzigen Zahl sichtbar und ist damit ideal für den Projektabschlussbericht.

Da `market_service.py` nach dem Refactoring in viele kleine Methoden aufgeteilt wurde, erwarten wir dort einen deutlich besseren MI als vor der Änderung. Dateien wie `coin_sync_service.py`, die API-Aufrufe und komplexe Synchronisationslogik enthalten, werden erwartungsgemäß einen niedrigeren MI aufweisen – was aber akzeptabel ist, da diese Komplexität durch die externe API-Abhängigkeit begründet ist und keine sinnvollere Aufteilung möglich ist.

### Wie wird sie berechnet?

```bash
radon mi cryptosim/ -s
```

`-s` zeigt die Note (A = gut, B = mittel, C = schlecht) je Datei.

---

## Metrik 3: Raw Metrics (LOC & Kommentaranteil)

### Was wird gemessen?

`radon raw` liefert für jede Datei mehrere Rohwerte:

| Kürzel | Bedeutung |
|--------|-----------|
| LOC | Lines of Code (alle Zeilen) |
| LLOC | Logical Lines of Code (Anweisungen) |
| SLOC | Source Lines of Code (Code ohne Kommentare/Leerzeilen) |
| Comments | Kommentarzeilen |
| Multi | Mehrzeilige Strings (Docstrings) |
| Blank | Leerzeilen |

Der **Kommentaranteil** ergibt sich als `Comments / LOC`. Er zeigt, ob Code ausreichend (aber nicht übermäßig) dokumentiert ist.

### Warum diese Metrik?

Im Clean-Code-Prinzip gilt: Code soll durch aussagekräftige Namen selbsterklärend sein, nicht durch Kommentare. Gleichzeitig sind Kommentare dort wichtig, wo das WIE nicht offensichtlich ist (z. B. die `bisect`-basierte Preis-Lookup-Logik in `_build_price_lookup`).

Die Raw-Metrics helfen uns:

1. **Modulgröße nachvollziehen**: `market_service.py` ist mit ~310 LOC die größte Datei. Die Metrik zeigt, ob das Wachstum proportional zur Logik ist.
2. **Kommentarqualität bewerten**: Ein hoher Kommentaranteil in einer einfachen Datei ist ein Warnsignal (Code erklärt sich nicht selbst). Ein niedriger Kommentaranteil in einer komplexen Datei (z. B. `coin_sync_service.py`) ist akzeptabel, solange die Methodennamen sprechend sind.
3. **Gesamtprojektgröße tracken**: Im Projektabschlussbericht können wir damit die Entwicklung der Codebasis über Zeit darstellen.

### Wie wird sie berechnet?

```bash
radon raw cryptosim/ -s
```

`-s` gibt am Ende eine Zusammenfassung über alle Dateien aus.

---

## Zusammenfassung: Warum genau diese drei?

| Kriterium | CC | MI | LOC/Raw |
|-----------|----|----|---------|
| Zeigt Refactoring-Erfolg | ✓ | ✓ | teilweise |
| Verknüpft mit Clean-Code-Prinzipien | ✓ | ✓ | ✓ |
| Einfach in CI/CD integrierbar | ✓ | ✓ | ✓ |
| Erfordert kein externes System | ✓ | ✓ | ✓ |
| Erklärt Tradeoffs (bewusst schlechte Werte) | ✓ | ✓ | teilweise |

Alle drei Metriken lassen sich mit einem einzigen Python-Paket (`radon`) berechnen, erfordern keine externe Infrastruktur und produzieren aussagekräftige Ergebnisse für den Projektabschlussbericht. Sie ergänzen die bereits vorhandene Test-Coverage-Metrik, ohne diese zu duplizieren.
