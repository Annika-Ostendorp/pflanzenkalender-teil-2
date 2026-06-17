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