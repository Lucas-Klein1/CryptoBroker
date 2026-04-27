# Refactoring nach Clean-Code-Prinzipien

**Projekt:** CryptoSim (Krypto-Trading-Simulation, Flask + SQLite)
**Vorlesung:** Software Engineering – Folien 11 „Clean Code" (Harald Ichters, DHBW Karlsruhe)
**Datum:** April 2026

## 1. Zielsetzung

Auf Grundlage der Clean-Code-Prinzipien aus der Vorlesung wurden ausgewählte Teile des Quellcodes refaktoriert. Ziel war nicht eine vollständige Überarbeitung, sondern eine fokussierte Verbesserung an den Stellen mit dem höchsten Nutzen (Lesbarkeit, Testbarkeit, Wartbarkeit). Die ausgewählten Änderungen orientieren sich vor allem an folgenden Prinzipien aus der Vorlesung:

- Funktionen sollen klein sein und nur eine Aufgabe erfüllen (Single Responsibility).
- Alle Teile einer Funktion sollen auf einer Abstraktionsebene liegen (Single Level of Abstraction).
- Don't Repeat Yourself (DRY) – Duplizierungen entfernen.
- Integration Operation Segregation Principle (IOSP) – Methoden trennen Aufrufe untereinander von eigentlichen Operationen.
- Anweisungen und Abfragen trennen.
- Aussagekräftige, zweckbeschreibende Namen.

## 2. Überblick der Änderungen

Es wurden zwei Dateien refaktoriert. Die externe Schnittstelle (Methodensignaturen, Rückgabewerte, Verhalten) wurde dabei nicht verändert, sodass aufrufender Code (insbesondere `app.py`) unverändert weiterläuft.

| Datei | Hauptproblem | Eingesetzte Prinzipien |
|---|---|---|
| `services/market_service.py` | `execute_trade` und `get_portfolio_history` vermischen DB-Zugriff, Validierung und Berechnung; BUY/SELL-Logik dupliziert. | SRP, IOSP, DRY, kleine Funktionen |
| `models/account.py` | `login_or_register` erfüllt zwei Aufgaben (Login + Registrierung) mit verschachteltem try/except; bcrypt-Logik mehrfach dupliziert. | DRY, Anweisungen/Abfragen trennen, kleine Funktionen |

## 3. Refactoring: `services/market_service.py`

### 3.1 Anwendung des IOSP auf `execute_trade`

Die Methode `execute_trade` vermischte vorher Validierung (Aktion prüfen, Coin laden, Bestand prüfen, Guthaben prüfen), Datenbankzugriff (Insert) und Geschäftslogik in einer einzigen Methode. Nach dem **Integration Operation Segregation Principle** wurde sie in eine kurze Integrationsmethode umgewandelt, die ausschließlich andere Methoden der eigenen Codebasis aufruft:

```python
def execute_trade(self, acc_id, coin_id, action, amount):
    action = self._normalize_action(action)
    coin   = self._require_coin(coin_id)
    self._validate_trade(acc_id, coin, action, amount)
    self._save_transaction(acc_id, coin, action, amount)
```

Die einzelnen Schritte (Aktion normalisieren, Coin laden, Trade validieren, Transaktion speichern) wurden in private Hilfsmethoden ausgelagert. Jede dieser Methoden enthält entweder reine Operationen (Kontrollstrukturen, DB-Aufrufe) oder reine Integration – aber nicht beides. Damit liegt `execute_trade` auf einer einheitlichen Abstraktionsebene und ist auf einen Blick lesbar.

### 3.2 DRY: Tabellennamen-Konvention zentralisiert

Der Ausdruck `f"{coin_id.lower().replace('-', '_')}_history"` tauchte in `get_history` und `get_portfolio_history` mehrfach auf. Daraus wurde eine zentrale Hilfsmethode `_history_table_name(coin_id)`. Wenn sich die Namenskonvention später ändert, muss nur eine Stelle angepasst werden.

### 3.3 DRY: BUY/SELL-Logik nur noch an einer Stelle

In `get_portfolio_history` wurde der gleiche BUY/SELL-Block (Bestand anpassen und Cash-Balance verrechnen) zweimal hintereinander ausgeschrieben – einmal für die Schleife über die Timeline und einmal für die nachgelagerten Transaktionen. Beide Stellen rufen jetzt `_apply_single_transaction` auf. Damit ist sichergestellt, dass eine spätere Änderung der Trade-Logik (z. B. Gebühren) nicht versehentlich nur an einer der beiden Stellen geändert wird.

### 3.4 Aufteilung von `get_portfolio_history`

Die Methode war ursprünglich rund 100 Zeilen lang und enthielt: DB-Abfragen für Transaktionen, DB-Abfragen für Coin-Historien, Aufbau eines Preis-Lookups, Sortieren der Timeline und das eigentliche schrittweise Hochzählen des Portfoliowerts. Sie verletzte damit deutlich das Prinzip „eine Funktion erfüllt nur eine Aufgabe" und „alle Teile auf einer Abstraktionsebene". Nach dem Refactoring liest sich der oberste Aufruf wie ein Inhaltsverzeichnis:

```python
def get_portfolio_history(self, acc_id):
    txs = self._load_transactions(acc_id)
    if not txs:
        return []
    coin_histories = self._load_histories_for_transactions(txs)
    timeline       = self._build_timeline(txs, coin_histories)
    portfolio      = self._compute_portfolio_values(txs, coin_histories, timeline)
    self._append_current_value(portfolio, txs, coin_histories)
    return portfolio
```

Ein Leser kann auf dieser Ebene das WAS verstehen, ohne sich gleichzeitig mit dem WIE (SQL, bisect, Schleifen-Indizes) auseinandersetzen zu müssen. Wer Details braucht, kann gezielt in die jeweilige Hilfsmethode springen.

## 4. Refactoring: `models/account.py`

### 4.1 Trennung von Anweisung und Abfrage in `login_or_register`

Die Methode `login_or_register` war ein klassisches „Teekesselchen" – sie loggte entweder einen bestehenden Account ein ODER legte einen neuen an, und fing in einem verschachtelten try/except sowohl Hashing-Fehler als auch logische Fehler ab.

**Vorher:**
```python
if acc:
    try:
        if not bcrypt.checkpw(pw.encode("utf-8"), acc.pw):
            raise ValueError("Falsches Passwort.")
        return acc
    except Exception:
        if pw != acc.pw:
            raise ValueError("Falsches Passwort.")
        return acc
return Account.create(name, pw)
```

**Nachher:**
```python
existing = Account.get_by_name(name)
if existing is None:
    return Account.create(name, pw)
if not _password_matches(pw, existing.pw):
    raise ValueError("Falsches Passwort.")
return existing
```

Die Logik liest sich jetzt linear (keine verschachtelten try/except), die Fälle „existiert nicht" und „Passwort falsch" sind klar getrennt, und der Sonderfall für Alt-Daten (Klartext-Passwort statt bcrypt-Hash) ist in `_password_matches` gekapselt – statt dupliziert in `login_or_register` UND `change_password`.

### 4.2 DRY: Hashen und Prüfen in eigene Funktionen

Die Bytefolgen `bcrypt.gensalt(rounds=12)` und `bcrypt.hashpw(pw.encode("utf-8"), salt)` standen vorher dreimal im Code (`create`, `change_password`, indirekt in der Verifikation). Sie wurden zu zwei kleinen Hilfsfunktionen mit zweckbeschreibenden Namen zusammengezogen:

- `_hash_password(pw)` – erzeugt einen bcrypt-Hash.
- `_password_matches(pw, stored_hash)` – prüft ein Klartextpasswort gegen den Hash, mit Fallback für Alt-Daten.

Die `change_password`-Methode wurde dadurch ebenfalls deutlich kürzer und ihre eigentliche Aufgabe (Prüfen → Validieren → Speichern) wieder lesbar.

## 5. Fazit

Die Änderungen verbessern vor allem die **Lesbarkeit** (kurze Methoden mit sprechenden Namen, einheitliche Abstraktionsebene), die **Wartbarkeit** (DRY: BUY/SELL-Logik, Tabellennamen-Konvention und Passwortprüfung jeweils nur noch an einer Stelle) und die **Testbarkeit** (durch das IOSP lassen sich die kleinen Operations-Methoden isoliert testen). Das öffentliche Verhalten des Systems ist unverändert.
