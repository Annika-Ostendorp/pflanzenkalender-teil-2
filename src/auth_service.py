from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import time

class AuthenticationService:
    # Statische Methode, damit Funktion direkt ohne Instanz der Klasse aufgerufen werden kann,
    # wie in Task 2 gefordert (über AuthenticationService.get_password_hash())
    @staticmethod
    def get_password_hash(password: str) -> str:
        return generate_password_hash(password) # Klartext-Passwort wird dank generate_password_hash(...) sofort verschlüsselt
                                                # siehe AK 5: Plaintext is never persisted

    
    @staticmethod
    def check_password(password: str, password_hash: str) -> bool:
        return check_password_hash(password_hash, password) # übergebenes Passwort wird gehasht --> dann vergleichen mit Hash aus unserer Datenbank 
                                                            # --> gibt True oder False zurück (Übereinstimmung oder nicht)
    

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return AuthenticationService.check_password(password, password_hash)
    

    @staticmethod
    def create_token(user_id: int) -> str:
        issued_at = int(time.time()) # aktuelle Zeit als int umwandeln (Unix Timestamp siehe KI-Issue #23)
        expires_at = issued_at + 3600

        payload = {
            "sub": str(user_id),
            "iat": issued_at,
            "exp": expires_at
        }

        return jwt.encode(payload, "test-secret", algorithm = "HS256") # Token verschlüsseln
    

    @staticmethod
    def verify_token(token: str):
        try:
            return jwt.decode(token, "test-secret", algorithms = ["HS256"]) # wenn gültig, dann kann Payload zurückgegeben werden
        
        except jwt.InvalidTokenError:
            return None