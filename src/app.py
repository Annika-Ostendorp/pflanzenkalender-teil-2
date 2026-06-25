from datetime import date, timedelta
from flask import Flask, jsonify, request, render_template
from werkzeug.exceptions import HTTPException, BadRequest
from models import Plant, CareSchedule, ActionLog, User
from auth_service import AuthenticationService

import re # empfohlenes Modul für Sonderzeichen-Prüfung (siehe KI-Issue #9)

VALID_CARE_TYPES = {'watering', 'fertilizing', 'repotting'}
UPDATABLE_PLANT_FIELDS = {'name', 'species', 'location'}

# Username & Passwort Validierung für Nutzer-Login
def validate_login_username(username) -> str:
    if username is None:
        return "Field 'username' is required."
    
    if username == "":
        return "Field 'username' must not be empty."
    
    return None

def validate_login_password(password) -> str:
    if password is None:
        return "Field 'password' is required."
    
    if password == "":
        return "Field 'password' must not be empty."
    
    return None

# Username & Passwort Validierung für Nutzer-Registrierung
def validate_username(username) -> str: # Benutzernamen prüfen nach Vorgaben aus Task 5
    # Feld fehlt komplett im JSON-Payload
    if username is None:
        return "Field 'username' is required."
    
    
    # username ist str, aber komplett leer
    if username == "":
        return "Field 'username' must not be empty."
    
    # username überschreitet maximal erlaubte Länge von 50 Zeichen
    if len(username) > 50:
        return "Field 'username' must not exceed 50 characters."
    
    # prüfen, ob username fälschlicherweise Sonderzeichen enthält
    pattern = r"^\w+$" # siehe KI-Issue (#9) -> enthält a-z, A-Z, 0-9 und _
    if not re.match(pattern, username):
        return "Field 'username' may only contain letters, digits, and underscores."

    return None # falls keine Fehler gefunden -> einfach None zurück


def validate_password(password) -> str:
    # Feld fehlt komplett im JSON-Payload
    if password is None:
        return "Field 'password' is required."
    
    # password ist str, aber komplett leer
    if password == "":
        return "Field 'password' must not be empty."
    
    # password unterschreitet geforderte Mindestlänge von 8 Zeichen
    if len(password) < 8:
        return "Field 'password' must be at least 8 characters long."
    
    return None # falls keine Fehler gefunden -> wieder None zurückgeben


class PlantAppManager:
    def __init__(self, plant_repo, schedule_repo, log_repo, user_repo):
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.plant_repo = plant_repo
        self.schedule_repo = schedule_repo
        self.log_repo = log_repo
        self.user_repo = user_repo
        self.app.register_error_handler(HTTPException, self._handle_http_exception)
        self._register_routes()

    def _handle_http_exception(self, e):
        if request.path.startswith('/api/'):
            return jsonify({'error': e.description}), e.code
        return e

    def _next_due_date(self, plant, schedule, plant_logs):
        relevant = [l for l in plant_logs if l.care_type == schedule.care_type]
        if relevant:
            last = max(relevant, key=lambda l: l.performed_at)
            base = date.fromisoformat(last.performed_at)
        else:
            base = date.fromisoformat(plant.created_at)
        return base + timedelta(days=schedule.interval_days)

    def _plant_status(self, plant_id):
        plant = self.plant_repo.get_by_id(plant_id)
        plant_schedules = self.schedule_repo.find_by_plant(plant_id)
        plant_logs = self.log_repo.find_by_plant(plant_id)
        today = date.today()
        status = 'ok'
        for sched in plant_schedules:
            nd = self._next_due_date(plant, sched, plant_logs)
            days = (nd - today).days
            if days < 0:
                return 'overdue'
            if days <= 3:
                status = 'soon'
        return status
    

    def _authenticate_request(self):
        auth_header = request.headers.get("Authorization")

        if auth_header is None:
            return None, jsonify({"error": "Authentication required."}), 401
        
        if not auth_header.startswith("Bearer "):
            return None, jsonify({"error": "Invalid or expired token."}), 401
        
        token = auth_header.replace("Bearer ", "", 1) # brauchen für verify_token() ja nur JWT -> nicht noch Bearer vorne dran -> nur einmal ersetzen
        payload = AuthenticationService.verify_token(token)

        if payload is None:
            return None, jsonify({"error": "Invalid or expired token."}), 401
        
        return payload["sub"], None, None
    

    def _get_owned_plant_or_error(self, plant_id, user_id):
        plant = self.plant_repo.get_by_id(plant_id)

        if plant is None:
            return None, jsonify({"error": "Plant not found."}), 404
        
        if str(plant.user_id) != str(user_id):
            return None, jsonify({"error": "Plant not found."}), 404
        
        return plant, None, None
    

    def _register_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/api/plants', methods=['GET'])
        def get_plants():
            user_id, error_response, status_code = self._authenticate_request()

            if error_response is not None:
                return error_response, status_code
            
            result = []

            # TODO: durch find_by_user(user_id) ersetzen, sobald Plant-Routes JWT-geschützt sind

            for plant in self.plant_repo.find_all():
                if plant.user_id != user_id: # User bekommt jetzt wirklich nur seine Pflanzen -> JWT-ID muss mit user_id übereinstimmen
                    continue

                d = plant.to_dict()
                d['status'] = self._plant_status(plant.id)
                result.append(d)
            return jsonify(result), 200

        @self.app.route('/api/plants', methods=['POST'])
        def create_plant():
            user_id, error_response, status_code = self._authenticate_request()

            if error_response is not None:
                return error_response, status_code
            
            data = request.get_json()

            if not data:
                return jsonify({'error': 'Request body required'}), 400
            
            if "user_id" in data:
                return jsonify({"error": "Field 'user_id' must not be set manually."}), 400
            
            missing = [f for f in ('name', 'species', 'location') if f not in data]
            if missing:
                return jsonify({'error': f'Missing required fields: {missing}'}), 400
            plant = Plant(
                name=data['name'],
                species=data['species'],
                location=data['location'],
                created_at=data.get('created_at'),
                user_id=user_id,
            )
            self.plant_repo.save(plant)
            d = plant.to_dict()
            d['status'] = self._plant_status(plant.id)
            return jsonify(d), 201

        @self.app.route('/api/plants/<int:plant_id>', methods=['GET'])
        def get_plant(plant_id):
            user_id, error_response, status_code = self._authenticate_request()

            if error_response is not None:
                return error_response, status_code
            
            plant, error_response, status_code = self._get_owned_plant_or_error(
                plant_id,
                user_id
            )

            if error_response is not None:
                return error_response, status_code
            
            d = plant.to_dict()
            d['status'] = self._plant_status(plant_id)
            d['schedules'] = [s.to_dict() for s in self.schedule_repo.find_by_plant(plant_id)]
            return jsonify(d), 200

        @self.app.route('/api/plants/<int:plant_id>', methods=['PUT'])
        def update_plant(plant_id):
            user_id, error_response, status_code = self._authenticate_request()

            if error_response is not None:
                return error_response, status_code
            
            plant, error_response, status_code = self._get_owned_plant_or_error(
                plant_id,
                user_id
            )

            if error_response is not None:
                return error_response, status_code
            

            data = request.get_json()
            if data is None:
                return jsonify({'error': 'Invalid or missing JSON body'}), 400
            invalid = [k for k in data if k not in UPDATABLE_PLANT_FIELDS]
            if invalid:
                return jsonify({'error': f'Invalid fields: {invalid}'}), 400
            for field in UPDATABLE_PLANT_FIELDS:
                if field in data:
                    setattr(plant, field, data[field])
            self.plant_repo.save(plant)
            d = plant.to_dict()
            d['status'] = self._plant_status(plant_id)
            return jsonify(d), 200

        @self.app.route('/api/plants/<int:plant_id>', methods=['DELETE'])
        def delete_plant(plant_id):
            user_id, error_response, status_code = self._authenticate_request()

            if error_response is not None:
                return error_response, status_code
            
            plant, error_response, status_code = self._get_owned_plant_or_error(
                plant_id,
                user_id
            )

            if error_response is not None:
                return error_response, status_code
            
            for schedule in self.schedule_repo.find_by_plant(plant_id):
                self.schedule_repo.delete(schedule.id)
            for log in self.log_repo.find_by_plant(plant_id):
                self.log_repo.delete(log.id)
            self.plant_repo.delete(plant_id)
            return '', 204

        @self.app.route('/api/plants/<int:plant_id>/schedules', methods=['GET'])
        def get_schedules(plant_id):
            user_id, error_response, status_code = self._authenticate_request()

            if error_response is not None:
                return error_response, status_code
            
            plant, error_response, status_code = self._get_owned_plant_or_error(
                plant_id,
                user_id
            )

            if error_response is not None:
                return error_response, status_code
            
            return jsonify([s.to_dict() for s in self.schedule_repo.find_by_plant(plant_id)]), 200

        @self.app.route('/api/plants/<int:plant_id>/schedules', methods=['POST'])
        def create_or_update_schedule(plant_id):
            user_id, error_response, status_code = self._authenticate_request()

            if error_response is not None:
                return error_response, status_code
            
            plant, error_response, status_code = self._get_owned_plant_or_error(
                plant_id,
                user_id
            )

            if error_response is not None:
                return error_response, status_code
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body required'}), 400
            care_type = data.get('care_type')
            interval_days = data.get('interval_days')
            if not care_type or interval_days is None:
                return jsonify({'error': 'care_type and interval_days are required'}), 400
            if care_type not in VALID_CARE_TYPES:
                return jsonify({'error': f'care_type must be one of {sorted(VALID_CARE_TYPES)}'}), 400
            if isinstance(interval_days, bool) or not isinstance(interval_days, int) or interval_days < 1:
                return jsonify({'error': 'interval_days must be a positive integer'}), 400
            existing = self.schedule_repo.find_by_plant_and_care_type(plant_id, care_type)

            if existing:
                existing.interval_days = interval_days
                self.schedule_repo.save(existing)
                return jsonify(existing.to_dict()), 201
            sched = CareSchedule(plant_id=plant_id, care_type=care_type, interval_days=interval_days)
            self.schedule_repo.save(sched)
            return jsonify(sched.to_dict()), 201

        @self.app.route('/api/plants/<int:plant_id>/schedules/<care_type>', methods=['DELETE'])
        def delete_schedule(plant_id, care_type):
            user_id, error_response, status_code = self._authenticate_request()

            if error_response is not None:
                return error_response, status_code
            
            plant, error_response, status_code = self._get_owned_plant_or_error(
                plant_id,
                user_id
            )

            if error_response is not None:
                return error_response, status_code
            
            sched = self.schedule_repo.find_by_plant_and_care_type(plant_id, care_type)

            if not sched:
                return jsonify({'error': 'Schedule not found'}), 404
            self.schedule_repo.delete(sched.id)
            return '', 204

        @self.app.route('/api/plants/<int:plant_id>/logs', methods=['GET'])
        def get_logs(plant_id):
            user_id, error_response, status_code = self._authenticate_request()

            if error_response is not None:
                return error_response, status_code
            
            plant, error_response, status_code = self._get_owned_plant_or_error(
                plant_id,
                user_id
            )

            if error_response is not None:
                return error_response, status_code
            
            result = sorted(
                [l.to_dict() for l in self.log_repo.find_by_plant(plant_id)],
                key=lambda l: l['performed_at'],
                reverse=True,
            )
            return jsonify(result), 200

        @self.app.route('/api/plants/<int:plant_id>/logs', methods=['POST'])
        def create_log(plant_id):
            user_id, error_response, status_code = self._authenticate_request()

            if error_response is not None:
                return error_response, status_code
            
            if not self.plant_repo.get_by_id(plant_id):
                return jsonify({'error': 'Plant not found.'}), 404
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body required'}), 400
            if not data.get('care_type'):
                return jsonify({'error': 'care_type is required'}), 400
            log = ActionLog(
                plant_id=plant_id,
                care_type=data['care_type'],
                performed_at=data.get('performed_at'),
                notes=data.get('notes') or '',
            )
            self.log_repo.save(log)
            return jsonify(log.to_dict()), 201

        @self.app.route('/api/plants/<int:plant_id>/next-actions', methods=['GET'])
        def get_next_actions(plant_id):
            user_id, error_response, status_code = self._authenticate_request()

            if error_response is not None:
                return error_response, status_code
            
            plant = self.plant_repo.get_by_id(plant_id)
            if not plant:
                return jsonify({'error': 'Plant not found.'}), 404
            plant_schedules = self.schedule_repo.find_by_plant(plant_id)
            plant_logs = self.log_repo.find_by_plant(plant_id)
            today = date.today()
            result = []
            for sched in plant_schedules:
                nd = self._next_due_date(plant, sched, plant_logs)
                days_until = (nd - today).days
                result.append({
                    'care_type': sched.care_type,
                    'interval_days': sched.interval_days,
                    'next_due': nd.isoformat(),
                    'days_until': days_until,
                    'overdue': days_until < 0,
                })
            result.sort(key=lambda x: x['days_until'])
            return jsonify(result), 200

        @self.app.route('/api/overdue', methods=['GET'])
        def get_overdue():
            user_id, error_response, status_code = self._authenticate_request()

            if error_response is not None:
                return error_response, status_code
            
            today = date.today()
            result = []
            
            # TODO: durch find_by_user(user_id) ersetzen, sobald Plant-Routes JWT-geschützt sind

            for plant in self.plant_repo.find_all():
                if plant.user_id != user_id:
                    continue

                plant_schedules = self.schedule_repo.find_by_plant(plant.id)
                plant_logs = self.log_repo.find_by_plant(plant.id)
                for sched in plant_schedules:
                    nd = self._next_due_date(plant, sched, plant_logs)
                    days_until = (nd - today).days
                    if days_until < 0:
                        result.append({
                            'plant_id': plant.id,
                            'plant_name': plant.name,
                            'plant_location': plant.location,
                            'care_type': sched.care_type,
                            'next_due': nd.isoformat(),
                            'days_overdue': -days_until,
                        })
            result.sort(key=lambda x: x['days_overdue'], reverse=True)
            return jsonify(result), 200
        
        # Endpoint POST /api/auth/register
        @self.app.route('/api/auth/register', methods=['POST'])
        def register_user():
            try:
                if not request.is_json: # wenn Content-Type Header kein JSON ist --> 415 Unsupported Media Type Error
                    return jsonify({"error": "Content-Type must be 'application/json'."}), 415
                
                try: # prüfen, ob Request-Body gültiges JSON ist -> falls nicht -> 400 Bad Request Error
                    payload = request.get_json() # erstmal alle gesendeten Daten holen -> Payload dann Dictionary
                
                except Exception:
                    return jsonify({"error": "Request body must be valid JSON."}), 400

                if payload is None: # falls Body komplett leer -> payload = None -> das aber auch ungültiges JSON -> 400 Bad Request Error
                    return jsonify({"error": "Request body must be valid JSON."}), 400
                

                username = payload.get("username") # aus payload-Dictionary jew. Einträge für username & password holen
                password = payload.get("password")
                

                username_error = validate_username(username) # prüfen, ob username gültig ist mit oben definierter Funktion validate_username()

                if username_error:
                    return jsonify({"error": username_error}), 400 # jew. Fehlermeldung siehe obige Funktion


                password_error = validate_password(password) # prüfen, ob password gültig ist mit oben definierter Funktion validate_password()

                if password_error:
                    return jsonify({"error": password_error}), 400 # wenn Fehler im Passwort -> abbrechen mit Statuscode 400 Bad Request
                

                existing_user = self.user_repo.find_by_username(username)
                if existing_user:
                    return jsonify({"error": "Username is already taken."}), 409
                
                password_hash = AuthenticationService.get_password_hash(password)
                new_user = User(username=username, password_hash=password_hash)
                self.user_repo.save(new_user)
                return jsonify(new_user.to_dict()), 201

            except Exception:
                return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500
            

        # Endpoint POST /api/auth/login
        @self.app.route('/api/auth/login', methods = ['POST'])
        def login_user():
            try:
                if not request.is_json:
                    return jsonify({"error": "Content-Type must be 'application/json'."}), 415
                
                try: # JSON parse errors abfangen
                    payload = request.get_json()

                    if payload is None: # falls Body komplett leer -> payload = None -> das aber auch ungültiges JSON -> 400 Bad Request Error
                        return jsonify({"error": "Request body must be valid JSON."}), 400
                
                except BadRequest:
                    return jsonify({"error": "Request body must be valid JSON."}), 400
                
    
                username_error = validate_login_username(payload.get("username"))
    
                if username_error: # falls username ungültig --> 400 Bad Request
                    return jsonify({"error": username_error}), 400
            
                password_error = validate_login_password(payload.get("password"))

                if password_error:
                    return jsonify({"error": password_error}), 400
            
                username = payload["username"]
                password = payload["password"]

                user = self.user_repo.find_by_username(username)

                # identischen Request-Body für unbekannten Username & falsches Passwort zurückgeben
                if user is None:
                    return jsonify({"error": "Invalid username or password."}), 401
            
                if not AuthenticationService.verify_password(password, user.password_hash):
                    return jsonify({"error": "Invalid username or password."}), 401
            
                try:
                    access_token = AuthenticationService.create_token(user.id)
            
                except Exception:
                    return jsonify({"error": "Service Unavailable."}), 503
            

                return jsonify({"access_token": access_token}), 200 # erfolgreich generierten Token am Ende zurückgeben
            
            except Exception:
                return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500
            

if __name__ == '__main__':  # pragma: no cover
    from json_repositories import (
        JsonPlantRepository, JsonCareScheduleRepository,
        JsonActionLogRepository, JsonUserRepository,
    )
    manager = PlantAppManager(
        JsonPlantRepository('data/plants.json'),
        JsonCareScheduleRepository('data/schedules.json'),
        JsonActionLogRepository('data/logs.json'),
        JsonUserRepository('data/users.json'),
    )
    app = manager.app
    app.run(debug=True, host='127.0.0.1', port=5000)
