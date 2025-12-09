from src.usecases.ports.repositories import RefreshTokenRepositoryPort
from src.frameworks.db import db
from typing import Optional
from datetime import datetime
from src.adapters.orm.models import RefreshTokenModel

class SQLAlchemyRefreshTokenRepository(RefreshTokenRepositoryPort):
    def create(self, user_id: int, token_hash: str, expires_at: datetime):
        model = RefreshTokenModel(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        db.session.add(model)
        db.session.commit()
        return model
    
    def find_by_hash(self, token_hash: str) -> Optional[RefreshTokenModel]:
        return RefreshTokenModel.query.filter_by(token_hash=token_hash).first()
    
    def revoke(self, token_hash: str):
        model = self.find_by_hash(token_hash)
        if model and not model.revoked:
            model.revoked = True
            db.session.add(model)
            db.session.commit()
        return model
    
    def revoke_all_for_user(self, user_id: int):
        RefreshTokenModel.query.filter_by(user_id=user_id, revoked=False).update({"revoked": True})
        db.session.commit()
        
    def rotate(self, old_hash: str, new_hash: str, new_expires_at: datetime):
        old = self.find_by_hash(old_hash)
        if old:
            old.revoked = True
            old.replaced_by = new_hash
            db.session.add(old)
        new = RefreshTokenModel(user_id=old.user_id, token_hash=new_hash, expires_at=new_expires_at)
        db.session.add(new)
        db.session.commit()
        return old, new