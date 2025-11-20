# config.py

class Config:
    SECRET_KEY = "dev-secret-key-change-later"

    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://root:root@localhost:3306/haksadb"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
