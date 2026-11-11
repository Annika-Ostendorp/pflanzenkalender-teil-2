import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from app import PlantAppManager
from json_repositories import (
    JsonPlantRepository,
    JsonCareScheduleRepository,
    JsonActionLogRepository,
    JsonUserRepository,
)

manager = PlantAppManager(
    JsonPlantRepository("data/plants.json"),
    JsonCareScheduleRepository("data/schedules.json"),
    JsonActionLogRepository("data/logs.json"),
    JsonUserRepository("data/users.json"),
)

app = manager.app
