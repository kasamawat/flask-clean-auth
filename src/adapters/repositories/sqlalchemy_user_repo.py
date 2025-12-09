from src.usecases.ports.repositories import UserRepositoryPort
from src.adapters.orm.models import UserModel
from src.frameworks.db import db
from typing import Optional
from src.domain.entities.user import User
from src.adapters.orm.mappers import model_to_entity

class SQLAlchemyUserRepository(UserRepositoryPort):
    def create(self, user: User) -> User:
        model = UserModel(email=user.email, password_hash=user.password_hash)
        db.session.add(model)
        db.session.commit()
        return model_to_entity(model)
    
    def find_by_email(self, email: str) -> Optional[User]:
        model = UserModel.query.filter_by(email=email).first()
        return model_to_entity(model) if model else None
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        model = UserModel.query.get(user_id)
        return model_to_entity(model) if model else None
    
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        model = UserModel.query.get(user_id)
        if not model:
            return None
        if "email" in kwargs and kwargs["email"] is not None:
            model.email = kwargs["email"]
        if "password_hash" in kwargs and kwargs["password_hash"] is not None:
            model.password_hash = kwargs["password_hash"]
        db.session.add(model)
        db.session.commit()
        return model_to_entity(model)
    
    def delete(self, user_id: int) -> bool:
        model = UserModel.query.get(user_id)
        if not model:
            return False
        db.session.delete(model)
        db.session.commit()
        return True
    