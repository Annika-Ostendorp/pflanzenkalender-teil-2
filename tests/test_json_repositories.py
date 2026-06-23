from src.json_repositories import JsonPlantRepository
from src.models import Plant


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