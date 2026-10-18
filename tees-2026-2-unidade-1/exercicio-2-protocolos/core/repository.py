from typing import List, Optional, Dict, Any
from core.database import get_db

# =====================================================================
# COMANDOS (Escrita / Modificação de Estado)
# =====================================================================

def criar_usuario(nome: str, email: str, bio: str = "", foto_url: str = "", db_path: str = None) -> Dict[str, Any]:
    """Cria um novo usuário e inicializa seu perfil 1:1."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO usuarios (nome, email) VALUES (?, ?);",
                (nome.strip(), email.strip().lower())
            )
            usuario_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO perfis (usuario_id, bio, foto_url) VALUES (?, ?, ?);",
                (usuario_id, bio.strip(), foto_url.strip())
            )
        except Exception as e:
            if "UNIQUE constraint failed: usuarios.email" in str(e):
                raise ValueError(f"Email '{email}' já está em uso.")
            raise
    return buscar_usuario(usuario_id, db_path=db_path)

def criar_post(usuario_id: int, texto: str, db_path: str = None) -> Dict[str, Any]:
    """Cria uma nova publicação para o usuário."""
    if not texto.strip():
        raise ValueError("O texto do post não pode ser vazio.")
    
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        # Verificar se usuário existe
        cursor.execute("SELECT id FROM usuarios WHERE id = ?;", (usuario_id,))
        if not cursor.fetchone():
            raise ValueError(f"Usuário com ID {usuario_id} não encontrado.")

        cursor.execute(
            "INSERT INTO posts (usuario_id, texto) VALUES (?, ?);",
            (usuario_id, texto.strip())
        )
        post_id = cursor.lastrowid
    return buscar_post(post_id, db_path=db_path)

def comentar(usuario_id: int, post_id: int, texto: str, db_path: str = None) -> Dict[str, Any]:
    """Adiciona um comentário a uma publicação (relacionamento N:M com atributo)."""
    if not texto.strip():
        raise ValueError("O comentário não pode ser vazio.")

    with get_db(db_path) as conn:
        cursor = conn.cursor()
        # Validar existência do usuário
        cursor.execute("SELECT nome FROM usuarios WHERE id = ?;", (usuario_id,))
        user_row = cursor.fetchone()
        if not user_row:
            raise ValueError(f"Usuário com ID {usuario_id} não encontrado.")

        # Validar existência do post
        cursor.execute("SELECT id FROM posts WHERE id = ?;", (post_id,))
        if not cursor.fetchone():
            raise ValueError(f"Post com ID {post_id} não encontrado.")

        cursor.execute(
            "INSERT INTO comentarios (usuario_id, post_id, texto) VALUES (?, ?, ?);",
            (usuario_id, post_id, texto.strip())
        )
        comentario_id = cursor.lastrowid
        cursor.execute(
            "SELECT id, usuario_id, post_id, texto, criado_em FROM comentarios WHERE id = ?;",
            (comentario_id,)
        )
        row = dict(cursor.fetchone())
        row["autor_nome"] = user_row["nome"]
        return row

def curtir(usuario_id: int, post_id: int, db_path: str = None) -> Dict[str, Any]:
    """Adiciona uma curtida em uma publicação (relacionamento N:M puro, idempotente)."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        # Validar usuário
        cursor.execute("SELECT id FROM usuarios WHERE id = ?;", (usuario_id,))
        if not cursor.fetchone():
            raise ValueError(f"Usuário com ID {usuario_id} não encontrado.")

        # Validar post
        cursor.execute("SELECT id FROM posts WHERE id = ?;", (post_id,))
        if not cursor.fetchone():
            raise ValueError(f"Post com ID {post_id} não encontrado.")

        cursor.execute(
            "INSERT OR IGNORE INTO curtidas (usuario_id, post_id) VALUES (?, ?);",
            (usuario_id, post_id)
        )

        cursor.execute("SELECT COUNT(*) AS total FROM curtidas WHERE post_id = ?;", (post_id,))
        total = cursor.fetchone()["total"]

        return {
            "post_id": post_id,
            "usuario_id": usuario_id,
            "curtido": True,
            "total_curtidas": total
        }

def seguir(usuario_id: int, alvo_id: int, db_path: str = None) -> Dict[str, Any]:
    """Cria uma relação de seguidor/seguido entre dois usuários (N:M auto)."""
    if usuario_id == alvo_id:
        raise ValueError("Um usuário não pode seguir a si mesmo.")

    with get_db(db_path) as conn:
        cursor = conn.cursor()
        # Validar ambos os usuários
        cursor.execute("SELECT id, nome FROM usuarios WHERE id = ?;", (usuario_id,))
        seguidor = cursor.fetchone()
        if not seguidor:
            raise ValueError(f"Usuário com ID {usuario_id} não encontrado.")

        cursor.execute("SELECT id, nome FROM usuarios WHERE id = ?;", (alvo_id,))
        alvo = cursor.fetchone()
        if not alvo:
            raise ValueError(f"Usuário alvo com ID {alvo_id} não encontrado.")

        cursor.execute(
            "INSERT OR IGNORE INTO segue (seguidor_id, seguido_id) VALUES (?, ?);",
            (usuario_id, alvo_id)
        )

        return {
            "seguidor_id": usuario_id,
            "seguidor_nome": seguidor["nome"],
            "alvo_id": alvo_id,
            "alvo_nome": alvo["nome"],
            "seguindo": True
        }


# =====================================================================
# CONSULTAS (Leitura de Dados)
# =====================================================================

def buscar_usuario(usuario_id: int, db_path: str = None) -> Optional[Dict[str, Any]]:
    """Consulta os dados de um usuário, seu perfil (1:1) e contadores."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.nome, u.email, u.criado_em,
                   COALESCE(p.bio, '') AS bio,
                   COALESCE(p.foto_url, '') AS foto_url
            FROM usuarios u
            LEFT JOIN perfis p ON p.usuario_id = u.id
            WHERE u.id = ?;
        """, (usuario_id,))
        row = cursor.fetchone()
        if not row:
            return None

        data = dict(row)

        # Contagens auxiliares
        cursor.execute("SELECT COUNT(*) AS total FROM segue WHERE seguido_id = ?;", (usuario_id,))
        data["total_seguidores"] = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM segue WHERE seguidor_id = ?;", (usuario_id,))
        data["total_seguindo"] = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM posts WHERE usuario_id = ?;", (usuario_id,))
        data["total_posts"] = cursor.fetchone()["total"]

        return data

def posts_do_usuario(usuario_id: int, db_path: str = None) -> List[Dict[str, Any]]:
    """Lista todas as postagens publicadas por um determinado usuário."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.usuario_id, p.texto, p.criado_em,
                   u.nome AS autor_nome,
                   (SELECT COUNT(*) FROM curtidas c WHERE c.post_id = p.id) AS total_curtidas,
                   (SELECT COUNT(*) FROM comentarios com WHERE com.post_id = p.id) AS total_comentarios
            FROM posts p
            JOIN usuarios u ON u.id = p.usuario_id
            WHERE p.usuario_id = ?
            ORDER BY p.criado_em DESC;
        """, (usuario_id,))
        return [dict(r) for r in cursor.fetchall()]

def buscar_post(post_id: int, db_path: str = None) -> Optional[Dict[str, Any]]:
    """Consulta uma postagem específica com autor, curtidas e comentários."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.usuario_id, p.texto, p.criado_em,
                   u.nome AS autor_nome,
                   (SELECT COUNT(*) FROM curtidas c WHERE c.post_id = p.id) AS total_curtidas
            FROM posts p
            JOIN usuarios u ON u.id = p.usuario_id
            WHERE p.id = ?;
        """, (post_id,))
        row = cursor.fetchone()
        if not row:
            return None

        post_data = dict(row)

        # Buscar comentários associados
        cursor.execute("""
            SELECT c.id, c.usuario_id, c.post_id, c.texto, c.criado_em,
                   u.nome AS autor_nome
            FROM comentarios c
            JOIN usuarios u ON u.id = c.usuario_id
            WHERE c.post_id = ?
            ORDER BY c.criado_em ASC;
        """, (post_id,))
        post_data["comentarios"] = [dict(c) for c in cursor.fetchall()]
        post_data["total_comentarios"] = len(post_data["comentarios"])

        return post_data

def seguidores_de(usuario_id: int, db_path: str = None) -> List[Dict[str, Any]]:
    """Lista quem segue o usuário especificado."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.nome, u.email, COALESCE(p.bio, '') AS bio, s.criado_em AS seguido_desde
            FROM usuarios u
            JOIN segue s ON s.seguidor_id = u.id
            LEFT JOIN perfis p ON p.usuario_id = u.id
            WHERE s.seguido_id = ?
            ORDER BY s.criado_em DESC;
        """, (usuario_id,))
        return [dict(r) for r in cursor.fetchall()]

def seguindo_de(usuario_id: int, db_path: str = None) -> List[Dict[str, Any]]:
    """Lista quem o usuário especificado está seguindo."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.nome, u.email, COALESCE(p.bio, '') AS bio, s.criado_em AS seguido_desde
            FROM usuarios u
            JOIN segue s ON s.seguido_id = u.id
            LEFT JOIN perfis p ON p.usuario_id = u.id
            WHERE s.seguidor_id = ?
            ORDER BY s.criado_em DESC;
        """, (usuario_id,))
        return [dict(r) for r in cursor.fetchall()]

def feed_do_usuario(usuario_id: int, db_path: str = None) -> List[Dict[str, Any]]:
    """Gera o feed cronológico com as postagens de todos os usuários seguidos."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.usuario_id, p.texto, p.criado_em,
                   u.nome AS autor_nome,
                   (SELECT COUNT(*) FROM curtidas c WHERE c.post_id = p.id) AS total_curtidas,
                   (SELECT COUNT(*) FROM comentarios com WHERE com.post_id = p.id) AS total_comentarios
            FROM posts p
            JOIN segue s ON s.seguido_id = p.usuario_id
            JOIN usuarios u ON u.id = p.usuario_id
            WHERE s.seguidor_id = ?
            ORDER BY p.criado_em DESC;
        """, (usuario_id,))
        return [dict(r) for r in cursor.fetchall()]
