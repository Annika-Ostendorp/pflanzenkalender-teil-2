"""Tests for GET /api/plants/<id>/schedules."""


def test_get_schedules_empty_list(client, plant):
    resp = client.get(f'/api/plants/{plant["id"]}/schedules')
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_get_schedules_contains_created_schedule(client, plant, schedule):
    resp = client.get(f'/api/plants/{plant["id"]}/schedules')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]['care_type'] == 'watering'
    assert data[0]['interval_days'] == 7


def test_get_schedules_response_items_have_required_fields(client, plant, schedule):
    data = client.get(f'/api/plants/{plant["id"]}/schedules').get_json()
    item = data[0]
    for field in ('id', 'plant_id', 'care_type', 'interval_days'):
        assert field in item, f"Missing field: {field}"


def test_get_schedules_plant_id_matches(client, plant, schedule):
    data = client.get(f'/api/plants/{plant["id"]}/schedules').get_json()
    assert data[0]['plant_id'] == plant['id']


def test_get_schedules_all_three_care_types(client, plant):
    pid = plant['id']
    for care_type, days in [('watering', 7), ('fertilizing', 30), ('repotting', 365)]:
        client.post(f'/api/plants/{pid}/schedules', json={'care_type': care_type, 'interval_days': days})
    data = client.get(f'/api/plants/{pid}/schedules').get_json()
    assert len(data) == 3
    care_types = {s['care_type'] for s in data}
    assert care_types == {'watering', 'fertilizing', 'repotting'}


def test_get_schedules_plant_not_found_returns_404(client):
    resp = client.get('/api/plants/999/schedules')
    assert resp.status_code == 404


def test_get_schedules_plant_not_found_has_error_field(client):
    resp = client.get('/api/plants/999/schedules')
    assert 'error' in resp.get_json()


def test_get_schedules_only_returns_schedules_for_this_plant(client):
    p1 = client.post('/api/plants', json={'name': 'A', 'species': 'sp', 'location': 'l'}).get_json()
    p2 = client.post('/api/plants', json={'name': 'B', 'species': 'sp', 'location': 'l'}).get_json()
    client.post(f'/api/plants/{p1["id"]}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    client.post(f'/api/plants/{p2["id"]}/schedules', json={'care_type': 'fertilizing', 'interval_days': 14})
    data = client.get(f'/api/plants/{p1["id"]}/schedules').get_json()
    assert all(s['plant_id'] == p1['id'] for s in data)
    assert len(data) == 1
