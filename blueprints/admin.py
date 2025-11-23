from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from sqlalchemy import text
from extensions import db
from blueprints import login_required, role_required
from sqlalchemy.exc import IntegrityError

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# 공통: 현재 로그인한 계정에서 admin_id 가져오기
def _get_current_admin_id():
    account_id = session.get("account_id")
    if account_id is None:
        return None
    
    sql = text(
        """
        SELECT account_id
        FROM account
        WHERE account_id = :account_id
           AND role = 'admin'
        """
    )
    row = db.session.execute(sql, {"account_id": account_id}).fetchone()
    if row is None:
        return None
    return row.accout_id

# 0) /admin/home → /admin/dashboard 로 보내기
@admin_bp.route("/home")
@login_required
@role_required("admin")
def home():
    return redirect(url_for("admin.dashboard"))

# 4-1. 어드민 대시보드: /admin/dashboard
@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def admin_dashboard():
    
    student_count = db.session.execute(text("SELECT COUNT(*) FROM student")).scalar()
    professor_count = db.session.execute(text("SELECT COUNT(*) FROM professor")).scalar()
    course_count = db.session.execute(text("SELECT COUNT(*) FROM course")).scalar()
    enrollment_count = db.session.execute(text("SELECT COUNT(*) FROM enrollment")).scalar()

    return render_template(
        "admin/dashboard.html",
        student_count=student_count,
        professor_count=professor_count,
        course_count=course_count,
        enrollment_count=enrollment_count,
    )

# 4-2. 학생 관리: admin/students
@admin_bp.route("/students")
@login_required
@role_required("admin")
def students():
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    search_name = request.args.get("name", type=str, default="").strip()
    search_student_id = request.args.get("student_id", type=str, default="").strip()
    search_dept_id = request.args.get("dept_id", type=str, default="").strip()

    base_sql = """
        SELECT
            s.student_id,
            s.student_name,
            d.dept_name,
            s.grade_level,
            s.phone
        FROM student s
        INNER JOIN department d USING(dept_id)
        WHERE 1 = 1
    """

    params = {}

    if search_name:
        base_sql += " AND s.student_name LIKE :name"
        params["name"] = f"%{search_name}%"

    if search_student_id:
        base_sql += " AND s.student_id = :student_id"
        try:
            params["student_id"] = int(search_student_id)
        except ValueError:
            params["student_id"] = -1

    if search_dept_id:
        base_sql += " AND s.dept_id = :dept_id"
        params["dept_id"] = int(search_dept_id)

    base_sql += " ORDER BY s.student_id"

    sql = text(base_sql)
    rows = db.session.execute(sql, params).fetchall()

    students = [
        {
            "student_id": r.student_id,
            "student_name": r.student_name,
            "dept_name": r.dept_name,
            "grade_level": r.grade_level,
            "phone": r.phone,
        }
        for r in rows
    ]

    dept_sql = text("SELECT dept_id, dept_name FROM department ORDER BY dept_name")
    depts = db.session.execute(dept_sql).fetchall()

    return render_template(
        "admin/students.html",
        students=students,
        depts=depts,
        search_name=search_name,
        search_student_id=search_student_id,
        search_dept_id=search_dept_id,
    )

# 4-2-1. 학생 관리 (추가): admin/students/new
@admin_bp.route("/students/new", methods = ["GET", "POST"])
@login_required
@role_required("admin")
def students_new():
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))
    
    if request.method == "POST":
        student_id = request.form.get("student_id")
        student_name = request.form.get("student_name")
        dept_id = request.form.get("dept_id")
        grade_level = request.form.get("grade_level")
        phone = request.form.get("phone")

        if not student_id or not student_name or not dept_id:
            flash("학번, 이름, 학과는 필수입니다.")
            return redirect(url_for("admin.student_new"))
        
        insert_sql = text(
            """
            INSERT INTO student (
                student_id,
                student_name,
                dept_id,
                grade_level,
                phone
            ) VALUES (
                :student_id,
                :student_name,
                :dept_id,
                :grade_level,
                :phone
            )
            """
        )

        db.session.execute(
            insert_sql,
            {
                "student_id": student_id,
                "student_name": student_name,
                "dept_id": dept_id,
                "grade_level": grade_level,
                "phone": phone,
            },
        )
        db.session.commit()

        flash("학생이 성공적으로 등록되었습니다.")
        return redirect(url_for("admin.students"))
    
    dept_sql = text(
        """
        SELECT dept_id, dept_name
        FROM department
        ORDER BY dept_name
        """
    )
    depts = db.session.execute(dept_sql).fetchall()

    return render_template("admin/students_new.html", depts=depts)

# 4-2-2. 학생 관리 (수정): admin/students/<id>/edit
@admin_bp.route("/students/<student_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def student_edit(student_id):
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    student_sql = text("""
        SELECT *
        FROM student
        WHERE student_id = :student_id
    """)
    student = db.session.execute(student_sql, {"student_id": student_id}).fetchone()

    if student is None:
        flash("학생 정보를 찾을 수 없습니다.")
        return redirect(url_for("admin.students"))

    if request.method == "POST":
        student_name = request.form.get("student_name")
        gender = request.form.get("gender")
        birth_date = request.form.get("birth_date")
        dept_id = request.form.get("dept_id")
        grade_level = request.form.get("grade_level")
        phone = request.form.get("phone")
        address = request.form.get("address")

        update_sql = text("""
            UPDATE student
            SET student_name = :student_name,
                gender = :gender,
                birth_date = :birth_date,
                dept_id = :dept_id,
                grade_level = :grade_level,
                phone = :phone,
                address = :address
            WHERE student_id = :student_id
        """)

        db.session.execute(update_sql, {
            "student_id": student_id,
            "student_name": student_name,
            "gender": gender,
            "birth_date": birth_date,
            "dept_id": dept_id,
            "grade_level": grade_level,
            "phone": phone,
            "address": address,
        })
        db.session.commit()

        flash("학생 정보가 수정되었습니다.")
        return redirect(url_for("admin.students"))

    dept_sql = text("SELECT dept_id, dept_name FROM department ORDER BY dept_name")
    depts = db.session.execute(dept_sql).fetchall()

    return render_template("admin/student_edit.html", student=student, depts=depts)

# 4-2-3. 학생 관리 (삭제): admin/students/<id>/delete
@admin_bp.route("/students/<student_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def student_delete(student_id):
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    delete_sql = text(
        """
        DELETE FROM student
        WHERE student_id = :student_id
        """
    )

    db.session.execute(delete_sql, {"student_id": student_id})
    db.session.commit()

    flash("학생이 삭제되었습니다.")
    return redirect(url_for("admin.students"))

# 4-2-4. 학생 관리 (상세 보기): admin/students/<id>
@admin_bp.route("/students/<student_id>")
@login_required
@role_required("admin")
def student_detail(student_id):
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    student_sql = text("""
        SELECT s.*, d.dept_name
        FROM student s
        INNER JOIN department d ON s.dept_id = d.dept_id
        WHERE s.student_id = :student_id
    """)
    student = db.session.execute(student_sql, {"student_id": student_id}).fetchone()

    if student is None:
        flash("학생 정보를 찾을 수 없습니다.")
        return redirect(url_for("admin.students"))

    enrollment_sql = text("""
        SELECT
            c.course_id,
            c.course_name,
            c.credit,
            p.professor_name,
            e.grade,
            e.year,
            e.semester
        FROM enrollment e
        INNER JOIN course c ON e.course_id = c.course_id
        INNER JOIN professor p ON c.professor_id = p.professor_id
        WHERE e.student_id = :student_id
        ORDER BY e.year DESC, e.semester DESC
    """)
    courses = db.session.execute(enrollment_sql, {"student_id": student_id}).fetchall()

    return render_template(
        "admin/student_detail.html",
        student=student,
        courses=courses
    )

# 4-3. 교수 관리: admin/professors
@admin_bp.route("/professors")
@login_required
@role_required("admin")
def professors():
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    sql = text("""
        SELECT
            p.professor_id,
            p.professor_name,
            d.dept_name,
            p.position,
            p.phone
        FROM professor p
        LEFT JOIN department d ON p.dept_id = d.dept_id
        ORDER BY p.professor_id
    """)
    rows = db.session.execute(sql).fetchall()

    professors = [
        {
            "professor_id": r.professor_id,
            "professor_name": r.professor_name,
            "dept_name": r.dept_name,
            "position": r.position,
            "phone": r.phone,
        }
        for r in rows
    ]

    return render_template("admin/professors.html", professors=professors)

# 4-3-1. 교수 관리 (등록): admin/professors/new
@admin_bp.route("/professors/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def professor_new():
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        professor_id = request.form.get("professor_id")
        professor_name = request.form.get("professor_name")
        dept_id = request.form.get("dept_id")
        position = request.form.get("position")
        phone = request.form.get("phone")
        office = request.form.get("office")
        hire_date = request.form.get("hire_date")  # 'YYYY-MM-DD' 문자열

        if not professor_id or not professor_name or not dept_id:
            flash("교수번호, 이름, 학과는 필수입니다.")
            return redirect(url_for("admin.professor_new"))

        insert_sql = text("""
            INSERT INTO professor (
                professor_id,
                professor_name,
                dept_id,
                position,
                phone,
                office,
                hire_date
            ) VALUES (
                :professor_id,
                :professor_name,
                :dept_id,
                :position,
                :phone,
                :office,
                :hire_date
            )
        """)

        db.session.execute(insert_sql, {
            "professor_id": professor_id,
            "professor_name": professor_name,
            "dept_id": dept_id,
            "position": position,
            "phone": phone,
            "office": office,
            "hire_date": hire_date if hire_date else None,
        })
        db.session.commit()

        flash("교수가 성공적으로 등록되었습니다.")
        return redirect(url_for("admin.professors"))

    # 학과 드롭다운용
    dept_sql = text("SELECT dept_id, dept_name FROM department ORDER BY dept_name")
    depts = db.session.execute(dept_sql).fetchall()

    return render_template("admin/professor_new.html", depts=depts)

# 4-3-2. 교수 관리 (수정): admin/professors/<id>/edit
@admin_bp.route("/professors/<int:professor_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def professor_edit(professor_id):
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    prof_sql = text("""
        SELECT *
        FROM professor
        WHERE professor_id = :professor_id
    """)
    professor = db.session.execute(prof_sql, {"professor_id": professor_id}).fetchone()

    if professor is None:
        flash("교수 정보를 찾을 수 없습니다.")
        return redirect(url_for("admin.professors"))

    if request.method == "POST":
        professor_name = request.form.get("professor_name")
        dept_id = request.form.get("dept_id")
        position = request.form.get("position")
        phone = request.form.get("phone")
        office = request.form.get("office")
        hire_date = request.form.get("hire_date")

        update_sql = text("""
            UPDATE professor
            SET professor_name = :professor_name,
                dept_id        = :dept_id,
                position       = :position,
                phone          = :phone,
                office         = :office,
                hire_date      = :hire_date
            WHERE professor_id = :professor_id
        """)

        db.session.execute(update_sql, {
            "professor_id": professor_id,
            "professor_name": professor_name,
            "dept_id": dept_id,
            "position": position,
            "phone": phone,
            "office": office,
            "hire_date": hire_date if hire_date else None,
        })
        db.session.commit()

        flash("교수 정보가 수정되었습니다.")
        return redirect(url_for("admin.professors"))

    # 학과 목록
    dept_sql = text("SELECT dept_id, dept_name FROM department ORDER BY dept_name")
    depts = db.session.execute(dept_sql).fetchall()

    return render_template("admin/professor_edit.html", professor=professor, depts=depts)

# 4-3-3. 교수 관리 (삭제): admin/professors/<id>/delete
@admin_bp.route("/professors/<int:professor_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def professor_delete(professor_id):
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    delete_sql = text("""
        DELETE FROM professor
        WHERE professor_id = :professor_id
    """)

    try:
        db.session.execute(delete_sql, {"professor_id": professor_id})
        db.session.commit()
        flash("교수가 삭제되었습니다.")
    except IntegrityError:
        db.session.rollback()
        flash("해당 교수는 강좌 또는 계정에 연결되어 있어 삭제할 수 없습니다.")

    return redirect(url_for("admin.professors"))

# 4-3-4. 교수 관리 (상세): admin/professors/<id>
@admin_bp.route("/professors/<int:professor_id>")
@login_required
@role_required("admin")
def professor_detail(professor_id):
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    prof_sql = text("""
        SELECT p.*, d.dept_name
        FROM professor p
        LEFT JOIN department d ON p.dept_id = d.dept_id
        WHERE p.professor_id = :professor_id
    """)
    professor = db.session.execute(prof_sql, {"professor_id": professor_id}).fetchone()

    if professor is None:
        flash("교수 정보를 찾을 수 없습니다.")
        return redirect(url_for("admin.professors"))

    course_sql = text("""
        SELECT
            c.course_id,
            c.course_name,
            c.credit,
            c.classroom,
            c.hours
        FROM course c
        WHERE c.professor_id = :professor_id
        ORDER BY c.course_id
    """)
    courses = db.session.execute(course_sql, {"professor_id": professor_id}).fetchall()

    return render_template(
        "admin/professor_detail.html",
        professor=professor,
        courses=courses
    )

# 4-4. 학과 관리: admin/departments
@admin_bp.route("/departments")
@login_required
@role_required("admin")
def departments():
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    sql = text("""
        SELECT
            dept_id,
            dept_name,
            phone
        FROM department
        ORDER BY dept_id
    """)

    rows = db.session.execute(sql).fetchall()

    departments = [
        {
            "dept_id": r.dept_id,
            "dept_name": r.dept_name,
            "phone": r.phone,
        }
        for r in rows
    ]

    return render_template("admin/departments.html", departments=departments)

# 4-4-1. 학과 관리 (등록): admin/departments/new
@admin_bp.route("/departments/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def department_new():
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        dept_name = request.form.get("dept_name")
        phone = request.form.get("phone")

        if not dept_name:
            flash("학과명은 반드시 입력해야 합니다.")
            return redirect(url_for("admin.department_new"))

        insert_sql = text("""
            INSERT INTO department (dept_name, phone)
            VALUES (:dept_name, :phone)
        """)

        db.session.execute(insert_sql, {
            "dept_name": dept_name,
            "phone": phone,
        })
        db.session.commit()

        flash("학과가 등록되었습니다.")
        return redirect(url_for("admin.departments"))

    return render_template("admin/department_new.html")

# 4-4-2. 학과 관리 (수정): admin/departments/<id>/edit
@admin_bp.route("/departments/<int:dept_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def department_edit(dept_id):
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    dept_sql = text("""
        SELECT *
        FROM department
        WHERE dept_id = :dept_id
    """)
    dept = db.session.execute(dept_sql, {"dept_id": dept_id}).fetchone()

    if dept is None:
        flash("학과 정보를 찾을 수 없습니다.")
        return redirect(url_for("admin.departments"))

    if request.method == "POST":
        dept_name = request.form.get("dept_name")
        phone = request.form.get("phone")

        update_sql = text("""
            UPDATE department
            SET dept_name = :dept_name,
                phone     = :phone
            WHERE dept_id = :dept_id
        """)

        db.session.execute(update_sql, {
            "dept_id": dept_id,
            "dept_name": dept_name,
            "phone": phone,
        })
        db.session.commit()

        flash("학과 정보가 수정되었습니다.")
        return redirect(url_for("admin.departments"))

    return render_template("admin/department_edit.html", dept=dept)

# 4-4-3. 학과 관리 (삭제): admin/departments/<id>/delete
@admin_bp.route("/departments/<int:dept_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def department_delete(dept_id):
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    delete_sql = text("""
        DELETE FROM department
        WHERE dept_id = :dept_id
    """)

    try:
        db.session.execute(delete_sql, {"dept_id": dept_id})
        db.session.commit()
        flash("학과가 삭제되었습니다.")
    except Exception:
        db.session.rollback()
        flash("이미 학생 또는 교수가 소속된 학과는 삭제할 수 없습니다.")

    return redirect(url_for("admin.departments"))

# 4-5. 강좌 관리: admin/courses
@admin_bp.route("/courses")
@login_required
@role_required("admin")
def courses():
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    sql = text(
        """
        SELECT
            c.course_id,
            c.course_name,
            d.dept_name,
            p.professor_name,
            c.credit,
            c.hours,
            c.classroom
        FROM course c
        LEFT JOIN professor p ON c.professor_id = p.professor_id
        LEFT JOIN department d ON p.dept_id = d.dept_id
        ORDER BY c.course_id
        """
    )
    rows = db.session.execute(sql).fetchall()

    courses = [
        {
            "course_id": r.course_id,
            "course_name": r.course_name,
            "dept_name": r.dept_name,
            "professor_name": r.professor_name,
            "credit": r.credit,
            "hours": r.hours,
            "classroom": r.classroom,
        }
        for r in rows
    ]

    return render_template("admin/courses.html", courses=courses)

# 4-5-1. 강좌 관리 (등록): /admin/courses/new
@admin_bp.route("/courses/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def course_new():
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        course_name = request.form.get("course_name")
        dept_id = request.form.get("dept_id")          # UI용, DB에는 저장 안 함
        professor_id = request.form.get("professor_id")
        credit = request.form.get("credit")
        hours = request.form.get("hours")
        classroom = request.form.get("classroom")

        if not course_name or not professor_id:
            flash("강좌명과 담당 교수는 필수입니다.")
            return redirect(url_for("admin.course_new"))

        insert_sql = text(
            """
            INSERT INTO course (
                course_name,
                credit,
                classroom,
                hours,
                professor_id
            ) VALUES (
                :course_name,
                :credit,
                :classroom,
                :hours,
                :professor_id
            )
            """
        )

        db.session.execute(
            insert_sql,
            {
                "course_name": course_name,
                "credit": int(credit) if credit else None,
                "classroom": classroom,
                "hours": int(hours) if hours else None,
                "professor_id": int(professor_id),
            },
        )
        db.session.commit()

        flash("강좌가 성공적으로 등록되었습니다.")
        return redirect(url_for("admin.courses"))

    # 학과/교수 드롭다운용 데이터
    dept_sql = text(
        """
        SELECT dept_id, dept_name
        FROM department
        ORDER BY dept_name
        """
    )
    depts = db.session.execute(dept_sql).fetchall()

    prof_sql = text(
        """
        SELECT professor_id, professor_name, dept_id
        FROM professor
        ORDER BY professor_name
        """
    )
    professors = db.session.execute(prof_sql).fetchall()

    return render_template(
        "admin/course_new.html",
        depts=depts,
        professors=professors,
    )

# 4-5-2. 강좌 관리 (수정): /admin/courses/<id>/edit
@admin_bp.route("/courses/<int:course_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def course_edit(course_id):
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    # 기존 강좌 정보 조회 (담당 교수의 학과까지 가져오기)
    course_sql = text(
        """
        SELECT c.*, p.dept_id AS professor_dept_id
        FROM course c
        LEFT JOIN professor p ON c.professor_id = p.professor_id
        WHERE c.course_id = :course_id
        """
    )
    course = db.session.execute(course_sql, {"course_id": course_id}).fetchone()

    if course is None:
        flash("강좌 정보를 찾을 수 없습니다.")
        return redirect(url_for("admin.courses"))

    if request.method == "POST":
        course_name = request.form.get("course_name")
        dept_id = request.form.get("dept_id")          # UI용
        professor_id = request.form.get("professor_id")
        credit = request.form.get("credit")
        hours = request.form.get("hours")
        classroom = request.form.get("classroom")

        update_sql = text(
            """
            UPDATE course
            SET course_name  = :course_name,
                credit       = :credit,
                classroom    = :classroom,
                hours        = :hours,
                professor_id = :professor_id
            WHERE course_id  = :course_id
            """
        )

        db.session.execute(
            update_sql,
            {
                "course_id": course_id,
                "course_name": course_name,
                "credit": int(credit) if credit else None,
                "classroom": classroom,
                "hours": int(hours) if hours else None,
                "professor_id": int(professor_id) if professor_id else None,
            },
        )
        db.session.commit()

        flash("강좌 정보가 수정되었습니다.")
        return redirect(url_for("admin.courses"))

    # 학과/교수 목록 조회
    dept_sql = text(
        """
        SELECT dept_id, dept_name
        FROM department
        ORDER BY dept_name
        """
    )
    depts = db.session.execute(dept_sql).fetchall()

    prof_sql = text(
        """
        SELECT professor_id, professor_name, dept_id
        FROM professor
        ORDER BY professor_name
        """
    )
    professors = db.session.execute(prof_sql).fetchall()

    return render_template(
        "admin/course_edit.html",
        course=course,
        depts=depts,
        professors=professors,
    )

# 4-5-3. 강좌 관리 (삭제): /admin/courses/<id>/delete
@admin_bp.route("/courses/<int:course_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def course_delete(course_id):
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 정보를 찾을 수 없습니다.")
        return redirect(url_for("auth.login"))

    delete_sql = text(
        """
        DELETE FROM course
        WHERE course_id = :course_id
        """
    )

    try:
        db.session.execute(delete_sql, {"course_id": course_id})
        db.session.commit()
        flash("강좌가 삭제되었습니다.")
    except Exception:
        db.session.rollback()
        flash("해당 강좌는 수강내역 등과 연결되어 있어 삭제할 수 없습니다.")

    return redirect(url_for("admin.courses"))

# 4-6. 수강 내역 관리 : admin/enrollments
@admin_bp.route("/enrollments")
@login_required
@role_required("admin")
def enrollments():
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 인증 실패")
        return redirect(url_for("auth.login"))

    search_year = request.args.get("year", type=str, default="").strip()
    search_semester = request.args.get("semester", type=str, default="").strip()
    search_student_id = request.args.get("student_id", type=str, default="").strip()
    search_course_id = request.args.get("course_id", type=str, default="").strip()

    base_sql = """
        SELECT
            e.enrollment_id,
            e.year,
            e.semester,
            s.student_id,
            s.student_name,
            c.course_id,
            c.course_name,
            e.grade
        FROM enrollment e
        INNER JOIN student s ON e.student_id = s.student_id
        INNER JOIN course  c ON e.course_id = c.course_id
        WHERE 1 = 1
    """

    params = {}

    if search_year:
        base_sql += " AND e.year = :year"
        params["year"] = int(search_year)

    if search_semester:
        base_sql += " AND e.semester = :semester"
        params["semester"] = int(search_semester)

    if search_student_id:
        base_sql += " AND e.student_id = :student_id"
        try:
            params["student_id"] = int(search_student_id)
        except ValueError:
            params["student_id"] = -1  # 잘못된 값이면 결과 안 나오게

    if search_course_id:
        base_sql += " AND e.course_id = :course_id"
        try:
            params["course_id"] = int(search_course_id)
        except ValueError:
            params["course_id"] = -1

    base_sql += " ORDER BY e.year DESC, e.semester DESC, s.student_id, c.course_id"

    rows = db.session.execute(text(base_sql), params).fetchall()

    enrollments = [
        {
            "enrollment_id": r.enrollment_id,
            "year": r.year,
            "semester": r.semester,
            "student_id": r.student_id,
            "student_name": r.student_name,
            "course_id": r.course_id,
            "course_name": r.course_name,
            "grade": r.grade,
        }
        for r in rows
    ]

    return render_template(
        "admin/enrollments.html",
        enrollments=enrollments,
        search_year=search_year,
        search_semester=search_semester,
        search_student_id=search_student_id,
        search_course_id=search_course_id,
    )

# 4-6-1. 수강내역 관리 (등록): /admin/enrollments/new
@admin_bp.route("/enrollments/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def enrollment_new():
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 인증 실패")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        student_id = request.form.get("student_id")
        course_id = request.form.get("course_id")
        year = request.form.get("year")
        semester = request.form.get("semester")
        grade = request.form.get("grade")

        if not student_id or not course_id or not year or not semester:
            flash("학생, 강좌, 연도, 학기는 필수입니다.")
            return redirect(url_for("admin.enrollment_new"))
 
        insert_sql = text(
            """
            INSERT INTO enrollment (
                enrollment_id,
                student_id,
                course_id,
                year,
                semester,
                grade
            ) VALUES (
                (SELECT IFNULL(MAX(enrollment_id), 0) + 1 FROM enrollment),
                :student_id,
                :course_id,
                :year,
                :semester,
                :grade
            )
            """
        )

        db.session.execute(
            insert_sql,
            {
                "student_id": int(student_id),
                "course_id": int(course_id),
                "year": int(year),
                "semester": int(semester),
                "grade": grade,
            },
        )
        db.session.commit()

        flash("수강내역이 등록되었습니다.")
        return redirect(url_for("admin.enrollments"))

    students = db.session.execute(
        text("SELECT student_id, student_name FROM student ORDER BY student_name")
    ).fetchall()

    courses = db.session.execute(
        text("SELECT course_id, course_name FROM course ORDER BY course_name")
    ).fetchall()

    return render_template(
        "admin/enrollment_new.html",
        students=students,
        courses=courses,
    )

# 4-6-2. 수강내역 관리 (수정): /admin/enrollments/<id>/edit
@admin_bp.route("/enrollments/<int:enrollment_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def enrollment_edit(enrollment_id):
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 인증 실패")
        return redirect(url_for("auth.login"))

    # 기존 수강내역 조회
    row = db.session.execute(
        text(
            """
            SELECT *
            FROM enrollment
            WHERE enrollment_id = :enrollment_id
            """
        ),
        {"enrollment_id": enrollment_id},
    ).fetchone()

    if row is None:
        flash("수강내역을 찾을 수 없습니다.")
        return redirect(url_for("admin.enrollments"))

    if request.method == "POST":
        student_id = request.form.get("student_id")
        course_id = request.form.get("course_id")
        year = request.form.get("year")
        semester = request.form.get("semester")
        grade = request.form.get("grade")

        update_sql = text(
            """
            UPDATE enrollment
            SET student_id = :student_id,
                course_id  = :course_id,
                year       = :year,
                semester   = :semester,
                grade      = :grade
            WHERE enrollment_id = :enrollment_id
            """
        )

        db.session.execute(
            update_sql,
            {
                "enrollment_id": enrollment_id,
                "student_id": int(student_id),
                "course_id": int(course_id),
                "year": int(year),
                "semester": int(semester),
                "grade": grade,
            },
        )
        db.session.commit()

        flash("수강내역이 수정되었습니다.")
        return redirect(url_for("admin.enrollments"))

    # 드롭다운용 학생 / 강좌 목록
    students = db.session.execute(
        text("SELECT student_id, student_name FROM student ORDER BY student_name")
    ).fetchall()

    courses = db.session.execute(
        text("SELECT course_id, course_name FROM course ORDER BY course_name")
    ).fetchall()

    return render_template(
        "admin/enrollment_edit.html",
        enrollment=row,
        students=students,
        courses=courses,
    )

# 4-6-3. 수강내역 관리 (삭제): /admin/enrollments/<id>/delete
@admin_bp.route("/enrollments/<int:enrollment_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def enrollment_delete(enrollment_id):
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 인증 실패")
        return redirect(url_for("auth.login"))

    delete_sql = text(
        """
        DELETE FROM enrollment
        WHERE enrollment_id = :enrollment_id
        """
    )

    db.session.execute(delete_sql, {"enrollment_id": enrollment_id})
    db.session.commit()

    flash("수강내역이 삭제되었습니다.")
    return redirect(url_for("admin.enrollments"))
  
# 4.7. 계정 관리: admin/accounts
@admin_bp.route("/accounts")
@login_required
@role_required("admin")
def accounts():
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 인증 실패")
        return redirect(url_for("auth.login"))

    sql = text("""
        SELECT
            a.account_id,
            a.login_id,
            a.role,
            a.student_id,
            s.student_name,
            a.professor_id,
            p.professor_name,
            a.is_active
        FROM account a
        LEFT JOIN student s ON a.student_id = s.student_id
        LEFT JOIN professor p ON a.professor_id = p.professor_id
        ORDER BY a.account_id
    """)
    rows = db.session.execute(sql).fetchall()

    accounts = [
        {
            "account_id": r.account_id,
            "login_id": r.login_id,
            "role": r.role,
            "student_id": r.student_id,
            "student_name": r.student_name,
            "professor_id": r.professor_id,
            "professor_name": r.professor_name,
            "is_active": r.is_active,
        }
        for r in rows
    ]

    return render_template("admin/accounts.html", accounts=accounts)

# 4-7-1. 계정 관리 (등록): /admin/accounts/new
@admin_bp.route("/accounts/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def account_new():
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 인증 실패")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        login_id = request.form.get("login_id")
        temp_password = request.form.get("password")   # 임시 비밀번호
        role = request.form.get("role")                # admin / student / professor
        student_id = request.form.get("student_id")
        professor_id = request.form.get("professor_id")
        is_active = request.form.get("is_active", "1")  # "1" or "0"

        if not login_id or not temp_password or not role:
            flash("아이디, 비밀번호, 권한(role)은 필수입니다.")
            return redirect(url_for("admin.account_new"))

        if role == "student":
            if not student_id:
                flash("학생 계정은 student_id 선택이 필요합니다.")
                return redirect(url_for("admin.account_new"))
            student_id_val = int(student_id)
            professor_id_val = None
        elif role == "professor":
            if not professor_id:
                flash("교수 계정은 professor_id 선택이 필요합니다.")
                return redirect(url_for("admin.account_new"))
            professor_id_val = int(professor_id)
            student_id_val = None
        else:  
            student_id_val = None
            professor_id_val = None

        insert_sql = text("""
            INSERT INTO account (
                login_id,
                password,
                role,
                student_id,
                professor_id,
                is_active
            ) VALUES (
                :login_id,
                :password,
                :role,
                :student_id,
                :professor_id,
                :is_active
            )
        """)

        try:
            db.session.execute(insert_sql, {
                "login_id": login_id,
                "password": temp_password,  # 실서비스면 해시 필수
                "role": role,
                "student_id": student_id_val,
                "professor_id": professor_id_val,
                "is_active": 1 if is_active == "1" else 0,
            })
            db.session.commit()
            flash("계정이 생성되었습니다.")
        except Exception:
            db.session.rollback()
            flash("계정 생성 중 오류가 발생했습니다. (아이디 중복 등)")
        return redirect(url_for("admin.accounts"))

    students = db.session.execute(
        text("SELECT student_id, student_name FROM student ORDER BY student_name")
    ).fetchall()

    professors = db.session.execute(
        text("SELECT professor_id, professor_name FROM professor ORDER BY professor_name")
    ).fetchall()

    return render_template(
        "admin/account_new.html",
        students=students,
        professors=professors,
    )

# 4-7-2. 계정 관리 (수정): /admin/accounts/<id>/edit
@admin_bp.route("/accounts/<int:account_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def account_edit(account_id):
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 인증 실패")
        return redirect(url_for("auth.login"))

    acc_sql = text("""
        SELECT *
        FROM account
        WHERE account_id = :account_id
    """)
    account = db.session.execute(acc_sql, {"account_id": account_id}).fetchone()

    if account is None:
        flash("계정 정보를 찾을 수 없습니다.")
        return redirect(url_for("admin.accounts"))

    if request.method == "POST":
        login_id = request.form.get("login_id")
        role = request.form.get("role")
        student_id = request.form.get("student_id")
        professor_id = request.form.get("professor_id")
        is_active = request.form.get("is_active", "1")

        if not login_id or not role:
            flash("아이디와 권한(role)은 필수입니다.")
            return redirect(url_for("admin.account_edit", account_id=account_id))

        if role == "student":
            if not student_id:
                flash("학생 계정은 student_id 선택이 필요합니다.")
                return redirect(url_for("admin.account_edit", account_id=account_id))
            student_id_val = int(student_id)
            professor_id_val = None
        elif role == "professor":
            if not professor_id:
                flash("교수 계정은 professor_id 선택이 필요합니다.")
                return redirect(url_for("admin.account_edit", account_id=account_id))
            professor_id_val = int(professor_id)
            student_id_val = None
        else:  # admin
            student_id_val = None
            professor_id_val = None

        update_sql = text("""
            UPDATE account
            SET login_id     = :login_id,
                role         = :role,
                student_id   = :student_id,
                professor_id = :professor_id,
                is_active    = :is_active
            WHERE account_id = :account_id
        """)

        try:
            db.session.execute(update_sql, {
                "account_id": account_id,
                "login_id": login_id,
                "role": role,
                "student_id": student_id_val,
                "professor_id": professor_id_val,
                "is_active": 1 if is_active == "1" else 0,
            })
            db.session.commit()
            flash("계정 정보가 수정되었습니다.")
        except Exception:
            db.session.rollback()
            flash("계정 수정 중 오류가 발생했습니다. (아이디 중복 등)")
        return redirect(url_for("admin.accounts"))

    students = db.session.execute(
        text("SELECT student_id, student_name FROM student ORDER BY student_name")
    ).fetchall()

    professors = db.session.execute(
        text("SELECT professor_id, professor_name FROM professor ORDER BY professor_name")
    ).fetchall()

    return render_template(
        "admin/account_edit.html",
        account=account,
        students=students,
        professors=professors,
    )

# 4-7-3. 계정 관리 (삭제): /admin/accounts/<id>/delete
@admin_bp.route("/accounts/<int:account_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def account_delete(account_id):
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 인증 실패")
        return redirect(url_for("auth.login"))

    delete_sql = text("""
        DELETE FROM account
        WHERE account_id = :account_id
    """)

    try:
        db.session.execute(delete_sql, {"account_id": account_id})
        db.session.commit()
        flash("계정이 삭제되었습니다.")
    except Exception:
        db.session.rollback()
        flash("계정 삭제 중 오류가 발생했습니다.")
    return redirect(url_for("admin.accounts"))

# 4-7-4. 계정 관리 (비밀번호 초기화): /admin/accounts/<id>/reset_password
@admin_bp.route("/accounts/<int:account_id>/reset_password", methods=["POST"])
@login_required
@role_required("admin")
def account_reset_password(account_id):
    admin_id = _get_current_admin_id()
    if admin_id is None:
        flash("관리자 인증 실패")
        return redirect(url_for("auth.login"))

    new_password = "pw1234"

    update_sql = text("""
        UPDATE account
        SET password = :password
        WHERE account_id = :account_id
    """)

    db.session.execute(update_sql, {
        "account_id": account_id,
        "password": new_password,
    })
    db.session.commit()

    flash(f"비밀번호가 '{new_password}' 로 초기화되었습니다.")
    return redirect(url_for("admin.accounts"))