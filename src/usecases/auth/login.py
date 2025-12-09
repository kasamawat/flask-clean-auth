from src.usecases.ports.repositories import UserRepositoryPort, RefreshTokenRepositoryPort
from src.domain.errors import InvalidCredentials
from src.utils.security_wrapper import SecurityWrapper

class LoginUser:
    def __init__(self, user_repo: UserRepositoryPort, refresh_repo: RefreshTokenRepositoryPort, password_hasher: SecurityWrapper, jwt_provider: SecurityWrapper, token_generator: SecurityWrapper):
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo
        self.password_hasher = password_hasher
        self.jwt_provider = jwt_provider
        self.token_generator = token_generator
        
    def execute(self, email: str, password: str) -> dict:
        email_norm = email.strip().lower()
        user = self.user_repo.find_by_email(email_norm)
        if not user or not self.password_hasher.verify(password, user.password_hash):
            raise InvalidCredentials()
        
        access_token = self.jwt_provider.generate_access_token({"sub": user.id, "email": user.email})
        raw_refresh = self.token_generator.generate_refresh_token_raw()
        hashed = self.token_generator.hash_refresh_token(raw_refresh)
        expires_at = self.token_generator.refresh_token_expiry()
        self.refresh_repo.create(user_id=user.id, token_hash=hashed, expires_at=expires_at)
        
        return {
            "access_token": access_token, 
            "token_type": "bearer", 
            "refresh_token": raw_refresh, 
            "refresh_expires_at": expires_at
        }