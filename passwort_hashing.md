# Passwörter sicher speichern mit `werkzeug.security`

## Warum Passwörter niemals im Klartext speichern?

Wenn Passwörter unverschlüsselt in einer Datenbank oder einem Dictionary gespeichert werden, können sie bei einem Datenleck sofort missbraucht werden. Stattdessen sollte man **Passwort-Hashes** speichern: Ein Hash ist eine Einweg-Transformation – aus dem Hash lässt sich das ursprüngliche Passwort nicht zurückrechnen.

**Vorteile von Passwort-Hashing:**

- **Sicherheit bei Datenlecks:** Angreifer erhalten nur unleserliche Hash-Werte.
- **Einwegfunktion:** Der Hash kann nicht in das Original-Passwort zurückverwandelt werden.
- **Salt-Schutz:** `werkzeug` fügt automatisch einen zufälligen *Salt* hinzu, der Rainbow-Table-Angriffe verhindert.
- **Adaptiver Algorithmus:** Der verwendete Algorithmus (standardmäßig `scrypt`, früher `pbkdf2`) ist bewusst rechenintensiv, um Brute-Force-Angriffe zu erschweren.

## Die zwei wichtigsten Funktionen

### `generate_password_hash(password)`

Nimmt ein Klartext-Passwort entgegen und gibt einen sicheren Hash-String zurück.

### `check_password_hash(pwhash, password)`

Vergleicht einen gespeicherten Hash mit einem eingegebenen Passwort und gibt `True` oder `False` zurück.

## Installation

`werkzeug` wird direkt mit Flask installiert. Es ist somit kein zusätzlicher Eintrag in der `requirements.txt` notwendig.

## Beispiel: Passwörter in einem Dictionary speichern

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Simulated user database (dictionary)
users = {}

def register(username: str, password: str) -> None:
    """Registriert einen neuen Benutzer mit gehasshtem Passwort."""
    if username in users:
        print(f"Benutzer '{username}' existiert bereits.")
        return

    hashed_pw = generate_password_hash(password)
    users[username] = {"password_hash": hashed_pw}
    print(f"Benutzer '{username}' erfolgreich registriert.")

def login(username: str, password: str) -> bool:
    """Prüft ob Benutzername und Passwort übereinstimmen."""
    if username not in users:
        print(f"Benutzer '{username}' nicht gefunden.")
        return False

    stored_hash = users[username]["password_hash"]

    if check_password_hash(stored_hash, password):
        print(f"Login erfolgreich für '{username}'.")
        return True
    else:
        print("Falsches Passwort.")
        return False


# --- Anwendung ---

register("alice", "meinSicheresPasswort123")
register("bob",   "hunter2")

print("\nGespeicherte Daten im Dictionary:")
for name, data in users.items():
    print(f"  {name}: {data['password_hash']}")

print()
login("alice", "meinSicheresPasswort123")  # True
login("alice", "falschesPasswort")          # False
login("bob",   "hunter2")                  # True
```

### Beispiel-Ausgabe

```
Benutzer 'alice' erfolgreich registriert.
Benutzer 'bob' erfolgreich registriert.

Gespeicherte Daten im Dictionary:
  alice: scrypt:32768:8:1$abc123...$<langer Hash-String>
  bob:   scrypt:32768:8:1$xyz789...$<langer Hash-String>

Login erfolgreich für 'alice'.
Falsches Passwort.
Login erfolgreich für 'bob'.
```

> Obwohl `alice` und `bob` verschiedene Passwörter haben, sind beide Hash-Werte lang und kryptisch – das echte Passwort ist **nirgendwo sichtbar**.

## Was steckt im Hash-String?

Der generierte String enthält alle notwendigen Informationen zur späteren Verifizierung:

```
scrypt:32768:8:1$SaltWertHier$EigentlicherHashWertHier
```

| Teil | Bedeutung |
|---|---|
| `scrypt` | Verwendeter Algorithmus |
| `32768:8:1` | Kosten-Parameter (CPU/Speicher-Aufwand) |
| `$SaltWert` | Zufälliger Salt (automatisch generiert) |
| `$HashWert` | Der eigentliche Hash des Passworts |

`check_password_hash` liest diese Metadaten und führt denselben Algorithmus mit demselben Salt aus – nur wenn das Ergebnis identisch ist, war das Passwort korrekt.

## Zusammenfassung

| Funktion | Aufgabe |
|---|---|
| `generate_password_hash(pw)` | Passwort → sicherer Hash (beim Registrieren) |
| `check_password_hash(hash, pw)` | Hash + Eingabe vergleichen (beim Login) |

**Merksatz:** Niemals das Rohpasswort speichern – immer nur den Hash. `werkzeug.security` erledigt den Rest automatisch und sicher.
