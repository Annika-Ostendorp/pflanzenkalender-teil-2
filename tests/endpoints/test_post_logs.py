"""Tests for POST /api/plants/<id>/logs."""
from datetime import date


def test_post_logs_returns_201(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/logs', json={
        'care_type': 'watering',
        'performed_at': '2026-04-20',
        'notes': 'Etwas weniger als sonst',
    })
    assert resp.status_code == 201


def test_post_logs_response_has_required_fields(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/logs', json={
        'care_type': 'watering',
        'performed_at': '2026-04-20',
    })
    data = resp.get_json()
    for field in ('id', 'plant_id', 'care_type', 'performed_at', 'notes'):
        assert field in data, f"Missing field: {field}"


def test_post_logs_response_values_match_input(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/logs', json={
        'care_type': 'fertilizing',
        'performed_at': '2026-03-15',
        'notes': 'Volldünger',
    })
    data = resp.get_json()
    assert data['care_type'] == 'fertilizing'
    assert data['performed_at'] == '2026-03-15'
    assert data['notes'] == 'Volldünger'
    assert data['plant_id'] == plant['id']


def test_post_logs_with_explicit_performed_at(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/logs', json={
        'care_type': 'repotting', 'performed_at': '2025-11-01',
    })
    assert resp.get_json()['performed_at'] == '2025-11-01'


def test_post_logs_default_performed_at_is_today(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/logs', json={'care_type': 'watering'})
    assert resp.get_json()['performed_at'] == date.today().isoformat()


# def test_post_logs_without_notes_defaults_to_empty_string(client, plant):
#     resp = client.post(f'/api/plants/{plant["id"]}/logs', json={
#         'care_type': 'watering', 'performed_at': '2026-04-20',
#     })
#     assert resp.get_json()['notes'] == ''


# def test_post_logs_null_notes_stored_as_empty_string(client, plant):
#     resp = client.post(f'/api/plants/{plant["id"]}/logs', json={
#         'care_type': 'watering', 'notes': None,
#     })
#     assert resp.get_json()['notes'] == ''


def test_post_logs_log_visible_in_get_logs(client, plant):
    client.post(f'/api/plants/{plant["id"]}/logs', json={
        'care_type': 'watering', 'performed_at': '2026-04-20',
    })
    logs = client.get(f'/api/plants/{plant["id"]}/logs').get_json()
    assert len(logs) == 1
    assert logs[0]['care_type'] == 'watering'


def test_post_logs_missing_care_type_returns_400(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/logs', json={
        'performed_at': '2026-04-20',
    })
    assert resp.status_code == 400


def test_post_logs_missing_care_type_has_error_field(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/logs', json={'performed_at': '2026-04-20'})
    assert 'error' in resp.get_json()


def test_post_logs_empty_body_returns_400(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/logs',
                       content_type='application/json', data='')
    assert resp.status_code == 400


def test_post_logs_empty_body_has_error_field(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/logs',
                       content_type='application/json', data='')
    assert 'error' in resp.get_json()


def test_post_logs_null_body_returns_400(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/logs',
                       data='null', content_type='application/json')
    assert resp.status_code == 400


def test_post_logs_null_body_has_error_field(client, plant):
    resp = client.post(f'/api/plants/{plant["id"]}/logs',
                       data='null', content_type='application/json')
    assert 'error' in resp.get_json()


def test_post_logs_plant_not_found_returns_404(client):
    resp = client.post('/api/plants/999/logs', json={'care_type': 'watering'})
    assert resp.status_code == 404


def test_post_logs_plant_not_found_has_error_field(client):
    resp = client.post('/api/plants/999/logs', json={'care_type': 'watering'})
    assert 'error' in resp.get_json()
