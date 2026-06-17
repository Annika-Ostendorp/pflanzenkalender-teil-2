def test_register_success(client): # aus Akzeptanzkriterien 1 & 2 der User Story:
                                   # Endpoint mit gültigen Daten erstellt User, ohne dass das Passwort/Hash versehentlich zurückgegeben wird
    payload = {
        "username": "Annika",
        "password": "passwort123"
    }    

    response = client.post("/api/auth/register", json = payload) # Daten werden wieder per POST an Server/ Backend geschickt
    data = response.get_json() # JSON-Antwort dann in Dictionary umgewandelt

    # Überprüfungen
    assert response.status_code == 201 # wurde Statuscode 201 Created zurückgegeben --> User erfolgreich registriert?
    assert "id" in data # hat neuer User eine ID zugewiesen bekommen?
    assert "username" in data # befindet sich username in Antwort?
    assert data["username"] == "Annika" # stimmt zurückgegebener Username mit dem Übergebenen überein?
    assert "password" not in data # befindet sich Klartext-Passwort nicht in der Server-Antwort? --> darf nicht zurückgegeben werden
    assert "password_hash" not in data # Passwort-Hash darf ja auch nicht zurückgegeben werden


def test_register_duplicate_username(client): # Kann sich nicht mit einem bereits vergebenem Namen registrieren --> 409 Conflict
    payload = {
        "username": "Tobi",
        "password": "sicheres_passwort"
    }

    client.post("/api/auth/register", json = payload) # payload mit Tobi als User als erstes registrieren, damit Test nachher fehlschlägt, da dann zweimal Tobi im System existieren würde

    # jetzt nochmal versuchen einen User mit Namen "Tobi" zu registrieren 
    response = client.post("/api/auth/register", json = payload) # Daten wieder per POST an Server geschickt & dann Antwort in Dictionary umgewandelt
    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 409 # Name jetzt doppelt im System --> wurde Statuscode 409 zurückgegeben?
    assert "error" in data # "error" muss in Server-Antwort drin sein
    assert data["error"] == "Username is already taken." # entspricht die Fehlermeldung exakt dieser Syntax?


def test_register_missing_username(client): # wenn "username" komplett in Payload fehlt --> 400 Bad Request
    # hier payload erstellen, der extra kein "username"-Attribut bekommt
    payload = {
        "password": "meinpasswort"
    }

    response = client.post("/api/auth/register", json = payload)
    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 400 # Pflichtfeld "username" fehlt --> Statuscode 400 zurückgegeben?
    assert "error" in data # 'error' muss in Server-Antwort drin sein
    assert data["error"] == "Field 'username' is required." # entspricht die Fehlermeldung exakt dieser Syntax?


def test_register_missing_password(client): # gleiche Logik wie vorhin --> diesmal fehlt "password" in Payload
    payload = {
        "username": "Annika"
    }

    response = client.post("/api/auth/register", json = payload)
    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 400 # Pflichtfeld "password" fehlt --> Statuscode 400 zurückgegeben?
    assert "error" in data # 'error' muss in Server-Antwort wieder drin sein
    assert data["error"] == "Field 'password' is required." # entspricht die Fehlermeldung exakt dieser Syntax?


def test_register_empty_username(client): # Übergebener Username darf kein leerer String sein --> sonst 400 Bad Request
    payload = {
        "username": "",
        "password": "Annika123"
    }

    response = client.post("/api/auth/register", json = payload)
    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 400 # Leerer String für "username" ist nicht erlaubt --> Statuscode 400 zurückgegeben?
    assert "error" in data # 'error' muss in Server-Antwort drin sein
    assert data["error"] == "Field 'username' must not be empty." # entspricht die Fehlermeldung exakt dieser Syntax?


def test_register_empty_password(client): # Übergebenes Passwort darf auch kein leerer String sein --> sonst 400 Bad Request
    payload = {
        "username": "Bob",
        "password": ""
    }

    response = client.post("/api/auth/register", json = payload)
    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 400 # Leerer String für "password" ist nicht erlaubt --> Statuscode 400 zurückgegeben?
    assert "error" in data # 'error' muss in Server-Antwort drin sein
    assert data["error"] == "Field 'password' must not be empty." # entspricht die Fehlermeldung exakt dieser Syntax?


def test_register_username_too_long(client): # Username darf Maximumlänge von 50 Zeichen nicht überschreiten --> sonst 400 Bad Request
    sehr_langer_Benutzername = "abc" * 50 # überschreitet sicher die geforderte Maximumlänge eines Benutzernamens

    payload = {
        "username": sehr_langer_Benutzername,
        "password": "meintollespasswort"
    }

    response = client.post("/api/auth/register", json = payload)
    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 400 # Maximumlänge überschritten --> Statuscode 400 zurückgegeben?
    assert "error" in data # 'error' muss in Server-Antwort drin sein
    assert data["error"] == "Field 'username' must not exceed 50 characters." # entspricht die Fehlermeldung exakt dieser Syntax?