import os
import jwt
from jwt import PyJWKClient
from fastapi import Header, HTTPException, status
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from typing import Optional

# Загрузка публичного ключа Laravel Passport (RS256)
def load_public_key():
    key_path = os.getenv("OAUTH_PUBLIC_KEY", "/app/oauth-public.key")
    try:
        with open(key_path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        # Если ключа нет (не запущен passport), возвращаем заглушку, чтобы сервис не падал
        return b"dummy-key-for-lab"
PUBLIC_KEY = load_public_key()

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Проверяет JWT токен от Laravel Passport (алгоритм RS256)"""
    
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token required',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    token = authorization.split(' ')[1]

    try:
        # Проверяем токен с помощью публичного ключа (асимметричное шифрование)
        payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=['RS256'],
            options={'verify_aud': False, 'verify_iss': False}  # Для учебного проекта
        )
        return payload  # {'sub': user_id, 'scopes': [...], ...}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token expired'
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Invalid token: {str(e)}'
        )
