from abc import ABC, abstractmethod


class PlantRepository(ABC):
    @abstractmethod
    def save(self, plant): ...

    @abstractmethod
    def get_by_id(self, plant_id): ...

    @abstractmethod
    def find_all(self): ...

    @abstractmethod
    def find_by_user(self, user_id): ...

    @abstractmethod
    def delete(self, plant_id): ...


class CareScheduleRepository(ABC):
    @abstractmethod
    def save(self, schedule): ...

    @abstractmethod
    def get_by_id(self, schedule_id): ...

    @abstractmethod
    def find_by_plant(self, plant_id): ...

    @abstractmethod
    def find_by_plant_and_care_type(self, plant_id, care_type): ...

    @abstractmethod
    def delete(self, schedule_id): ...


class ActionLogRepository(ABC):
    @abstractmethod
    def save(self, log): ...

    @abstractmethod
    def get_by_id(self, log_id): ...

    @abstractmethod
    def find_by_plant(self, plant_id): ...

    @abstractmethod
    def delete(self, log_id): ...


class UserRepository(ABC):
    @abstractmethod
    def save(self, user): ...

    @abstractmethod
    def get_by_id(self, user_id): ...

    @abstractmethod
    def find_by_username(self, username): ...
    
    @abstractmethod
    def delete(self, user_id): ...