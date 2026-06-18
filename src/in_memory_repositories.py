from repositories import (
    PlantRepository,
    CareScheduleRepository,
    ActionLogRepository,
    UserRepository,
)
from models import Plant, CareSchedule, ActionLog, User


class InMemoryPlantRepository(PlantRepository):
    def __init__(self):
        self._store = {}
        self._next_id = 1
    def save(self, plant):
        if plant.id is None:
            plant.id = self._next_id
            self._next_id += 1
        self._store[plant.id] = plant
    def get_by_id(self, plant_id):
        return self._store.get(plant_id)
    def find_all(self):
        return list(self._store.values())
    def find_by_user(self, user_id):
        return [p for p in self._store.values() if p.user_id == user_id]
    def delete(self, plant_id):
        self._store.pop(plant_id, None)