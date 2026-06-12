"""Tests for GET /api/plants/<id>."""
from datetime import date, timedelta


def test_get_plant_by_id_returns_200(client, plant):
    resp = client.get(f'/api/plants/{plant["id"]}')
    assert resp.status_code == 200


def test_get_plant_by_id_has_all_required_fields(client, plant):
    data = client.get(f'/api/plants/{plant["id"]}').get_json()
    for field in ('id', 'name', 'species', 'location', 'created_at', 'status', 'schedules'):
        assert field in data, f"Missing field: {field}"


def test_get_plant_by_id_values_match_created_plant(client, plant):
    data = client.get(f'/api/plants/{plant["id"]}').get_json()
    assert data['id'] == plant['id']
    assert data['name'] == plant['name']
    assert data['species'] == plant['species']
    assert data['location'] == plant['location']
    assert data['created_at'] == plant['created_at']


def test_get_plant_by_id_schedules_empty_initially(client, plant):
    data = client.get(f'/api/plants/{plant["id"]}').get_json()
    assert data['schedules'] == []


def test_get_plant_by_id_schedules_contains_created_schedule(client, plant, schedule):
    data = client.get(f'/api/plants/{plant["id"]}').get_json()
    assert len(data['schedules']) == 1
    assert data['schedules'][0]['care_type'] == 'watering'
    assert data['schedules'][0]['interval_days'] == 7


def test_get_plant_by_id_schedules_lists_all_types(client, plant):
    for care_type, interval in [('watering', 7), ('fertilizing', 14), ('repotting', 180)]:
        client.post(f'/api/plants/{plant["id"]}/schedules', json={
            'care_type': care_type, 'interval_days': interval,
        })
    data = client.get(f'/api/plants/{plant["id"]}').get_json()
    assert len(data['schedules']) == 3


def test_get_plant_by_id_not_found_returns_404(client):
    resp = client.get('/api/plants/999')
    assert resp.status_code == 404


def test_get_plant_by_id_not_found_has_error_field(client):
    resp = client.get('/api/plants/999')
    assert 'error' in resp.get_json()


def test_get_plant_by_id_status_ok_no_schedules(client, plant):
    data = client.get(f'/api/plants/{plant["id"]}').get_json()
    assert data['status'] == 'ok'


def test_get_plant_by_id_status_overdue(client, plant, schedule):
    # plant created 2026-01-01, interval 7 → next_due 2026-01-08, definitely overdue today
    data = client.get(f'/api/plants/{plant["id"]}').get_json()
    assert data['status'] == 'overdue'


def test_get_plant_by_id_status_soon(client):
    today = date.today()
    created_at = (today - timedelta(days=5)).isoformat()  # interval=7 → next_due = today+2 → soon
    resp = client.post('/api/plants', json={
        'name': 'P', 'species': 'sp', 'location': 'loc', 'created_at': created_at,
    })
    pid = resp.get_json()['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    data = client.get(f'/api/plants/{pid}').get_json()
    assert data['status'] == 'soon'


def test_get_plant_by_id_schedules_have_required_fields(client, plant, schedule):
    data = client.get(f'/api/plants/{plant["id"]}').get_json()
    sched = data['schedules'][0]
    for field in ('id', 'plant_id', 'care_type', 'interval_days'):
        assert field in sched, f"Missing schedule field: {field}"
