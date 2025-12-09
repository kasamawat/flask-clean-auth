from flask import Blueprint, jsonify, request, current_app, g
from src.utils.auth_decorator import require_auth
from src.usecases.ports.repositories import UserRepositoryPort, RefreshTokenRepositoryPort
from src.utils.security_wrapper import SecurityWrapper

bp = Blueprint("user", __name__)

def init_app(app, user_repo: UserRepositoryPort, refresh_repo: RefreshTokenRepositoryPort, security: SecurityWrapper):
    user_bp = Blueprint("user", __name__, url_prefix="/api/user")
    
    from src.usecases.auth.profile import ProfileUsecase
    profile_uc = ProfileUsecase(user_repo=user_repo, refresh_repo=refresh_repo, password_hasher=security)
    
    @user_bp.route("/profile", methods=["GET"])
    @require_auth
    def profile():
        try:
            res = profile_uc.get_profile(g.current_user.id)
            if isinstance(res.get("created_at"), (object,)):
                res["created_at"] = res["created_at"].isoformat()
            return jsonify({'data': res}), 200
        except Exception as e:
            current_app.logger.exception(e)
            return jsonify({"error": str(e)}), 404
    
    @user_bp.route("/profile", methods=["PATCH"])
    @require_auth
    def update_profile():
        body = request.json or {}
        email = body.get("email")
        password = body.get("password")
        try:
            res = profile_uc.update_profile(g.current_user.id, email=email, password=password)
            if isinstance(res.get("created_at"), (object,)):
                res["created_at"] = res["created_at"].isoformat()
            return jsonify({"data": res}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            current_app.logger.exception(e)
            return jsonify({"error": "internal"}), 500
    
    @user_bp.route("/profile", methods=["DELETE"])
    @require_auth
    def delete_profile():
        try:
            profile_uc.delete_account(g.current_user.id)
            return jsonify({"data": "account deleted"}), 200
        except Exception as e:
            current_app.logger.exception(e)
            return jsonify({"error": str(e)}), 400
    
    app.register_blueprint(user_bp)