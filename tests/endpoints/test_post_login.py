import jwt

def test_post_login_success(client):
    register_payload = { # erst registrieren, damit man sich danach ja nochmal einloggen kann
        "username": "Annika",
        "password": "passwort123"
    }

    client.post("api/auth/register", json = register_payload)
    
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

def test_post_login_token_contains_required_claims(client):
    register_payload = {
        "username": "Bob",
        "password": "sicherespasswort"
    }
    client.post("/api/auth/register", json = register_payload)

    payload = {
        "username": "Bob",
        "password": "sicherespasswort"
    } 

    response = client.post("/api/auth/login", json = payload)
    data = response.get_json()
    token_payload = jwt.decode(data["access_token"], "test-secret", algorithms=["HS256"])

    # Überprüfungen
    assert response.status_code == 200 # Login muss erfolgreich sein -> sonst kommt kein valider Token zurück 
    assert "sub" in token_payload
    assert "iat" in token_payload
    assert "exp" in token_payload
    assert isinstance(token_payload["sub"], str) # muss laut Akzeptanzkriterium ein str sein
    assert token_payload["sub"] != ""
    assert token_payload["exp"] > token_payload["iat"] # Ablaufzeitpunkt logischerweise nach Ausstellungszeitpunkt
    assert token_payload["exp"] - token_payload["iat"] == 3600 # Token soll 1 Stunde gültig sein


def test_post_login_unknown_username(client): # unbekannter Username --> 401 Unauthorized
    payload = {
        "username": "Ungültig",
        "password": "irgendeinpasswort"
    }

    response = client.post("/api/auth/login", json = payload)
    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 401
    assert "error" in data 
    assert data["error"] == "Invalid username or password."


def test_post_login_wrong_password(client):
    register_payload = {
        "username": "Tobi",
        "password": "richtigespasswort"
    }

    client.post("/api/auth/register", json = register_payload)

    payload = {
        "username": "Tobi",
        "password": "falschespasswort"
    }

    response = client.post("/api/auth/login", json = payload)
    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 401
    assert "error" in data
    assert data["error"] == "Invalid username or password."