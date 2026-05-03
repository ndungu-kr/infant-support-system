from flask import Blueprint, jsonify, request ,redirect, url_for, render_template
from database import db
from extensions import bcrypt
from models import Nurse, InfantStatusHistory, CheckInHistory, AlertHistory, CribCheckout
from datetime import datetime, timezone, timedelta
from flask_jwt_extended import jwt_required,create_access_token,get_jwt
import re

frontRoute = Blueprint("frontRoute",__name__, url_prefix="")

# store all the token when a user choose to logout
logoutTokenList = set()

# validate the input send from user to upload to database (prevent XSS)
def validate_input(input):
    if not input:
        return False
    return re.match(r"^[a-zA-Z0-9 _-]+$", input) is not None

# for user login, return the jwt token for session control
@frontRoute.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.get_json().get("username")
        password = request.get_json().get("password")

        # get nurse with the username from database
        nurse = Nurse.query.filter_by(username=username).first()
        
        # check if there is nurse with the username then check for password
        if nurse and bcrypt.check_password_hash(nurse.password, password):
            token = create_access_token(identity=str(nurse.id)) # create access token and return it to store at front end
            return jsonify({
                "token": token,
                "id": nurse.id,
                "name": nurse.name
            }), 200
        
        else:
            return jsonify({"error": "Invalid credentials"}), 200
    
    else:
        #return render_template("")
        return "loginPage"
    
# return the dashboard page
@frontRoute.route("/dashboard")
@jwt_required()
def dashboard():
    #return render_template("")
    return "dashboard"

# return the latest telemetry data + online flag (if the last telemetry < 60s ago)
@frontRoute.route("/status")
@jwt_required()
def status():
    now = datetime.now()
    statusHistory = InfantStatusHistory.query.order_by(InfantStatusHistory.id.desc()).first()
    
    if not statusHistory:
        return jsonify({}), 200
    
    diff = (now-statusHistory.timestamp).total_seconds()

    # get the most recent unresolved alert
    latestAlert = AlertHistory.query.filter_by(resolved=False).order_by(AlertHistory.id.desc()).first()

    # calculate minutes since last check-in
    lastCheckin = CheckInHistory.query.order_by(CheckInHistory.id.desc()).first()
    if lastCheckin:
        minutesSinceCare = int((now - lastCheckin.timestamp).total_seconds() / 60)
    else:
        minutesSinceCare = -1

    statusHistoryDict = statusHistory.to_dict()
    statusHistoryDict.update({
        "online": diff <= 60,
        "alertLevel": latestAlert.level if latestAlert else "NONE",
        "alertReason": latestAlert.reason if latestAlert else "",
        "possibleCauses": [latestAlert.possibleCause] if latestAlert and latestAlert.possibleCause else [],
        "minutesSinceCare": minutesSinceCare
    })

    return jsonify(statusHistoryDict), 200

# return the latest checkin history and the total checkins today
@frontRoute.route("/summary")
@jwt_required()
def summary():
    now = datetime.now()

    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_tomorrow = start_of_today + timedelta(days=1)

    count = CheckInHistory.query.filter(
        CheckInHistory.timestamp >= start_of_today,
        CheckInHistory.timestamp < start_of_tomorrow
    ).count()

    # count crying episodes today
    cryingCount = AlertHistory.query.filter(
        AlertHistory.timestamp >= start_of_today,
        AlertHistory.timestamp < start_of_tomorrow,
        AlertHistory.infantState == "CRYING"
    ).count()

    lastCheckIn = CheckInHistory.query.order_by(CheckInHistory.id.desc()).first()
    
    if not lastCheckIn:
        return jsonify({
            "cryingEpisodesToday": cryingCount,
            "totalCheckinsToday": 0,
            "lastCheckinTime": None,
            "lastCheckinNurse": None
        }), 200

    return jsonify({
        "cryingEpisodesToday": cryingCount,
        "totalCheckinsToday": count,
        "lastCheckinTime": lastCheckIn.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "lastCheckinNurse": lastCheckIn.nurse.name
    }), 200

# return all the checkin record based on the given date
@frontRoute.route("/checkins")
@jwt_required()
def checkins():
    start_str = request.args.get("start")
    end_str = request.args.get("end")

    if not start_str or not end_str:
        return jsonify({"status": "failed", "error":"parameter not provided"}), 401
    
    start_date = datetime.strptime(start_str,"%Y-%m-%d")
    end_date = datetime.strptime(end_str,"%Y-%m-%d")+ timedelta(days=1)

    checkinHistorys = CheckInHistory.query.filter(
        CheckInHistory.timestamp >= start_date,
        CheckInHistory.timestamp < end_date
    ).order_by(CheckInHistory.id.desc()).all()

    return jsonify([h.to_dict() for h in checkinHistorys]), 200

# return all the telemetry record based on the given date
@frontRoute.route("/history")
@jwt_required()
def history(): 
    start_str = request.args.get("start")
    end_str = request.args.get("end")

    if not start_str or not end_str:
        return jsonify({"status": "failed", "error":"parameter not provided"}), 401

    start_date = datetime.strptime(start_str,"%Y-%m-%d")
    end_date = datetime.strptime(end_str,"%Y-%m-%d")+ timedelta(days=1)

    infantStatusHistorys = InfantStatusHistory.query.filter(
        InfantStatusHistory.timestamp >= start_date,
        InfantStatusHistory.timestamp < end_date
    ).order_by(InfantStatusHistory.id.desc()).all()

    return jsonify([h.to_dict() for h in infantStatusHistorys]), 200

# return all the alert record based on the given date
@frontRoute.route("/alert")
@jwt_required()
def alert(): 
    start_str = request.args.get("start")
    end_str = request.args.get("end")

    if not start_str or not end_str:
        return jsonify({"status": "failed", "error":"parameter not provided"}), 401

    start_date = datetime.strptime(start_str,"%Y-%m-%d")
    end_date = datetime.strptime(end_str,"%Y-%m-%d")+ timedelta(days=1)

    alertHistorys = AlertHistory.query.filter(
        AlertHistory.timestamp >= start_date,
        AlertHistory.timestamp < end_date
    ).order_by(AlertHistory.id.desc()).all()

    return jsonify([h.to_dict() for h in alertHistorys]), 200

# update the checkin record with an action
@frontRoute.route("/checkin/update", methods=["POST"])
@jwt_required()
def checkinUpdate(): 
    id = request.get_json().get("id")
    action = request.get_json().get("action")

    if not validate_input(action):
        return jsonify({"status": "failed", "error":"Invalid input"}), 401

    checkinHistory = CheckInHistory.query.get(id)

    if checkinHistory:
        checkinHistory.action = action
        db.session.commit()
    
    return jsonify({"status": "success"}), 200

@frontRoute.route("/logout",methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    logoutTokenList.add(jti)

    return jsonify({"message": "Logged out successfully"}), 200

@frontRoute.route("/crib-status")
@jwt_required()
def cribStatus():
    checkout = CribCheckout.query.filter_by(returned_at=None).order_by(CribCheckout.id.desc()).first()

    if not checkout:
        return jsonify({
            "checkedOut": False,
            "reason": None,
            "checkedOutBy": None,
            "checkedOutAt": None,
            "expectedReturnAt": None,
            "expired": False
        }), 200

    expected_return = checkout.checked_out_at + timedelta(minutes=checkout.duration_minutes)
    expired = datetime.now(timezone.utc) > expected_return

    return jsonify({
        "checkedOut": True,
        "reason": checkout.reason,
        "checkedOutBy": checkout.nurse.name,
        "checkedOutAt": checkout.checked_out_at.strftime("%Y-%m-%d %H:%M:%S"),
        "expectedReturnAt": expected_return.strftime("%Y-%m-%d %H:%M:%S"),
        "expired": expired
    }), 200


@frontRoute.route("/crib-checkout", methods=["POST"])
@jwt_required()
def cribCheckout():
    data = request.get_json()
    reason = data.get("reason")
    duration_minutes = data.get("durationMinutes")

    if not reason or not duration_minutes:
        return jsonify({"success": False, "error": "Missing reason or duration"}), 400

    nurse_id = get_jwt()["sub"]

    checkout = CribCheckout(
        nurse_id=int(nurse_id),
        reason=reason,
        duration_minutes=duration_minutes
    )
    db.session.add(checkout)
    db.session.commit()

    return jsonify({"success": True}), 200


@frontRoute.route("/crib-return", methods=["POST"])
@jwt_required()
def cribReturn():
    checkout = CribCheckout.query.filter_by(returned_at=None).order_by(CribCheckout.id.desc()).first()

    if not checkout:
        return jsonify({"success": False, "error": "Baby is not checked out"}), 400

    checkout.returned_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({"success": True}), 200