import pytest
from src.usecases.auth.login import LoginUser
from tests.test_utils import FakeUserRepo, FakeSecurity
from datetime import datetime

def test_login_success():
    user_repo = FakeUserRepo()
    refresh_repo = type("R", (), {"create": lambda *a, **k: None})()
    security = FakeSecurity()
    
    # create user
    u = type("U", (), {"email": "a@a.com", "password_hash": security.hash("pw")})
    user_repo.create(u)
    
    uc = LoginUser(user_repo=user_repo, refresh_repo=refresh_repo, password_hasher=security, jwt_provider=security, token_generator=security)
    out = uc.execute("a@a.com", "pw")
    
    assert out["access_token"] == "access-1"
    assert out["token_type"] == "bearer"
    assert out["refresh_token"].startswith("raw-")
    
def test_login_invalid_credentials():
    user_repo = FakeUserRepo()
    refresh_repo = type("R", (), {"create": lambda *a, **k: None})()
    security = FakeSecurity()
    
    uc = LoginUser(user_repo=user_repo, refresh_repo=refresh_repo, password_hasher=security, jwt_provider=security, token_generator=security)
    with pytest.raises(Exception):
        uc.execute("test@gmail.com", "pw")