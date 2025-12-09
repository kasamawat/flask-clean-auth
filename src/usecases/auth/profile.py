from src.usecases.ports.repositories import UserRepositoryPort, RefreshTokenRepositoryPort
from src.domain.errors import UserNotFound
from src.utils.security_wrapper import SecurityWrapper

class ProfileUsecase:
    def __init__(self, user_repo: UserRepositoryPort, refresh_repo: RefreshTokenRepositoryPort, password_hasher: SecurityWrapper):
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo
        self.password_hasher = password_hasher
        
    def get_profile(self, user_id: int):
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFound()
        return {
            "id": user.id, 
            "email": user.email, 
            "created_at": user.created_at
        }
        
    def update_profile(self, user_id: int, email: str = None, password: str = None):
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFound()
        update_data = {}
        if email:
            email_norm = email.strip().lower()
            existing = self.user_repo.find_by_email(email_norm)
            if existing and existing.id != user_id:
                raise ValueError("Email already in use")
            update_data["email"] = email_norm
        if password:
            update_data["password_hash"] = self.password_hasher.hash(password)
        updated = self.user_repo.update(user_id, **update_data)
        return {
            "id": updated.id,
            "email": updated.email,
            "created_at": updated.created_at
        }
    
    def delete_account(self, user_id: int):
        try:
            self.refresh_repo.revoke_all_for_user(user_id)
        except Exception:
            pass
        deleted = self.user_repo.delete(user_id)
        if not deleted:
            raise UserNotFound()
        return True