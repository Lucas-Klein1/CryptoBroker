# Aufgabe 2 - Architekturdokumentation CryptoBroker

## 📋 Aufgabenstellung (Aufgabenblatt 12)

Dokumentiere deine aktuelle Softwarearchitektur nach arc42 mit folgenden Kapiteln:

- ✅ Kapitel 1-4: Einführung, Ziele, Randbedingungen, Kontext
- ✅ Kapitel 5: Bausteinsicht (Komponenten + Paketdiagramme)
- ✅ Kapitel 6: Laufzeitsicht (Sequenzdiagramme)
- ✅ Kapitel 7: Verteilungssicht (Deployment-Diagramme)
- ✅ Kapitel 8: Querschnittliche Konzepte
- ✅ Kapitel 9: Architekturentscheidungen (5 ADRs)
- ✅ Kapitel 10: Qualitätsanforderungen (Szenarien & Metriken)
- ✅ Kapitel 11: Glossar
- ✅ Kapitel 12: Anhänge

---

## 📁 Erstellte Dokumente

### 1. Hauptdokumentation
**Datei:** `cryptosim/ARCHITEKTURDOKUMENTATION.md`
- Vollständige arc42-Dokumentation nach Template
- Über 1000 Zeilen Dokumentation
- Alle 10+ Kapitel detailliert beschrieben
- Inklusive Diagramme im Text

### 2. UML-Diagramme

#### A) PlantUML-Dateien (im `cryptosim/uml/` Verzeichnis)
```
📦 uml/
├── 01_component_diagram.puml          ← Komponenten & Abhängigkeiten
├── 02_sequence_login.puml             ← Login/Authentifizierung
├── 03_sequence_trade.puml             ← Trade-Ausführung (BUY/SELL)
├── 04_sequence_portfolio.puml         ← Portfolio-Berechnung
├── 05_deployment_diagram.puml         ← Server, Datenbank, API
├── 06_package_diagram.puml            ← 3-Schichten-Architektur
└── README.md                           ← Konvertierungsanleitung
```

#### B) Mermaid-Diagramme (in Markdown)
**Datei:** `cryptosim/UML_DIAGRAMME.md`
- 10 Mermaid-Diagramme in einem Dokument
- Direkt in GitHub/GitLab/Markdown renderbar
- Keine Installation erforderlich
- Diagrammtypen:
  1. Komponenten-Diagramm (graph)
  2. Sequenzdiagramm: Login
  3. Sequenzdiagramm: Trade
  4. Sequenzdiagramm: Portfolio
  5. Deployment-Diagramm (graph)
  6. Paketdiagramm (3-Schichten)
  7. Use-Case Diagramm
  8. Entity-Relationship Diagram (ER)
  9. Architektur-Übersicht (C4 Level 1)
  10. State-Diagram (Transaktionszustand)

---

## 🎨 Diagramm-Übersicht

### Komponenten-Sicht
```
Presentation Layer
    ↓ (Flask Routes)
Service Layer
    ↓ (Business Logic)
Model & Data Layer
    ↓ (Database Access)
SQLite Datenbank ← CoinGecko API
```

### Sequenz-Abläufe
1. **Login-Flow:** User → Browser → Flask → Account Model → DB
2. **Trade-Flow:** User → Coin Selection → Validation → DB Insert
3. **Portfolio-Flow:** User → Aggregation → Calculation → Display

### Deployment
```
Client (Browser) ←HTTP/HTTPS→ Flask App + SQLite
                                    ↓
                            CoinGecko API
```

---

## 📊 Statistik der Dokumentation

| Metrik | Wert |
|--------|------|
| Zeilen Architekturdokumentation | 1200+ |
| Kapitel | 12 |
| Qualitätsszenarien | 7 |
| Architekturentscheidungen (ADRs) | 5 |
| UML-Diagramme (PlantUML) | 6 |
| UML-Diagramme (Mermaid) | 10 |
| Komponenten dokumentiert | 15+ |
| Abbildungen & Diagramme | 20+ |

---

## 🔗 Links zur Dokumentation

### Hauptdokumentation
- **Architekturdokumentation:** `./cryptosim/ARCHITEKTURDOKUMENTATION.md`

### UML-Diagramme
- **Mermaid-Diagramme (Markdown):** `./cryptosim/UML_DIAGRAMME.md`
- **PlantUML-Quellen:** `./cryptosim/uml/`

### Team-Information
- **README:** `./README.md`
- **Team:** Sara (Dev), Lucas (PO), Jonathan (Dev), Julian (SM)

---

## 🚀 Für den Blog-Eintrag (bis 14.04.2026 20:00 Uhr)

### Zu berichten:
1. ✅ **Architekturdokumentation** nach arc42
2. ✅ **UML-Modelle** (Komponenten, Sequenz, Deployment, Package)
3. ✅ **Qualitätsanforderungen** und Szenarien
4. ✅ **Architekturentscheidungen** (5 ADRs)

### Blog-Post Struktur

```markdown
# CryptoBroker - Architekturdokumentation (Aufgabe 2)

## Überblick
CryptoBroker ist eine Flask-basierte Web-Anwendung für Kryptowährungs-Portfolio-Management.
Sie folgt einer 3-Schichten-Architektur (Presentation, Business Logic, Data).

## Dokumentation
- [Vollständige Architekturdokumentation](cryptosim/arc42_Architekturdokumentation.md)
- [UML-Diagramme](./cryptosim/UML_DIAGRAMME.md)

## Highlights

### Komponenten
- **Presentation Layer:** Flask Web App mit Jinja2 Templates
- **Service Layer:** Portfolio Service, Market Service, Coin Sync Service
- **Data Layer:** SQLite mit Account, Coin, Transaction Models

### Architektur-Entscheidungen (ADRs)
1. 3-Schichten-Architektur für bessere Testbarkeit
2. Flask für schnelle Entwicklung
3. SQLite für einfaches Deployment
4. bcrypt für sichere Password-Verwaltung
5. CoinGecko API als externe Datenquelle

### Qualitätsziele
- Verfügbarkeit > 95%
- Response-Zeit < 200ms
- 100% Transaktionsgenauigkeit
- Benutzerfreundlichkeit

## UML-Diagramme
[Screenshots der Diagramme einbinden]

## Erkannte Verbesserungspotentiale
- Datenbank-Indizes für Abfragen
- Logging-System implementieren
- Unit-Tests erweitern (>70% Coverage)
- Rate-Limiting gegen Brute-Force
- HTTPS in Production erzwingen
```

---

## 📋 Checkliste für Aufgabe 2

- [x] Kapitel 1: Einführung und Ziele
  - [x] Aufgabenstellung
  - [x] Qualitätsziele
  - [x] Stakeholder
- [x] Kapitel 2: Randbedingungen
  - [x] Technisch
  - [x] Organisatorisch
- [x] Kapitel 3 & 4: Kontextabgrenzung & Lösungsstrategie
- [x] Kapitel 5: Bausteinsicht
  - [x] Komponenten-Übersicht
  - [x] Detaillierte Beschreibungen
  - [x] Paketdiagramm
- [x] Kapitel 6: Laufzeitsicht
  - [x] Sequenzdiagramm Login
  - [x] Sequenzdiagramm Trade
  - [x] Sequenzdiagramm Portfolio
- [x] Kapitel 7: Verteilungssicht
  - [x] Deployment-Architektur
  - [x] Deployment-Varianten
- [x] Kapitel 8: Querschnittliche Konzepte
  - [x] Persistierung
  - [x] Authentifizierung
  - [x] Fehlerbehandlung
  - [x] Caching
- [x] Kapitel 9: Architekturentscheidungen
  - [x] ADR-001: 3-Schichten-Architektur
  - [x] ADR-002: Flask als Framework
  - [x] ADR-003: SQLite als Datenbank
  - [x] ADR-004: bcrypt für Password-Hashing
  - [x] ADR-005: CoinGecko API
- [x] Kapitel 10: Qualitätsanforderungen
  - [x] Qualitätsziele & Szenarien
  - [x] Qualitäts-Baum
  - [x] Qualitäts-Metriken
- [x] Kapitel 11: Glossar
- [x] Kapitel 12: Anhänge

---

## 🎯 Nächste Schritte

### 1. UML-Diagramme exportieren (Optional)
```bash
# Mit Online-Tool: https://www.plantuml.com/plantuml/uml/
# Oder mit Docker:
cd cryptosim/uml
docker run --rm -v $(pwd):/data mplantuml/plantuml *.puml
```

### 2. PNG-Bilder in Dokumentation einbinden
```markdown
![Component Diagram](uml/01_component_diagram.png)
```

### 3. Blog-Post schreiben
- Zusammenfassung der Architektur
- Links zu Dokumentation und Diagrammen
- Screenshots der UML-Modelle
- Reflexion über Entwurfsentscheidungen

### 4. Kommentare auf 2 anderen Blogs
- Bis 15.04.2026 20:00 Uhr
- Konstruktives Feedback geben

---

## 📚 Ressourcen

- **arc42-Template:** https://arc42.org
- **arc42 Dokumentation:** https://docs.arc42.org/
- **PlantUML:** https://plantuml.com/
- **Mermaid:** https://mermaid.js.org/

---

**Dokument erstellt:** April 2026
**Status:** ✅ Aufgabe 2 vollständig dokumentiert
**Autor:** SE-Team (Lucas, Sara, Jonathan, Julian)
