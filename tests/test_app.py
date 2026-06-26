"""Student-written integration tests covering business logic and boundary conditions."""
from datetime import date, timedelta


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_plant(client, *, days_ago=0, name='Pflanze', species='Art', location='Ort'):
    created_at = (date.today() - timedelta(days=days_ago)).isoformat()
    resp = client.post('/api/plants', json={
        'name': name, 'species': species, 'location': location,
        'created_at': created_at,
    })
    return resp.get_json()


def add_schedule(client, plant_id, care_type='watering', interval_days=7):
    return client.post(f'/api/plants/{plant_id}/schedules',
                       json={'care_type': care_type, 'interval_days': interval_days}).get_json()


def add_log(client, plant_id, care_type='watering', days_ago=0):
    performed_at = (date.today() - timedelta(days=days_ago)).isoformat()
    return client.post(f'/api/plants/{plant_id}/logs',
                       json={'care_type': care_type, 'performed_at': performed_at}).get_json()


# ── Plant status: boundary conditions ─────────────────────────────────────────

def test_status_ok_with_no_schedules(client):
    p = make_plant(client)
    assert client.get(f'/api/plants/{p["id"]}').get_json()['status'] == 'ok'


def test_status_ok_when_due_in_4_days(client):
    # created 3 days ago, interval 7 → next_due = today+4 → ok
    p = make_plant(client, days_ago=3)
    add_schedule(client, p['id'], interval_days=7)
    assert client.get(f'/api/plants/{p["id"]}').get_json()['status'] == 'ok'


def test_status_soon_when_due_in_3_days(client):
    # created 4 days ago, interval 7 → next_due = today+3 → soon (boundary: days <= 3)
    p = make_plant(client, days_ago=4)
    add_schedule(client, p['id'], interval_days=7)
    assert client.get(f'/api/plants/{p["id"]}').get_json()['status'] == 'soon'


def test_status_soon_when_due_today(client):
    # created 7 days ago, interval 7 → next_due = today → days=0 → soon (not overdue)
    p = make_plant(client, days_ago=7)
    add_schedule(client, p['id'], interval_days=7)
    assert client.get(f'/api/plants/{p["id"]}').get_json()['status'] == 'soon'


def test_status_overdue_when_due_yesterday(client):
    # created 8 days ago, interval 7 → next_due = today-1 → overdue (days < 0)
    p = make_plant(client, days_ago=8)
    add_schedule(client, p['id'], interval_days=7)
    assert client.get(f'/api/plants/{p["id"]}').get_json()['status'] == 'overdue'


def test_status_overdue_takes_priority_over_soon(client):
    # watering: overdue; fertilizing: soon → overall status = overdue
    p = make_plant(client, days_ago=8)
    add_schedule(client, p['id'], 'watering', interval_days=7)
    add_schedule(client, p['id'], 'fertilizing', interval_days=11)
    assert client.get(f'/api/plants/{p["id"]}').get_json()['status'] == 'overdue'


def test_status_soon_when_one_schedule_soon_other_ok(client):
    p = make_plant(client, days_ago=4)
    add_schedule(client, p['id'], 'watering', interval_days=7)    # next_due = today+3 → soon
    add_schedule(client, p['id'], 'fertilizing', interval_days=30)  # next_due = today+26 → ok
    assert client.get(f'/api/plants/{p["id"]}').get_json()['status'] == 'soon'


# ── next_due uses most-recent log (not plant.created_at) ─────────────────────

def test_status_uses_log_date_instead_of_created_at(client):
    # created 14 days ago → without log: next_due = today-7 → overdue
    # but with log 3 days ago + interval 7 → next_due = today+4 → ok
    p = make_plant(client, days_ago=14)
    add_schedule(client, p['id'], interval_days=7)
    add_log(client, p['id'], days_ago=3)
    assert client.get(f'/api/plants/{p["id"]}').get_json()['status'] == 'ok'


def test_status_uses_most_recent_log(client):
    # Two logs: 10 days ago and 3 days ago. interval=7 → next_due from most recent = today+4 → ok
    p = make_plant(client, days_ago=20)
    add_schedule(client, p['id'], interval_days=7)
    add_log(client, p['id'], days_ago=10)
    add_log(client, p['id'], days_ago=3)
    assert client.get(f'/api/plants/{p["id"]}').get_json()['status'] == 'ok'


def test_status_uses_most_recent_not_earliest_log(client):
    # Oldest log: 3 days ago (would give next_due=today+4 → ok)
    # Most recent log: 6 days ago... wait, oldest should be most recent.
    # Let's do: log1=10 days ago, log2=6 days ago. interval=7 → next_due from log2 = today+1 → soon
    p = make_plant(client, days_ago=20)
    add_schedule(client, p['id'], interval_days=7)
    add_log(client, p['id'], days_ago=10)
    add_log(client, p['id'], days_ago=6)
    assert client.get(f'/api/plants/{p["id"]}').get_json()['status'] == 'soon'


# ── next-actions endpoint ─────────────────────────────────────────────────────

def test_next_actions_empty_for_no_schedules(client):
    p = make_plant(client)
    data = client.get(f'/api/plants/{p["id"]}/next-actions').get_json()
    assert data == []


def test_next_actions_next_due_date_from_created_at(client):
    today = date.today()
    p = make_plant(client, days_ago=3)
    add_schedule(client, p['id'], interval_days=7)
    data = client.get(f'/api/plants/{p["id"]}/next-actions').get_json()
    expected_due = (today - timedelta(days=3) + timedelta(days=7)).isoformat()
    assert data[0]['next_due'] == expected_due


def test_next_actions_days_until_positive_when_future(client):
    p = make_plant(client, days_ago=3)
    add_schedule(client, p['id'], interval_days=7)
    data = client.get(f'/api/plants/{p["id"]}/next-actions').get_json()
    assert data[0]['days_until'] == 4


def test_next_actions_days_until_zero_when_due_today(client):
    p = make_plant(client, days_ago=7)
    add_schedule(client, p['id'], interval_days=7)
    data = client.get(f'/api/plants/{p["id"]}/next-actions').get_json()
    assert data[0]['days_until'] == 0


def test_next_actions_days_until_negative_when_overdue(client):
    p = make_plant(client, days_ago=8)
    add_schedule(client, p['id'], interval_days=7)
    data = client.get(f'/api/plants/{p["id"]}/next-actions').get_json()
    assert data[0]['days_until'] == -1


def test_next_actions_overdue_false_when_due_today(client):
    p = make_plant(client, days_ago=7)
    add_schedule(client, p['id'], interval_days=7)
    data = client.get(f'/api/plants/{p["id"]}/next-actions').get_json()
    assert data[0]['overdue'] is False


def test_next_actions_overdue_true_when_past_due(client):
    p = make_plant(client, days_ago=8)
    add_schedule(client, p['id'], interval_days=7)
    data = client.get(f'/api/plants/{p["id"]}/next-actions').get_json()
    assert data[0]['overdue'] is True


def test_next_actions_sorted_soonest_first(client):
    p = make_plant(client, days_ago=0)
    add_schedule(client, p['id'], 'watering', interval_days=3)    # due in 3 days
    add_schedule(client, p['id'], 'fertilizing', interval_days=10)  # due in 10 days
    data = client.get(f'/api/plants/{p["id"]}/next-actions').get_json()
    assert data[0]['care_type'] == 'watering'
    assert data[1]['care_type'] == 'fertilizing'


def test_next_actions_next_due_updated_by_log(client):
    today = date.today()
    p = make_plant(client, days_ago=14)
    add_schedule(client, p['id'], interval_days=7)
    add_log(client, p['id'], days_ago=2)
    data = client.get(f'/api/plants/{p["id"]}/next-actions').get_json()
    expected_due = (today - timedelta(days=2) + timedelta(days=7)).isoformat()
    assert data[0]['next_due'] == expected_due
    assert data[0]['days_until'] == 5


# ── /api/overdue endpoint ─────────────────────────────────────────────────────

def test_overdue_empty_when_no_plants(client):
    assert client.get('/api/overdue').get_json() == []


def test_overdue_empty_when_not_overdue(client):
    p = make_plant(client, days_ago=3)
    add_schedule(client, p['id'], interval_days=7)
    assert client.get('/api/overdue').get_json() == []


def test_overdue_not_listed_when_due_today(client):
    p = make_plant(client, days_ago=7)
    add_schedule(client, p['id'], interval_days=7)
    assert client.get('/api/overdue').get_json() == []


def test_overdue_listed_when_due_yesterday(client):
    p = make_plant(client, days_ago=8)
    add_schedule(client, p['id'], interval_days=7)
    data = client.get('/api/overdue').get_json()
    assert len(data) == 1
    assert data[0]['plant_id'] == p['id']


def test_overdue_days_overdue_correct(client):
    # next_due = today - 3 → days_overdue = 3
    p = make_plant(client, days_ago=10)
    add_schedule(client, p['id'], interval_days=7)
    data = client.get('/api/overdue').get_json()
    assert data[0]['days_overdue'] == 3


def test_overdue_days_overdue_is_1_when_due_yesterday(client):
    p = make_plant(client, days_ago=8)
    add_schedule(client, p['id'], interval_days=7)
    data = client.get('/api/overdue').get_json()
    assert data[0]['days_overdue'] == 1


def test_overdue_sorted_most_overdue_first(client):
    p1 = make_plant(client, days_ago=14, name='P1')  # next_due = today-7 → 7 days overdue
    p2 = make_plant(client, days_ago=9, name='P2')   # next_due = today-2 → 2 days overdue
    add_schedule(client, p1['id'], interval_days=7)
    add_schedule(client, p2['id'], interval_days=7)
    data = client.get('/api/overdue').get_json()
    assert data[0]['plant_id'] == p1['id']
    assert data[1]['plant_id'] == p2['id']


def test_overdue_shows_plant_name_and_location(client):
    p = make_plant(client, days_ago=8, name='Kakao', location='Küche')
    add_schedule(client, p['id'], interval_days=7)
    data = client.get('/api/overdue').get_json()
    assert data[0]['plant_name'] == 'Kakao'
    assert data[0]['plant_location'] == 'Küche'


def test_overdue_resolved_after_logging(client):
    p = make_plant(client, days_ago=14)
    add_schedule(client, p['id'], interval_days=7)
    assert len(client.get('/api/overdue').get_json()) == 1
    add_log(client, p['id'], days_ago=0)
    assert client.get('/api/overdue').get_json() == []


# ── Plant CRUD ────────────────────────────────────────────────────────────────

def test_create_plant_increments_id(client):
    p1 = client.post('/api/plants', json={'name': 'A', 'species': 'B', 'location': 'C'}).get_json()
    p2 = client.post('/api/plants', json={'name': 'X', 'species': 'Y', 'location': 'Z'}).get_json()
    assert p2['id'] == p1['id'] + 1


def test_plant_appears_in_list_after_creation(client):
    p = make_plant(client, name='Ficus')
    ids = [x['id'] for x in client.get('/api/plants').get_json()]
    assert p['id'] in ids


def test_delete_plant_removes_from_list(client):
    p = make_plant(client)
    client.delete(f'/api/plants/{p["id"]}')
    ids = [x['id'] for x in client.get('/api/plants').get_json()]
    assert p['id'] not in ids


def test_delete_plant_removes_its_schedules(client):
    p = make_plant(client)
    add_schedule(client, p['id'])
    client.delete(f'/api/plants/{p["id"]}')
    resp = client.get(f'/api/plants/{p["id"]}/schedules')
    assert resp.status_code == 404


def test_delete_plant_removes_its_logs(client):
    p = make_plant(client)
    add_log(client, p['id'])
    client.delete(f'/api/plants/{p["id"]}')
    resp = client.get(f'/api/plants/{p["id"]}/logs')
    assert resp.status_code == 404


def test_update_plant_name(client):
    p = make_plant(client, name='Alt')
    client.put(f'/api/plants/{p["id"]}', json={'name': 'Neu'})
    assert client.get(f'/api/plants/{p["id"]}').get_json()['name'] == 'Neu'


# ── Schedule upsert ───────────────────────────────────────────────────────────

def test_schedule_upsert_changes_interval(client):
    p = make_plant(client)
    add_schedule(client, p['id'], 'watering', interval_days=7)
    add_schedule(client, p['id'], 'watering', interval_days=14)
    schedules = client.get(f'/api/plants/{p["id"]}/schedules').get_json()
    watering = [s for s in schedules if s['care_type'] == 'watering']
    assert len(watering) == 1
    assert watering[0]['interval_days'] == 14


# ── Log sorting ───────────────────────────────────────────────────────────────

def test_logs_sorted_newest_first(client):
    p = make_plant(client)
    add_log(client, p['id'], days_ago=5)
    add_log(client, p['id'], days_ago=1)
    logs = client.get(f'/api/plants/{p["id"]}/logs').get_json()
    assert logs[0]['performed_at'] > logs[1]['performed_at']


def test_create_log_invalid_care_type_returns_400(client):
    plant = make_plant(client)

    response = client.post(
        f"/api/plants/{plant["id"]}/logs",
        json = {
            "care_type": "invalid",
            "performed_at": "2026-06-01",
        },
    )

    # Überprüfungen
    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid care type"}