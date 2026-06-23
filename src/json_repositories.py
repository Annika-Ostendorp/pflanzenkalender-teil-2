import json
import os

from repositories import PlantRepository, CareScheduleRepository
from models import Plant, CareSchedule


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


class JsonCareScheduleRepository(CareScheduleRepository):
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
            schedule = CareSchedule(
                plant_id=d["plant_id"],
                care_type=d["care_type"],
                interval_days=d["interval_days"],
                id=d.get("id"),
            )
            self._store[schedule.id] = schedule
        if self._store:
            self._next_id = max(self._store) + 1


    def _persist(self):
        directory = os.path.dirname(self._file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        records = [s.to_dict() for s in self._store.values()]
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)


    def save(self, schedule: CareSchedule) -> None:
        if schedule.id is None:
            schedule.id = self._next_id
            self._next_id += 1
        self._store[schedule.id] = schedule
        self._persist()


    def get_by_id(self, schedule_id: int) -> CareSchedule | None:
        return self._store.get(schedule_id)


    def find_by_plant(self, plant_id: int) -> list[CareSchedule]:
        return [s for s in self._store.values() if s.plant_id == plant_id]


    def find_by_plant_and_care_type(self, plant_id: int, care_type: str) -> CareSchedule | None:
        return next(
            (s for s in self._store.values()
             if s.plant_id == plant_id and s.care_type == care_type),
            None,
        )


    def delete(self, schedule_id: int) -> None:
        self._store.pop(schedule_id, None)
        self._persist()