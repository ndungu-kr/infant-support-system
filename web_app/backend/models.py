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
            "nurseName": self.nurse.name if self.nurse else None,
            "action": self.action,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
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
    motion = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime,default= lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "infantState": self.state,
            "cryingDurationMins": self.cryingDuration,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "light": self.light,
            "loudness": self.loudness,
            "cameraPresence": "infant_present" if self.presence else "unknown",
            "cameraFaceState": self.state.lower() if self.state else "unknown",
            "cameraCrying": self.crying,
            "motion": self.motion,
            "cameraMotion": None,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

# store all the alerts history------------------------------
class AlertHistory(db.Model):
    __tablename__ = "alert_history"
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    possibleCause = db.Column(db.String(255), nullable=False)
    infantState = db.Column(db.String(50), nullable=False)
    resolved = db.Column(db.Boolean, default=False)
    resolvedAt = db.Column(db.DateTime, nullable=True)
    timestamp = db.Column(db.DateTime,default= lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "alertLevel": self.level,
            "alertReason": self.reason,
            "possibleCauses": [self.possibleCause] if self.possibleCause else [],
            "infantState": self.infantState,
            "resolved": self.resolved,
            "resolvedAt": self.resolvedAt.strftime("%Y-%m-%d %H:%M:%S") if self.resolvedAt else None,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

