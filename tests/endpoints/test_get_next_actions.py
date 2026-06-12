"""Tests for GET /api/plants/<id>/next-actions."""
from datetime import date, timedelta


def test_get_next_actions_empty_when_no_schedules(client, plant):
    resp = client.get(f'/api/plants/{plant["id"]}/next-actions')
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_get_next_actions_plant_not_found_returns_404(client):
    resp = client.get('/api/plants/999/next-actions')
    assert resp.status_code == 404


def test_get_next_actions_plant_not_found_has_error_field(client):
    resp = client.get('/api/plants/999/next-actions')
    assert 'error' in resp.get_json()


def test_get_next_actions_items_have_required_fields(client, plant, schedule):
    # plant created 2026-01-01, watering every 7 days → definitely overdue today
    data = client.get(f'/api/plants/{plant["id"]}/next-actions').get_json()
    for field in ('care_type', 'interval_days', 'next_due', 'days_until', 'overdue'):
        assert field in data[0], f"Missing field: {field}"


def test_get_next_actions_uses_created_at_when_no_log(client):
    today = date.today()
    created_at = (today - timedelta(days=3)).isoformat()  # interval=7 → next_due = today+4
    next_due_expected = (today + timedelta(days=4)).isoformat()
    resp = client.post('/api/plants', json={
        'name': 'P', 'species': 'sp', 'location': 'loc', 'created_at': created_at,
    })
    pid = resp.get_json()['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    data = client.get(f'/api/plants/{pid}/next-actions').get_json()
    assert data[0]['next_due'] == next_due_expected
    assert data[0]['days_until'] == 4


def test_get_next_actions_uses_last_log_date(client):
    today = date.today()
    created_at = (today - timedelta(days=20)).isoformat()
    last_log_date = (today - timedelta(days=4)).isoformat()   # interval=7 → next_due = today+3
    next_due_expected = (today + timedelta(days=3)).isoformat()
    resp = client.post('/api/plants', json={
        'name': 'P', 'species': 'sp', 'location': 'loc', 'created_at': created_at,
    })
    pid = resp.get_json()['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    client.post(f'/api/plants/{pid}/logs', json={'care_type': 'watering', 'performed_at': last_log_date})
    data = client.get(f'/api/plants/{pid}/next-actions').get_json()
    assert data[0]['next_due'] == next_due_expected
    assert data[0]['days_until'] == 3


def test_get_next_actions_overdue_true_when_past_due(client, plant, schedule):
    # plant created 2026-01-01, watering every 7 days → next_due 2026-01-08, definitely overdue today
    data = client.get(f'/api/plants/{plant["id"]}/next-actions').get_json()
    assert data[0]['overdue'] is True
    assert data[0]['days_until'] < 0


def test_get_next_actions_overdue_false_when_future(client):
    today = date.today()
    created_at = (today - timedelta(days=2)).isoformat()  # interval=7 → next_due = today+5
    resp = client.post('/api/plants', json={
        'name': 'P', 'species': 'sp', 'location': 'loc', 'created_at': created_at,
    })
    pid = resp.get_json()['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    data = client.get(f'/api/plants/{pid}/next-actions').get_json()
    assert data[0]['overdue'] is False
    assert data[0]['days_until'] > 0


def test_get_next_actions_exactly_today_is_not_overdue(client):
    today = date.today()
    created_at = (today - timedelta(days=7)).isoformat()  # interval=7 → next_due = today → days_until=0
    resp = client.post('/api/plants', json={
        'name': 'P', 'species': 'sp', 'location': 'loc', 'created_at': created_at,
    })
    pid = resp.get_json()['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    data = client.get(f'/api/plants/{pid}/next-actions').get_json()
    assert data[0]['days_until'] == 0
    assert data[0]['overdue'] is False


def test_get_next_actions_days_until_negative_when_overdue(client):
    today = date.today()
    created_at = (today - timedelta(days=14)).isoformat()  # interval=7 → next_due = today-7 → days_until=-7
    resp = client.post('/api/plants', json={
        'name': 'P', 'species': 'sp', 'location': 'loc', 'created_at': created_at,
    })
    pid = resp.get_json()['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    data = client.get(f'/api/plants/{pid}/next-actions').get_json()
    assert data[0]['days_until'] == -7


def test_get_next_actions_sorted_ascending_by_days_until(client, plant):
    pid = plant['id']
    # plant created 2026-01-01; both overdue today
    # watering (interval=7) → next_due 2026-01-08 → more overdue → smaller days_until → first
    # fertilizing (interval=30) → next_due 2026-01-31 → less overdue → larger days_until → second
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'fertilizing', 'interval_days': 30})
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    data = client.get(f'/api/plants/{pid}/next-actions').get_json()
    assert len(data) == 2
    assert data[0]['days_until'] <= data[1]['days_until']
    assert data[0]['care_type'] == 'watering'


def test_get_next_actions_most_overdue_first(client, plant):
    pid = plant['id']
    # plant created 2026-01-01
    # fertilizing (interval=3) → next_due 2026-01-04 → most overdue → first
    # watering (interval=7) → next_due 2026-01-08 → less overdue → second
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'fertilizing', 'interval_days': 3})
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    data = client.get(f'/api/plants/{pid}/next-actions').get_json()
    assert data[0]['days_until'] < data[1]['days_until']
    assert data[0]['care_type'] == 'fertilizing'


def test_get_next_actions_interval_days_matches_schedule(client, plant):
    pid = plant['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'repotting', 'interval_days': 180})
    data = client.get(f'/api/plants/{pid}/next-actions').get_json()
    assert data[0]['interval_days'] == 180
