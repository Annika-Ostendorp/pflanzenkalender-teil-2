import pytest
from src.app import PlantAppManager
from src.in_memory_repositories import (
    InMemoryPlantRepository,
    InMemoryCareScheduleRepository,
    InMemoryActionLogRepository,
    InMemoryUserRepository,
)



@pytest.fixture
def client():
    manager = PlantAppManager(
        plant_repo=InMemoryPlantRepository(),
        schedule_repo=InMemoryCareScheduleRepository(),
        log_repo=InMemoryActionLogRepository(),
        user_repo=InMemoryUserRepository(),
    )
    manager.app.config['TESTING'] = True
    with manager.app.test_client() as c:
        yield c


@pytest.fixture
def plant(client):
    """Create a plant with a known created_at for deterministic date tests."""
    resp = client.post('/api/plants', json={
        'name': 'Testpflanze',
        'species': 'Testus species',
        'location': 'Wohnzimmer',
        'created_at': '2026-01-01',
    })
    return resp.get_json()


@pytest.fixture
def schedule(client, plant):
    """Create a watering schedule with interval 7 for the default plant."""
    resp = client.post(f'/api/plants/{plant["id"]}/schedules', json={
        'care_type': 'watering',
        'interval_days': 7,
    })
    return resp.get_json()


@pytest.fixture
def log_entry(client, plant):
    """Create a watering log on 2026-01-05 for the default plant."""
    resp = client.post(f'/api/plants/{plant["id"]}/logs', json={
        'care_type': 'watering',
        'performed_at': '2026-01-05',
        'notes': 'Test Notiz',
    })
    return resp.get_json()


@pytest.fixture
def register_user(client):
    def _register_user(username, password):
        return client.post("/api/auth/register",
            json = {
            "username": username,
            "password": password
            }
        )
    return _register_user


@pytest.fixture
def unauthenticated_client():
    manager = PlantAppManager(
        plant_repo = InMemoryPlantRepository(),
        schedule_repo = InMemoryCareScheduleRepository(),
        log_repo = InMemoryActionLogRepository(),
        user_repo = InMemoryUserRepository(),
    )

    manager.app.config['TESTING'] = True
    with manager.app.test_client() as c:
        yield c