from flask import Blueprint
from blueprints import login_required, role_required

prof_bp = Blueprint("prof", __name__, url_prefix="/prof")

@prof_bp.route("/home")
@login_required
@role_required("prof")
def home():
    return "교수 홈 화면 (나중에 구현)"
