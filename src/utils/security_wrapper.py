import hashlib
import secrets
from passlib.hash import bcrypt
import jwt
from datetime import datetime, timedelta
from flask import current_app

class SecurityWrapper:
    def __init__(self, app=None):
        self.app = app
        
    def init_app(self, app):
        self.app = app
        
        # Register to extensions
        app.extensions["security"] = self
        app.extensions["token_generator"] = self
        
    # password hashing (normalize with sha256 then bcrypt)
    def _normalize_password(self, plain: str) -> str:
        if plain is None:
            plain = ""
        return hashlib.sha256(plain.encode("utf-8")).hexdigest()
    
    def hash(self, plain: str) -> str:
        normalized = self._normalize_password(plain)
        return bcrypt.hash(normalized)
    
    def verify(self, plain: str, hashed: str) -> bool:
        normalized = self._normalize_password(plain)
        return bcrypt.verify(normalized, hashed)
    
    # jwt
    def generate_access_token(self, payload: dict) -> str:
        secret = self.app.config.get("SECRET_KEY")
        exp = datetime.utcnow() + timedelta(seconds=self.app.config.get("JWT_EXPIRATION_SECONDS", 3600))
        to_encode = payload.copy()
        to_encode.update({"exp": exp})
        token = jwt.encode(to_encode, secret, algorithm="HS256")
        if isinstance(token, bytes):
            token = token.decode()
        return token
    
    def decode_token(self, token: str) -> dict:
        secret = self.app.config.get("SECRET_KEY")
        return jwt.decode(token, secret, algorithms=["HS256"])
    
    # refresh token helpers
    def generate_refresh_token_raw(self, length: int = 48) -> str:
        return secrets.token_urlsafe(length)

    def hash_refresh_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def refresh_token_expiry(self, minutes: int = 60 * 24 * 30):
        return datetime.utcnow() + timedelta(minutes=minutes)