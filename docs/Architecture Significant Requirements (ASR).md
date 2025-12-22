# Architektur-Dokumentation – ASR (Architecture Significant Requirements)

## Projekt: CryptoBroker


---

# **Schritt 1 – Qualitätsziele & Qualitätsszenarien**

##  **1. Qualitätsszenarien**

| **Qualitätsattribut (Quelle)** | **Stimulus** | **Artefakt / Gegenstand** | **Umgebung** | **Antwort** | **Antwortmaß (Messgröße)** |
|-------------------------------|-------------|----------------------------|--------------|-------------|------------------------------|
| **Performance (User)** | Nutzer führt Kauf-/Verkauf aus | Flask Backend | Lokaler Betrieb | Backend verarbeitet Request schnell | Reaktionszeit ≤ 2s |
| **Sicherheit (User)** | Login wird gestartet | Authentifizierungslogik | Web-Client | Authentifizierung erfolgt sicher | Erfolgreicher Login |
| **Wartbarkeit (Entwickler)** | Frontend-Komponente wird überarbeitet | Backend/Frontend-Schnittstelle | Entwicklungsumgebung | Keine Anpassung an Schnittstelle nötig | Schnittstelle bleibt unverändert |
| **Zuverlässigkeit (System)** | Ungültige Order wird eingegeben | Handelslogik | Backend | Backend validiert Eingaben | Validierungsfehler werden dem Nutzer angezeigt |
| **Benutzbarkeit (User)** | User öffnet Dashboard | UI-Modul | Browser | Übersichtliche Darstellung | Nutzer versteht Daten sofort |
| **Portabilität (Entwickler/User)** | Start auf neuer Maschine | Gesamtsystem | Localhost | System startet ohne Zusatzdienste | Start funktioniert direkt |

---

##  **2. Qualitätsbaum**

| **Qualitätsattribut** | **Verfeinerung** | **Qualitätsszenario** | **Nutzen** | **Risiko** |
|----------------------|------------------|------------------------|------------|------------|
| **Performance** | Antwortzeit | System reagiert innerhalb von 2 Sekunden bei Handelstransaktionen | **Hoch** | **Mittel** |
| **Sicherheit** | Zugriffsschutz | Benutzer muss sich sicher authentifizieren, bevor Dashboard-Daten angezeigt werden | **Hoch** | **Hoch** |
| **Wartbarkeit** | Modularität | Änderungen im Frontend sollen das Backend nicht beeinflussen | **Mittel** | **Niedrig** |
| **Zuverlässigkeit** | Fehlervermeidung | Backend soll bei ungültigen Handelseingaben stabile Fehlermeldungen liefern | **Mittel** | **Mittel** |
| **Benutzbarkeit** | Verständlichkeit | User soll auf dem Dashboard Kursdaten ohne technische Vorkenntnisse verstehen | **Mittel** | **Niedrig** |
| **Portabilität** | Laufbarkeit | Die Anwendung soll lokal ohne zusätzliche Services laufen | **Niedrig** | **Niedrig** |

---

# **Schritt 2 – Architekturstrategien für höchste Priorität**

Höchste Nutzen+Risiko Kombination laut Qualitätsbaum:

1. **Sicherheit – Hoch Nutzen / Hoch Risiko**
2. **Performance – Hoch Nutzen / Mittel Risiko**

---

## **1. Sicherheitsstrategie**

- Session-basierte Authentifizierung
- Gesicherte Passwörter (bcrypt)
- Eingabevalidierung im Backend
- Zugriffsbeschränkte Bereiche (Logged-In Only)

---

## **2. Performancestrategie**

- Leichtgewichtiges Flask-Backend
- SQLite (lokal, kurze Latenzen)
- Caching von Kursdaten
- Clientseitige Verarbeitung für Visualisierung (z. B. Charts)

---

# **Schritt 3 – Architekturentscheidungen (ADR)**

Nur die **2 höchstpriorisierten** Qualitätsattribute werden betrachtet:  
**Sicherheit & Performance**

---

## **ADR 001 – Session-basierte Authentifizierung**

### Kontext und Problemstellung
Das System benötigt sichere Authentifizierung für Login und Dashboard-Daten.

### Betrachtete Varianten
* Session Auth
* JWT Auth
* Basic Auth

### Entscheidung
**Session Authentication**, da einfach, sicher und ideal für lokale Anwendungen.

### Status
**Angenommen**

### Konsequenzen
* Gut weil, Sicher und unkompliziert
* Gut weil, kein externer Key-Store notwendig
* Nicht gut weil, optimal bei skalierter Cloud-Nutzung

---

## **ADR 002 – Nutzung eines leichten Flask-Backends mit Kursdaten-Caching**

### Kontext und Problemstellung
Handelstransaktionen sollen serverseitig innerhalb von ≤ 2 Sekunden verarbeitet werden.

### Betrachtete Varianten
* Flask Backend
* FastAPI
* Node.js API

### Entscheidung
**Flask-Backend mit Caching**, da geringste Komplexität und lokal ausreichend performant.

### Status 
**Angenommen**

### Konsequenzen
* Gut, weil die Performance für lokale Nutzung optimal ist
* Gut, weil dadurch Minimale Architekturkomplexität entsteht
* Nicht gut weil, nicht optimal bei sehr hoher Skalierung

---

# **Fazit**

Dieses ASR-Dokument enthält:
- Qualitätsbaum mit Nutzen UND Risiko (Hoch/Mittel/Niedrig)
- Qualitätsszenarien für jedes Qualitätsziel
- Strategien für die wichtigsten zwei Ziele
- Zwei vollständige ADRs

