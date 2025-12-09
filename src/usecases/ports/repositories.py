from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.user import User
from datetime import datetime

class UserRepositoryPort(ABC):
    @abstractmethod
    def create(self, user:User) -> User:
        raise NotImplementedError
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError
    
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        raise NotImplementedError
    
    @abstractmethod
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        raise NotImplementedError
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        raise NotImplementedError
    
class RefreshTokenRepositoryPort(ABC):
    @abstractmethod
    def create(self, user_id: int, token_hash: str, expires_at: datetime):
        raise NotImplementedError
    
    @abstractmethod
    def find_by_hash(self, token_hash: str):
        raise NotImplementedError
    
    @abstractmethod
    def revoke(self, token_hash: str):
        raise NotImplementedError

    @abstractmethod
    def revoke_all_for_user(self, user_id: int):
        raise NotImplementedError
    
    @abstractmethod
    def rotate(self, old_hash: str, new_hash: str, new_expires_at: datetime):
        raise NotImplementedError