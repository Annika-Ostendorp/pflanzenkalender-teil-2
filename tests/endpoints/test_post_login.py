def test_post_login_success(client):
    register_payload = { # erst registrieren, damit man sich danach ja nochmal einloggen kann
        "username": "Annika",
        "password": "passwort123"
    }

    client.post("api/auth/login", json = register_payload)
    
    payload = {
        "username": "Annika",
        "password": "passwort123"
    }

    response = client.post("api/auth/login", json = payload)
    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 200
    assert "access_token" in data
    assert isinstance(data["access_token"], str) # Token muss vom Typ str sein
    assert data["access_token"] != ""
    assert "password" not in data
    assert "password_hash" not in data