from datetime import datetime, timedelta, timezone

from jose import jwt
from pwdlib import PasswordHash

from ..config import settings


password_hash = PasswordHash.recommended()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def gerar_hash_senha(senha: str) -> str:
    return password_hash.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return password_hash.verify(senha, senha_hash)


def criar_token_acesso(usuario_id: int) -> str:
    agora = datetime.now(timezone.utc)
    expiracao = agora + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(usuario_id),
        "iat": agora,
        "exp": expiracao,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=ALGORITHM,
    )