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


