import pytest
from src.usecases.auth.register import RegisterUser
from tests.test_utils import FakeUserRepo, FakeSecurity
from src.domain.errors import EmailAlreadyExists

def test_register_success():
    user_repo = FakeUserRepo()
    security = FakeSecurity()
    uc = RegisterUser(user_repo=user_repo, password_hasher=security)
    
    res = uc.execute("A@B.COM", "123456")
    assert res["id"] == 1
    assert res["email"] == "a@b.com" # normalized to lowercase
    
def test_register_email_exists():
    user_repo = FakeUserRepo()
    security = FakeSecurity()
    
    # create existing user
    from types import SimpleNamespace
    existing = SimpleNamespace(email="x@x.com", password_hash=security.hash("p"))
    user_repo.create(existing)
    
    uc = RegisterUser(user_repo=user_repo, password_hasher=security)
    with pytest.raises(EmailAlreadyExists):
        uc.execute("x@x.com", "another")