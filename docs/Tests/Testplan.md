# Testplan – CryptoBroker (Cryptosim)

**Projekt:** CryptoBroker / Cryptosim  
**Version:** 1.1  
**Stand:** 2026-05-05  
**Kurs:** Software Engineering – TINF24B4  

---

## 1. Überblick

Cryptosim ist eine Flask-basierte Web-Applikation für simulierten Krypto-Handel. Der Testfokus liegt bewusst eng: Wir testen nur den Service-Layer, da dort die gesamte kritische Geschäftslogik (Balance, Positionen, Trade-Validierung) liegt. Das ist für ein 4-Personen-Team realistisch umsetzbar und ergibt die höchste Risikoreduktion pro investierter Testzeit.

**Bewusst nicht getestet:** Flask-Routen, Templates, CoinGecko-Sync.

---

## 2. Testfokus: `market_service.py`

`services/market_service.py` enthält alle kritischen Berechnungen und Validierungen:

- `get_balance(acc_id)` – EUR-Kontostand aus Transaktionen
- `get_position(acc_id, coin_id)` – Crypto-Bestand aus Transaktionen
- `execute_trade(acc_id, coin_id, action, amount)` – Kauf/Verkauf mit Validierung

Optional (Bonus, wenn Zeit bleibt): `services/portfolio_service.py`

---

## 3. Konkrete Testfälle

### Unit-Tests – `test_market_service.py`

| # | Testfall | Methode | Erwartetes Ergebnis |
|---|---|---|---|
| U1 | Startguthaben ohne Transaktionen | `get_balance` | 100.000 € |
| U2 | Kauf reduziert Balance korrekt | `get_balance` nach BUY | `100.000 - (amount × price)` |
| U3 | Verkauf erhöht Balance korrekt | `get_balance` nach SELL | Balance steigt um `amount × price` |
| U4 | Kauf ohne ausreichendes Guthaben | `execute_trade` BUY | `ValueError` |
| U5 | Verkauf ohne ausreichende Position | `execute_trade` SELL | `ValueError` |
| U6 | Ungültige Trade-Aktion | `execute_trade` mit `"HODL"` | `ValueError` |
| U7 | Position nach Kauf korrekt | `get_position` nach BUY | entspricht gekaufter Menge |
| U8 | Position nach vollständigem Verkauf | `get_position` nach BUY + SELL | 0.0 |
| U9 | Trade mit unbekanntem Coin | `execute_trade` mit ungültiger Coin-ID | `ValueError` |
| U10 | Historische Daten ohne History-Tabelle | `get_history` | leere Liste |
| U11 | Historische Daten für unbekannten Coin | `get_history` | leere Liste |
| U12 | Transaktionshistorie nach Kauf | `get_transactions` | 1 Eintrag mit korrekten Werten |
| U13 | Gehandelte Coins ohne Trades | `get_traded_coin_ids` | leere Liste |
| U14 | Gehandelte Coins nach Kauf | `get_traded_coin_ids` | enthält Coin-ID |
| U15 | Portfolio-Verlauf ohne Trades | `get_portfolio_history` | leere Liste |
| U16 | Portfolio-Verlauf mit Kauf und Preishistorie | `get_portfolio_history` | ≥ 2 Datenpunkte, Startpunkt = 100.000 € |

### Integrations-Test – `test_trade_flow.py`

| # | Testfall | Beschreibung |
|---|---|---|
| I1 | Vollständiger Trade-Zyklus | Kauf → Verkauf gleicher Menge → Balance wieder 100.000 € |
| I2 | Mehrere Käufe kumulieren korrekt | 2× BUY → Position = Summe beider Käufe |

**Gesamt: 18 Testfälle** – aufgeteilt auf 4 Personen ca. 4–5 Testfälle pro Person.

---

## 4. Testabdeckung

| Ziel | Wert |
|---|---|
| `services/market_service.py` | ≥ 80 % |
| `services/portfolio_service.py` (optional) | ≥ 80 % |

Die Coverage wird nur auf `market_service.py` gemessen, nicht global über das gesamte Projekt. Das wird mit `--cov=services.market_service` in pytest eingestellt.

---

## 5. Testwerkzeuge

| Werkzeug | Zweck |
|---|---|
| `pytest` | Test-Runner |
| `pytest-cov` | Coverage-Messung auf `services.market_service` |
| GitHub Actions | Automatische Ausführung bei Push / PR |

**Installation:**
```bash
pip install pytest pytest-cov
```

Kein `pytest-flask` nötig – Services werden direkt mit In-Memory-SQLite getestet, ohne Flask-App zu starten.

---

## 6. Teststruktur im Repository

```
cryptosim/
├── pytest.ini                   # pythonpath + testpaths
└── tests/
    ├── conftest.py              # Fixtures: in_memory_db, test_account, test_coin
    ├── test_market_service.py   # Unit-Tests U1–U16
    └── test_trade_flow.py       # Integrations-Tests I1–I2
```

---

## 7. Verwaltung der Testfälle und Rückverfolgbarkeit

### Traceability über GitHub Actions

Jeder Push auf `main` und jeder Pull Request triggert die CI-Pipeline. Die Pipeline speichert:

- **JUnit-XML** (`test-results.xml`) → GitHub Actions zeigt Passed/Failed pro Testfall
- **Coverage-HTML** → als Artifact downloadbar

Damit ist für jeden Commit-SHA nachvollziehbar, welche Testfälle bestanden oder fehlgeschlagen sind.

### Testfall-Benennung

```
test_<was_getestet_wird>_<erwartetes_ergebnis>
```

Beispiele:
- `test_get_balance_without_transactions_returns_starting_balance`
- `test_execute_trade_buy_without_funds_raises_value_error`

### Fehlgeschlagene Tests

Fehlschlagende Tests werden als Bug-Issue im GitHub-Repository angelegt und dem Scrum Board zugeordnet (Phase: Testing, Disziplin: Quality Assurance).

---

## 8. CI/CD-Integration (GitHub Actions)

Erweiterung der bestehenden `.github/workflows/ci.yml` um einen Test-Job **vor** dem Smoke-Test:

```yaml
  tests:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: cryptosim
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests with coverage
        run: |
          pytest tests/ \
            --cov=services.market_service \
            --cov-report=html:coverage-html \
            --cov-fail-under=80 \
            --junit-xml=test-results.xml \
            -v

      - name: Upload coverage report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: cryptosim/coverage-html/

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: cryptosim/test-results.xml
```

---

## 9. Testumgebung

| Eigenschaft | Wert |
|---|---|
| Betriebssystem | Ubuntu (GitHub Actions Runner) |
| Python-Version | 3.13 |
| Datenbank | SQLite In-Memory (`:memory:`) |
| Externe APIs | Nicht aufgerufen – kein Mock nötig, da `coin_sync_service` nicht getestet wird |
| Isolation | Jeder Test bekommt eine frische DB-Instanz via `conftest.py` |

---

## 10. Abnahmekriterien

Ein Build gilt als **bestanden**, wenn:

- [ ] Alle 18 Testfälle grün
- [ ] Coverage auf `services/market_service.py` ≥ 80 %
- [ ] Smoke-Test: Container startet und antwortet auf `/`
