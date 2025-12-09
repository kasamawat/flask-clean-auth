import hashlib
from datetime import datetime, timedelta

# Fake Security Warpper
class FakeSecurity:
    def __init__(self):
        self._next_refresh_counter = 1
        
    # password: normalize as sha256-hex then prefix 'H:' for hash to make deterministic.
    def _normalize(self, plain: str) -> str:
        if plain is None:
            plain = ""
        return hashlib.sha256(plain.encode("utf-8")).hexdigest()
    
    def hash(self, plain: str) -> str:
        return "H:" + self._normalize(plain)
    
    def verify(self, plain: str, hashed: str) -> bool:
        return self.hash(plain) == hashed
    
    def generate_access_token(self, payload: dict) -> str:
        # return deterministic token that encodes user_id
        user_id = payload.get("sub")
        return f"access-{user_id}"
    
    def generate_refresh_token_raw(self, length: int = 48) -> str:
        # deterministic uniqure raw token each call
        token = f"raw-{self._next_refresh_counter}"
        self._next_refresh_counter += 1
        return token
    
    def hash_refresh_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()
    
    def refresh_token_expiry(self, days: int = 30):
        return datetime.utcnow() + timedelta(days=days)
    
# Fake User Repo
class FakeUserRepo:
    def __init__(self):
        # id -> user dict: {id, email, password_hash, created_at}
        self._store = {}
        self._next_id = 1
        
    def create(self, user):
        # user is domain entity or with email/password_hash
        uid = self._next_id
        self._next_id += 1
        row = {
            "id": uid,
            "email": user.email,
            "password_hash": user.password_hash,
            "created_at": getattr(user, "created_at", None) or datetime.utcnow()
        }
        self._store[uid] = row
        # return object with attributes used by usecases (id, email, password_hash, created_at)
        return type("U", (), row)
    
    def find_by_email(self, email: str):
        for r in self._store.values():
            if r["email"] == email:
                return type("U", (), r)
        return None
    
    def find_by_id(self, user_id: int):
        r = self._store.get(user_id)
        return type("U", (), r) if r else None
    
    def update(self, user_id: int, **kwargs):
        r = self._store.get(user_id)
        if not r:
            return None
        if "email" in kwargs and kwargs["email"] is not None:
            r["email"] = kwargs["email"]
        if "password_hash" in kwargs and kwargs["password_hash"] is not None:
            r["password_hash"] = kwargs["password_hash"]
        return type("U", (), r)
    
    def delete(self, user_id: int):
        if user_id in self._store:
            del self._store[user_id]
            return True
        return False
    
# Fake Refresh Repo
class FakeRefreshRepo:
    def __init__(self):
        # token_hash -> record dict
        self._store = {}
    
    def create(self, user_id: int, token_hash: str, expires_at):
        rec = {
            "user_id": user_id,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "revoked": False,
            "created_at": datetime.utcnow(),
            "replaced_by": None
        }
        self._store[token_hash] = rec
        return type("R", (), rec)
    
    def find_by_hash(self, token_hash: str):
        r = self._store.get(token_hash)
        return type("R", (), r) if r else None

    def revoke(self, token_hash: str):
        r = self._store.get(token_hash)
        if r:
            r["revoked"] = True
            return type("R", (), r)
        return None

    def revoke_all_for_user(self, user_id: int):
        for r in self._store.values():
            if r["user_id"] == user_id:
                r["revoked"] = True

    def rotate(self, old_hash: str, new_hash: str, new_expires_at):
        old = self._store.get(old_hash)
        if not old:
            return None, None
        old["revoked"] = True
        old["replaced_by"] = new_hash
        new_rec = {
            "user_id": old["user_id"],
            "token_hash": new_hash,
            "expires_at": new_expires_at,
            "revoked": False,
            "created_at": datetime.utcnow(),
            "replaced_by": None
        }
        self._store[new_hash] = new_rec
        return type("R", (), old), type("R", (), new_rec)