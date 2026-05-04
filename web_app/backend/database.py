# store all database config
import os
from flask_sqlalchemy import SQLAlchemy
from extensions import bcrypt

db = SQLAlchemy()

# get all the info from os and return the connection string
def get_database_uri():
    db_host = os.getenv("MYSQL_SERVICE_HOST","localhost")
    db_name = os.getenv("MYSQL_DATABASE")
    db_user = os.getenv("MYSQL_USER")
    db_pass = os.getenv("MYSQL_PASSWORD")
    
    if db_name:
        return f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:3306/{db_name}"
    return "sqlite:///local.db" 

# insert default data (nurses) to the table if the table is empty
def seed_data():
    from models import Nurse
    
    # check if the table is empty
    if Nurse.query.count() == 0:
        nurses = [
            Nurse(rfid_tag="asdasd", name="Sarah", username="user1", password=bcrypt.generate_password_hash("abcd1234").decode('utf-8')),
            Nurse(rfid_tag="asdasd123", name="Berah", username="user2", password=bcrypt.generate_password_hash("abcd1234").decode('utf-8'))
        ]
        db.session.add_all(nurses)

    db.session.commit()

# Bind db to app
def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"]= get_database_uri()
    db.init_app(app)

    # import all the models so create_all() can read and create
    from models import Nurse, CheckInHistory, InfantStatusHistory, AlertHistory

    with app.app_context():
        db.create_all() # create all imported model tables
        seed_data() # insert default data