from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from core import repository

router = APIRouter(prefix="/api", tags=["Protocolo REST"])

# =====================================================================
# MODELOS PYDANTIC (Entrada e Saída)
# =====================================================================

class CriarUsuarioRequest(BaseModel):
    nome: str = Field(..., min_length=1, description="Nome do usuário")
    email: str = Field(..., min_length=3, description="Email único do usuário")
    bio: Optional[str] = Field("", description="Biografia do perfil (1:1)")
    foto_url: Optional[str] = Field("", description="URL da foto de perfil")

class CriarPostRequest(BaseModel):
    usuario_id: int = Field(..., description="ID do autor do post")
    texto: str = Field(..., min_length=1, description="Conteúdo do post")

class CriarComentarioRequest(BaseModel):
    usuario_id: int = Field(..., description="ID do autor do comentário")
    texto: str = Field(..., min_length=1, description="Texto do comentário")

class SeguirUsuarioRequest(BaseModel):
    alvo_id: int = Field(..., description="ID do usuário a ser seguido")


# =====================================================================
# COMANDOS (Escrita via POST)
# =====================================================================

@router.post("/usuarios", status_code=status.HTTP_201_CREATED, summary="1. Criar Usuário")
def rota_criar_usuario(payload: CriarUsuarioRequest):
    """Cria um novo usuário e inicializa seu perfil (1:1)."""
    try:
        usuario = repository.criar_usuario(
            nome=payload.nome,
            email=payload.email,
            bio=payload.bio or "",
            foto_url=payload.foto_url or ""
        )
        return usuario
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/posts", status_code=status.HTTP_201_CREATED, summary="2. Criar Post")
def rota_criar_post(payload: CriarPostRequest):
    """Cria um novo post para o usuário autor (1:N autor)."""
    try:
        post = repository.criar_post(usuario_id=payload.usuario_id, texto=payload.texto)
        return post
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/posts/{post_id}/comentarios", status_code=status.HTTP_201_CREATED, summary="3. Comentar em Post")
def rota_comentar(post_id: int, payload: CriarComentarioRequest):
    """Adiciona um comentário ao post (relacionamento N:M com atributo)."""
    try:
        comentario = repository.comentar(
            usuario_id=payload.usuario_id,
            post_id=post_id,
            texto=payload.texto
        )
        return comentario
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/posts/{post_id}/curtidas", status_code=status.HTTP_200_OK, summary="4. Curtir Post")
def rota_curtir(post_id: int, usuario_id: int):
    """Registra uma curtida do usuário no post (relacionamento N:M puro)."""
    try:
        resultado = repository.curtir(usuario_id=usuario_id, post_id=post_id)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/usuarios/{usuario_id}/seguir", status_code=status.HTTP_200_OK, summary="5. Seguir Usuário")
def rota_seguir(usuario_id: int, payload: SeguirUsuarioRequest):
    """Estabelece a relação de seguidor/seguido entre usuários (N:M auto)."""
    try:
        resultado = repository.seguir(usuario_id=usuario_id, alvo_id=payload.alvo_id)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =====================================================================
# CONSULTAS (Leitura via GET)
# =====================================================================

@router.get("/usuarios/{usuario_id}", summary="6. Buscar Usuário")
def rota_buscar_usuario(usuario_id: int):
    """Consulta dados do usuário, perfil 1:1 e contadores."""
    usuario = repository.buscar_usuario(usuario_id=usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return usuario

@router.get("/usuarios/{usuario_id}/posts", summary="7. Posts do Usuário")
def rota_posts_do_usuario(usuario_id: int):
    """Lista todas as postagens publicadas por um determinado autor."""
    # Verificar se o usuário existe
    if not repository.buscar_usuario(usuario_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return repository.posts_do_usuario(usuario_id=usuario_id)

@router.get("/posts/{post_id}", summary="8. Buscar Post")
def rota_buscar_post(post_id: int):
    """Consulta um post específico com lista de comentários e curtidas."""
    post = repository.buscar_post(post_id=post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post não encontrado.")
    return post

@router.get("/usuarios/{usuario_id}/seguidores", summary="9a. Seguidores de Usuário")
def rota_seguidores_de(usuario_id: int):
    """Lista quem segue o usuário especificado."""
    if not repository.buscar_usuario(usuario_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return repository.seguidores_de(usuario_id=usuario_id)

@router.get("/usuarios/{usuario_id}/seguindo", summary="9b. Quem o Usuário está Seguindo")
def rota_seguindo_de(usuario_id: int):
    """Lista quem o usuário especificado está seguindo."""
    if not repository.buscar_usuario(usuario_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return repository.seguindo_de(usuario_id=usuario_id)

@router.get("/usuarios/{usuario_id}/feed", summary="10. Feed do Usuário")
def rota_feed_do_usuario(usuario_id: int):
    """Gera o feed cronológico com postagens de todos os perfis que o usuário segue."""
    if not repository.buscar_usuario(usuario_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return repository.feed_do_usuario(usuario_id=usuario_id)
