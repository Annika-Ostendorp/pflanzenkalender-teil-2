def test_post_plants_rejects_manual_user_id(client): # Request-Body darf keine manuelle hinzugefügte user_id haben -> 400 Bad Request (siehe Security Notes & AC 3 von User Story)
    payload = {
        "name": "Monstera",
        "species": "Deliciosa",
        "location": "Wohnzimmer",
        "user_id": 999
    }

    response = client.post("/api/plants", json = payload)
    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 400
    assert "error" in data
    assert data["error"] == "Field 'user_id' must not be set manually." 