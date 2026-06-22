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


def test_post_login_unknown_username_and_wrong_password_same_response(client): # gegen Username Enumeration -> unbekannter Username & falsches Passwort
                                                                               # führen zur selben Antwort
    register_payload = {
        "username": "Lena",
        "password": "richtigespasswort"
    }                                 

    client.post("/api/auth/register", json = register_payload)

    unknown_user_payload = {
        "username": "unbekannt",
        "password": "richtigespasswort"
    }

    wrong_password_payload = {
        "username": "Lena",
        "password": "falschespasswort"
    }                                

    unknown_user_response = client.post("/api/auth/login", json = unknown_user_payload)
    wrong_password_response = client.post("/api/auth/login", json = wrong_password_payload)

    unknown_user_data = unknown_user_response.get_json()
    wrong_password_data = wrong_password_response.get_json()

    # Überprüfungen
    assert unknown_user_response.status_code == 401
    assert wrong_password_response.status_code == 401
    assert unknown_user_data == wrong_password_data
    assert "error" in unknown_user_data
    assert unknown_user_data["error"] == "Invalid username or password."


def test_post_login_missing_username(client):
    payload = {
        "password": "meinpasswort"
    }

    response = client.post("/api/auth/login", json = payload)
    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 400
    assert "error" in data
    assert data["error"] == "Field 'username' is required."


def test_post_login_missing_password(client):
    payload = {
        "username": "Annika"
    }

    response = client.post("/api/auth/login", json = payload)
    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 400
    assert "error" in data
    assert data["error"] == "Field 'password' is required."


def test_post_login_empty_username(client):
    payload = {
        "username": "",
        "password": "Annika123"
    }

    response = client.post("/api/auth/login", json = payload)
    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 400
    assert "error" in data
    assert data["error"] == "Field 'username' must not be empty."


def test_post_login_empty_password(client):
    payload = {
        "username": "Bob",
        "password": ""
    }

    response = client.post("/api/auth/login", json = payload)
    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 400
    assert "error" in data
    assert data["error"] == "Field 'password' must not be empty."


def test_post_login_invalid_json_body(client):
    invalid_json = "{username: Annika}"

    response = client.post("/api/auth/login", data = invalid_json)
    data = response.get_json()

    # Überprüfungen:
    assert response.status_code == 400
    assert "error" in data
    assert data["error"] == "Request body must be valid JSON."


def test_post_login_invalid_content_type(client):
    payload = {
        "username": "Annika",
        "password": "passwort123"
    }

    response = client.post("/api/auth/login", data = str(payload), content_type = "text/plain")
    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 415
    assert "error" in data
    assert data["error"] == "Content-Type must be 'application/json'."


def test_post_login_unexpected_server_error(client):
    payload = {
        "username": ["Ungültig"],
        "password": "meinsicherespasswort"
    }

    response = client.post("/api/auth/login", json = payload)
    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 500
    assert "error" in data
    assert data["error"] == "An unexpected error occured. Please try again later."