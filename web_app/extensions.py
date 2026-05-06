# store all extensions library in another python file to prevent circular imports

# bcrypt for hashing password--------------------------
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# for HMAC security--------------------------------------
import hmac
import hashlib
import os
import json

SECRET_KEY = os.getenv("HMAC_SECRET")

# Generate HMAC signature for a json payload
def sign_payload(data:dict) -> str:
    body = json.dumps(data, separators=(",",":"),sort_keys=True)
    signature = hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).hexdigest()
    return signature

# Verify the payload is the same as the signature
def verify_payload(data: dict, signature: str) -> bool:
    expected = sign_payload(data)
    return hmac.compare_digest(expected, signature)

# jwt session token-------------------------------------------
from flask_jwt_extended import JWTManager

jwt = JWTManager()