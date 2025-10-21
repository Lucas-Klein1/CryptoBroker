# CryptoBrokerProject

## Softwareanforderungen

### 1. Einleitung

#### 1.1 Übersicht

Das **CryptoBrokerProject** ist eine JavaFX-Anwendung, mit der Benutzer Kryptowährungsdaten einsehen, ein Konto erstellen und Investitionen simulieren können.  
Die Anwendung verwendet eine **lokale SQLite-Datenbank** zur Speicherung von Nutzerdaten und Kryptoinformationen.  

#### 1.2 Geltungsbereich

Dieses Dokument beschreibt die funktionalen und nicht-funktionalen Anforderungen des gesamten Systems.  
Es dient der Umsetzung eines Desktop-Tools zur Verwaltung und Anzeige von Kryptodaten.

#### 1.3 Definitionen und Abkürzungen

| Begriff | Bedeutung |
|----------|------------|
| **DB** | Datenbank |
| **GUI** | Graphical User Interface |
| **UML** | Unified Modeling Language |
| **BLOB** | Binary Large Object (z. B. Bilder) |

---

### 2. Funktionale Anforderungen

#### 2.1 Übersicht

Das System umfasst vier Hauptfunktionen, wie im folgenden **UML-Anwendungsfalldiagramm** dargestellt:
![UML Use Case Diagram](UML-UseCaseDiagram.png "UML Use Case Diagram")

Hauptanwendungsfälle:

1. **Create Account**  
2. **Invest**  
3. **View Crypto Data**  
4. **Database**

---

#### 2.2 Create Account

- **Beschreibung:** Benutzer können ein Konto anlegen, um personalisierte Daten zu speichern.  
- **Voraussetzung:** Die Anwendung ist gestartet.  
- **Nachbedingung:** Der Benutzer wird in der Datenbank registriert.  
- **Aufwand:** Niedrig  

#### 2.3 Invest

- **Beschreibung:** Benutzer können Investitionen in Kryptowährungen simulieren oder speichern.  
- **Voraussetzung:** Ein Benutzerkonto existiert.  
- **Nachbedingung:** Investitionsdaten werden in der Datenbank gesichert.  
- **Aufwand:** Mittel  

#### 2.4 View Crypto Data

- **Beschreibung:** Benutzer können Kryptoinformationen (z. B. Preise, Symbole, Bilder) einsehen.  
- **Voraussetzung:** Die Datenbank ist initialisiert.  
- **Nachbedingung:** Daten werden aus der DB gelesen und angezeigt.  
- **Aufwand:** Niedrig  

#### 2.5 Database

- **Beschreibung:** Verwaltung der SQLite-Datenbank inkl. Speichern, Abrufen und Aktualisieren von Daten.  
- **Voraussetzung:** Anwendung gestartet, Datenbank vorhanden oder initialisiert.  
- **Nachbedingung:** Datenbankoperationen erfolgreich durchgeführt.  
- **Aufwand:** Mittel  

---

### 3. Nicht-funktionale Anforderungen

| Kategorie | Beschreibung |
|------------|--------------|
| **Benutzerfreundlichkeit** | Einfache, übersichtliche GUI in JavaFX |
| **Zuverlässigkeit** | Lokale Datenhaltung über SQLite |
| **Leistung** | Antwortzeiten unter 1 Sekunde |
| **Sicherheit** | Keine sensiblen Datenübertragungen, lokale Speicherung |
| **Wartbarkeit** | Modularer Aufbau in MVC-Struktur |

---

### 4. Technische Einschränkungen

- Programmiersprache: **Java 17+**  
- Frameworks: **JavaFX**, **BootstrapFX**, **ControlsFX**  
- Datenbank: **SQLite**  
- Systemtyp: **Desktop-Anwendung**  
- Lizenz: **Akademisches Projekt**
