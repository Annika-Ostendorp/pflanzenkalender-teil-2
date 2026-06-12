"""Tests for GET /api/overdue."""
from datetime import date, timedelta


def test_get_overdue_empty_when_no_plants(client):
    resp = client.get('/api/overdue')
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_get_overdue_empty_when_no_schedules(client, plant):
    resp = client.get('/api/overdue')
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_get_overdue_empty_when_not_yet_overdue(client):
    today = date.today()
    created_at = (today - timedelta(days=2)).isoformat()  # interval=7 → next_due = today+5 → not overdue
    resp = client.post('/api/plants', json={
        'name': 'P', 'species': 'sp', 'location': 'loc', 'created_at': created_at,
    })
    pid = resp.get_json()['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    assert client.get('/api/overdue').get_json() == []


def test_get_overdue_exactly_today_is_not_overdue(client):
    today = date.today()
    created_at = (today - timedelta(days=7)).isoformat()  # interval=7 → next_due = today → not overdue
    resp = client.post('/api/plants', json={
        'name': 'P', 'species': 'sp', 'location': 'loc', 'created_at': created_at,
    })
    pid = resp.get_json()['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    assert client.get('/api/overdue').get_json() == []


def test_get_overdue_returns_overdue_item(client):
    today = date.today()
    created_at = (today - timedelta(days=14)).isoformat()  # interval=7 → next_due = today-7 → 7 days overdue
    resp = client.post('/api/plants', json={
        'name': 'P', 'species': 'sp', 'location': 'loc', 'created_at': created_at,
    })
    pid = resp.get_json()['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    data = client.get('/api/overdue').get_json()
    assert len(data) == 1
    assert data[0]['plant_id'] == pid
    assert data[0]['care_type'] == 'watering'
    assert data[0]['days_overdue'] == 7


def test_get_overdue_items_have_required_fields(client):
    today = date.today()
    created_at = (today - timedelta(days=14)).isoformat()  # interval=7 → next_due = today-7 → overdue
    resp = client.post('/api/plants', json={
        'name': 'P', 'species': 'sp', 'location': 'loc', 'created_at': created_at,
    })
    pid = resp.get_json()['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    data = client.get('/api/overdue').get_json()
    item = data[0]
    for field in ('plant_id', 'plant_name', 'plant_location', 'care_type', 'next_due', 'days_overdue'):
        assert field in item, f"Missing field: {field}"


def test_get_overdue_item_values_are_correct(client):
    today = date.today()
    created_at = (today - timedelta(days=14)).isoformat()
    next_due_expected = (today - timedelta(days=7)).isoformat()
    resp = client.post('/api/plants', json={
        'name': 'Testpflanze', 'species': 'sp', 'location': 'Wohnzimmer', 'created_at': created_at,
    })
    pid = resp.get_json()['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    data = client.get('/api/overdue').get_json()
    item = data[0]
    assert item['plant_name'] == 'Testpflanze'
    assert item['plant_location'] == 'Wohnzimmer'
    assert item['next_due'] == next_due_expected
    assert item['days_overdue'] == 7


def test_get_overdue_sorted_descending_by_days_overdue(client, plant):
    pid = plant['id']
    # plant created 2026-01-01
    # watering every 7 days → next_due 2026-01-08 → overdue today
    # fertilizing every 3 days → next_due 2026-01-04 → more overdue today
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'fertilizing', 'interval_days': 3})
    data = client.get('/api/overdue').get_json()
    assert len(data) == 2
    assert data[0]['days_overdue'] >= data[1]['days_overdue']
    assert data[0]['care_type'] == 'fertilizing'


def test_get_overdue_uses_last_log_date(client):
    today = date.today()
    created_at = (today - timedelta(days=20)).isoformat()
    last_log_date = (today - timedelta(days=8)).isoformat()   # interval=7 → next_due = today-1 → 1 day overdue
    next_due_expected = (today - timedelta(days=1)).isoformat()
    resp = client.post('/api/plants', json={
        'name': 'P', 'species': 'sp', 'location': 'loc', 'created_at': created_at,
    })
    pid = resp.get_json()['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    client.post(f'/api/plants/{pid}/logs', json={'care_type': 'watering', 'performed_at': last_log_date})
    data = client.get('/api/overdue').get_json()
    assert len(data) == 1
    assert data[0]['next_due'] == next_due_expected
    assert data[0]['days_overdue'] == 1


def test_get_overdue_multiple_plants(client):
    today = date.today()
    created_at = (today - timedelta(days=14)).isoformat()
    p1 = client.post('/api/plants', json={
        'name': 'Pflanze 1', 'species': 'sp1', 'location': 'Zimmer', 'created_at': created_at,
    }).get_json()
    p2 = client.post('/api/plants', json={
        'name': 'Pflanze 2', 'species': 'sp2', 'location': 'Flur', 'created_at': created_at,
    }).get_json()
    client.post(f'/api/plants/{p1["id"]}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    client.post(f'/api/plants/{p2["id"]}/schedules', json={'care_type': 'fertilizing', 'interval_days': 7})
    data = client.get('/api/overdue').get_json()
    assert len(data) == 2
    plant_ids = {item['plant_id'] for item in data}
    assert p1['id'] in plant_ids
    assert p2['id'] in plant_ids


def test_get_overdue_excludes_non_overdue_schedules(client):
    today = date.today()
    created_at = (today - timedelta(days=14)).isoformat()
    resp = client.post('/api/plants', json={
        'name': 'P', 'species': 'sp', 'location': 'loc', 'created_at': created_at,
    })
    pid = resp.get_json()['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'repotting', 'interval_days': 365})
    data = client.get('/api/overdue').get_json()
    assert len(data) == 1
    assert data[0]['care_type'] == 'watering'
