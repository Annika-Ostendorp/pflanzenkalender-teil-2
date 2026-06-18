from werkzeug.security import generate_password_hash, check_password_hash

class AuthenticationService:
    # Statische Methode, damit Funktion direkt ohne Instanz der Klasse aufgerufen werden kann,
    # wie in Task 2 gefordert (über AuthenticationService.get_password_hash())
    @staticmethod
    def get_password_hash(password: str) -> str:
        if not password: # falls Passwort leer ist -> leeren String zurückgeben
            return ""
        
        return generate_password_hash(password) # Klartext-Passwort wird dank generate_password_hash(...) sofort verschlüsselt
                                                # siehe AK 5: Plaintext is never persisted

    
    @staticmethod
    def check_password(password: str, password_hash: str) -> bool:
        return check_password_hash(password_hash, password) # übergebenes Passwort wird gehasht --> dann vergleichen mit Hash aus unserer Datenbank 
                                                            # --> gibt True oder False zurück (Übereinstimmung oder nicht)