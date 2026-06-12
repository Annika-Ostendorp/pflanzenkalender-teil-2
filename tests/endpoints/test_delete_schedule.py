"""Tests for DELETE /api/plants/<id>/schedules/<care_type>."""


def test_delete_schedule_returns_204(client, plant, schedule):
    resp = client.delete(f'/api/plants/{plant["id"]}/schedules/watering')
    assert resp.status_code == 204


def test_delete_schedule_returns_no_body(client, plant, schedule):
    resp = client.delete(f'/api/plants/{plant["id"]}/schedules/watering')
    assert resp.data == b''


def test_delete_schedule_removed_from_list(client, plant, schedule):
    pid = plant['id']
    client.delete(f'/api/plants/{pid}/schedules/watering')
    schedules = client.get(f'/api/plants/{pid}/schedules').get_json()
    assert not any(s['care_type'] == 'watering' for s in schedules)


def test_delete_schedule_leaves_other_schedules_intact(client, plant):
    pid = plant['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'watering', 'interval_days': 7})
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'fertilizing', 'interval_days': 14})
    client.delete(f'/api/plants/{pid}/schedules/watering')
    schedules = client.get(f'/api/plants/{pid}/schedules').get_json()
    assert len(schedules) == 1
    assert schedules[0]['care_type'] == 'fertilizing'


def test_delete_schedule_not_found_returns_404(client, plant):
    resp = client.delete(f'/api/plants/{plant["id"]}/schedules/watering')
    assert resp.status_code == 404


def test_delete_schedule_not_found_has_error_field(client, plant):
    resp = client.delete(f'/api/plants/{plant["id"]}/schedules/watering')
    assert 'error' in resp.get_json()


def test_delete_schedule_plant_not_found_returns_404(client):
    resp = client.delete('/api/plants/999/schedules/watering')
    assert resp.status_code == 404


def test_delete_schedule_plant_not_found_has_error_field(client):
    resp = client.delete('/api/plants/999/schedules/watering')
    assert 'error' in resp.get_json()


def test_delete_schedule_second_delete_returns_404(client, plant, schedule):
    pid = plant['id']
    client.delete(f'/api/plants/{pid}/schedules/watering')
    resp = client.delete(f'/api/plants/{pid}/schedules/watering')
    assert resp.status_code == 404


def test_delete_schedule_fertilizing_returns_204(client, plant):
    pid = plant['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'fertilizing', 'interval_days': 30})
    resp = client.delete(f'/api/plants/{pid}/schedules/fertilizing')
    assert resp.status_code == 204


def test_delete_schedule_repotting_returns_204(client, plant):
    pid = plant['id']
    client.post(f'/api/plants/{pid}/schedules', json={'care_type': 'repotting', 'interval_days': 365})
    resp = client.delete(f'/api/plants/{pid}/schedules/repotting')
    assert resp.status_code == 204
