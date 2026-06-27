# Testbericht – CryptoBroker (Cryptosim)

**Projekt:** CryptoBroker / Cryptosim  
**Version:** 1.0  
**Stand:** 2026-06-27  
**Kurs:** Software Engineering – TINF24B4  

---

## 1. Einleitung

Dieser Testbericht dokumentiert die Ergebnisse der Testaktivitäten für das CryptoBroker-Projekt (Cryptosim). Das System ist eine Flask-basierte Webanwendung zur Simulation von Kryptowährungshandel. Der Testprozess umfasst Unit-Tests und Integrationstests des Service-Layers sowie automatisierte Ausführung über eine CI/CD-Pipeline.

**Umfang der Testaktivitäten:**
- Service-Layer (`services/market_service.py`) vollständig getestet
- Drei Testdateien mit insgesamt 35 Testfällen
- Automatische Ausführung bei jedem Push und Pull Request via GitHub Actions

---

## 2. Teststrategie

### Testmethodik

Der Testfokus liegt bewusst auf dem Service-Layer, da dort die gesamte kritische Geschäftslogik konzentriert ist: Guthaben-Berechnung, Positions-Berechnung, Trade-Validierung und Order-Verarbeitung. Flask-Routen, Templates und der CoinGecko-Sync-Service werden bewusst nicht getestet, da diese stark von externen Abhängigkeiten (API, Browser) abhängen und mit vertretbarem Aufwand nicht sinnvoll isoliert testbar sind.

### Testarten

| Testart | Werkzeug | Dateien |
|---|---|---|
| Unit-Tests | pytest | `test_market_service.py`, `test_place_order.py` |
| Integrationstests | pytest | `test_trade_flow.py` |
| Coverage-Messung | pytest-cov | automatisch in CI |
| Smoke-Test | Docker + curl | in CI-Pipeline |

### Testumgebung

- **Isolierung:** Jeder Test erhält eine frische SQLite-In-Memory-Datenbank via `conftest.py`-Fixtures. Keine gemeinsamen Zustände zwischen Tests.
- **Externe APIs:** werden nicht aufgerufen. Die `coin_sync_service`-Schicht wird nicht getestet.
- **Python-Version:** 3.13 (GitHub Actions Runner: Ubuntu)

### Automatisierte Testwerkzeuge

- `pytest` – Test-Runner
- `pytest-cov` – Coverage-Messung
- GitHub Actions – CI/CD-Pipeline (Trigger: Push auf `main`, Pull Requests)

---

## 3. Testplan

Der vollständige Testplan ist in `docs/Tests/Testplan.md` dokumentiert. Dieser Bericht referenziert die dort definierten Testfall-IDs (U1–U16, P1–P17, I1–I2).

**Geplante Testabdeckung:** ≥ 80 % auf `services/market_service.py`  
**Tatsächlich erreichte Abdeckung:** 92 %

---

## 4. Testfälle und Ergebnisse

### 4.1 Unit-Tests – `test_market_service.py`

| ID | Testfall | Use Case | Status | Fehler |
|---|---|---|---|---|
| U1 | Startguthaben ohne Transaktionen | UC View Crypto Data | ✅ bestanden | – |
| U2 | Kauf reduziert Balance korrekt | UC Crypto Kaufen | ✅ bestanden | – |
| U3 | Verkauf erhöht Balance korrekt | UC Crypto Verkaufen | ✅ bestanden | – |
| U4 | Position nach Kauf korrekt | UC Crypto Kaufen | ✅ bestanden | – |
| U5 | Position nach vollständigem Verkauf = 0 | UC Crypto Verkaufen | ✅ bestanden | – |
| U6 | Kauf ohne ausreichendes Guthaben | UC Crypto Kaufen | ✅ bestanden | – |
| U7 | Verkauf ohne ausreichende Position | UC Crypto Verkaufen | ✅ bestanden | – |
| U8 | Ungültige Trade-Aktion | UC Crypto Kaufen | ✅ bestanden | – |
| U9 | Trade mit unbekanntem Coin | UC Crypto Kaufen | ✅ bestanden | – |
| U10 | Historische Daten ohne History-Tabelle | UC View Crypto Data | ✅ bestanden | – |
| U11 | Historische Daten für unbekannten Coin | UC View Crypto Data | ✅ bestanden | – |
| U12 | Transaktionshistorie nach Kauf | UC Crypto Kaufen | ✅ bestanden | – |
| U13 | Gehandelte Coins ohne Trades | UC View Crypto Data | ✅ bestanden | – |
| U14 | Gehandelte Coins nach Kauf | UC Crypto Kaufen | ✅ bestanden | – |
| U15 | Portfolio-Verlauf ohne Trades | UC View Crypto Data | ✅ bestanden | – |
| U16 | Portfolio-Verlauf mit Kauf und Preishistorie | UC Crypto Kaufen | ✅ bestanden | – |

### 4.2 Unit-Tests – `test_place_order.py`

| ID | Testfall | Use Case | Status | Fehler |
|---|---|---|---|---|
| P1 | AMOUNT-Modus: Wert direkt als Menge | UC Crypto Kaufen | ✅ bestanden | – |
| P2 | EUR-Modus: EUR-Betrag wird umgerechnet | UC Crypto Kaufen | ✅ bestanden | – |
| P3 | PERCENT-Modus: 50 % der Position verkaufen | UC Crypto Verkaufen | ✅ bestanden | – |
| P4 | Komma als Dezimaltrennzeichen | UC Crypto Kaufen | ✅ bestanden | – |
| P5 | Unbekannter Modus fällt auf AMOUNT zurück | UC Crypto Kaufen | ✅ bestanden | – |
| P6 | Nicht-numerischer Wert → ValueError | UC Crypto Kaufen | ✅ bestanden | – |
| P7 | Wert = 0 → ValueError | UC Crypto Kaufen | ✅ bestanden | – |
| P8 | Negativer Wert → ValueError | UC Crypto Kaufen | ✅ bestanden | – |
| P9 | Unbekannter Coin → ValueError | UC Crypto Kaufen | ✅ bestanden | – |
| P10 | Coin mit Preis 0 → ValueError | UC Crypto Kaufen | ✅ bestanden | – |
| P11 | Unter Mindestbetrag → ValueError | UC Crypto Kaufen | ✅ bestanden | – |
| P12 | PERCENT beim Kauf → ValueError | UC Crypto Kaufen | ✅ bestanden | – |
| P13 | PERCENT > 100 → ValueError | UC Crypto Verkaufen | ✅ bestanden | – |
| P14 | PERCENT ohne Position → ValueError | UC Crypto Verkaufen | ✅ bestanden | – |
| P15 | Kauf ohne Guthaben → ValueError | UC Crypto Kaufen | ✅ bestanden | – |
| P16 | Verkauf mehr als Bestand → ValueError | UC Crypto Verkaufen | ✅ bestanden | – |
| P17 | Erfolgreicher Kauf persistiert Transaktion | UC Crypto Kaufen | ✅ bestanden | – |

### 4.3 Integrationstests – `test_trade_flow.py`

| ID | Testfall | Use Case | Status | Fehler |
|---|---|---|---|---|
| I1 | Kauf-Verkauf-Zyklus stellt Balance wieder her | UC Kaufen + Verkaufen | ✅ bestanden | – |
| I2 | Mehrere Käufe kumulieren korrekt | UC Crypto Kaufen | ✅ bestanden | – |

**Gesamtergebnis: 35 / 35 Tests bestanden – 0 Fehler**

---

## 5. Testergebnisse

### Zusammenfassung

| Metrik | Wert |
|---|---|
| Testfälle gesamt | 35 |
| Bestanden | 35 |
| Fehlgeschlagen | 0 |
| Übersprungen | 0 |
| Testdateien | 3 |
| Testklassen | 10 |

### Gefundene Fehler

Während des Entwicklungsprozesses wurden folgende Fehler durch Tests aufgedeckt und behoben:

| # | Fehler | Schweregrad | Behebung |
|---|---|---|---|
| F1 | `place_order` akzeptierte Komma nicht als Dezimaltrenner | Mittel | Eingabe-Parsing um Komma-Ersatz ergänzt |
| F2 | PERCENT-Modus war ursprünglich auch für Kauf erlaubt | Mittel | Guard-Klausel in `place_order` ergänzt |
| F3 | Coin mit Preis 0 führte zu Division-by-Zero | Hoch | Validierung des Preises vor Berechnung ergänzt |

Alle gefundenen Fehler wurden vor dem Merge in den `main`-Branch behoben.

---

## 6. Metriken

| Metrik | Wert |
|---|---|
| Code Coverage `market_service.py` | 92 % |
| Coverage-Schwellwert (CI schlägt fehl bei) | < 80 % |
| Anzahl gefundener Fehler | 3 |
| Durchschnittliche Fehlerbehebungszeit | < 1 Sprint |
| Testausführungszeit (lokal) | ca. 0,8 s |
| Testausführungszeit (GitHub Actions) | ca. 25 s (inkl. Setup) |

### Coverage-Details `market_service.py`

| Methode | Abgedeckt |
|---|---|
| `get_balance` | ✅ |
| `get_position` | ✅ |
| `execute_trade` | ✅ |
| `place_order` | ✅ |
| `get_history` | ✅ |
| `get_transactions` | ✅ |
| `get_traded_coin_ids` | ✅ |
| `get_portfolio_history` | ✅ |

---

## 7. Empfehlungen

1. **Integrationstests erweitern:** Aktuell decken I1 und I2 nur grundlegende Trade-Zyklen ab. Szenarien mit mehreren Coins gleichzeitig oder gleichzeitigen Transaktionen wären sinnvoll.
2. **Flask-Routen testen:** Mit `pytest-flask` und einem Test-Client könnten HTTP-Endpunkte (z. B. `/dashboard`, `/buy`) geprüft werden, ohne echten Browser oder API-Abhängigkeiten.
3. **Smoke-Tests ausbauen:** Der aktuelle Smoke-Test prüft nur ob der Container startet. Ein Test ob kritische Seiten (Login, Dashboard) erreichbar sind, wäre robuster.
4. **CoinGecko-Sync mocken:** Mit `unittest.mock` könnte `coin_sync_service.py` getestet werden, ohne echte API-Anfragen zu stellen.

---

## 8. Schlussfolgerung

Die Teststrategie für CryptoBroker ist aufgegangen: Mit 35 Testfällen und 92 % Coverage auf dem kritischsten Modul des Systems (`market_service.py`) ist die Kerngeschäftslogik vollständig abgesichert. Alle drei durch Tests aufgedeckten Fehler (F1–F3) konnten behoben werden, bevor sie in Produktion gelangten.

Der Gesamtstatus der Softwarequalität ist **gut**. Die CI/CD-Pipeline stellt sicher, dass Regressionen sofort erkannt werden. Für eine Weiterentwicklung des Projekts wird empfohlen, die Testabdeckung auf Flask-Routen auszuweiten.
