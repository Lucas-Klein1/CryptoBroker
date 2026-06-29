# CryptoBroker

Gruppenprojekt für die Vorlesung Software Engineering – TINF24B4, DHBW Karlsruhe

## Team

| Person   | Rolle          |
|----------|----------------|
| Sara     | Developer      |
| Lucas    | Product Owner  |
| Jonathan | Developer      |
| Julian   | Scrum Master   |

---

## Projektbeschreibung

CryptoBroker (Cryptosim) ist eine webbasierte Anwendung, mit der Nutzer den Kryptowährungshandel realitätsnah simulieren können – ohne echtes Geld einzusetzen. Nach der Registrierung erhält jeder Nutzer ein virtuelles Startguthaben und kann damit live gehandelte Coins kaufen und verkaufen, die Kurse werden direkt von der CoinGecko API bezogen. Drei flexible Handelsmodi (nach Menge, Betrag in Euro oder Prozentsatz des eigenen Bestands) machen den Einstieg niedrigschwellig und das Ausprobieren verschiedener Strategien einfach. Das eigene Portfolio lässt sich jederzeit einsehen, und eine Bestenliste zeigt, wer aus dem virtuellen Kapital am meisten gemacht hat.

---

## Dokumenten-Index

### Anforderungen
- [Software-Anforderungsspezifikation (SRS)](docs/SoftwareAnforderungsspezifikation.md)
- [Architecture Significant Requirements (ASR)](docs/Architecture%20Significant%20Requirements%20(ASR).md)

### Architektur
- [arc42-Architekturdokumentation](docs/arc42_Architekturdokumentation_Cryptosim.md)

### Tests & Qualität
- [Testplan](docs/Tests/Testplan.md)
- [Testbericht](docs/Tests/Testbericht.md)
- [Software-Metriken](docs/metrics/metriken_auswahl.md)
- [Refactoring-Zusammenfassung (Clean Code)](docs/Refactoring_summary_cleancode.md)
- [Review-Protokoll](docs/review-protocol.md)

### Risiken
- [RMMM-Liste](docs/RMMM_CryptoBroker.xlsx)

### Präsentation & Demo
- [Abschlussfolien](Abschlusspraesentation/CryptoBroker_Abschlusspraesentation%20(2).pptx)
- [Handout](Abschlusspraesentation/CryptoBroker_Handout.docx)
- [Demo-Screenshots](docs/Screenshots/)

### Weitere Ressourcen
- [Retrospektive](https://github.com/Lucas-Klein1/CryptoBroker/blob/main/docs/Screenshots/11_retrospektive.png)
- [Scrum-Board (GitHub Projects)](https://github.com/Lucas-Klein1/CryptoBroker/projects)
- [Blogs & Diskussionen](https://github.com/Lucas-Klein1/CryptoBroker/discussions)
- [CI/CD-Workflow](.github/workflows/ci.yml)

---

## Voraussetzungen

- **Python 3.13 oder höher**
- **pip** (Python Package Manager)
- Ein moderner Webbrowser (z. B. Chrome, Firefox)

## Abhängigkeiten installieren

Stelle sicher, dass du dich im Projektverzeichnis befindest: [cryptosim](cryptosim)

```bash
pip install -r requirements.txt
```

## Anwendung starten

```bash
python app.py
```

Bei erfolgreichem Start gibt Flask eine Meldung wie diese aus:

```bash
Running on http://127.0.0.1:5000/
```

## Anwendung im Browser öffnen

```
http://127.0.0.1:5000
```
