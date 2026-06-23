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


