# Metriken – Messwerte und Verbesserungen – CryptoSim

**Projekt:** CryptoSim (Krypto-Trading-Simulation, Flask + SQLite)
**Vorlesung:** Software Engineering – Aufgabenblatt 17 (Metriken)
**Datum:** Juli 2026 (Neumessung: 05.07.2026)

> Die Auswahl und Begründung der gemessenen Metriken (zyklomatische Komplexität, Wartbarkeitsindex, Raw Metrics) ist in [`metriken_auswahl.md`](metriken_auswahl.md) dokumentiert. Dieses Dokument enthält die **Messwerte**, die daraus **abgeleiteten Codeänderungen** und die **Neumessung**.

---

## 1. Messaufbau

Alle Werte werden mit [`radon`](https://radon.readthedocs.io/) über den Kerncode gemessen (`app.py`, `services/`, `models/` – Testcode ausgeschlossen), identisch zur Messung in der CI/CD-Pipeline:

```bash
radon cc cryptosim -a -s --exclude "tests/*"   # zyklomatische Komplexität
radon mi cryptosim -s --exclude "tests/*"      # Wartbarkeitsindex
radon raw cryptosim -s --exclude "tests/*"     # Raw Metrics (LOC/SLOC/Kommentare)
```

---

## 2. Erstmessung (Mai 2026)

| Metrik | Wert |
|---|---|
| Ø zyklomatische Komplexität | **A (2,9)** über 76 Blöcke |
| Schlechtester Block | `/trade`-Route in `app.py`: **D (21)** |
| `execute_trade` (nach IOSP-Refactoring) | **A (1)** |
| Umfang Kerncode | ~930 SLOC |

Wartbarkeitsindex (MI) je Modul – alle Rang „A", aber mit deutlichen Unterschieden:

| Modul | MI (Mai 2026) |
|---|---|
| `models/coin.py`, `models/transaction.py`, `models/database.py` | 100 |
| `models/favorite.py` | 70 |
| `services/coin_sync_service.py` | 60 |
| `services/portfolio_service.py` | 56 |
| `models/account.py` | 54 |
| `app.py` | **42** |
| `services/market_service.py` | **34** |

**Interpretation:** Der Durchschnitt war gut, aber zwei Auffälligkeiten stachen heraus: die `/trade`-Route als einziger D-Block und `app.py` als Modul mit auffällig niedrigem MI. Beides wurde zu konkreten Maßnahmen.

---

## 3. Abgeleitete Codeänderungen und ihre Wirkung

### 3.1 `/trade`-Route: D (21) → B (7)

**Befund:** Die Route vermischte HTTP-Handling mit der kompletten Handelslogik (drei Eingabemodi: Menge / EUR-Betrag / Prozent des Bestands bzw. Guthabens, jeweils mit Validierung).

**Maßnahme:** Die gesamte Auflösung der Eingabemodi wurde als `place_order()` in den Service-Layer extrahiert (Thin Controller – Fat Service). Die Route enthält nur noch HTTP-Kontext:

```python
@app.route("/trade/<coin_id>", methods=["POST"])
@login_required
def trade(coin_id):
    ...
    market_service.place_order(acc_id, coin_id, action, mode, raw_value)
    ...
```

Die Modus-Auflösung liegt jetzt in kleinen Service-Methoden (`_resolve_amount`, `_amount_from_percent`, `_parse_positive_value`), die jede für sich **A (4)** oder besser sind und einzeln testbar wurden.

**Wirkung:** `/trade` = **B (7)**, `place_order` = **A (2)**. Der einzige D-Block des Projekts ist beseitigt.

### 3.2 `app.py`: MI 42 → 48 trotz neuer Features

**Befund:** Der niedrige MI von `app.py` kam vor allem durch die in fast jeder Route duplizierte Login-Prüfung (`session.get(...)` + Redirect) zustande – derselbe Befund wurde unabhängig davon auch im technischen Review (Befund #2) erhoben.

**Maßnahme:** Zentraler `@login_required`-Decorator, der die Prüfung an einer Stelle kapselt; die fünf geschützten Routen sind nur noch annotiert. Zusätzlich wurden `import datetime` und die Konstante `MIN_TRADE_EUR` an den Modulanfang verschoben (Review-Befund #5; die Konstante liegt jetzt fachlich korrekt in `market_service.py`).

**Wirkung:** MI von `app.py` stieg von **42 auf 48**, obwohl seit der Erstmessung neue Routen (Leaderboard, Passwort ändern, Favoriten) hinzukamen.

### 3.3 IOSP- und DRY-Refactorings in `market_service.py` und `account.py`

Die in [`Refactoring_summary_cleancode.md`](../Refactoring_summary_cleancode.md) dokumentierten Maßnahmen (IOSP bei `execute_trade`, Aufteilung der ~100 Zeilen langen `get_portfolio_history`, Entflechtung von `login_or_register`) spiegeln sich direkt in den Messwerten: `execute_trade` = **A (1)**, `get_portfolio_history` = **A (2)**, und sämtliche daraus entstandenen Hilfsmethoden liegen bei **A (≤ 5)**. Kein einziger Block des Trading-Kernmoduls ist schlechter als **B (7)**.

---

## 4. Bewusst nicht veränderte Stellen (schlechtere Werte ohne Handlungsbedarf)

Nicht jeder auffällige Messwert ist ein Problem. Folgende Stellen haben wir geprüft und **bewusst unverändert** gelassen:

**`PortfolioService.get_leaderboard` – C (11), schlechtester Block des Projekts.** Die Methode berechnet das Gesamtvermögen aller Accounts: Sie lädt Accounts, Preise und alle Transaktionen jeweils genau einmal, klassifiziert dann jede Transaktion (BUY/SELL) und baut die sortierte Bestenliste auf. Die Komplexität entsteht durch mehrere flache, aufeinander folgende Schleifen mit einfachen Fallunterscheidungen – nicht durch tiefe Verschachtelung. Ein Aufteilen würde den eng zusammenhängenden Zustand (Cash- und Bestands-Dictionaries pro Account) über mehrere Methoden verstreuen und die Lesbarkeit eher verschlechtern. Der Ablauf ist linear von oben nach unten lesbar und pro Schritt kommentiert; C (11) liegt zudem noch klar unter der üblichen Warnschwelle von 15–20.

**`CoinSyncService.sync_coin_history` – B (9).** Die erhöhte Komplexität stammt aus bewusst defensiver Fehlerbehandlung rund um die externe CoinGecko-API (Guard Clauses für fehlende Daten, API-Fehler, leere Antworten). Robustheit bei API-Ausfall war ein explizites Review-Kriterium für dieses Modul – die Guards zu entfernen würde die Metrik verbessern, aber die Robustheit verschlechtern.

**`services/market_service.py` – MI 34, niedrigster Wert des Projekts.** Der MI bestraft primär die Modullänge (330 LOC), nicht die Komplexität: Das Modul besteht nach den Refactorings aus vielen kleinen Methoden (Ø-Komplexität der Blöcke: A). Es bündelt bewusst die gesamte Handelsdomäne (Kauf/Verkauf, Portfolio-Berechnung, Validierung); ein Aufteilen in mehrere Dateien würde die fachliche Kohäsion zerreißen. Der Wert ist mit Rang „A" (Schwelle: ≥ 20) weiterhin unkritisch.

**`models/transaction.py` – MI 100 → 62.** Die Verschlechterung ist reines Wachstum: Für Portfolio und Leaderboard kamen neue Abfragemethoden hinzu (`net_cash_flow`, `traded_coin_ids`, `for_account_with_coin_info`). Jede einzelne Methode liegt bei **A (≤ 2)**; der gesunkene MI reflektiert nur die größere Dateilänge.

---

## 5. Neumessung (05.07.2026)

| Metrik | Mai 2026 | **Juli 2026** | Veränderung |
|---|---|---|---|
| Ø zyklomatische Komplexität | A (2,9) / 76 Blöcke | **A (2,68) / 87 Blöcke** | ✅ besser, trotz +11 Blöcken (neue Features) |
| Schlechtester Block | `/trade` **D (21)** | `get_leaderboard` **C (11)** | ✅ kein D/E-Block mehr; genau 1 C-Block (begründet, s. Kap. 4) |
| `/trade`-Route | D (21) | **B (7)** | ✅ |
| `execute_trade` | A (1) | **A (1)** | unverändert gut |
| Umfang Kerncode | ~930 SLOC | 958 SLOC | Wachstum durch neue Features |

Wartbarkeitsindex je Modul (alle weiterhin Rang „A"):

| Modul | Mai 2026 | Juli 2026 |
|---|---|---|
| `models/coin.py` | 100 | 100 |
| `models/database.py` | 100 | 100 |
| `models/favorite.py` | 70 | 71 |
| `models/transaction.py` | 100 | 62 *(Wachstum, s. Kap. 4)* |
| `services/coin_sync_service.py` | 60 | 60 |
| `services/portfolio_service.py` | 56 | 56 |
| `models/account.py` | 54 | 54 |
| `app.py` | 42 | **48** ✅ |
| `services/market_service.py` | 34 | 34 |

Ergänzend aus den Test-Metriken (siehe [Testbericht](../Tests/Testbericht.md)): 35 Testfälle, 92 % Zeilenabdeckung auf dem Kernmodul `market_service.py`.

---

## 6. Zusammenfassung aller Verbesserungen

1. **Einziger D-Block beseitigt:** `/trade` von D (21) auf B (7) durch Extraktion von `place_order` in den Service-Layer.
2. **Duplizierung in `app.py` entfernt:** `@login_required`-Decorator; MI von 42 auf 48 gestiegen, obwohl das Modul gewachsen ist.
3. **Trading-Kern durchgängig einfach:** Nach IOSP/DRY-Refactorings liegt jeder Block in `market_service.py` bei B (7) oder besser; `execute_trade` und `get_portfolio_history` sind auf einen Blick lesbar.
4. **Ø-Komplexität gesunken (2,9 → 2,68), obwohl der Code gewachsen ist** (76 → 87 Blöcke, ~930 → 958 SLOC) – neue Features wurden von Anfang an in kleinen Methoden umgesetzt.
5. **Bewusste Tradeoffs dokumentiert statt wegoptimiert:** `get_leaderboard` C (11), `sync_coin_history` B (9) und der MI von `market_service.py` bleiben mit nachvollziehbarer Begründung unverändert (Kap. 4).

Die Metriken werden weiterhin bei jedem Push automatisch in der CI/CD-Pipeline mitgemessen, sodass Verschlechterungen früh sichtbar werden.
