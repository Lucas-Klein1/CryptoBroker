# CI/CD-Setup im Überblick – CryptoSim

**Projekt:** CryptoSim (Krypto-Trading-Simulation, Flask + SQLite)
**Vorlesung:** Software Engineering – Aufgabenblatt 20 (Abschluss)
**Plattform:** GitHub Actions
**Konfiguration:** [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)

---

## Trigger

Die Pipeline wird automatisch ausgelöst bei:
- **Push** auf den Branch `main`
- **Pull Request** gegen den Branch `main`

Dadurch wird jede Änderung, die in `main` einfließt (direkt oder über einen PR), vor der Integration automatisch geprüft.

---

## Die drei Stufen der Pipeline

### 1. Tests (`tests`)

- Checkout des Repositories, Setup von Python 3.13
- Installation der Abhängigkeiten aus `requirements.txt`
- Syntaxprüfung aller `.py`-Dateien (`compileall`)
- Ausführung der automatisierten Tests mit `pytest`, inkl. Code-Coverage (`pytest-cov`) für `services.market_service`
- Ergebnisse (Coverage-Report, Testergebnisse als JUnit-XML) werden als Artefakte hochgeladen

### 2. Metriken (`metrics`)

- Läuft erst nach erfolgreicher Test-Stufe (`needs: tests`)
- Berechnung von drei Software-Metriken mit [`radon`](https://radon.readthedocs.io/):
  1. Zyklomatische Komplexität (`radon cc`)
  2. Wartbarkeitsindex (`radon mi`)
  3. Raw Metrics / LOC & Kommentaranteil (`radon raw`)
- Details zur Metrikauswahl und den gemessenen Werten: [Metriken – Auswahl](metrics/metriken_auswahl.md) und [Metriken – Messwerte](metrics/metriken_messwerte.md)

### 3. Docker-Build + Smoke-Test (`build-test`)

- Läuft ebenfalls erst nach erfolgreicher Test-Stufe (`needs: tests`)
- Baut das Docker-Image der Anwendung (`docker build`)
- Startet einen Container aus diesem Image
- Führt einen Smoke-Test durch: Es wird wiederholt geprüft, ob die Startseite unter `http://localhost:5000` erreichbar ist (HTTP 200/403)
- Container wird anschließend gestoppt und entfernt (auch bei Fehlschlag)

---

## Vorteile dieses Setups

- **Frühzeitiges Feedback:** Fehler (Syntax, fehlschlagende Tests) werden direkt bei Push/PR erkannt, bevor sie in `main` landen.
- **Automatisierte Qualitätssicherung:** Tests und Metriken laufen bei jeder Änderung, ohne manuellen Aufwand – Code-Qualität bleibt nachvollziehbar über die Zeit.
- **Lauffähigkeit der Anwendung abgesichert:** Der Docker-Build- und Smoke-Test stellt sicher, dass die Anwendung nicht nur kompiliert, sondern auch tatsächlich in einem containerisierten Umfeld startet und erreichbar ist.
- **Reproduzierbarkeit:** Da die Anwendung über Docker gebaut und getestet wird, entspricht die CI-Umgebung der späteren Zielumgebung.
- **Nachvollziehbarkeit:** Coverage- und Testreports werden als Artefakte gespeichert und sind für jeden Lauf einsehbar.
