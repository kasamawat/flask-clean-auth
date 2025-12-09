import pytest
from src.usecases.auth.refresh import RefreshTokenUsecase
from tests.test_utils import FakeUserRepo, FakeSecurity, FakeRefreshRepo
from datetime import datetime, timedelta

def test_refresh_success_rotate():
    user_repo = FakeUserRepo()
    refresh_repo = FakeRefreshRepo()
    security = FakeSecurity()
    
    # create user
    u = type("U", (), {"email": "a@a.com", "password_hash": security.hash("p")})
    user = user_repo.create(u)
    
    # create refresh token record
    raw = security.generate_refresh_token_raw()
    hashed = security.hash_refresh_token(raw)
    expires = security.refresh_token_expiry()
    refresh_repo.create(user_id=user.id, token_hash=hashed, expires_at=expires)
    
    uc = RefreshTokenUsecase(refresh_repo=refresh_repo, user_repo=user_repo, jwt_provider=security, token_generator=security)
    out = uc.execute(raw)
    
    assert out["access_token"] == f"access-{user.id}"
    assert out["refresh_token"].startswith("raw-")
    
    # old token should be revoked
    old = refresh_repo.find_by_hash(hashed)
    assert old.revoked is True

def test_refresh_invalid_token():
    user_repo = FakeUserRepo()
    refresh_repo = FakeRefreshRepo()
    security = FakeSecurity()
    
    uc = RefreshTokenUsecase(refresh_repo=refresh_repo, user_repo=user_repo, jwt_provider=security, token_generator=security)
    with pytest.raises(Exception):
        uc.execute("no-such-token")
        
def test_refresh_revoked_behavior_revokes_all():
    user_repo = FakeUserRepo()
    refresh_repo = FakeRefreshRepo()
    security = FakeSecurity()
    
    # create user and token
    u = type("U", (), {"email": "a@a.com", "password_hash": security.hash("p")})
    user = user_repo.create(u)
    raw = security.generate_refresh_token_raw()
    hashed = security.hash_refresh_token(raw)
    expires = security.refresh_token_expiry()
    refresh_repo.create(user_id=user.id, token_hash=hashed, expires_at=expires)
    
    # manually revoke
    refresh_repo.revoke(hashed)
    
    uc = RefreshTokenUsecase(refresh_repo=refresh_repo, user_repo=user_repo, jwt_provider=security, token_generator=security)
    with pytest.raises(Exception):
        uc.execute(raw)
    
    # ensure all tokens for user are revoked (already only one)
    rec = refresh_repo.find_by_hash(hashed)
    assert rec.revoked is True