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