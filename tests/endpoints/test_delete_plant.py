"""Tests for DELETE /api/plants/<id>."""


def test_delete_plant_returns_204(client, plant):
    resp = client.delete(f'/api/plants/{plant["id"]}')
    assert resp.status_code == 204


def test_delete_plant_returns_no_body(client, plant):
    resp = client.delete(f'/api/plants/{plant["id"]}')
    assert resp.data == b''


def test_delete_plant_makes_plant_unreachable_via_get_by_id(client, plant):
    pid = plant['id']
    client.delete(f'/api/plants/{pid}')
    resp = client.get(f'/api/plants/{pid}')
    assert resp.status_code == 404


def test_delete_plant_removes_plant_from_list(client, plant):
    pid = plant['id']
    client.delete(f'/api/plants/{pid}')
    all_plants = client.get('/api/plants').get_json()
    assert not any(p['id'] == pid for p in all_plants)


def test_delete_plant_associated_schedules_deleted(client, plant, schedule):
    pid = plant['id']
    client.delete(f'/api/plants/{pid}')
    resp = client.get(f'/api/plants/{pid}/schedules')
    assert resp.status_code == 404


def test_delete_plant_associated_logs_deleted(client, plant, log_entry):
    pid = plant['id']
    client.delete(f'/api/plants/{pid}')
    resp = client.get(f'/api/plants/{pid}/logs')
    assert resp.status_code == 404


def test_delete_plant_second_delete_returns_404(client, plant):
    pid = plant['id']
    client.delete(f'/api/plants/{pid}')
    resp = client.delete(f'/api/plants/{pid}')
    assert resp.status_code == 404


def test_delete_plant_not_found_returns_404(client):
    resp = client.delete('/api/plants/999')
    assert resp.status_code == 404


def test_delete_plant_not_found_has_error_field(client):
    resp = client.delete('/api/plants/999')
    assert 'error' in resp.get_json()


def test_delete_plant_does_not_affect_other_plants(client):
    p1 = client.post('/api/plants', json={'name': 'A', 'species': 'sp', 'location': 'l'}).get_json()
    p2 = client.post('/api/plants', json={'name': 'B', 'species': 'sp', 'location': 'l'}).get_json()
    client.delete(f'/api/plants/{p1["id"]}')
    resp = client.get(f'/api/plants/{p2["id"]}')
    assert resp.status_code == 200
