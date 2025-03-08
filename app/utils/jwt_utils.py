import os
from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or "secret"


def create_access_token(user_id: str):
    payload = {
        "user_id": user_id,
        "exp": datetime.now() + timedelta(days=1),
        "iat": datetime.now(),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="令牌已过期") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="无效的令牌") from e


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = decode_token(token)
    return payload
