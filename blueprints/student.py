from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from sqlalchemy import text
from extensions import db
from blueprints import login_required, role_required

student_bp = Blueprint("student", __name__, url_prefix="/student")


# 공통: 현재 로그인한 계정에서 student_id를 가져오는 헬퍼 함수
def _get_current_student_id():
    account_id = session.get("account_id")
    if account_id is None:
        return None

    sql = text(
        """
        SELECT student_id
        FROM account
        WHERE account_id = :account_id
          AND role = 'student'
        """
    )
    row = db.session.execute(sql, {"account_id": account_id}).fetchone()
    if row is None:
        return None
    # row.student_id 로 접근 가능
    return row.student_id


# 0) /student/home → /student/dashboard 로 보내기 (이미 있던 라우트 개선)
@student_bp.route("/home")
@login_required
@role_required("student")
def home():
    return redirect(url_for("student.dashboard"))


# 2-1. 학생 대시보드: /student/dashboard
@student_bp.route("/dashboard")
@login_required
@role_required("student")
def dashboard():
    """
    학생 대시보드
    - "○○학생님 환영합니다" 인삿말
    - 빠른 링크: 내 정보, 내 수강내역
    """
    student_id = _get_current_student_id()
    if student_id is None:
        flash("학생 정보가 없습니다. 관리자에게 문의하세요.")
        return redirect(url_for("auth.login"))

    # 학생 이름만 간단히 가져오기
    sql = text(
        """
        SELECT student_name
        FROM student
        WHERE student_id = :student_id
        """
    )
    row = db.session.execute(sql, {"student_id": student_id}).fetchone()
    if row is None:
        flash("학생 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    student_name = row.student_name

    return render_template(
        "student/dashboard.html",
        student_name=student_name,
    )


# 2-2. 내 정보 보기: /student/profile
@student_bp.route("/profile")
@login_required
@role_required("student")
def profile():
    """
    내 정보 보기
    - STUDENT + DEPARTMENT (+ 지도교수 추정) 조인
    """
    student_id = _get_current_student_id()
    if student_id is None:
        flash("학생 정보가 없습니다. 관리자에게 문의하세요.")
        return redirect(url_for("auth.login"))

    # 지도교수: 스키마에 'advisor_id'가 없어서,
    # 같은 학과의 첫 번째 교수(최소 professor_id)를 지도교수로 가정합니다. (추측입니다)
    # 수정해야함
    sql = text(
        """
        SELECT
            s.student_id,
            s.student_name,
            s.grade_level,
            s.phone,
            s.address,
            d.dept_name,
            s.dept_id,
            (
                SELECT p.professor_name
                FROM professor p
                WHERE p.dept_id = s.dept_id
                ORDER BY p.professor_id
                LIMIT 1
            ) AS advisor_name
        FROM student s
        LEFT JOIN department d ON s.dept_id = d.dept_id
        WHERE s.student_id = :student_id
        """
    )

    row = db.session.execute(sql, {"student_id": student_id}).fetchone()
    if row is None:
        flash("학생 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    student = {
        "name": row.student_name,
        "student_id": row.student_id,
        "department_name": row.dept_name,
        "advisor_name": row.advisor_name or "지도교수 미지정",
        "year": row.grade_level,
        "semester": 1,  # 학기 정보는 student 테이블에 없어서 임시로 1학기로 표시 (추측입니다)
        "phone": row.phone,
        "email": None,  # 스키마에 이메일 컬럼이 없어서 None 처리 (추측입니다)
        "address": row.address,
    }

    return render_template(
        "student/profile.html",
        student=student,
    )


# 2-3. 내 수강내역 / 성적 조회: /student/enrollments
@student_bp.route("/enrollments")
@login_required
@role_required("student")
def enrollments():
    """
    내 수강내역 / 성적 조회
    - 선택 필터: 연도(year), 학기(semester)
    - 테이블: 강좌번호, 강좌명, 담당교수, 학점, 성적
    """
    student_id = _get_current_student_id()
    if student_id is None:
        flash("학생 정보가 없습니다. 관리자에게 문의하세요.")
        return redirect(url_for("auth.login"))

    year = request.args.get("year", type=int)
    semester = request.args.get("semester", type=int)

    # 기본 WHERE 조건과 파라미터
    conditions = ["e.student_id = :student_id"]
    params = {"student_id": student_id}

    if year is not None:
        conditions.append("e.year = :year")
        params["year"] = year

    if semester is not None:
        conditions.append("e.semester = :semester")
        params["semester"] = semester

    where_clause = " AND ".join(conditions)

    sql = text(
        f"""
        SELECT
            c.course_id,
            c.course_name,
            c.credit,
            p.professor_name,
            e.grade,
            e.year,
            e.semester
        FROM enrollment e
        JOIN course c ON e.course_id = c.course_id
        LEFT JOIN professor p ON c.professor_id = p.professor_id
        WHERE {where_clause}
        ORDER BY e.year DESC, e.semester DESC, c.course_id
        """
    )

    rows = db.session.execute(sql, params).fetchall()

    enrollments_data = []
    for row in rows:
        enrollments_data.append(
            {
                "course_id": row.course_id,
                "course_name": row.course_name,
                "professor": row.professor_name,
                "credit": row.credit,
                "grade": row.grade,
                "year": row.year,
                "semester": row.semester,
            }
        )

    return render_template(
        "student/enrollments.html",
        enrollments=enrollments_data,
        selected_year=year,
        selected_semester=semester,
    )
