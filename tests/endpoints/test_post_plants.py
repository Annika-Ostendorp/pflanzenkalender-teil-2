"""Tests for POST /api/plants."""
from datetime import date


def test_post_plants_returns_201(client):
    resp = client.post('/api/plants', json={
        'name': 'Efeutute', 'species': 'Epipremnum aureum', 'location': 'Küche',
    })
    assert resp.status_code == 201


def test_post_plants_response_has_all_fields(client):
    resp = client.post('/api/plants', json={
        'name': 'Efeutute', 'species': 'Epipremnum aureum', 'location': 'Küche',
    })
    data = resp.get_json()
    for field in ('id', 'name', 'species', 'location', 'created_at', 'status'):
        assert field in data, f"Missing field: {field}"


def test_post_plants_response_values_match_input(client):
    resp = client.post('/api/plants', json={
        'name': 'Gummibaum',
        'species': 'Ficus elastica',
        'location': 'Wohnzimmer',
        'created_at': '2026-04-01',
    })
    data = resp.get_json()
    assert data['name'] == 'Gummibaum'
    assert data['species'] == 'Ficus elastica'
    assert data['location'] == 'Wohnzimmer'
    assert data['created_at'] == '2026-04-01'


def test_post_plants_with_explicit_created_at(client):
    resp = client.post('/api/plants', json={
        'name': 'X', 'species': 'Y', 'location': 'Z', 'created_at': '2025-06-15',
    })
    assert resp.get_json()['created_at'] == '2025-06-15'


def test_post_plants_default_created_at_is_today(client):
    resp = client.post('/api/plants', json={'name': 'X', 'species': 'Y', 'location': 'Z'})
    assert resp.get_json()['created_at'] == date.today().isoformat()


def test_post_plants_new_plant_has_status_ok(client):
    resp = client.post('/api/plants', json={'name': 'X', 'species': 'Y', 'location': 'Z'})
    assert resp.get_json()['status'] == 'ok'


def test_post_plants_plant_appears_in_get_all(client):
    resp = client.post('/api/plants', json={'name': 'Visible', 'species': 'sp', 'location': 'loc'})
    pid = resp.get_json()['id']
    all_plants = client.get('/api/plants').get_json()
    assert any(p['id'] == pid for p in all_plants)


def test_post_plants_each_plant_gets_unique_id(client):
    id1 = client.post('/api/plants', json={'name': 'A', 'species': 'sp', 'location': 'l'}).get_json()['id']
    id2 = client.post('/api/plants', json={'name': 'B', 'species': 'sp', 'location': 'l'}).get_json()['id']
    assert id1 != id2


def test_post_plants_missing_name_returns_400(client):
    resp = client.post('/api/plants', json={'species': 'Ficus', 'location': 'Flur'})
    assert resp.status_code == 400


def test_post_plants_missing_species_returns_400(client):
    resp = client.post('/api/plants', json={'name': 'X', 'location': 'Flur'})
    assert resp.status_code == 400


def test_post_plants_missing_location_returns_400(client):
    resp = client.post('/api/plants', json={'name': 'X', 'species': 'sp'})
    assert resp.status_code == 400


def test_post_plants_empty_body_returns_400(client):
    resp = client.post('/api/plants', content_type='application/json', data='')
    assert resp.status_code == 400


def test_post_plants_error_response_has_error_field(client):
    resp = client.post('/api/plants', json={'species': 'Ficus', 'location': 'Flur'})
    assert 'error' in resp.get_json()


def test_post_plants_missing_all_fields_returns_400(client):
    resp = client.post('/api/plants', json={})
    assert resp.status_code == 400
