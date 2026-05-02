from database import db
from datetime import datetime, timezone

#Nurse table-----------------------------
class Nurse(db.Model):
    __tablename__="nurse"

    id = db.Column(db.Integer, primary_key=True)
    rfid_tag = db.Column(db.String(50), unique = True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    checkin_history = db.relationship("CheckInHistory",back_populates="nurse",cascade="all, delete-orphan")

# store all the check in history------------------------
class CheckInHistory(db.Model):
    __tablename__ = "check_in_history"

    id = db.Column(db.Integer, primary_key=True)
    nurse_id = db.Column(db.Integer, db.ForeignKey("nurse.id"), nullable=False)
    action = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # foreign key
    nurse = db.relationship("Nurse", back_populates="checkin_history")

    def to_dict(self):
        return {
            "id": self.id,
            "nurse": self.nurse.name if self.nurse else None,
            "action": self.action,
            "timestamp":self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

# store all the sensor history-------------------------------
class InfantStatusHistory(db.Model):
    __tablename__ = "infant_status_history"

    id = db.Column(db.Integer, primary_key=True)
    presence = db.Column(db.Boolean, nullable=False)
    state = db.Column(db.String(50), nullable=False)
    crying = db.Column(db.Boolean, nullable=False)
    cryingDuration = db.Column(db.Integer, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    light = db.Column(db.Integer, nullable=False)
    loudness = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime,default= lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "presence": self.presence,
            "state": self.state,
            "crying": self.crying,
            "cryingDuration":self.cryingDuration,
            "temperature":self.temperature,
            "humidity":self.humidity,
            "light":self.light,
            "loudness":self.loudness,
            "timestamp":self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

# store all the alerts history------------------------------
class AlertHistory(db.Model):
    __tablename__ = "alert_history"
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    possibleCause = db.Column(db.String(255), nullable=False)
    infantState = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime,default= lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "level": self.level,
            "reason": self.reason,
            "possibleCause":self.possibleCause,
            "infantState": self.infantState,
            "timestamp":self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

