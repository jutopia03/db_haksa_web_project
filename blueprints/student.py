from flask import Blueprint
from blueprints import login_required, role_required

student_bp = Blueprint("student", __name__, url_prefix="/student")

@student_bp.route("/home")
@login_required
@role_required("student")
def home():
    return "학생 홈 화면 (나중에 구현)"
