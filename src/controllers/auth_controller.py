from flask import Blueprint, request, jsonify, current_app
from src.usecases.ports.repositories import UserRepositoryPort, RefreshTokenRepositoryPort
from src.utils.security_wrapper import SecurityWrapper

# contollers will expose init_app to accept dependencies

bp = Blueprint("auth", __name__)

def init_app(app, user_repo: UserRepositoryPort, refresh_repo: RefreshTokenRepositoryPort, security: SecurityWrapper):
    auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
    
    from src.usecases.auth.register import RegisterUser
    from src.usecases.auth.login import LoginUser
    from src.usecases.auth.refresh import RefreshTokenUsecase
    
    register_uc = RegisterUser(user_repo=user_repo, password_hasher=security)
    login_uc = LoginUser(user_repo=user_repo, refresh_repo=refresh_repo, password_hasher=security, jwt_provider=security, token_generator=security)
    refresh_uc = RefreshTokenUsecase(refresh_repo=refresh_repo, user_repo=user_repo, jwt_provider=security, token_generator=security)
    
    @auth_bp.route("/register", methods=["POST"])
    def register():
        body = request.json or {}
        email = body.get("email")
        password = body.get("password")
        try:
            res = register_uc.execute(email, password)
            return jsonify({"data": res}), 201
        except Exception as e:
            current_app.logger.exception(e)
            return jsonify({"error": str(e)}), 400
    
    @auth_bp.route("/login", methods=["POST"])
    def login():
        body = request.json or {}
        email = body.get("email")
        password = body.get("password")
        try:
            res = login_uc.execute(email, password)
            # convert expires to iso if datetime
            if isinstance(res.get("refresh_expires_at"), (object,)):
                res["refresh_expires_at"] = res["refresh_expires_at"].isoformat()
            return jsonify({"data": res}), 200
        except Exception as e:
            current_app.logger.exception(e)
            return jsonify({"error": str(e)}), 401
    
    @auth_bp.route("/refresh", methods=["POST"])
    def refresh():
        body = request.json or {}
        token = body.get("refresh_token")
        try:
            res = refresh_uc.execute(token)
            if isinstance(res.get("refresh_expires_at"), (object,)):
                res["refresh_expires_at"] = res["refresh_expires_at"].isoformat()
            return jsonify({"data": res}), 200
        except Exception as e:
            current_app.logger.exception(e)
            return jsonify({"error": str(e)}), 401
    
    @auth_bp.route("/logout", methods=["POST"])
    def logout():
        # simple: accept refresh_token to revoke, or use Authorization header to revoke all
        body = request.json or {}
        refresh_token = body.get("refresh_token")
        try:
            if refresh_token:
                refresh_repo.revoke(security.hash_refresh_token(refresh_token))
                return jsonify({"data": "logged out"}), 200
            auth = request.headers.get("Authorization","")
            if auth.startswith("Bearer "):
                token = auth.split(" ", 1)[1]
                try:
                    payload = security.decode_token(token)
                    user_id = payload.get("sub")
                    if user_id:
                        refresh_repo.revoke_all_for_user(user_id)
                        return jsonify({"data": "logged out all"}), 200
                except Exception:
                    pass
            return jsonify({"error": "missing refresh or auth"}), 400
        except Exception as e:
            current_app.logger.exception(e)
            return jsonify({"error": "internal"}), 500
    
    app.register_blueprint(auth_bp)