from src.domain.entities.user import User
from src.adapters.orm.models import UserModel

def model_to_entity(m: UserModel) -> User:
    if m is None:
        return None
    return User(id=m.id, email=m.email, password_hash=m.password_hash, created_at=m.created_at)

def entity_to_model(e: User) -> UserModel:
    m = UserModel()
    m.id = e.id
    m.email = e.email
    m.password_hash = e.password_hash
    m.created_at = e.created_at
    return m