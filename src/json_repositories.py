import json
import os

from repositories import PlantRepository
from models import Plant


class JsonPlantRepository(PlantRepository):
    def __init__(self, file_path: str):
        self._file_path = file_path
        self._store = {}
        self._next_id = 1
        self._load()


    def _load(self):
        if not os.path.exists(self._file_path):
            return
        with open(self._file_path, encoding="utf-8") as f:
            data = json.load(f)
        for d in data:
            plant = Plant(
                name=d["name"],
                species=d["species"],
                location=d["location"],
                created_at=d.get("created_at"),
                id=d.get("id"),
                user_id=d.get("user_id"),
            )
            self._store[plant.id] = plant
        if self._store:
            self._next_id = max(self._store) + 1

