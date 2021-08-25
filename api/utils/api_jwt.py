import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, DecodeError # noqa
from dotenv import load_dotenv
from flask import request, jsonify
import os
from functools import wraps


load_dotenv()


def check_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        jwt_secret = os.environ.get('HOTELS_APP_JWT_SECRET_KEY')
        token = request.headers['Authorization']
        print(token)
        try:
            jwt.decode(
                token,
                jwt_secret,
                algorithms=["HS256"]
            )
            print(request.get_json())
            return f(*args, **kwargs)
        except (
                InvalidSignatureError,
                ExpiredSignatureError,
                DecodeError
        ):
            return jsonify({'msg': 'invalid token'}), 400
    return decorated
