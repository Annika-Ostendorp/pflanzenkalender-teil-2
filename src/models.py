from datetime import date


class Plant:
    _next_id = 1

    def __init__(self, name, species, location, created_at=None):
        self.id = Plant._next_id
        Plant._next_id += 1
        self.name = name
        self.species = species
        self.location = location
        self.created_at = created_at or date.today().isoformat()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'species': self.species,
            'location': self.location,
            'created_at': self.created_at,
        }


class CareSchedule:
    _next_id = 1

    def __init__(self, plant_id, care_type, interval_days):
        self.id = CareSchedule._next_id
        CareSchedule._next_id += 1
        self.plant_id = plant_id
        self.care_type = care_type
        self.interval_days = interval_days

    def to_dict(self):
        return {
            'id': self.id,
            'plant_id': self.plant_id,
            'care_type': self.care_type,
            'interval_days': self.interval_days,
        }


class ActionLog:
    _next_id = 1

    def __init__(self, plant_id, care_type, performed_at=None, notes=None):
        self.id = ActionLog._next_id
        ActionLog._next_id += 1
        self.plant_id = plant_id
        self.care_type = care_type
        self.performed_at = performed_at or date.today().isoformat()
        self.notes = notes or ''

    def to_dict(self):
        return {
            'id': self.id,
            'plant_id': self.plant_id,
            'care_type': self.care_type,
            'performed_at': self.performed_at,
            'notes': self.notes,
        }
