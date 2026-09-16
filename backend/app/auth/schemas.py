from pydantic import BaseModel, EmailStr, Field


class UsuarioCadastro(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    telefone: str | None = Field(default=None, max_length=30)
    senha: str = Field(min_length=8, max_length=128)


class UsuarioResposta(BaseModel):
    id: int
    nome: str
    email: EmailStr
    telefone: str | None

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1, max_length=128)


class TokenResposta(BaseModel):
    access_token: str
    token_type: str = "bearer" 