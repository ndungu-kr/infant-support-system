from flask import Blueprint, jsonify, request ,redirect, url_for, render_template
from database import db
from extensions import verify_payload, SECRET_KEY
from models import Nurse, CheckInHistory, AlertHistory, InfantStatusHistory
from extensions import verify_payload
from datetime import datetime

piRoute = Blueprint("piRoute",__name__, url_prefix="/api")

# Verify the json sent from pi with HMAC-SHA256
def verifyJson(data:dict):
    signature = data.pop("signature", None)
    if SECRET_KEY and (not signature or not verify_payload(data, signature)):
        return False, jsonify({"error":"Unauthorized"})
    return True, ""

# Store checkin record into database (only if the rfid is legit)
@piRoute.route("/checkin", methods=["POST"])
def rfidTap():
    data = request.get_json()
    success, message = verifyJson(data)

    if not success:
        return message, 401
    
    # check who the rfid tag belongs to
    nurse = Nurse.query.filter_by(rfid_tag = data["rfidTagID"]).first()

    if nurse:
        checkin = CheckInHistory(
            nurse_id = nurse.id,
            timestamp = datetime.fromisoformat(data["timestamp"].replace("Z","+00:00")).replace(tzinfo=None)
        )

        db.session.add(checkin)
        db.session.commit()

    return jsonify({"status": "success"}), 200

# Store alert record into database
@piRoute.route("/alert", methods=["POST"])
def piAlert():
    data = request.get_json()
    success, message = verifyJson(data)

    if not success:
        return message, 401
    
    # record alert
    alert = AlertHistory(
        level = data["alertLevel"],
        reason = data["alertReason"],
        possibleCause = data["possibleCauses"],
        infantState = data["infantState"],
        timestamp = datetime.fromisoformat(data["timestamp"].replace("Z","+00:00")).replace(tzinfo=None)
    )

    db.session.add(alert)
    db.session.commit()

    return jsonify({"status": "success"}), 200

# store the telemetry record into database
@piRoute.route("/telemetry", methods=["POST"])
def telemetry():
    data = request.get_json()
    success, message = verifyJson(data)

    if not success:
        return message, 401
    
    # record telemetry data
    status = InfantStatusHistory(
        presence = data["presence"],
        state = data["state"],
        crying = data["crying"],
        cryingDuration = data["cryingDuration"],
        temperature = data["temperature"],
        humidity = data["humidity"],
        light = data["light"],
        loudness = data["loudness"],
        timestamp = datetime.fromisoformat(data["timestamp"].replace("Z","+00:00")).replace(tzinfo=None)
    )

    db.session.add(status)
    db.session.commit()

    return jsonify({"status": "success"}), 200