import pytest
from src.usecases.auth.profile import ProfileUsecase
from tests.test_utils import FakeUserRepo, FakeSecurity, FakeRefreshRepo

def test_get_profile_not_found():
    user_repo = FakeUserRepo()
    refresh_repo = FakeRefreshRepo()
    security = FakeSecurity()
    
    uc = ProfileUsecase(user_repo=user_repo, refresh_repo=refresh_repo, password_hasher=security)
    with pytest.raises(Exception):
        uc.get_profile(999)

def test_update_email_conflict():
    user_repo = FakeUserRepo()
    refresh_repo = FakeRefreshRepo()
    security = FakeSecurity()
    
    # create 2 users
    a = type("U", (), {"email": "a@a.com", "password_hash": security.hash("p")})
    b = type("U", (), {"email": "b@b.com", "password_hash": security.hash("p")})
    ua = user_repo.create(a)
    ub = user_repo.create(b)
    
    uc = ProfileUsecase(user_repo=user_repo, refresh_repo=refresh_repo, password_hasher=security)
    # attempt to update ua's email to ub's email -> should raise ValueError "Email already in use"
    with pytest.raises(ValueError):
        uc.update_profile(ua.id, email="b@b.com")

def test_update_password_and_email_success():
    user_repo = FakeUserRepo()
    refresh_repo = FakeRefreshRepo()
    security = FakeSecurity()
    
    a = type("U", (), {"email": "a@a.com", "password_hash": security.hash("p")})
    ua = user_repo.create(a)
    
    uc = ProfileUsecase(user_repo=user_repo, refresh_repo=refresh_repo, password_hasher=security)
    res = uc.update_profile(ua.id, email="new@new.com", password="newpw")
    assert res["email"] == "new@new.com"
    
    # confirm password changed in repo
    stored = user_repo.find_by_id(ua.id)
    assert security.verify("newpw", stored.password_hash)