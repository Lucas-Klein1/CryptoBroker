# Review-Protokoll – CryptoBroker
*Software Engineering · DHBW Karlsruhe*

---

## 1. Datum

| | |
|---|---|
| **Datum** | 25.05.2026 |
| **Startzeit** | 14:00 Uhr |
| **Endzeit** | 15:30 Uhr |

---

## 2. Teilnehmende

| Name | Rolle | Aufgabe |
|---|---|---|
| Lucas | Moderator | Leitet die Sitzung, sorgt für Fokus und dass alle zu Wort kommen |
| Julian | Vorleser | Trägt den Code Abschnitt für Abschnitt vor |
| Sara | Protokollführerin | Notiert alle Befunde und Auffälligkeiten |
| Jonathan | Zeitwächter | Achtet auf die Zeit und begrenzt zu lange Diskussionen |

---

## 3. Ziel und Schwerpunkt des Reviews

Ziel des Reviews war es, den Kerncode der Anwendung auf Codequalität, Wartbarkeit und Robustheit zu prüfen, bevor weitere Features hinzugefügt werden.

**Begründung der Auswahl:** Die ausgewählten Komponenten bilden das Herzstück der Anwendung. Fehler hier wirken sich direkt auf alle anderen Teile aus. Außerdem wächst die Komplexität dieser Dateien mit jedem Sprint – ein guter Zeitpunkt, sie strukturiert zu prüfen, bevor technische Schulden entstehen.

---

## 4. Komponenten für den Review

- `app.py` – Routing und zentrale Steuerung der Anwendung
- `services/market_service.py` – Handelslogik, Portfolio- und Guthabenberechnung
- `services/coin_sync_service.py` – Anbindung an die CoinGecko-API und Datenbankbefüllung

---

## 5. Kriterien für den Review

| Komponente | Kriterien |
|---|---|
| `app.py` | Codequalität, Wartbarkeit (Codeduplizierung), Lesbarkeit |
| `market_service.py` | Codequalität, Wartbarkeit, Korrektheit der Logik |
| `coin_sync_service.py` | Robustheit (Fehlerbehandlung bei API-Ausfall), Codequalität |

---

## 6. Review-Methodik

Wir haben ein informales Review in Sitzungstechnik durchgeführt, konkret einen Walkthrough. Dabei hat Julian den Code Abschnitt für Abschnitt vorgetragen. Die anderen Teilnehmenden haben Fragen gestellt und Auffälligkeiten gemeldet, die Sara direkt notiert hat. Jonathan hat auf die Zeit geachtet und dafür gesorgt, dass Diskussionen nicht zu lang werden. Lucas hat die Sitzung moderiert.

Alle Teilnehmenden haben sich vorab ca. 30 Minuten selbstständig mit dem Code beschäftigt.

---

## 7. Ergebnisse der Sitzung

### Abgeleitete Aufgaben

| # | Datei | Befund | Maßnahme | Verantwortlich | Frist | Status |
|---|---|---|---|---|---|---|
| 1 | `coin_sync_service.py` | Beim App-Start wird die coins-Tabelle per `DROP TABLE` gelöscht. Bei einem API-Fehler bleibt die Tabelle leer und die App ist unbrauchbar. | `INSERT OR REPLACE` statt `DROP + CREATE` verwenden. | Julian | 01.06. | ✅ Erledigt |
| 2 | `app.py` | Die Login-Prüfung (`session.get`) wird in fast jeder Route einzeln wiederholt – Codeduplizierung. | Zentralen `@login_required` Decorator einführen. | Julian | 01.06. | ✅ Erledigt |
| 3 | `coin_sync_service.py` | In `_fetch_coin_history()` ist `days='365'` fest eingetragen, obwohl eine `while`-Schleife dynamische Zeiträume suggeriert. Die Schleife bewirkt nichts. | Schleife korrekt implementieren oder entfernen. | Julian | 01.06. | ✅ Erledigt |
| 4 | `market_service.py` | `_append_current_value()` berechnet alle Transaktionen erneut von vorne, obwohl das kurz davor in `_compute_portfolio_values()` schon passiert ist. | Zwischenergebnis weitergeben statt neu berechnen. | Julian | 01.06. | ✅ Erledigt |
| 5 | `app.py` | `import datetime` steht innerhalb einer Funktion; Konstante `MIN_TRADE_EUR` ist mitten in der Datei definiert. | Imports und Konstanten an den Dateianfang verschieben. | Julian | 01.06. | ✅ Erledigt |

### Bewährte Praktiken

- Passwort-Hashing mit bcrypt ist sauber umgesetzt.
- Der inkrementelle API-Sync lädt nur fehlende Tage nach – keine unnötigen API-Aufrufe.
- `_apply_single_transaction()` wird an mehreren Stellen wiederverwendet (gutes DRY-Prinzip).

### Gelernte Lektionen

- Das `DROP TABLE`-Problem war uns allen nicht bewusst – es fiel erst durch das gemeinsame Draufschauen auf.
- Codeduplizierung ist leichter zu sehen, wenn jemand anderes den Code vorliest.
- Regelmäßige kurze Reviews während der Entwicklung würden helfen, solche Probleme früher zu finden.

---

*Protokollführerin: Sara · Moderator: Lucas · 25.05.2026 · Bearbeitungsstand aktualisiert: 05.07.2026*