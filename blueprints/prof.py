# blueprints/prof.py

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from sqlalchemy import text
from extensions import db
from blueprints import login_required, role_required

prof_bp = Blueprint("prof", __name__, url_prefix="/prof")


# 공통: 현재 로그인한 계정에서 professor_id 가져오기
def _get_current_professor_id():
    account_id = session.get("account_id")
    if account_id is None:
        return None

    sql = text(
        """
        SELECT professor_id
        FROM account
        WHERE account_id = :account_id
          AND role = 'professor'
        """
    )
    row = db.session.execute(sql, {"account_id": account_id}).fetchone()
    if row is None:
        return None
    return row.professor_id


# 0) /prof/home → /prof/dashboard 로 보내기
@prof_bp.route("/home")
@login_required
@role_required("professor")  # account.role 값이 'professor' 이므로 이렇게 맞춰야 함
def home():
    return redirect(url_for("prof.dashboard"))


# 3-1. 교수 대시보드: /prof/dashboard
@prof_bp.route("/dashboard")
@login_required
@role_required("professor")
def dashboard():
    """
    교수 대시보드
    - "○○교수님 환영합니다"
    - 링크: 내 정보, 내 강좌 목록
    """
    professor_id = _get_current_professor_id()
    if professor_id is None:
        flash("교수 정보를 찾을 수 없습니다. 관리자에게 문의하세요.")
        return redirect(url_for("auth.login"))

    sql = text(
        """
        SELECT professor_name
        FROM professor
        WHERE professor_id = :professor_id
        """
    )
    row = db.session.execute(sql, {"professor_id": professor_id}).fetchone()
    if row is None:
        flash("교수 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    professor_name = row.professor_name

    return render_template(
        "prof/dashboard.html",
        professor_name=professor_name,
    )


# 3-2. 내 정보 보기: /prof/profile
@prof_bp.route("/profile")
@login_required
@role_required("professor")
def profile():
    """
    교수 프로필
    - PROFESSOR + DEPARTMENT 조인
    """
    professor_id = _get_current_professor_id()
    if professor_id is None:
        flash("교수 정보를 찾을 수 없습니다. 관리자에게 문의하세요.")
        return redirect(url_for("auth.login"))

    sql = text(
        """
        SELECT
            p.professor_id,
            p.professor_name,
            p.position,
            p.phone,
            p.office,
            d.dept_name,
            d.office AS dept_office,
            d.phone  AS dept_phone
        FROM professor p
        LEFT JOIN department d ON p.dept_id = d.dept_id
        WHERE p.professor_id = :professor_id
        """
    )
    row = db.session.execute(sql, {"professor_id": professor_id}).fetchone()
    if row is None:
        flash("교수 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    professor = {
        "professor_id": row.professor_id,
        "name": row.professor_name,
        "position": row.position,
        "department_name": row.dept_name,
        "phone": row.phone,
        "office": row.office,
        # 스키마에 이메일/주소 컬럼이 없어서 임시로 None 처리
        "email": None,
        "address": None,
        "dept_office": row.dept_office,
        "dept_phone": row.dept_phone,
    }

    return render_template("prof/profile.html", professor=professor)


# 3-3. 담당 강좌 목록: /prof/courses
@prof_bp.route("/courses")
@login_required
@role_required("professor")
def courses():
    """
    담당 강좌 목록
    - 강좌번호, 강좌명, 개설학과, 강의시간(hours), 강의실
    """
    professor_id = _get_current_professor_id()
    if professor_id is None:
        flash("교수 정보를 찾을 수 없습니다. 관리자에게 문의하세요.")
        return redirect(url_for("auth.login"))

    sql = text(
        """
        SELECT
            c.course_id,
            c.course_name,
            c.credit,
            c.hours,
            c.classroom,
            d.dept_name
        FROM course c
        LEFT JOIN department d ON c.professor_id IS NOT NULL
            AND d.dept_id = (
                SELECT p.dept_id
                FROM professor p
                WHERE p.professor_id = c.professor_id
            )
        WHERE c.professor_id = :professor_id
        ORDER BY c.course_id
        """
    )
    rows = db.session.execute(sql, {"professor_id": professor_id}).fetchall()

    courses_data = []
    for row in rows:
        courses_data.append(
            {
                "course_id": row.course_id,
                "course_name": row.course_name,
                "dept_name": row.dept_name,
                "hours": row.hours,
                "classroom": row.classroom,
            }
        )

    return render_template("prof/courses.html", courses=courses_data)


# 3-4. 강좌별 수강 학생 목록: /prof/courses/<course_id>/students
@prof_bp.route("/courses/<int:course_id>/students")
@login_required
@role_required("professor")
def course_students(course_id):
    """
    강좌별 수강 학생 목록
    - 학생번호, 이름, 학과, 학년, 성적
    """
    professor_id = _get_current_professor_id()
    if professor_id is None:
        flash("교수 정보를 찾을 수 없습니다. 관리자에게 문의하세요.")
        return redirect(url_for("auth.login"))

    # (선택) 이 강좌가 현재 교수의 강좌인지 확인
    course_sql = text(
        """
        SELECT
            c.course_id,
            c.course_name,
            c.professor_id
        FROM course c
        WHERE c.course_id = :course_id
        """
    )
    course_row = db.session.execute(course_sql, {"course_id": course_id}).fetchone()
    if course_row is None:
        flash("강좌 정보를 찾을 수 없습니다.")
        return redirect(url_for("prof.courses"))

    if course_row.professor_id != professor_id:
        flash("이 강좌에 대한 접근 권한이 없습니다.")
        return redirect(url_for("prof.courses"))

    # 수강 학생 목록 조회
    sql = text(
        """
        SELECT
            s.student_id,
            s.student_name,
            s.grade_level,
            d.dept_name,
            e.grade
        FROM enrollment e
        JOIN student s ON e.student_id = s.student_id
        LEFT JOIN department d ON s.dept_id = d.dept_id
        WHERE e.course_id = :course_id
        ORDER BY s.student_id
        """
    )
    rows = db.session.execute(sql, {"course_id": course_id}).fetchall()

    students = []
    for row in rows:
        students.append(
            {
                "student_id": row.student_id,
                "student_name": row.student_name,
                "dept_name": row.dept_name,
                "grade_level": row.grade_level,
                "grade": row.grade,
            }
        )

    return render_template(
        "prof/course_students.html",
        course_id=course_row.course_id,
        course_name=course_row.course_name,
        students=students,
    )
