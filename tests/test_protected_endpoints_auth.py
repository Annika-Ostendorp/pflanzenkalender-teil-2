import jwt
import time

protected_requests = [
    ("GET", "/api/plants", None),
    ("POST", "/api/plants", {"name": "Monstera"}),
    ("GET", "/api/plants/1", None),
    ("PUT", "/api/plants/1", {"name": "Monstera"}),
    ("DELETE", "/api/plants/1", None),
    ("GET", "/api/plants/1/schedules", None),
    ("POST", "/api/plants/1/schedules", {"care_type": "watering", "interval_days": 7}),
    ("DELETE", "/api/plants/1/schedules/watering", None),
    ("GET", "/api/plants/1/logs", None),
    ("POST", "/api/plants/1/logs", {"care_type": "watering"}),
    ("GET", "/api/plants/1/next-actions", None),
    ("GET", "api/overdue", None),
 ]