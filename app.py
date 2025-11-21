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

    from blueprints.student import student_bp
    from blueprints.prof import prof_bp
    from blueprints.admin import admin_bp

    app.register_blueprint(student_bp)
    app.register_blueprint(prof_bp)
    app.register_blueprint(admin_bp)

    # 메인 라우트
    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))
    
    return app


if __name__ == "__main__":
    app = create_app()
    # 여기서 진짜 서버를 띄움
    app.run(debug=True)
