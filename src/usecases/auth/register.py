from src.usecases.ports.repositories import UserRepositoryPort
from src.domain.entities.user import User
from src.domain.errors import EmailAlreadyExists
from src.utils.security_wrapper import SecurityWrapper

class RegisterUser:
    # injection
    def __init__(self, user_repo: UserRepositoryPort, password_hasher: SecurityWrapper):
        self.user_repo = user_repo
        self.password_hasher = password_hasher
        
    def execute(self, email: str, password: str) -> dict:
        email_norm = email.strip().lower()
        existing = self.user_repo.find_by_email(email_norm)
        if existing:
            raise EmailAlreadyExists(email_norm)
        
        pw_hash = self.password_hasher.hash(password)
        entity = User(id=None, email=email_norm, password_hash=pw_hash)
        created = self.user_repo.create(entity)
        return {"id": created.id, "email": created.email, "created_at": created.created_at}