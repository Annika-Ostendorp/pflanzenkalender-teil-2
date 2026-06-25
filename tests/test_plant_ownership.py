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