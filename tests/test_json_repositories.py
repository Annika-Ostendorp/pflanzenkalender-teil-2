import pytest

from src.json_repositories import (
    JsonPlantRepository, JsonCareScheduleRepository,
    JsonActionLogRepository, JsonUserRepository,
)
from src.models import Plant, CareSchedule, ActionLog, User

# ── Helpers ───────────────────────────────────────────────────────────────────

def _repo_path(tmp_path, filename):
    return tmp_path / filename


def _test_starts_empty_without_file(tmp_path, repo_class, filename, assert_empty):
    file_path = _repo_path(tmp_path, filename)
    repo = repo_class(str(file_path))
    assert_empty(repo)
    assert not file_path.exists()


def _test_save_creates_file(tmp_path, repo_class, filename, entity):
    file_path = _repo_path(tmp_path, filename)
    repo = repo_class(str(file_path))
    repo.save(entity)
    assert file_path.exists()


def _test_data_survives_restart(tmp_path, repo_class, filename, entity, assert_loaded):
    file_path = _repo_path(tmp_path, filename)
    repo1 = repo_class(str(file_path))
    repo1.save(entity)
    repo2 = repo_class(str(file_path))
    assert_loaded(repo2)


def _test_save_assigns_id(tmp_path, repo_class, filename, entity):
    file_path = _repo_path(tmp_path, filename)
    repo = repo_class(str(file_path))
    repo.save(entity)
    assert entity.id == 1


def _test_delete_removes(tmp_path, repo_class, filename, entity, assert_gone=None):
    file_path = _repo_path(tmp_path, filename)
    repo = repo_class(str(file_path))
    repo.save(entity)
    repo.delete(entity.id)
    assert repo.get_by_id(entity.id) is None
    if assert_gone:
        assert_gone(repo)


def _assert_plant_empty(repo):
    assert repo.find_by_user(1) == []

def _assert_list_repo_empty(repo):
    assert repo.find_by_plant(1) == []


def _assert_user_empty(repo):
    assert repo.find_by_username("alice") is None


def _assert_plant_loaded(repo):
    plant = repo.get_by_id(1)
    assert plant is not None
    assert plant.name == "Monstera"
    assert plant.id == 1


def _assert_schedule_loaded(repo):
    schedules = repo.find_by_plant(1)
    assert len(schedules) == 1
    assert schedules[0].care_type == "watering"
    assert schedules[0].plant_id == 1
    assert schedules[0].interval_days == 7
    assert schedules[0].id == 1


def _assert_log_loaded(repo):
    logs = repo.find_by_plant(1)
    assert len(logs) == 1
    assert logs[0].care_type == "watering"
    assert logs[0].plant_id == 1
    assert logs[0].id == 1


def _assert_user_loaded(repo):
    user = repo.find_by_username("alice")
    assert user is not None
    assert user.username == "alice"
    assert user.password_hash == "hash123"
    assert user.id == 1

# ── Plant ──────────────────────────────────────────────────────────────────────

def test_json_plant_starts_empty_when_file_missing(tmp_path):
    _test_starts_empty_without_file(
        tmp_path, JsonPlantRepository, "plants.json", _assert_plant_empty)


def test_json_plant_save_creates_file(tmp_path):
    _test_save_creates_file(
        tmp_path, JsonPlantRepository, "plants.json",
        Plant(name="Monstera", species="Araceae", location="Wohnzimmer"))


def test_json_plant_data_survives_restart(tmp_path):
    _test_data_survives_restart(
        tmp_path, JsonPlantRepository, "plants.json",
        Plant(name="Monstera", species="Araceae", location="Wohnzimmer"),
        _assert_plant_loaded)


def test_json_plant_save_assigns_id(tmp_path):
    _test_save_assigns_id(
        tmp_path, JsonPlantRepository, "plants.json",
        Plant(name="A", species="B", location="C"))


def test_json_plant_delete_removes_plant(tmp_path):
    _test_delete_removes(
        tmp_path, JsonPlantRepository, "plants.json",
        Plant(name="A", species="B", location="C"), _assert_plant_empty)


# ── Schedule ──────────────────────────────────────────────────────────────────

def test_json_schedule_starts_empty_when_file_missing(tmp_path):
    _test_starts_empty_without_file(
        tmp_path, JsonCareScheduleRepository, "schedules.json", _assert_list_repo_empty)


def test_json_schedule_save_creates_file(tmp_path):
    _test_save_creates_file(
        tmp_path, JsonCareScheduleRepository, "schedules.json",
        CareSchedule(plant_id=1, care_type="watering", interval_days=7))


def test_json_schedule_data_survives_restart(tmp_path):
    _test_data_survives_restart(
        tmp_path, JsonCareScheduleRepository, "schedules.json",
        CareSchedule(plant_id=1, care_type="watering", interval_days=7),
        _assert_schedule_loaded)


def test_json_schedule_save_assigns_id(tmp_path):
    _test_save_assigns_id(
        tmp_path, JsonCareScheduleRepository, "schedules.json",
        CareSchedule(plant_id=1, care_type="watering", interval_days=7))


def test_json_schedule_delete_removes_schedule(tmp_path):
    _test_delete_removes(
        tmp_path, JsonCareScheduleRepository, "schedules.json",
        CareSchedule(plant_id=1, care_type="watering", interval_days=7))


# ── Log ───────────────────────────────────────────────────────────────────────

def test_json_log_starts_empty_when_file_missing(tmp_path):
    _test_starts_empty_without_file(
        tmp_path, JsonActionLogRepository, "logs.json", _assert_list_repo_empty)


def test_json_log_save_creates_file(tmp_path):
    _test_save_creates_file(
        tmp_path, JsonActionLogRepository, "logs.json",
        ActionLog(plant_id=1, care_type="watering"))


def test_json_log_data_survives_restart(tmp_path):
    _test_data_survives_restart(
        tmp_path, JsonActionLogRepository, "logs.json",
        ActionLog(plant_id=1, care_type="watering"), _assert_log_loaded)


def test_json_log_save_assigns_id(tmp_path):
    _test_save_assigns_id(
        tmp_path, JsonActionLogRepository, "logs.json",
        ActionLog(plant_id=1, care_type="watering"))


def test_json_log_delete_removes_log(tmp_path):
    _test_delete_removes(
        tmp_path, JsonActionLogRepository, "logs.json",
        ActionLog(plant_id=1, care_type="watering"))


# ── User ──────────────────────────────────────────────────────────────────────

def test_json_user_starts_empty_when_file_missing(tmp_path):
    _test_starts_empty_without_file(
        tmp_path, JsonUserRepository, "users.json", _assert_user_empty)


def test_json_user_save_creates_file(tmp_path):
    _test_save_creates_file(
        tmp_path, JsonUserRepository, "users.json",
        User(username="alice", password_hash="hash123"))


def test_json_user_data_survives_restart(tmp_path):
    _test_data_survives_restart(
        tmp_path, JsonUserRepository, "users.json",
        User(username="alice", password_hash="hash123"), _assert_user_loaded)


def test_json_user_save_assigns_id(tmp_path):
    _test_save_assigns_id(
        tmp_path, JsonUserRepository, "users.json",
        User(username="alice", password_hash="hash123"))


def test_json_user_delete_removes_user(tmp_path):
    _test_delete_removes(
        tmp_path, JsonUserRepository, "users.json",
        User(username="alice", password_hash="hash123"))


# ── Special cases ─────────────────────────────────────────────────────────────

def test_json_plant_save_creates_data_subdirectory(tmp_path):
    file_path = tmp_path / "data" / "plants.json"
    repo = JsonPlantRepository(str(file_path))
    repo.save(Plant(name="Monstera", species="Araceae", location="Wohnzimmer"))
    assert (tmp_path / "data").is_dir()
    assert file_path.exists()


@pytest.mark.parametrize("repo_class,empty_query", [
    (JsonPlantRepository, lambda repo: repo.find_by_user(1)),
    (JsonCareScheduleRepository, lambda repo: repo.find_by_plant(1)),
    (JsonActionLogRepository, lambda repo: repo.find_by_plant(1)),
    (JsonUserRepository, lambda repo: repo.find_by_username("alice")),
])
def test_json_repo_starts_empty_when_json_invalid(tmp_path, repo_class, empty_query):
    file_path = tmp_path / "data.json"
    file_path.write_text("{ invalid json", encoding="utf-8")
    repo = repo_class(str(file_path))
    result = empty_query(repo)
    assert result == [] or result is None


@pytest.mark.parametrize("repo_class,empty_query", [
    (JsonPlantRepository, lambda repo: repo.find_by_user(1)),
    (JsonCareScheduleRepository, lambda repo: repo.find_by_plant(1)),
    (JsonActionLogRepository, lambda repo: repo.find_by_plant(1)),
    (JsonUserRepository, lambda repo: repo.find_by_username("alice")),
])
def test_json_repo_starts_empty_when_json_file_empty(tmp_path, repo_class, empty_query):
    file_path = tmp_path / "data.json"
    file_path.write_text("", encoding="utf-8")
    repo = repo_class(str(file_path))
    result = empty_query(repo)
    assert result == [] or result is None