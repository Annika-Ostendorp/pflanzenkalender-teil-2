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