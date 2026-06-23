from src.json_repositories import (
    JsonPlantRepository, JsonCareScheduleRepository,
    JsonActionLogRepository, JsonUserRepository,
)
from src.models import Plant, CareSchedule, ActionLog, User


def test_json_plant_starts_empty_when_file_missing(tmp_path):
    file_path = tmp_path / "plants.json"
    repo = JsonPlantRepository(str(file_path))
    assert repo.find_all() == []
    assert not file_path.exists()


def test_json_plant_save_creates_file(tmp_path):
    file_path = tmp_path / "plants.json"
    repo = JsonPlantRepository(str(file_path))
    repo.save(Plant(name="Monstera", species="Araceae", location="Wohnzimmer"))
    assert file_path.exists()


def test_json_plant_data_survives_restart(tmp_path):
    file_path = tmp_path / "plants.json"
    repo1 = JsonPlantRepository(str(file_path))
    repo1.save(Plant(name="Monstera", species="Araceae", location="Wohnzimmer"))
    repo2 = JsonPlantRepository(str(file_path))
    plants = repo2.find_all()
    assert len(plants) == 1
    assert plants[0].name == "Monstera"
    assert plants[0].id == 1


def test_json_plant_save_assigns_id(tmp_path):
    file_path = tmp_path / "plants.json"
    repo = JsonPlantRepository(str(file_path))
    plant = Plant(name="A", species="B", location="C")
    repo.save(plant)
    assert plant.id == 1


def test_json_plant_delete_removes_plant(tmp_path):
    file_path = tmp_path / "plants.json"
    repo = JsonPlantRepository(str(file_path))
    plant = Plant(name="A", species="B", location="C")
    repo.save(plant)

    repo.delete(plant.id)

    assert repo.get_by_id(plant.id) is None
    assert repo.find_all() == []


def test_json_schedule_starts_empty_when_file_missing(tmp_path):
    file_path = tmp_path / "schedules.json"
    repo = JsonCareScheduleRepository(str(file_path))
    assert repo.find_by_plant(1) == []
    assert not file_path.exists()


def test_json_schedule_save_creates_file(tmp_path):
    file_path = tmp_path / "schedules.json"
    repo = JsonCareScheduleRepository(str(file_path))
    repo.save(CareSchedule(plant_id=1, care_type="watering", interval_days=7))
    assert file_path.exists()


def test_json_schedule_data_survives_restart(tmp_path):
    file_path = tmp_path / "schedules.json"
    repo1 = JsonCareScheduleRepository(str(file_path))
    repo1.save(CareSchedule(plant_id=1, care_type="watering", interval_days=7))
    repo2 = JsonCareScheduleRepository(str(file_path))
    assert len(repo2.find_by_plant(1)) == 1


def test_json_schedule_save_assigns_id(tmp_path):
    file_path = tmp_path / "schedules.json"
    repo = JsonCareScheduleRepository(str(file_path))
    s = CareSchedule(plant_id=1, care_type="watering", interval_days=7)
    repo.save(s)
    assert s.id == 1


def test_json_schedule_delete_removes_schedule(tmp_path):
    file_path = tmp_path / "schedules.json"
    repo = JsonCareScheduleRepository(str(file_path))
    s = CareSchedule(plant_id=1, care_type="watering", interval_days=7)
    repo.save(s)
    repo.delete(s.id)
    assert repo.get_by_id(s.id) is None


def test_json_log_starts_empty_when_file_missing(tmp_path):
    file_path = tmp_path / "logs.json"
    repo = JsonActionLogRepository(str(file_path))
    assert repo.find_by_plant(1) == []
    assert not file_path.exists()


def test_json_log_save_creates_file(tmp_path):
    file_path = tmp_path / "logs.json"
    repo = JsonActionLogRepository(str(file_path))
    repo.save(ActionLog(plant_id=1, care_type="watering"))
    assert file_path.exists()


def test_json_log_data_survives_restart(tmp_path):
    file_path = tmp_path / "logs.json"
    repo1 = JsonActionLogRepository(str(file_path))
    repo1.save(ActionLog(plant_id=1, care_type="watering"))
    repo2 = JsonActionLogRepository(str(file_path))
    assert len(repo2.find_by_plant(1)) == 1


def test_json_log_save_assigns_id(tmp_path):
    file_path = tmp_path / "logs.json"
    repo = JsonActionLogRepository(str(file_path))
    log = ActionLog(plant_id=1, care_type="watering")
    repo.save(log)
    assert log.id == 1


def test_json_log_delete_removes_log(tmp_path):
    file_path = tmp_path / "logs.json"
    repo = JsonActionLogRepository(str(file_path))
    log = ActionLog(plant_id=1, care_type="watering")
    repo.save(log)
    repo.delete(log.id)
    assert repo.get_by_id(log.id) is None


def test_json_user_starts_empty_when_file_missing(tmp_path):
    file_path = tmp_path / "users.json"
    repo = JsonUserRepository(str(file_path))
    assert repo.find_by_username("alice") is None
    assert not file_path.exists()


def test_json_user_save_creates_file(tmp_path):
    file_path = tmp_path / "users.json"
    repo = JsonUserRepository(str(file_path))
    repo.save(User(username="alice", password_hash="hash123"))
    assert file_path.exists()