import os
from flask import Flask, redirect, url_for, jsonify
from flask_cors import CORS
from datetime import timedelta

from database import init_db
from routes.frontend_route import frontRoute, logoutTokenList
from routes.pi_route import piRoute
from extensions import bcrypt, jwt

# read .env into os environment (ignore if found nothing)
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__,instance_path="/tmp")

# JWT config---------------------------------------
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)

# init all extensions-------------------------
CORS(app, supports_credentials=True)
init_db(app)
bcrypt.init_app(app)
jwt.init_app(app)

# Error handlers for jwt-----------------------
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    return jsonify({"error":"Token has expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"error":"Invalid token"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"error":"No token provided"}), 401

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_data):
    return jwt_data["jti"] in logoutTokenList

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_data):
    return jsonify({"error": "Token has been revoked"}), 401

# blueprints for routers----------------------------
app.register_blueprint(frontRoute)
app.register_blueprint(piRoute)

# basic route----------------------------------------
@app.route("/")
def home():
    return redirect(url_for("frontRoute.login"))

# main -----------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)