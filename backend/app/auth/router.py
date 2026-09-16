from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Usuario
from .schemas import (
    LoginRequest,
    TokenResposta,
    UsuarioCadastro,
    UsuarioResposta,
)
from .dependencies import get_current_user
from .security import (
    criar_token_acesso,
    gerar_hash_senha,
    verificar_senha,
)


router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"],
)


@router.get(
    "/me",
    response_model=UsuarioResposta,
)
def obter_usuario_atual(
    usuario: Usuario = Depends(get_current_user),
):
    return usuario


@router.post(
    "/register",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_usuario(
    dados: UsuarioCadastro,
    db: Session = Depends(get_db),
):
    usuario_existente = db.scalar(
        select(Usuario).where(Usuario.email == dados.email)
    )

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado.",
        )

    novo_usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        telefone=dados.telefone,
        senha_hash=gerar_hash_senha(dados.senha),
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


@router.post(
    "/login",
    response_model=TokenResposta,
)
def login(
    dados: LoginRequest,
    db: Session = Depends(get_db),
):
    usuario = db.scalar(
        select(Usuario).where(Usuario.email == dados.email)
    )

    if not usuario or not verificar_senha(
        dados.senha,
        usuario.senha_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = criar_token_acesso(usuario.id)

    return {
        "access_token": token,
        "token_type": "bearer",
    }
