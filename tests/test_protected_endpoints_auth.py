import jwt
import time

protected_requests = [
    ("GET", "/api/plants", None),
    ("POST", "/api/plants", {"name": "Monstera"}),
    ("GET", "/api/plants/1", None),
    ("PUT", "/api/plants/1", {"name": "Monstera"}),
    ("DELETE", "/api/plants/1", None),
    ("GET", "/api/plants/1/schedules", None),
    ("POST", "/api/plants/1/schedules", {"care_type": "watering", "interval_days": 7}),
    ("DELETE", "/api/plants/1/schedules/watering", None),
    ("GET", "/api/plants/1/logs", None),
    ("POST", "/api/plants/1/logs", {"care_type": "watering"}),
    ("GET", "/api/plants/1/next-actions", None),
    ("GET", "api/overdue", None),
 ]

def test_protected_endpoints_missing_token(unauthenticated_client):
    for method, url, payload in protected_requests:
        response = unauthenticated_client.open(
            url,
            method = method,
            json = payload
        )

        data = response.get_json()

        # Überprüfungen
        assert response.status_code == 401
        assert "error" in data
        assert data["error"] == "Authentication required."


def test_protected_endpoints_invalid_token(unauthenticated_client):
    unauthenticated_client.environ_base["HTTP_AUTHORIZATION"] = "Bearer invalid-token"

    for method, url, payload in protected_requests:
        response = unauthenticated_client.open(
            url,
            method = method,
            json = payload
        )

        data = response.get_json()

        # Überprüfungen
        assert response.status_code == 401
        assert "error" in data
        assert data["error"] == "Invalid or expired token."


def test_protected_endpoints_expired_token(unauthenticated_client):
    expired_payload = {
        "sub": "1",
        "iat": int(time.time()) - 7200,
        "exp": int(time.time()) - 3600
    }

    expired_token = jwt.encode(
        expired_payload,
        "test-secret",
        algorithm = "HS256"
    )

    unauthenticated_client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {expired_token}"

    for method, url, payload in protected_requests:
        response = unauthenticated_client.open(
            url,
            method = method,
            json = payload
        )

        data = response.get_json()

        # Überprüfungen
        assert response.status_code == 401
        assert "error" in data
        assert data["error"] == "Invalid or expired token."