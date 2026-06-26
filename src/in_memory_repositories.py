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

    def save(self, plant: Plant) -> None:
        if plant.id is None:
            plant.id = self._next_id
            self._next_id += 1
        self._store[plant.id] = plant

    def get_by_id(self, plant_id: int) -> Plant | None:
        return self._store.get(plant_id)

    def find_by_user(self, user_id: int) -> list[Plant]:
        return [p for p in self._store.values() if p.user_id == user_id]

    def delete(self, plant_id: int) -> None:
        self._store.pop(plant_id, None)


class InMemoryCareScheduleRepository(CareScheduleRepository):
    def __init__(self):
        self._store = {}
        self._next_id = 1

    def save(self, schedule: CareSchedule) -> None:
        if schedule.id is None:
            schedule.id = self._next_id
            self._next_id += 1
        self._store[schedule.id] = schedule

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


class InMemoryActionLogRepository(ActionLogRepository):
    def __init__(self):
        self._store = {}
        self._next_id = 1

    def save(self, log: ActionLog) -> None:
        if log.id is None:
            log.id = self._next_id
            self._next_id += 1
        self._store[log.id] = log

    def get_by_id(self, log_id: int) -> ActionLog | None:
        return self._store.get(log_id)

    def find_by_plant(self, plant_id: int) -> list[ActionLog]:
        return [l for l in self._store.values() if l.plant_id == plant_id]

    def delete(self, log_id: int) -> None:
        self._store.pop(log_id, None)


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._store = {}
        self._next_id = 1

    def save(self, user: User) -> None:
        if user.id is None:
            user.id = self._next_id
            self._next_id += 1
        self._store[user.id] = user

    def get_by_id(self, user_id: int) -> User | None:
        return self._store.get(user_id)

    def find_by_username(self, username: str) -> User | None:
        return next(
            (u for u in self._store.values() if u.username == username),
            None,
        )

    def delete(self, user_id: int) -> None:
        self._store.pop(user_id, None)