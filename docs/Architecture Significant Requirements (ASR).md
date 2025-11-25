# Architektur – Qualitätsanforderungen, Strategien und Entscheidungen (ASR)

---

## Schritt 1 – Qualitätsmerkmale & Qualitätsszenarien

### Tabelle der ASR-Szenarien

| **Qualitätsattribut (Quelle)** | **Stimulus** | **Artefakt / Gegenstand** | **Umgebung** | **Antwort** | **Antwortmaß (Messgröße)** |
|-------------------------------|--------------|----------------------------|--------------|-------------|-----------------------------|
| **Benutzerfreundlichkeit** | Ein neuer Nutzer öffnet erstmals das Web-Dashboard. | Benutzeroberfläche (UI), Navigationsstruktur | Normalbetrieb | Intuitives UI, geführtes Onboarding | Funktion in **< 5s / ≤ 2 Klicks** |
| **Benutzerfreundlichkeit** | Fehlerhafte Eingaben | Eingabevalidierung, Formulare | Normalbetrieb | Verständliche Fehlermeldung | Meldung in **< 1s** |
| **Zuverlässigkeit** | Serverausfall | Backend-Services, Cluster | Ausfallbetrieb | Automatisches Failover | Ausfallzeit **< 5s**, kein Datenverlust |
| **Zuverlässigkeit** | Externe API nicht erreichbar | API-Schnittstellen | Normalbetrieb | Fallback auf Cache oder sekundäre Quelle | Verzögerung **≤ 30s** |
| **Performance** | Nutzer öffnet Startseite | Frontend, API | Normalbetrieb | Caching, asynchrones Laden | Ladezeit **≤ 2s** |
| **Performance** | 10.000 gleichzeitige Nutzer | Streaming-Service, API | Hochlast | Auto-Skalierung | Antwortzeit **< 300ms** |
| **Sicherheit** | Unautorisierter Zugriff | Auth/Role-Modul | Normalbetrieb | Zugriff blockiert, Logging | Blockierung **< 100ms** |
| **Sicherheit** | Nutzer startet Transaktion | Transaktionsmodul | Normalbetrieb | Verschlüsselte Verarbeitung, 2FA | Verarbeitung **< 2s** |
| **Wartbarkeit** | Update während Betrieb | Backend, CI/CD | Rolling Deployment | Update ohne Downtime | Rollback **< 10s** |
| **Wartbarkeit** | Fehleranalyse | Logging, Monitoring | Normalbetrieb | Reproduzierbarkeit | Analyse **< 15 min** |

---

## Qualitätsbaum (Utility Tree)

| **Qualitätsattribut** | **Verfeinerung** | **Qualitätsszenario** | **Bewertung (Nutzen/Risiko)** |
|------------------------|------------------|------------------------|-------------------------------|
| **Performance** | Reaktionszeit | Live-Preise ≤ **300ms** auch unter Last | (H, H) |
| **Performance** | Durchsatz | 10.000 Preisabfragen/s | (H, M) |
| **Benutzbarkeit** | Effizienz | Erstkauf in **< 40s** | (M, L) |
| **Benutzbarkeit** | Training | Support geschult in **< 1h** | (M, M) |
| **Sicherheit** | Zugriffskontrolle | Blockierung unautorisierter Zugriffe in **< 0,1s** | (H, H) |
| **Sicherheit** | Datenintegrität | Atomare Transaktionen ohne Datenverlust | (H, M) |
| **Zuverlässigkeit** | Fehlertoleranz | Failover in **< 5s** | (H, M) |
| **Zuverlässigkeit** | Verfügbarkeit | ≥ **99,9%** im Jahresmittel | (H, M) |
| **Wartbarkeit** | Routine-Änderungen | Bugfix-Deploy < **2 PT** | (H, M) |
| **Wartbarkeit** | Erweiterbarkeit | Feature-Integration < **5 PT** | (H, M) |
| **Wartbarkeit** | Upgrade API-Version | Upgrade < **2 Tage** | (M, M) |

---

# Schritt 2 – Potenzielle Architekturstrategien

Basierend auf der Bewertung (Nutzen/Risiko) wurden folgende **zwei hochpriorisierte Szenarien** ausgewählt:

1. **Performance: Live-Preisabfragen ≤ 300 ms** (H/H)
2. **Sicherheit: Zugriffskontrolle – Blockierung unautorisierter Zugriffe < 0,1 s** (H/H)

Für diese Szenarien eignen sich folgende Architekturstrategien:

---

## **1. Strategie für Performance (≤ 300 ms bei Live-Preisdaten)**

### Geeignete Strategien:
- **Event-Driven Architecture** für Preis-Updates (z. B. Kafka / WebSocket-Streams)
- **In-Memory-Caching (Redis)** zum schnellen Zugriff
- **Horizontal skalierbare Preis-API** (z. B. Kubernetes HPA)
- **CQRS** zur Trennung von Lese-/Schreiboperationen
- **Load-Balancing mit Round-Robin oder Least Connections**
- **Asynchrone Datenverarbeitung** statt synchroner API-Calls zu externen Quellen

### Begründung:
Diese Strategien reduzieren Antwortzeiten massiv, stellen hohe Skalierbarkeit sicher und vermeiden Flaschenhälse bei Preis-Streams.

---

## **2. Strategie für Sicherheit (unautorisierte Zugriffe < 100ms blockieren)**

### Geeignete Strategien:
- **Zentrale Identity & Access Management (IAM)**
- **JWT-basierte Sessions mit kurzen Laufzeiten**
- **Rate-Limiting + IP-Blocking**
- **Zero-Trust-Ansatz** (jede Anfrage muss validiert werden)
- **Security-Event Logging** mit direkter Weiterleitung an SIEM
- **API-Gateway mit integriertem Auth-Filter**

### Begründung:
Diese Maßnahmen sorgen für eine extrem schnelle und sichere Blockierung unerlaubter Zugriffe sowie lückenloses Monitoring.

---

# Schritt 3 – Architekturentscheidungen (ADRs)

Im Folgenden die ADRs basierend auf den ausgewählten Strategien.

---

## ADR 1 – Einführung von In-Memory-Caching (Redis) für Preis-API

### Kontext und Problemstellung
Um Live-Kryptopreise mit einer Antwortzeit von **unter 300 ms** bereitzustellen, muss das System unnötige API-Abfragen und Latenzen vermeiden. Externe Preislieferanten sind zu langsam für direkte Live-Abfragen.

### Betrachtete Varianten
* Direkte API-Abfragen an externen Provider
* Redis-In-Memory-Caching
* Speicherung in SQL-Datenbank
* Speicherung in NoSQL-Datenbank

### Entscheidung
Gewählte Variante: „**Redis-In-Memory-Caching**“, da es als einzige Option **sub-100-ms** Zugriffszeiten zuverlässig ermöglicht.

### Status
Angenommen

### Konsequenzen
* Gut: Extrem schnelle Lesezugriffe, weniger Last auf Preis-APIs
* Gut: Hohe Skalierbarkeit durch horizontale Replikation
* Schlecht: Cache-Invaliderung wird komplexer
* Schlecht: Erfordert Monitoring (Cache-Miss-Raten)

---

## ADR 002 – Einsatz eines API-Gateways mit integriertem Auth-Filter

### Kontext und Problemstellung
Unautorisierte Zugriffe müssen **innerhalb von < 100 ms** erkannt und blockiert werden. Eine verteilte Logik in einzelnen Services wäre zu langsam und fehleranfällig.

### Betrachtete Varianten
* Authentifizierung in jedem Microservice
* API-Gateway mit zentralem Auth-Filter
* Reverse Proxy + Middleware
* Firewall-Regeln auf Netzwerkebene

### Entscheidung
Gewählte Variante: „**API-Gateway mit zentralem Auth-Filter**“, da diese Lösung die beste Kombination aus **Geschwindigkeit**, **Sicherheit** und **Wartbarkeit** bietet.

### Status
Angenommen

### Konsequenzen
* Gut: Sehr schnelle Authentifizierung/Autorisierung
* Gut: Konsistente Security-Policy für alle Endpunkte
* Gut: Zentrales Logging & Monitoring
* Schlecht: API-Gateway wird ein kritischer Single Point of Failure → durch Redundanz lösbar
* Schlecht: Höhere Komplexität beim Setup

---

# Gesamtfazit

Diese Dokumentation umfasst:

✔ Qualitätsanforderungen und definierte Qualitätsszenarien  
✔ Vollständigen Qualitätsbaum  
✔ Auswahl der wichtigsten Szenarien  
✔ Architekturstrategien für Performance & Sicherheit  
✔ Zwei vollständige ADRs basierend auf den Entscheidungen

Dieses Dokument ist direkt als Markdown speicherbar.
