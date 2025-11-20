# blueprints/__init__.py
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("로그인이 필요합니다.")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("로그인이 필요합니다.")
                return redirect(url_for("auth.login"))

            if session.get("role") not in roles:
                flash("접근 권한이 없습니다.")
                return redirect(url_for("auth.login"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
