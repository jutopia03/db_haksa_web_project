# blueprints/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from extensions import db
from models import Account

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    input_id = request.form.get("user_id")     # login.html에서 name="user_id"
    input_pw = request.form.get("password")

    # 1단계: 아이디로만 먼저 찾기 (디버깅용)
    user = Account.query.filter_by(login_id=input_id).first()

    if not user:
        flash("해당 아이디의 계정을 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    # 2단계: 비밀번호 확인
    if user.password != input_pw:
        flash("아이디 또는 비밀번호가 잘못되었습니다.")
        return redirect(url_for("auth.login"))

    # 3단계: 활성 여부 확인
    if not user.is_active:
        flash("비활성화된 계정입니다. 관리자에게 문의하세요.")
        return redirect(url_for("auth.login"))

    # 4단계: 로그인 성공 → 세션 저장
    session["account_id"] = user.account_id
    session["user_id"] = user.account_id
    session["login_id"] = user.login_id
    session["role"] = user.role
    

    # 역할에 따른 분기 (임시)
    if user.role == "student":
        return redirect(url_for("student.dashboard"))
    elif user.role == "professor":
        return "교수 로그인 성공! (prof/home 나중에 구현)"
    elif user.role == "admin":
        return "관리자 로그인 성공! (admin/home 나중에 구현)"
    else:
        flash("알 수 없는 권한입니다.")
        return redirect(url_for("auth.login"))
