from src.in_memory_repositories import (
    InMemoryPlantRepository,
    InMemoryCareScheduleRepository,
    InMemoryActionLogRepository,
    InMemoryUserRepository,
)
from src.models import Plant, CareSchedule, ActionLog, User


def test_save_assigns_id_starting_at_1():
    repo = InMemoryPlantRepository()
    plant = Plant(name='A', species='B', location='C')
    repo.save(plant)
    assert plant.id == 1


def test_save_second_plant_increments_id():
    repo = InMemoryPlantRepository()
    p1 = Plant(name='A', species='B', location='C')
    p2 = Plant(name='X', species='Y', location='Z')
    repo.save(p1)
    repo.save(p2)
    assert p2.id == 2


def test_get_by_id_returns_plant():
    repo = InMemoryPlantRepository()
    plant = Plant(name='A', species='B', location='C')
    repo.save(plant)
    assert repo.get_by_id(1) is plant


def test_get_by_id_returns_none_when_missing():
    repo = InMemoryPlantRepository()
    assert repo.get_by_id(999) is None


def test_find_all_returns_all_plants():
    repo = InMemoryPlantRepository()
    repo.save(Plant(name='A', species='B', location='C'))
    repo.save(Plant(name='X', species='Y', location='Z'))
    assert len(repo.find_all()) == 2


def test_delete_removes_plant():
    repo = InMemoryPlantRepository()
    plant = Plant(name='A', species='B', location='C')
    repo.save(plant)
    repo.delete(plant.id)
    assert repo.get_by_id(plant.id) is None


def test_find_by_user_returns_only_matching_plants():
    repo = InMemoryPlantRepository()
    p1 = Plant(name='A', species='B', location='C', user_id=1)
    p2 = Plant(name='X', species='Y', location='Z', user_id=2)
    repo.save(p1)
    repo.save(p2)
    result = repo.find_by_user(1)
    assert len(result) == 1
    assert result[0] is p1


def test_save_updates_existing_plant():
    repo = InMemoryPlantRepository()
    plant = Plant(name='Old', species='B', location='C')
    repo.save(plant)
    plant.name = 'New'
    repo.save(plant)
    assert len(repo.find_all()) == 1
    assert repo.get_by_id(plant.id).name == 'New'


def test_find_all_returns_empty_list_when_no_plants():
    repo = InMemoryPlantRepository()
    assert repo.find_all() == []


def test_find_by_user_returns_empty_when_no_match():
    repo = InMemoryPlantRepository()
    repo.save(Plant(name='A', species='B', location='C', user_id=1))
    assert repo.find_by_user(999) == []


def test_find_by_plant_and_care_type_returns_correct_schedule():
    repo = InMemoryCareScheduleRepository()
    s = CareSchedule(plant_id=1, care_type='watering', interval_days=7)
    repo.save(s)
    result = repo.find_by_plant_and_care_type(1, 'watering')
    assert result is s


def test_find_by_plant_and_care_type_returns_none_when_missing():
    repo = InMemoryCareScheduleRepository()
    assert repo.find_by_plant_and_care_type(1, 'watering') is None


def test_find_by_username_returns_user():
    repo = InMemoryUserRepository()
    user = User(username='alice', password_hash='hash123')
    repo.save(user)
    assert repo.find_by_username('alice') is user


def test_find_by_username_returns_none_when_missing():
    repo = InMemoryUserRepository()
    assert repo.find_by_username('nobody') is None


# ── InMemoryCareScheduleRepository ──────────────────────────────

def test_care_schedule_save_assigns_id():
    repo = InMemoryCareScheduleRepository()
    s = CareSchedule(plant_id=1, care_type='watering', interval_days=7)
    repo.save(s)
    assert s.id == 1

    
def test_care_schedule_find_by_plant_returns_schedules():
    repo = InMemoryCareScheduleRepository()
    s = CareSchedule(plant_id=1, care_type='watering', interval_days=7)
    repo.save(s)
    assert repo.find_by_plant(1) == [s]


def test_care_schedule_find_by_plant_returns_empty_when_no_match():
    repo = InMemoryCareScheduleRepository()
    repo.save(CareSchedule(plant_id=1, care_type='watering', interval_days=7))
    assert repo.find_by_plant(999) == []

# ── InMemoryActionLogRepository ──────────────────────────────────

def test_action_log_save_assigns_id():
    repo = InMemoryActionLogRepository()
    log = ActionLog(plant_id=1, care_type='watering')
    repo.save(log)
    assert log.id == 1


def test_action_log_find_by_plant_returns_logs():
    repo = InMemoryActionLogRepository()
    log = ActionLog(plant_id=1, care_type='watering')
    repo.save(log)
    assert repo.find_by_plant(1) == [log]


def test_action_log_find_by_plant_returns_empty_when_no_match():
    repo = InMemoryActionLogRepository()
    repo.save(ActionLog(plant_id=1, care_type='watering'))
    assert repo.find_by_plant(999) == []