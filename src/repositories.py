from abc import ABC, abstractmethod
from models import Plant, CareSchedule, ActionLog, User

class PlantRepository(ABC):
    @abstractmethod
    def save(self, plant: Plant) -> None: ...

    @abstractmethod
    def get_by_id(self, plant_id: int) -> Plant | None: ...

    @abstractmethod
    def find_by_user(self, user_id: int) -> list[Plant]: ...

    @abstractmethod
    def delete(self, plant_id: int) -> None: ...


class CareScheduleRepository(ABC):
    @abstractmethod
    def save(self, schedule: CareSchedule) -> None: ...

    @abstractmethod
    def get_by_id(self, schedule_id: int) -> CareSchedule | None: ...

    @abstractmethod
    def find_by_plant(self, plant_id: int) -> list[CareSchedule]: ...

    @abstractmethod
    def find_by_plant_and_care_type(self, plant_id: int, care_type: str) -> CareSchedule | None: ...

    @abstractmethod
    def delete(self, schedule_id: int) -> None: ...


class ActionLogRepository(ABC):
    @abstractmethod
    def save(self, log: ActionLog) -> None: ...

    @abstractmethod
    def get_by_id(self, log_id: int) -> ActionLog | None: ...

    @abstractmethod
    def find_by_plant(self, plant_id: int) -> list[ActionLog]: ...

    @abstractmethod
    def delete(self, log_id: int) -> None: ...


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None: ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    def find_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    def delete(self, user_id: int) -> None: ...