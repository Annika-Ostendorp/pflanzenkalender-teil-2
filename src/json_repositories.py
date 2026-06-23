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


    def _persist(self):
        directory = os.path.dirname(self._file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        records = []
        for plant in self._store.values():
            record = plant.to_dict()
            record["user_id"] = plant.user_id
            records.append(record)
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)


    def save(self, plant: Plant) -> None:
        if plant.id is None:
            plant.id = self._next_id
            self._next_id += 1
        self._store[plant.id] = plant
        self._persist()


    def get_by_id(self, plant_id: int) -> Plant | None:
        return self._store.get(plant_id)


    def find_all(self) -> list[Plant]:
        return list(self._store.values())


    def find_by_user(self, user_id: int) -> list[Plant]:
        return [p for p in self._store.values() if p.user_id == user_id]
 
 
    def delete(self, plant_id: int) -> None:
        self._store.pop(plant_id, None)
        self._persist()