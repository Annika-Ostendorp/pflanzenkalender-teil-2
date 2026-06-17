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
