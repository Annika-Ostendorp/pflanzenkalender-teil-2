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


class InMemoryCareScheduleRepository(CareScheduleRepository):
    def __init__(self):
        self._store = {}
        self._next_id = 1

    def save(self, schedule):
        if schedule.id is None:
            schedule.id = self._next_id
            self._next_id += 1
        self._store[schedule.id] = schedule

    def get_by_id(self, schedule_id):
        return self._store.get(schedule_id)

    def find_by_plant(self, plant_id):
        return [s for s in self._store.values() if s.plant_id == plant_id]

    def find_by_plant_and_care_type(self, plant_id, care_type):
        return next(
            (s for s in self._store.values()
             if s.plant_id == plant_id and s.care_type == care_type),
            None,
        )

    def delete(self, schedule_id):
        self._store.pop(schedule_id, None)


class InMemoryActionLogRepository(ActionLogRepository):
    def __init__(self):
        self._store = {}
        self._next_id = 1

    def save(self, log):
        if log.id is None:
            log.id = self._next_id
            self._next_id += 1
        self._store[log.id] = log

    def get_by_id(self, log_id):
        return self._store.get(log_id)

    def find_by_plant(self, plant_id):
        return [l for l in self._store.values() if l.plant_id == plant_id]
        
    def delete(self, log_id):
        self._store.pop(log_id, None)