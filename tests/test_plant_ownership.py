import pytest

# Liste mit allen Endpunkten, die auf konkrete Pflanze zugreifen --> alle Endpunkte mit <id>
foreign_plant_requests = [

    ("GET", "/api/plants/{plant_id}", None),
    ("PUT", "/api/plants/{plant_id}", {"name": "Fremde Monstera", "species": "Monstera deliciosa", "location": "Schlafzimmer"}),
    ("DELETE", "/api/plants/{plant_id}", None),
    ("GET", "/api/plants/{plant_id}/schedules", None),
    ("POST", "/api/plants/{plant_id}/schedules", {"care_type": "watering", "interval_days": 7}),
    ("DELETE", "/api/plants/{plant_id}/schedules/watering", None),
    ("GET", "/api/plants/{plant_id}/logs", None),
    ("POST", "/api/plants/{plant_id}/logs", {"care_type": "watering", "performed_at": "2026-01-05", "notes": "Test Notiz"}),
    ("GET", "/api/plants/{plant_id}/next-actions", None),
]


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


@pytest.mark.parametrize( # pytest soll denselben Test mehrfach ausführen
    "method, url_template, payload",
    foreign_plant_requests
)

def test_foreign_plant_access_returns_404(client, second_client, method, url_template, payload):
    plant_response = client.post("/api/plants", json = {
        "name": "Monstera",
        "species": "Deliciosa",
        "location": "Wohnzimmer"
    })

    plant_id = plant_response.get_json()["id"]
    url = url_template.format(plant_id = plant_id) # aus URL-Template echte URL bauen --> aus "/api/plants/{plant_id}" wird dann "/api/plants/1"

    response = second_client.open( # second_client ist anderer eingeloggter Nutzer -> versucht auf Pflanze von User 1 zuzugreifen
        url,
        method = method,
        json = payload
    )

    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 404
    assert "error" in data
    assert data["error"] == "Plant not found." # User bekommt aber dieselbe Antwort wie bei Pflanze, die gar nicht existiert


@pytest.mark.parametrize(
    "method, url_template, payload",
    foreign_plant_requests
)

def test_missing_plant_returns_404(client, method, url_template, payload):
    missing_plant_id = 999

    response = client.open(
        url_template.format(plant_id = missing_plant_id),
        method = method,
        json = payload
    )

    data = response.get_json()

    # Überprüfungen
    assert response.status_code == 404
    assert "error" in data
    assert data["error"] == "Plant not found."