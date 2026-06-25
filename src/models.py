from datetime import date


class Plant:

    def __init__(
        self,
        name: str,
        species: str,
        location: str,
        created_at: str | None = None,
        id: int | None = None,
        user_id: int | None = None,
    ):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.species = species
        self.location = location  
        self.created_at = created_at or date.today().isoformat()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'species': self.species,
            'location': self.location,
            'created_at': self.created_at,
        }
        

class CareSchedule:
    def __init__(
        self,
        plant_id: int,
        care_type: str,
        interval_days: int,
        id: int | None = None,
    ):
        self.id = id
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
    def __init__(
        self,
        plant_id: int,
        care_type: str,
        performed_at: str | None = None,
        notes: str | None = None,
        id: int | None = None,
    ):
        self.id = id
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


class User:
    def __init__(self, username: str, password_hash: str, id: int = None):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def to_dict(self): # ID & Username zurückgeben, aber nicht Passwort/Passwort-Hash
                       # siehe Akzeptanzkriterium 2: The response contains id and username, but never the password or its hash.
        return {
            'id': self.id,
            'username': self.username
        }