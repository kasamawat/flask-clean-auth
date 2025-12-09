# 🔐 Flask Clean Architecture — Authentication Service

โปรเจคนี้เป็นระบบ Authentication ที่สร้างด้วย **Flask + Clean Architecture (Advanced Version)**  
รองรับ:

- Register / Login  
- JWT Access Token  
- Refresh Token Rotation (Security best practice)  
- User Profile CRUD  
- Unit Test (pytest) พร้อม Fake Dependencies  
- Clean Architecture พร้อมแยก Layer อย่างถูกต้อง  

โปรเจคนี้ออกแบบให้ **ทดสอบง่าย**, **แก้ไขง่าย**, และ **ขยายใหญ่ได้ในอนาคต** เช่นเพิ่ม OAuth2, RBAC หรือ Microservices  

---

# 🏛️ Clean Architecture Overview

```
                      +-----------------------------+
                      |       Presentation Layer    |
                      |   (Flask Controllers &      |
                      |    HTTP Adapters)           |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |     Application Layer       |
                      |         (Usecases)          |
                      |                             |
                      |  - RegisterUser             |
                      |  - LoginUser                |
                      |  - RefreshTokenUsecase      |
                      |  - ProfileUsecase           |
                      +--------------+--------------+
                                     |
                    (Input/Output Ports = Interfaces)
                                     |
                                     v
+---------------------------+     +-----------------------------+
|   Infrastructure Layer    |     |   Infrastructure Layer      |
| (Repositories / ORM / DB) |     |  (Security / JWT / Hashing) |
|---------------------------|     |-----------------------------|
| - SQLAlchemyUserRepo      |     | - SecurityWrapper           |
| - SQLAlchemyRefreshRepo   |     |   (hash, verify, jwt,       |
| - SQLAlchemy ORM Models   |     |    refresh token)           |
+---------------------------+     +-----------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |         Domain Layer         |
                      |  (Entities + Domain Errors)  |
                      |                               |
                      |  - User entity                |
                      |  - EmailAlreadyExists         |
                      |  - InvalidCredentials         |
                      |  - RefreshTokenError          |
                      +-------------------------------+
```

---

# 📁 Project Structure

```
src/
├─ domain/
│  ├─ entities/
│  │  └─ user.py
│  └─ errors.py
│
├─ usecases/
│  ├─ ports/
│  │  └─ repositories.py
│  └─ auth/
│     ├─ register.py
│     ├─ login.py
│     ├─ refresh.py
│     └─ profile.py
│
├─ adapters/
│  ├─ orm/
│  │  ├─ models.py
│  │  └─ mappers.py
│  └─ repositories/
│     ├─ sqlalchemy_user_repo.py
│     └─ sqlalchemy_refresh_repo.py
│
├─ frameworks/
│  ├─ db.py
│  └─ flask_app.py
│
├─ controllers/
│  ├─ auth_controller.py
│  └─ user_controller.py
│
└─ utils/
   ├─ security_wrapper.py
   └─ auth_decorator.py

tests/
├─ test_register_usecase.py
├─ test_login_usecase.py
├─ test_refresh_usecase.py
└─ test_profile_usecase.py
```

---

# 🚀 Getting Started

### 1) Install dependencies
```
pip install -r requirements.txt
```

### 2) Setup Flask environment
```
set FLASK_APP=app:create_app
```

### 3) Database Migration
```
flask db init
flask db migrate -m "initial"
flask db upgrade
```

### 4) Run server
```
python app.py
```

Server running at:
```
http://127.0.0.1:5000
```

---

# 🔐 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get access+refresh tokens |
| POST | `/auth/refresh` | Rotate refresh token + new access token |
| POST | `/auth/logout` | Revoke refresh token |

### User Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/user/me` | Get profile |
| PATCH | `/user/me` | Update profile |
| DELETE | `/user/me` | Delete account |

---

# 🧪 Unit Tests

### Run all tests:
```
pytest -q
```

Test coverage includes:

| Test File | Description |
|-----------|-------------|
| test_register_usecase.py | Register flow + duplicate email |
| test_login_usecase.py | Login success + invalid credentials |
| test_refresh_usecase.py | Refresh token rotation + revoke logic |
| test_profile_usecase.py | Profile read/update/delete |

---

# 🔧 Security

SecurityWrapper:
- Hash password (SHA256 → bcrypt)
- Verify password
- JWT encode/decode
- Refresh token rotation
- Refresh token hashing + expiry

---

# 🧩 Why Clean Architecture?

- ง่ายต่อการ test (business logic ไม่ผูก framework)
- เปลี่ยน DB ได้ ไม่ต้องแก้ usecase
- Controller บาง ทำแค่แปลง request/response
- ใช้ซ้ำกับ GraphQL / gRPC ได้ทันที
- Scale ดีมาก รองรับ microservices

---

# 📜 License

MIT License
