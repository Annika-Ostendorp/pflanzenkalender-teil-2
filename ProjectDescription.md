# Pflanzen-Pflegekalender

**Wichtig: Lesen Sie unbedingt zuerst die Datei `README.md` vollständig durch, bevor Sie diese Beschreibung lesen.**

Im Rahmen der ersten Modularbeit haben Sie erfolgreich eine webbasierte Anwendung zur Verwaltung von Zimmerpflanzen und deren Pflegeplänen entwickelt.
In diesem Teil der Modularbeit ist eine Musterlösung des ersten Teils inklusive Tests vorgegeben, welche Sie weiterentwickeln sollen.

WICHTIG: Entwickeln Sie den Code dieses Projekts weiter! Nehmen Sie sich hierfür die Zeit, um sich einen Überblick über den Code und die Tests zu verschaffen.

Der vorgegebene Code soll um folgende Features erweitert werden:

* Nutzer sollen sich in die Webanwendung einloggen können.
* Noch nicht registrierte Nutzer sollen sich registrieren können.
* Eingeloggte Nutzer sollen nur ihre eigenen Pflanzen, zugehörige Pflegekalender und Logs sehen. 
* Änderungen sollen persistent gespeichert werden können.


**Wichtig:** Testen Sie zunächst die aktuelle Anwendung und machen Sie sich mit der Struktur des Codes vertraut, bevor Sie irgendwelche Änderungen durchführen.

## Technischer Rahmen

Das Frontend (`static/app.js`) ist zusammen mit dem Style Sheet (`static/style.css`) und der `templates/index.html` bereits vorgegeben.
Die für den Login / die Registrierung notwendigen Änderungen am Frontend finden Sie im Branch `feature-frontend-login`.
Um an der entsprechenden User Story arbeiten zu können, müssen Sie diese Features in den Branch des Merge Requests mergen.

## User Stories

Sie finden im Gitlab-Projekt für die umzusetzenden Features entsprechende User Stories, die sie im Team zu Beginn des Sprints aufteilen sollen (siehe `README.md`).

Empfehlung für die Aufteilung: 

* Ein Team-Mitglied kümmert sich um Registrierung, Login und Filterung der Pflanzen nach Nutzer.
* Das andere Team-Mitglied setzt das Repository Pattern zusammen mit der Persistenz um.
