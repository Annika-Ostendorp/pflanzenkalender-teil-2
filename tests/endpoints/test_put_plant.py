"""Tests for PUT /api/plants/<id>."""


def test_put_plant_returns_200(client, plant):
    resp = client.put(f'/api/plants/{plant["id"]}', json={'name': 'Neuer Name'})
    assert resp.status_code == 200


def test_put_plant_updates_name(client, plant):
    client.put(f'/api/plants/{plant["id"]}', json={'name': 'Umbenannt'})
    data = client.get(f'/api/plants/{plant["id"]}').get_json()
    assert data['name'] == 'Umbenannt'


def test_put_plant_updates_species(client, plant):
    client.put(f'/api/plants/{plant["id"]}', json={'species': 'Neue Art'})
    data = client.get(f'/api/plants/{plant["id"]}').get_json()
    assert data['species'] == 'Neue Art'


def test_put_plant_updates_location(client, plant):
    client.put(f'/api/plants/{plant["id"]}', json={'location': 'Schlafzimmer'})
    data = client.get(f'/api/plants/{plant["id"]}').get_json()
    assert data['location'] == 'Schlafzimmer'


def test_put_plant_updates_all_three_fields(client, plant):
    client.put(f'/api/plants/{plant["id"]}', json={
        'name': 'Neu', 'species': 'Neue Art', 'location': 'Flur',
    })
    data = client.get(f'/api/plants/{plant["id"]}').get_json()
    assert data['name'] == 'Neu'
    assert data['species'] == 'Neue Art'
    assert data['location'] == 'Flur'


def test_put_plant_partial_update_leaves_other_fields_unchanged(client, plant):
    original_species = plant['species']
    client.put(f'/api/plants/{plant["id"]}', json={'name': 'Anderer Name'})
    data = client.get(f'/api/plants/{plant["id"]}').get_json()
    assert data['species'] == original_species


def test_put_plant_empty_body_returns_200(client, plant):
    resp = client.put(f'/api/plants/{plant["id"]}', json={})
    assert resp.status_code == 200


def test_put_plant_empty_body_leaves_plant_unchanged(client, plant):
    client.put(f'/api/plants/{plant["id"]}', json={})
    data = client.get(f'/api/plants/{plant["id"]}').get_json()
    assert data['name'] == plant['name']
    assert data['species'] == plant['species']
    assert data['location'] == plant['location']


def test_put_plant_response_contains_updated_values(client, plant):
    resp = client.put(f'/api/plants/{plant["id"]}', json={'location': 'Keller'})
    assert resp.get_json()['location'] == 'Keller'


def test_put_plant_invalid_field_id_returns_400(client, plant):
    resp = client.put(f'/api/plants/{plant["id"]}', json={'id': 99})
    assert resp.status_code == 400


def test_put_plant_invalid_field_status_returns_400(client, plant):
    resp = client.put(f'/api/plants/{plant["id"]}', json={'status': 'ok'})
    assert resp.status_code == 400


def test_put_plant_invalid_field_created_at_returns_400(client, plant):
    resp = client.put(f'/api/plants/{plant["id"]}', json={'created_at': '2020-01-01'})
    assert resp.status_code == 400


def test_put_plant_invalid_field_schedules_returns_400(client, plant):
    resp = client.put(f'/api/plants/{plant["id"]}', json={'schedules': []})
    assert resp.status_code == 400


def test_put_plant_invalid_field_has_error_field(client, plant):
    resp = client.put(f'/api/plants/{plant["id"]}', json={'id': 1})
    assert 'error' in resp.get_json()


def test_put_plant_no_body_returns_400(client, plant):
    resp = client.put(f'/api/plants/{plant["id"]}',
                      content_type='application/json', data='')
    assert resp.status_code == 400


def test_put_plant_no_body_has_error_field(client, plant):
    resp = client.put(f'/api/plants/{plant["id"]}',
                      content_type='application/json', data='')
    assert 'error' in resp.get_json()


def test_put_plant_null_body_returns_400(client, plant):
    resp = client.put(f'/api/plants/{plant["id"]}',
                      data='null', content_type='application/json')
    assert resp.status_code == 400


def test_put_plant_null_body_has_error_field(client, plant):
    resp = client.put(f'/api/plants/{plant["id"]}',
                      data='null', content_type='application/json')
    assert 'error' in resp.get_json()


def test_put_plant_not_found_returns_404(client):
    resp = client.put('/api/plants/999', json={'name': 'x'})
    assert resp.status_code == 404


def test_put_plant_not_found_has_error_field(client):
    resp = client.put('/api/plants/999', json={'name': 'x'})
    assert 'error' in resp.get_json()
