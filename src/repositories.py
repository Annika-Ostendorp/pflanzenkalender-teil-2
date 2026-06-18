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