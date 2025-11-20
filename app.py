# app.py
from flask import Flask, redirect, url_for, session
from config import Config
from extensions import db

# 로그인 블루프린트
from blueprints.auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # DB 초기화
    db.init_app(app)

    # 블루프린트 등록
    app.register_blueprint(auth_bp)

    # 메인 라우트
    @app.route("/")
    def index():
        role = session.get("role")
        if role == "student":
            # 나중에 student 블루프린트 만들면 여기도 살릴 예정
            return "학생 홈 (student/home 라우트 구현 예정)"
        elif role == "prof":
            return "교수 홈 (prof/home 라우트 구현 예정)"
        elif role == "admin":
            return "관리자 홈 (admin/home 라우트 구현 예정)"
        else:
            return redirect(url_for("auth.login"))

    return app


if __name__ == "__main__":
    app = create_app()
    # 여기서 진짜 서버를 띄움
    app.run(debug=True)
