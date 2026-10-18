from typing import List, Optional
import strawberry
from strawberry.fastapi import GraphQLRouter

from core import repository

# =====================================================================
# TIPOS GRAPHQL
# =====================================================================

@strawberry.type(description="Comentário em uma publicação (N:M com atributo)")
class ComentarioType:
    id: int
    usuario_id: int
    post_id: int
    texto: str
    criado_em: str
    autor_nome: str

@strawberry.type(description="Publicação feita por um autor")
class PostType:
    id: int
    usuario_id: int
    texto: str
    criado_em: str
    autor_nome: str
    total_curtidas: int
    total_comentarios: int

    @strawberry.field(description="Lista de comentários associados ao post")
    def comentarios(self) -> List[ComentarioType]:
        detalhes = repository.buscar_post(self.id)
        if not detalhes or "comentarios" not in detalhes:
            return []
        return [
            ComentarioType(
                id=c["id"],
                usuario_id=c["usuario_id"],
                post_id=c["post_id"],
                texto=c["texto"],
                criado_em=str(c["criado_em"]),
                autor_nome=c["autor_nome"]
            )
            for c in detalhes["comentarios"]
        ]

@strawberry.type(description="Usuário da rede social e seu perfil (1:1)")
class UsuarioType:
    id: int
    nome: str
    email: str
    criado_em: str
    bio: str
    foto_url: str
    total_seguidores: int
    total_seguindo: int
    total_posts: int

    @strawberry.field(description="Posts publicados por este usuário")
    def posts(self) -> List[PostType]:
        posts_raw = repository.posts_do_usuario(self.id)
        return [
            PostType(
                id=p["id"],
                usuario_id=p["usuario_id"],
                texto=p["texto"],
                criado_em=str(p["criado_em"]),
                autor_nome=p["autor_nome"],
                total_curtidas=p["total_curtidas"],
                total_comentarios=p["total_comentarios"]
            )
            for p in posts_raw
        ]

@strawberry.type(description="Resumo de seguidor ou seguido")
class UsuarioResumoType:
    id: int
    nome: str
    email: str
    bio: str
    seguido_desde: str

@strawberry.type(description="Resultado de ação de curtir (N:M puro)")
class CurtidaResultadoType:
    post_id: int
    usuario_id: int
    curtido: bool
    total_curtidas: int

@strawberry.type(description="Resultado de ação de seguir (N:M auto)")
class SeguirResultadoType:
    seguidor_id: int
    seguidor_nome: str
    alvo_id: int
    alvo_nome: str
    seguindo: bool


# =====================================================================
# CONSULTAS (Query)
# =====================================================================

@strawberry.type
class Query:
    @strawberry.field(description="1. Consulta dados do usuário, perfil 1:1 e contadores")
    def buscar_usuario(self, id: int) -> Optional[UsuarioType]:
        u = repository.buscar_usuario(id)
        if not u:
            return None
        return UsuarioType(
            id=u["id"],
            nome=u["nome"],
            email=u["email"],
            criado_em=str(u["criado_em"]),
            bio=u["bio"],
            foto_url=u["foto_url"],
            total_seguidores=u["total_seguidores"],
            total_seguindo=u["total_seguindo"],
            total_posts=u["total_posts"]
        )

    @strawberry.field(description="2. Lista postagens publicadas por um usuário autor")
    def posts_do_usuario(self, usuario_id: int) -> List[PostType]:
        posts_raw = repository.posts_do_usuario(usuario_id)
        return [
            PostType(
                id=p["id"],
                usuario_id=p["usuario_id"],
                texto=p["texto"],
                criado_em=str(p["criado_em"]),
                autor_nome=p["autor_nome"],
                total_curtidas=p["total_curtidas"],
                total_comentarios=p["total_comentarios"]
            )
            for p in posts_raw
        ]

    @strawberry.field(description="3. Consulta uma publicação específica com comentários")
    def buscar_post(self, id: int) -> Optional[PostType]:
        p = repository.buscar_post(id)
        if not p:
            return None
        return PostType(
            id=p["id"],
            usuario_id=p["usuario_id"],
            texto=p["texto"],
            criado_em=str(p["criado_em"]),
            autor_nome=p["autor_nome"],
            total_curtidas=p["total_curtidas"],
            total_comentarios=p["total_comentarios"]
        )

    @strawberry.field(description="4a. Lista quem segue o usuário")
    def seguidores_de(self, id: int) -> List[UsuarioResumoType]:
        lista = repository.seguidores_de(id)
        return [
            UsuarioResumoType(
                id=item["id"],
                nome=item["nome"],
                email=item["email"],
                bio=item["bio"],
                seguido_desde=str(item["seguido_desde"])
            )
            for item in lista
        ]

    @strawberry.field(description="4b. Lista quem o usuário está seguindo")
    def seguindo_de(self, id: int) -> List[UsuarioResumoType]:
        lista = repository.seguindo_de(id)
        return [
            UsuarioResumoType(
                id=item["id"],
                nome=item["nome"],
                email=item["email"],
                bio=item["bio"],
                seguido_desde=str(item["seguido_desde"])
            )
            for item in lista
        ]

    @strawberry.field(description="5. Feed cronológico com posts de quem o usuário segue")
    def feed_do_usuario(self, usuario_id: int) -> List[PostType]:
        posts_raw = repository.feed_do_usuario(usuario_id)
        return [
            PostType(
                id=p["id"],
                usuario_id=p["usuario_id"],
                texto=p["texto"],
                criado_em=str(p["criado_em"]),
                autor_nome=p["autor_nome"],
                total_curtidas=p["total_curtidas"],
                total_comentarios=p["total_comentarios"]
            )
            for p in posts_raw
        ]


# =====================================================================
# MUTAÇÕES (Mutation)
# =====================================================================

@strawberry.type
class Mutation:
    @strawberry.mutation(description="1. Criar novo usuário e perfil 1:1")
    def criar_usuario(
        self,
        nome: str,
        email: str,
        bio: Optional[str] = "",
        foto_url: Optional[str] = ""
    ) -> UsuarioType:
        u = repository.criar_usuario(nome=nome, email=email, bio=bio or "", foto_url=foto_url or "")
        return UsuarioType(
            id=u["id"],
            nome=u["nome"],
            email=u["email"],
            criado_em=str(u["criado_em"]),
            bio=u["bio"],
            foto_url=u["foto_url"],
            total_seguidores=u["total_seguidores"],
            total_seguindo=u["total_seguindo"],
            total_posts=u["total_posts"]
        )

    @strawberry.mutation(description="2. Criar publicação vinculada a um autor")
    def criar_post(self, usuario_id: int, texto: str) -> PostType:
        p = repository.criar_post(usuario_id=usuario_id, texto=texto)
        return PostType(
            id=p["id"],
            usuario_id=p["usuario_id"],
            texto=p["texto"],
            criado_em=str(p["criado_em"]),
            autor_nome=p["autor_nome"],
            total_curtidas=p["total_curtidas"],
            total_comentarios=p["total_comentarios"]
        )

    @strawberry.mutation(description="3. Comentar em uma publicação (N:M com atributo)")
    def comentar(self, usuario_id: int, post_id: int, texto: str) -> ComentarioType:
        c = repository.comentar(usuario_id=usuario_id, post_id=post_id, texto=texto)
        return ComentarioType(
            id=c["id"],
            usuario_id=c["usuario_id"],
            post_id=c["post_id"],
            texto=c["texto"],
            criado_em=str(c["criado_em"]),
            autor_nome=c["autor_nome"]
        )

    @strawberry.mutation(description="4. Curtir publicação (N:M puro)")
    def curtir(self, usuario_id: int, post_id: int) -> CurtidaResultadoType:
        r = repository.curtir(usuario_id=usuario_id, post_id=post_id)
        return CurtidaResultadoType(
            post_id=r["post_id"],
            usuario_id=r["usuario_id"],
            curtido=r["curtido"],
            total_curtidas=r["total_curtidas"]
        )

    @strawberry.mutation(description="5. Seguir usuário (N:M auto)")
    def seguir(self, usuario_id: int, alvo_id: int) -> SeguirResultadoType:
        r = repository.seguir(usuario_id=usuario_id, alvo_id=alvo_id)
        return SeguirResultadoType(
            seguidor_id=r["seguidor_id"],
            seguidor_nome=r["seguidor_nome"],
            alvo_id=r["alvo_id"],
            alvo_nome=r["alvo_nome"],
            seguindo=r["seguindo"]
        )


# =====================================================================
# SCHEMA E ROTEADOR FASTAPI
# =====================================================================

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)
