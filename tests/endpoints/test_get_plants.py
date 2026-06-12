"""Tests for GET /api/plants."""
from datetime import date, timedelta


def test_get_plants_empty_list(client):
    resp = client.get('/api/plants')
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_get_plants_returns_created_plant(client, plant):
    resp = client.get('/api/plants')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]['id'] == plant['id']


def test_get_plants_returns_multiple_plants(client):
    client.post('/api/plants', json={'name': 'A', 'species': 'sp', 'location': 'loc'})
    client.post('/api/plants', json={'name': 'B', 'species': 'sp', 'location': 'loc'})
    resp = client.get('/api/plants')
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_get_plants_response_has_required_fields(client, plant):
    data = client.get('/api/plants').get_json()
    item = data[0]
    for field in ('id', 'name', 'species', 'location', 'created_at', 'status'):
        assert field in item, f"Missing field: {field}"


def test_get_plants_status_ok_when_no_schedules(client, plant):
    data = client.get('/api/plants').get_json()
    assert data[0]['status'] == 'ok'


def test_get_plants_status_overdue_when_action_past_due(client, plant, schedule):
    # plant created 2026-01-01, watering interval 7 → next_due 2026-01-08, definitely overdue today
    data = client.get('/api/plants').get_json()
    assert data[0]['status'] == 'overdue'


def test_get_plants_status_soon_when_action_due_in_three_days(client):
    today = date.today()
    created_at = (today - timedelta(days=4)).isoformat()  # interval=7 → next_due = today+3 → soon
    resp = client.post('/api/plants', json={'name': 'P', 'species': 'sp', 'location': 'loc', 'created_at': created_at})
    pid = resp.get_json()['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    data = client.get('/api/plants').get_json()
    plant_data = next(p for p in data if p['id'] == pid)
    assert plant_data['status'] == 'soon'


def test_get_plants_status_ok_when_action_more_than_three_days_away(client):
    today = date.today()
    created_at = today.isoformat()  # interval=7 → next_due = today+7 → ok
    resp = client.post('/api/plants', json={'name': 'P', 'species': 'sp', 'location': 'loc', 'created_at': created_at})
    pid = resp.get_json()['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    data = client.get('/api/plants').get_json()
    plant_data = next(p for p in data if p['id'] == pid)
    assert plant_data['status'] == 'ok'


def test_get_plants_overdue_takes_priority_over_soon(client):
    today = date.today()
    # watering (interval=7): next_due = today-11 → overdue
    # fertilizing (interval=20): next_due = today+2 → soon
    created_at = (today - timedelta(days=18)).isoformat()
    resp = client.post('/api/plants', json={'name': 'P', 'species': 'sp', 'location': 'loc', 'created_at': created_at})
    pid = resp.get_json()['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'fertilizing', 'interval_days': 20})
    data = client.get('/api/plants').get_json()
    plant_data = next(p for p in data if p['id'] == pid)
    assert plant_data['status'] == 'overdue'


def test_get_plants_data_matches_created_values(client):
    client.post('/api/plants', json={
        'name': 'Gummibaum',
        'species': 'Ficus elastica',
        'location': 'Flur',
        'created_at': '2026-03-01',
    })
    data = client.get('/api/plants').get_json()
    item = data[0]
    assert item['name'] == 'Gummibaum'
    assert item['species'] == 'Ficus elastica'
    assert item['location'] == 'Flur'
    assert item['created_at'] == '2026-03-01'
