from src.usecases.ports.repositories import RefreshTokenRepositoryPort, UserRepositoryPort
from src.domain.errors import RefreshTokenError
from src.utils.security_wrapper import SecurityWrapper
from datetime import datetime

class RefreshTokenUsecase:
    def __init__(self, refresh_repo: RefreshTokenRepositoryPort, user_repo: UserRepositoryPort, jwt_provider: SecurityWrapper, token_generator: SecurityWrapper):
        self.refresh_repo = refresh_repo
        self.user_repo = user_repo
        self.jwt_provider = jwt_provider
        self.token_generator = token_generator
        
    def execute(self, raw_refresh_token: str) -> dict:
        hashed = self.token_generator.hash_refresh_token(raw_refresh_token)
        record = self.refresh_repo.find_by_hash(hashed)
        if not record:
            raise RefreshTokenError("invalid_refresh_token")
        if record.revoked:
            self.refresh_repo.revoke_all_for_user(record.user_id)
            raise RefreshTokenError("refresh_token_revoked")
        if record.expires_at < datetime.utcnow():
            raise RefreshTokenError("refresh_token_expired")

        new_raw = self.token_generator.generate_refresh_token_raw()
        new_hash = self.token_generator.hash_refresh_token(new_raw)
        new_expires = self.token_generator.refresh_token_expiry()
        self.refresh_repo.rotate(old_hash=hashed, new_hash=new_hash, new_expires_at=new_expires)

        user = self.user_repo.find_by_id(record.user_id)
        access_token = self.jwt_provider.generate_access_token({"sub": user.id, "email": user.email})

        return {
            "access_token": access_token, 
            "token_type": "bearer", 
            "refresh_token": new_raw, 
            "refresh_expires_at": new_expires
        }