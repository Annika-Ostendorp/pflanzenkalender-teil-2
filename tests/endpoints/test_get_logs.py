"""Tests for GET /api/plants/<id>/logs."""


def test_get_logs_empty_list(client, plant):
    resp = client.get(f'/api/plants/{plant["id"]}/logs')
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_get_logs_contains_created_log(client, plant, log_entry):
    resp = client.get(f'/api/plants/{plant["id"]}/logs')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]['care_type'] == 'watering'
    assert data[0]['performed_at'] == '2026-01-05'


def test_get_logs_items_have_required_fields(client, plant, log_entry):
    data = client.get(f'/api/plants/{plant["id"]}/logs').get_json()
    item = data[0]
    for field in ('id', 'plant_id', 'care_type', 'performed_at', 'notes'):
        assert field in item, f"Missing field: {field}"


def test_get_logs_plant_id_matches(client, plant, log_entry):
    data = client.get(f'/api/plants/{plant["id"]}/logs').get_json()
    assert data[0]['plant_id'] == plant['id']


def test_get_logs_sorted_descending_by_date(client, plant):
    pid = plant['id']
    for d in ['2026-01-10', '2026-01-20', '2026-01-05']:
        client.post(f'/api/plants/{pid}/logs', json={'care_type': 'watering', 'performed_at': d})
    data = client.get(f'/api/plants/{pid}/logs').get_json()
    dates = [entry['performed_at'] for entry in data]
    assert dates == sorted(dates, reverse=True)


def test_get_logs_most_recent_first(client, plant):
    pid = plant['id']
    client.post(f'/api/plants/{pid}/logs', json={'care_type': 'watering', 'performed_at': '2026-01-01'})
    client.post(f'/api/plants/{pid}/logs', json={'care_type': 'watering', 'performed_at': '2026-06-01'})
    data = client.get(f'/api/plants/{pid}/logs').get_json()
    assert data[0]['performed_at'] == '2026-06-01'
    assert data[1]['performed_at'] == '2026-01-01'


def test_get_logs_multiple_care_types(client, plant):
    pid = plant['id']
    client.post(f'/api/plants/{pid}/logs', json={'care_type': 'watering', 'performed_at': '2026-01-10'})
    client.post(f'/api/plants/{pid}/logs', json={'care_type': 'fertilizing', 'performed_at': '2026-01-05'})
    data = client.get(f'/api/plants/{pid}/logs').get_json()
    assert len(data) == 2
    care_types = {entry['care_type'] for entry in data}
    assert 'watering' in care_types
    assert 'fertilizing' in care_types


def test_get_logs_only_returns_this_plants_logs(client):
    p1 = client.post('/api/plants', json={'name': 'A', 'species': 'sp', 'location': 'l'}).get_json()
    p2 = client.post('/api/plants', json={'name': 'B', 'species': 'sp', 'location': 'l'}).get_json()
    client.post(f'/api/plants/{p1["id"]}/logs', json={'care_type': 'watering'})
    client.post(f'/api/plants/{p2["id"]}/logs', json={'care_type': 'fertilizing'})
    data = client.get(f'/api/plants/{p1["id"]}/logs').get_json()
    assert len(data) == 1
    assert all(entry['plant_id'] == p1['id'] for entry in data)


def test_get_logs_plant_not_found_returns_404(client):
    resp = client.get('/api/plants/999/logs')
    assert resp.status_code == 404


def test_get_logs_plant_not_found_has_error_field(client):
    resp = client.get('/api/plants/999/logs')
    assert 'error' in resp.get_json()
