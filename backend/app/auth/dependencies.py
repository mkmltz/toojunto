from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import Usuario
from .security import ALGORITHM


bearer_scheme = HTTPBearer(auto_error=False)


def _credenciais_invalidas() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credenciais: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    if credenciais is None:
        raise _credenciais_invalidas()

    try:
        payload = jwt.decode(
            credenciais.credentials,
            settings.jwt_secret,
            algorithms=[ALGORITHM],
        )
        usuario_id = int(payload["sub"])
    except (JWTError, KeyError, TypeError, ValueError):
        raise _credenciais_invalidas() from None

    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise _credenciais_invalidas()

    return usuario
