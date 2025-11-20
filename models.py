from extensions import db

class Account(db.Model):
    __tablename__ = "account"


    account_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    login_id = db.Column(db.String(30), unique = True, nullable = False)
    password = db.Column(db.String(100), nullable = False)
    role = db.Column(db.String(20), nullable = False)

    student_id = db.Column(db.Integer, nullable = True)
    professor_id = db.Column(db.Integer, nullable = True)

    is_active = db.Column(db.Boolean, nullable = False, default = True)