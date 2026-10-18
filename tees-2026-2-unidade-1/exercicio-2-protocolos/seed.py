"""
Script para gerenciar o banco de dados SQLite (social.db):

1. Resetar o banco (apaga e recria tabelas vazias):
    python seed.py --reset

2. Popular o banco com dados fictícios:
    python seed.py
"""

import sys
import os
from core.database import init_db, get_db
from core import repository

def reset_db():
    print("🧹 Resetando banco de dados do zero...")
    db_file = os.environ.get("DB_PATH", "social.db")
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except Exception:
            pass
    init_db()
    print("✨ Banco de dados limpo e reinicializado com sucesso (tabelas criadas e vazias)!")
    print("💡 Para popular com os dados fictícios, execute: python seed.py")

def populate():
    print("🌱 Populando banco de dados com dados iniciais...")
    init_db()

    # 1. Criar Usuários e Perfis (1:1)
    u_alice = repository.criar_usuario(
        nome="Alice Silva",
        email="alice@email.com",
        bio="Engenheira de Software focada em arquitetura de microsserviços.",
        foto_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330"
    )
    u_bob = repository.criar_usuario(
        nome="Bob Santos",
        email="bob@email.com",
        bio="Desenvolvedor Frontend & entusiasta de GraphQL e TypeScript.",
        foto_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d"
    )
    u_charlie = repository.criar_usuario(
        nome="Charlie Lima",
        email="charlie@email.com",
        bio="Tech Lead e apaixonado por performance e protocolos de rede.",
        foto_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e"
    )
    print(f"  ✓ {u_alice['nome']} (ID {u_alice['id']}) criado.")
    print(f"  ✓ {u_bob['nome']} (ID {u_bob['id']}) criado.")
    print(f"  ✓ {u_charlie['nome']} (ID {u_charlie['id']}) criado.")

    # 2. Relações de Seguir (N:M auto)
    # Bob segue Alice e Charlie
    repository.seguir(u_bob["id"], u_alice["id"])
    repository.seguir(u_bob["id"], u_charlie["id"])
    # Charlie segue Alice
    repository.seguir(u_charlie["id"], u_alice["id"])
    # Alice segue Bob
    repository.seguir(u_alice["id"], u_bob["id"])
    print("  ✓ Relações de seguidores estabelecidas.")

    # 3. Criar Posts (1:N autor)
    p1 = repository.criar_post(
        usuario_id=u_alice["id"],
        texto="Comparando REST e GraphQL na prática: sintam a diferença de fazer 1 query declarativa vs múltiplos roundtrips!"
    )
    p2 = repository.criar_post(
        usuario_id=u_bob["id"],
        texto="Acabei de redesenhar a tela de feed usando o GraphQL. A experiência do cliente web melhorou 100%."
    )
    p3 = repository.criar_post(
        usuario_id=u_charlie["id"],
        texto="Em sistemas distribuídos de alta escala, o cache HTTP nativo do REST ainda é imbativel na borda."
    )
    print(f"  ✓ 3 postagens criadas (IDs: {p1['id']}, {p2['id']}, {p3['id']}).")

    # 4. Criar Comentários (N:M com atributo)
    c1 = repository.comentar(
        usuario_id=u_bob["id"],
        post_id=p1["id"],
        texto="Excelente ponto Alice! O fim do under-fetching é o maior benefício do GraphQL."
    )
    c2 = repository.comentar(
        usuario_id=u_charlie["id"],
        post_id=p1["id"],
        texto="Concordo, mas não esqueça da complexidade adicional no backend para evitar N+1!"
    )
    c3 = repository.comentar(
        usuario_id=u_alice["id"],
        post_id=p3["id"],
        texto="Com certeza, Charlie! Caching HTTP com ETag/Max-Age no REST é simples e robusto."
    )
    print("  ✓ Comentários inseridos nos posts.")

    # 5. Criar Curtidas (N:M puro)
    repository.curtir(u_bob["id"], p1["id"])
    repository.curtir(u_charlie["id"], p1["id"])
    repository.curtir(u_alice["id"], p2["id"])
    repository.curtir(u_bob["id"], p3["id"])
    print("  ✓ Curtidas registradas.")

    print("\n✨ Banco de dados populado com sucesso!")
    print("=" * 60)
    print("IDs de teste gerados:")
    print(f"  - Alice:   ID {u_alice['id']} (possui posts e comentários)")
    print(f"  - Bob:     ID {u_bob['id']} (segue Alice e Charlie, tem feed rico)")
    print(f"  - Charlie: ID {u_charlie['id']}")
    print("=" * 60)
    print("Pronto para testar em:")
    print("  - REST Swagger: http://localhost:8000/docs")
    print("  - GraphQL:      http://localhost:8000/graphql")

if __name__ == "__main__":
    if "--reset" in sys.argv:
        reset_db()
    else:
        try:
            populate()
        except Exception as e:
            if "UNIQUE constraint failed: usuarios.email" in str(e):
                print("⚠️ Os dados já existem no banco. Para resetar e recriar, use 'python seed.py --reset'.")
            else:
                raise e
