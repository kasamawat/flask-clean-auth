from functools import wraps
from flask import request, jsonify, g, current_app
import jwt

# Note: this decorator assumes that controllers wired 'security' globally or available
# For simplicity, we'll import SecurityWrapper lazily from app context

def require_auth(f):
    @wraps(f)
    def warpper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth:
            return jsonify({"error": "Authorization header missing"}), 401
        parts = auth.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "invalid Authorization header format. Use: Bearer <token>"}), 401
        
        token = parts[1]
        try:
            security = current_app.extensions.get("security")
            if not security:
                # fallback: decode with secret
                payload = jwt.decode(token, current_app.config.get("SECRET_KEY"), algorithms=['HS256'])
            else:
                payload = security.decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception:
            current_app.logger.exception("Error decoding token")
            return jsonify({"error": "Invalid token"}), 401
        print("payload",payload)
        user_id = payload.get("sub")
        if not user_id:
            return jsonify({"error": "Invalid token payload"}), 401
        
        # fetch user via repo attached to app (controller init_app registers user_repo in app.extensions)
        user_repo = current_app.extensions.get("user_repo")
        if not user_repo:
            return jsonify({"error": "Server misconfigured"}), 500
        user = user_repo.find_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 401
        
        g.current_user = user
        return f(*args, **kwargs)
    return warpper