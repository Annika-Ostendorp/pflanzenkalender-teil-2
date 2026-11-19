# 🌿 Pflanzenkalender – Teil 2

**Benutzerverwaltung, JWT-Authentifizierung und kollaborative Softwareentwicklung**

## Projektübersicht

Im zweiten Teil des Hochschulprojekts Pflanzenkalender wurde die bestehende Python-/Flask-Anwendung um weitere Funktionen ergänzt.

Ein zentraler Schwerpunkt war die Erweiterung der ursprünglich entwickelten Pflanzenverwaltung um Benutzerkonten, Authentifizierung und benutzerspezifischen Zugriffsschutz.

Im Unterschied zum ersten Teil erfolgte die Entwicklung in einem **Team aus zwei Studierenden**.

Neben der technischen Umsetzung standen insbesondere UML-Modellierung, gegenseitige Code Reviews, automatisiertes Testing und die Zusammenarbeit über GitLab im Mittelpunkt.

## Funktionsumfang

### Benutzerregistrierung

Neue Benutzer können sich mit einem Benutzernamen und Passwort registrieren.

Die Implementierung berücksichtigt unter anderem:

- Überprüfung von Eingabedaten
- Passwortvalidierung
- Speicherung von Passwörtern als Hashwerte
- Behandlung bereits vorhandener Benutzernamen
- Geeignete Fehlermeldungen und HTTP-Statuscodes

### JWT-basierte Anmeldung

Registrierte Benutzer können sich anmelden und erhalten ein JSON Web Token (JWT), das zur Authentifizierung weiterer API-Anfragen verwendet wird.

Auch ungültige Zugangsdaten und fehlgeschlagene Anmeldeversuche werden behandelt.

### Zugriffsschutz für Benutzerdaten

Geschützte API-Funktionen überprüfen, ob eine Anfrage authentifiziert ist und der angemeldete Benutzer auf die angeforderten Daten zugreifen darf.

Dadurch soll verhindert werden, dass Benutzer durch manipulierte Ressourcen-IDs auf die Pflanzendaten anderer Personen zugreifen.

### Pflanzen- und Pflegeverwaltung

Die Anwendung umfasst außerdem die bestehenden Funktionen zur Verwaltung von Pflanzen, Pflegeintervallen und dokumentierten Pflegeaktivitäten.

## Verwendete Technologien

| Technologie | Einsatz |
|---|---|
| Python | Backend-Entwicklung |
| Flask | REST-API |
| JWT | Tokenbasierte Authentifizierung |
| Passwort-Hashing | Geschützte Speicherung von Passwörtern |
| pytest | Automatisierte Tests |
| Flask-Testclient | Tests der API-Endpunkte |
| pytest-cov | Testabdeckung |
| PlantUML | UML-Modellierung |
| Git & GitLab | Teamarbeit und Versionsverwaltung |
| Render | Bereitstellung der Demo |

## Mein persönlicher Beitrag

Im Teamprojekt übernahm ich die Verantwortung für die **User Stories #1, #2 und #3**.

### User Story #1 – Benutzerregistrierung

Mein erster Schwerpunkt war die Implementierung der Benutzerregistrierung.

Dabei beschäftigte ich mich mit der Validierung von Benutzernamen und Passwörtern, der Speicherung von Passwort-Hashes sowie mit der Behandlung ungültiger oder bereits verwendeter Benutzernamen.

### User Story #2 – Benutzeranmeldung

Meine zweite User Story beschäftigte sich mit der Anmeldung bestehender Benutzer.

Dazu gehörten die Prüfung der Zugangsdaten und die Verwendung von JWT für authentifizierte API-Anfragen.

### User Story #3 – Schutz benutzerspezifischer Daten

Meine dritte User Story konzentrierte sich auf die Zugriffsbeschränkung für persönliche Pflanzendaten.

Dafür mussten bestehende API-Funktionen um Authentifizierungsprüfungen und Benutzerzuordnungen erweitert werden.

Ein besonderer Testfall war die Frage, ob sich Daten anderer Benutzer durch die Änderung einer Pflanzen-ID abrufen lassen.

### Zusammenarbeit im Team

Die Entwicklung erfolgte gemeinsam mit einer weiteren Studentin.

Andere Aufgabenbereiche, darunter Arbeiten an der Datenhaltung und am Repository Pattern, wurden von meiner Teampartnerin übernommen.

Unsere Arbeit organisierten wir über GitLab-Issues, Feature-Branches und Merge Requests.

Die gegenseitige Überprüfung von Diagrammen, Tests und Implementierungen gehörte ebenfalls zum Entwicklungsprozess.

## UML-Modellierung

Ein zusätzlicher Bestandteil der zweiten Modularbeit war die Modellierung von Softwarestrukturen und Abläufen mit PlantUML.

Für die User Stories wurden geeignete Diagramme erstellt, beispielsweise zur Beschreibung von Klassenbeziehungen oder Interaktionsabläufen.

Die Modellierung half dabei, technische Zusammenhänge vor beziehungsweise während der Implementierung nachvollziehbar darzustellen.

## Testing und Qualitätssicherung

Die Anwendung wurde mit pytest und dem Flask-Testclient getestet.

Neben erfolgreichen API-Anfragen gehörten dazu unter anderem:

- Ungültige Registrierungsdaten
- Fehlerhafte Anmeldeversuche
- Fehlende oder ungültige Authentifizierung
- Unberechtigte Zugriffe auf fremde Pflanzendaten
- Fehlende Ressourcen und ungültige Anfragen

**Zuletzt dokumentiertes lokales Testergebnis:**

| Kennzahl | Ergebnis |
|---|---|
| Erfolgreiche Tests | 308 |
| Codeabdeckung | 99 % |

Die Angaben beziehen sich auf den zuletzt dokumentierten lokalen Testlauf. Sie stellen keine unabhängige Sicherheitsprüfung der Anwendung dar.

## Lokale Einrichtung und Tests

Voraussetzung ist eine passende Python-Installation.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Die Tests können mit folgendem Befehl gestartet werden:

```bash
python -m pytest
```

**Anwendung lokal starten (im Repository-Hauptverzeichnis):**

```bash
python src/app.py
```

Danach ist die Anwendung unter **http://127.0.0.1:5000** erreichbar. Für den Produktionsbetrieb gibt es zusätzlich `wsgi.py` als WSGI-Einstiegspunkt.

Für Render **muss** die Umgebungsvariable `JWT_SECRET_KEY` gesetzt sein. Auch lokal ist ein stabiler, zufällig erzeugter Schlüssel sinnvoll; Passwörter und Schlüssel gehören nicht ins Repository.

## Live-Demo

**[Pflanzenkalender – Demo auf Render](https://pflanzenkalender-teil-2.onrender.com)**

Für die Hochschularbeit wurde eine öffentlich zugängliche Demonstrationsversion bereitgestellt.

Die Demo verwendet lediglich eine temporäre Datenhaltung. Eingegebene Daten sind nicht als dauerhaft gespeicherte persönliche Pflanzenverwaltung zu verstehen.

## Technische Referenz: Authentifizierung und API

### Architektur und Datenhaltung

Die Flask-Anwendung wird über `PlantAppManager` in `src/app.py` erstellt. Der `AuthenticationService` in `src/auth_service.py` übernimmt Passwort-Hashing, Passwortprüfung sowie die Erstellung und Verifikation der JWTs.

Die Anwendung verwendet austauschbare Repository-Implementierungen: **In-Memory-Repositories** beispielsweise für isolierte Tests und **JSON-Repositories** für die lokale Ausführung. Diese Komponenten für Datenhaltung und Repository Pattern entstanden im Team; mein persönlicher Schwerpunkt lag auf den User Stories **#1–#3**.

Die lokale Startkonfiguration verwendet JSON-Dateien unter `data/`. Beim Deployment auf Render ist Dateispeicherung ohne dauerhaftes Volume nicht als verlässliche Persistenz anzusehen.

### Authentifizierungs-Endpunkte

| Methode | Pfad | Funktion |
|---|---|---|
| POST | `/api/auth/register` | Benutzerkonto mit `username` und `password` anlegen |
| POST | `/api/auth/login` | Anmelden und `access_token` erhalten |

Ein erfolgreiches Registrieren liefert den HTTP-Status **201**. Ein bereits vergebener Benutzername wird mit **409 Conflict** behandelt. Erfolgreicher Login liefert **200** und ein JWT, ungültige Anmeldedaten führen zu **401 Unauthorized**.

Die in `auth_service.py` implementierten JWTs verwenden **HS256** und eine Laufzeit von **3.600 Sekunden (eine Stunde)**. Für geschützte Anfragen wird der Header `Authorization: Bearer <token>` erwartet.

### Geschützte Pflanzen-Endpunkte

Die API stellt die Pflanzen- und Pflegefunktionen aus Teil 1 weiterhin bereit, unter anderem:

| Methode | Pfad | Funktion |
|---|---|---|
| GET, POST | `/api/plants` | Eigene Pflanzen abrufen beziehungsweise anlegen |
| GET, PUT, DELETE | `/api/plants/<id>` | Eigene Pflanze lesen, ändern oder löschen |
| GET, POST | `/api/plants/<id>/schedules` | Pflegepläne abrufen und verwalten |
| DELETE | `/api/plants/<id>/schedules/<care_type>` | Pflegeplan löschen |
| GET, POST | `/api/plants/<id>/logs` | Pflegeprotokolle abrufen und anlegen |
| GET | `/api/plants/<id>/next-actions` | Nächste Pflegeaktionen berechnen |
| GET | `/api/overdue` | Überfällige eigene Pflegeaktionen abrufen |

Diese Routen prüfen die JWT-Authentifizierung. Bei fehlendem beziehungsweise ungültigem Token wird die Anfrage mit **401** abgelehnt. Ein Zugriff auf nicht vorhandene oder fremde Pflanzen liefert **404**, um fremde Ressourcenzuordnungen nicht offenzulegen.

### Testkonfiguration

Die Tests verwenden `pytest` und den Flask-Testclient. `tests/conftest.py` stellt unter anderem getrennte authentifizierte Testclients für verschiedene Benutzer bereit. `pytest.ini` aktiviert bereits die Coverage-Messung:

```bash
python -m pytest
```

Dabei werden `--cov=src`, ein XML-Coverage-Bericht und die Anzeige nicht abgedeckter Zeilen verwendet. Die in der README genannten **308 erfolgreichen Tests bei 99 % Coverage** sind ein zuvor dokumentierter lokaler Teststand; sie wurden für diese README-Prüfung nicht neu ausgeführt.

## KI-Unterstützung

Auch im zweiten Projektteil verwendete ich KI-Werkzeuge, insbesondere ChatGPT, zur Unterstützung beim Lernen, Implementieren und Debuggen.

Dazu gehörten unter anderem Fragen zu Flask, JWT-Authentifizierung, Tests, UML-Diagrammen und technischen Fehlermeldungen.

Die Verwendung wurde entsprechend den Vorgaben des Moduls dokumentiert.

Die KI-Unterstützung ersetzte dabei nicht die Notwendigkeit, technische Lösungen zu verstehen, zu überprüfen und innerhalb des gemeinsamen Entwicklungsprozesses zu testen.

## Projektkontext

**Hochschule:** Hochschule München  
**Studiengang:** Informatik & Design (B.Sc.)  
**Modul:** Software Engineering  
**Semester:** Sommersemester 2026  
**Projektform:** Teamarbeit (zwei Studierende)  
**Meine Verantwortung:** User Stories #1–#3  
**Status:** Abgeschlossen

## Projektverbindung

Die zweite Modularbeit baut auf dem Pflanzenkalender-Projekt aus Teil 1 auf und erweitert die Anwendung um Benutzerverwaltung, Authentifizierung und zusätzliche Software-Engineering-Anforderungen.

**[Pflanzenkalender – Teil 1 auf GitHub](https://github.com/Annika-Ostendorp/pflanzenkalender-teil-1)**
