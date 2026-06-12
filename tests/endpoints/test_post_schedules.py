"""Tests for POST /api/plants/<id>/schedules."""


def test_post_schedules_watering_returns_201(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules', json={
        'care_type': 'watering', 'interval_days': 7,
    })
    assert resp.status_code == 201


def test_post_schedules_fertilizing_returns_201(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules', json={
        'care_type': 'fertilizing', 'interval_days': 30,
    })
    assert resp.status_code == 201


def test_post_schedules_repotting_returns_201(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules', json={
        'care_type': 'repotting', 'interval_days': 365,
    })
    assert resp.status_code == 201


def test_post_schedules_response_has_required_fields(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules', json={
        'care_type': 'watering', 'interval_days': 7,
    })
    data = resp.get_json()
    for field in ('id', 'plant_id', 'care_type', 'interval_days'):
        assert field in data, f"Missing field: {field}"


def test_post_schedules_response_values_match_input(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules', json={
        'care_type': 'fertilizing', 'interval_days': 14,
    })
    data = resp.get_json()
    assert data['care_type'] == 'fertilizing'
    assert data['interval_days'] == 14
    assert data['plant_id'] == plant['id']


def test_post_schedules_minimum_interval_one_returns_201(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules', json={
        'care_type': 'watering', 'interval_days': 1,
    })
    assert resp.status_code == 201
    assert resp.get_json()['interval_days'] == 1


def test_post_schedules_upsert_updates_interval(client, plant, schedule):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules', json={
        'care_type': 'watering', 'interval_days': 21,
    })
    assert resp.status_code == 201
    assert resp.get_json()['interval_days'] == 21


def test_post_schedules_upsert_keeps_single_schedule_per_type(client, plant, schedule):
    client.post(f'/api/plants/{plant["id"]}/schedules', json={
        'care_type': 'watering', 'interval_days': 21,
    })
    data = client.get(f'/api/plants/{plant["id"]}/schedules').get_json()
    watering_schedules = [s for s in data if s['care_type'] == 'watering']
    assert len(watering_schedules) == 1


def test_post_schedules_invalid_care_type_returns_400(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules', json={
        'care_type': 'dancing', 'interval_days': 7,
    })
    assert resp.status_code == 400


def test_post_schedules_invalid_care_type_has_error_field(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules', json={
        'care_type': 'invalid', 'interval_days': 7,
    })
    assert 'error' in resp.get_json()


def test_post_schedules_interval_zero_returns_400(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules', json={
        'care_type': 'watering', 'interval_days': 0,
    })
    assert resp.status_code == 400


def test_post_schedules_interval_negative_returns_400(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules', json={
        'care_type': 'watering', 'interval_days': -5,
    })
    assert resp.status_code == 400


def test_post_schedules_interval_float_returns_400(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules', json={
        'care_type': 'watering', 'interval_days': 7.5,
    })
    assert resp.status_code == 400


def test_post_schedules_missing_care_type_returns_400(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules', json={'interval_days': 7})
    assert resp.status_code == 400


def test_post_schedules_missing_interval_returns_400(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules', json={'care_type': 'watering'})
    assert resp.status_code == 400


def test_post_schedules_empty_body_returns_400(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules',
                       content_type='application/json', data='')
    assert resp.status_code == 400


def test_post_schedules_null_body_returns_400(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules',
                       data='null', content_type='application/json')
    assert resp.status_code == 400


def test_post_schedules_null_body_has_error_field(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/schedules',
                       data='null', content_type='application/json')
    assert 'error' in resp.get_json()


def test_post_schedules_plant_not_found_returns_404(client):
    resp = client.post('/api/plants/999/schedules', json={
        'care_type': 'watering', 'interval_days': 7,
    })
    assert resp.status_code == 404


def test_post_schedules_plant_not_found_has_error_field(client):
    resp = client.post('/api/plants/999/schedules', json={
        'care_type': 'watering', 'interval_days': 7,
    })
    assert 'error' in resp.get_json()


def test_post_schedules_schedule_visible_in_get(client, plant):
    client.post(f'/api/plants/{plant["id"]}/schedules', json={
        'care_type': 'fertilizing', 'interval_days': 30,
    })
    schedules = client.get(f'/api/plants/{plant["id"]}/schedules').get_json()
    assert any(s['care_type'] == 'fertilizing' for s in schedules)
