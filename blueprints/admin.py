from flask import Blueprint
from blueprints import login_required, role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/home")
@login_required
@role_required("admin")
def home():
    return "관리자 홈 화면 (나중에 구현)"
