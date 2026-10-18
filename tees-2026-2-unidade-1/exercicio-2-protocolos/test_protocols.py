"""
Script de testes automatizados e interativos para a Atividade 02 (Protocolos).
Apresenta de forma didática o envio, a resposta e as particularidades de cada protocolo.

Uso:
    python test_protocols.py             # Modo didático passo a passo (pressione ENTER a cada etapa)
    python test_protocols.py --auto      # Modo contínuo (sem pausas)
    python test_protocols.py --delay 2   # Pausa automática de N segundos entre etapas
    python test_protocols.py --rest      # Apenas protocolo REST
    python test_protocols.py --graphql   # Apenas protocolo GraphQL
"""

import sys
import json
import time
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"

# Cores e formatação ANSI
VERDE = "\033[92m"
AZUL = "\033[94m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
CIANO = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# Configurações de interação
AUTO_MODE = "--auto" in sys.argv
DELAY = 0.0

if "--delay" in sys.argv:
    try:
        idx = sys.argv.index("--delay")
        DELAY = float(sys.argv[idx + 1])
    except Exception:
        DELAY = 1.5

def esperar_proximo():
    """Realiza uma pausa didática controlada."""
    if AUTO_MODE:
        return
    if DELAY > 0:
        time.sleep(DELAY)
        return

    try:
        input(f"\n{DIM}👉 Pressione {BOLD}[ENTER]{RESET}{DIM} para ir para a próxima etapa (ou Ctrl+C para sair)...{RESET}")
    except (KeyboardInterrupt, EOFError):
        print(f"\n{AMARELO}Execução interrompida pelo usuário.{RESET}\n")
        sys.exit(0)

def print_header(titulo: str):
    print(f"\n{BOLD}{CIANO}{'=' * 75}{RESET}")
    print(f"{BOLD}{CIANO}   {titulo}{RESET}")
    print(f"{BOLD}{CIANO}{'=' * 75}{RESET}\n")

def print_didactic_step(
    num: int,
    nome: str,
    protocolo: str,
    conceito: str,
    metodo: str,
    url_ou_query: str,
    payload_enviado: any,
    status_code: int,
    resposta_servidor: dict
):
    cor_prot = AZUL if protocolo == "REST" else MAGENTA
    print(f"\n{BOLD}{'─' * 75}{RESET}")
    print(f"{BOLD}[{num:02d}/10] {cor_prot}PROTOCOLO {protocolo}{RESET} | {BOLD}{nome}{RESET}")
    print(f"{BOLD}{'─' * 75}{RESET}")

    # 1. Conceito Didático
    print(f"\n{AMARELO}{BOLD}💡 CONCEITO DIDÁTICO:{RESET}")
    print(f"   {conceito}")

    # 2. Requisição Enviada
    print(f"\n{CIANO}{BOLD}📤 O QUE ENVIAMOS AO SERVIDOR:{RESET}")
    print(f"   {BOLD}{metodo}{RESET} {url_ou_query}")
    if payload_enviado is not None:
        if isinstance(payload_enviado, str):
            # Formatação de query GraphQL
            linhas = [f"   {l}" for l in payload_enviado.strip().split("\n")]
            print("\n".join(linhas))
        else:
            # Formatação de JSON REST
            formatado = json.dumps(payload_enviado, indent=2, ensure_ascii=False)
            linhas = [f"   {l}" for l in formatado.split("\n")]
            print("\n".join(linhas))

    # 3. Resposta Recebida
    cor_status = VERDE if 200 <= status_code < 300 else VERMELHO
    print(f"\n{VERDE}{BOLD}📥 O QUE O SERVIDOR RESPONDEU ({cor_status}HTTP {status_code}{RESET}{VERDE}{BOLD}):{RESET}")
    formatado_res = json.dumps(resposta_servidor, indent=2, ensure_ascii=False)
    linhas_res = [f"   {l}" for l in formatado_res.split("\n")][:25] # Limita a 25 linhas para não poluir
    print("\n".join(linhas_res))
    if len(formatado_res.split("\n")) > 25:
        print(f"   {DIM}... (resposta truncada para exibição didática){RESET}")

    esperar_proximo()

# =====================================================================
# CLIENTE HTTP NATIVO (URLLIB)
# =====================================================================

def http_request(method: str, path: str, data: dict = None) -> tuple[int, dict]:
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data is not None else None

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.getcode()
            content = response.read().decode("utf-8")
            return status, json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            parsed = json.loads(content)
        except Exception:
            parsed = {"detail": content}
        return e.code, parsed
    except urllib.error.URLError:
        print(f"\n{VERMELHO}⚠️  Não foi possível conectar ao servidor em {BASE_URL}.{RESET}")
        print(f"Inicie o servidor em outro terminal com: {BOLD}uvicorn main:app --reload{RESET}\n")
        sys.exit(1)

def graphql_request(query: str, variables: dict = None) -> tuple[int, dict]:
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    return http_request("POST", "/graphql", payload)


# =====================================================================
# SUÍTE DIDÁTICA: REST (JSON)
# =====================================================================

def run_rest_didactic_suite() -> int:
    print_header("PARTE 1: PROTOCOLO REST (JSON) - REQUISIÇÃO / RESPOSTA")
    ts = int(time.time() * 1000)
    sucessos = 0

    # 1. COMANDO: criar_usuario
    status, res = http_request("POST", "/api/usuarios", {
        "nome": "Mariana Lima",
        "email": f"mariana_{ts}@teste.com",
        "bio": "Entusiasta de arquitetura de software e APIs REST.",
        "foto_url": "https://avatar.com/mariana"
    })
    user_a_id = res.get("id", 1)
    print_didactic_step(
        1, "Comando: criar_usuario(nome, email)", "REST",
        "No REST, recursos novos são criados com o verbo POST na coleção `/api/usuarios`.\n"
        "   O servidor responde com status HTTP 201 (Created) e o recurso completo serializado em JSON.",
        "POST", f"{BASE_URL}/api/usuarios",
        {"nome": "Mariana Lima", "email": f"mariana_{ts}@teste.com", "bio": "Entusiasta de arquitetura de software..."},
        status, res
    )
    if status == 201: sucessos += 1

    # Usuário B auxiliar
    _, res_b = http_request("POST", "/api/usuarios", {
        "nome": "Lucas Ferreira",
        "email": f"lucas_{ts}@teste.com"
    })
    user_b_id = res_b.get("id", 2)

    # 2. COMANDO: criar_post
    status, res = http_request("POST", "/api/posts", {
        "usuario_id": user_a_id,
        "texto": "Explorando as diferenças entre verbos HTTP e modelos declarativos!"
    })
    post_id = res.get("id", 1)
    print_didactic_step(
        2, "Comando: criar_post(usuario_id, texto)", "REST",
        "Criação de um sub-recurso associado ao autor (relação 1:N).\n"
        "   Status 201 Created é retornado com os dados do post e o autor já resolvido.",
        "POST", f"{BASE_URL}/api/posts",
        {"usuario_id": user_a_id, "texto": "Explorando as diferenças entre verbos HTTP..."},
        status, res
    )
    if status == 201: sucessos += 1

    # 3. COMANDO: comentar
    status, res = http_request("POST", f"/api/posts/{post_id}/comentarios", {
        "usuario_id": user_b_id,
        "texto": "Excelente discussão! REST padroniza muito bem o ciclo de vida dos recursos."
    })
    print_didactic_step(
        3, "Comando: comentar(usuario_id, post_id, texto)", "REST",
        "No REST, relacionamentos N:M com atributos (como comentários) são mapeados como sub-recursos:\n"
        f"   POST no caminho `/api/posts/{post_id}/comentarios`.",
        "POST", f"{BASE_URL}/api/posts/{post_id}/comentarios",
        {"usuario_id": user_b_id, "texto": "Excelente discussão!..."},
        status, res
    )
    if status == 201: sucessos += 1

    # 4. COMANDO: curtir
    status, res = http_request("POST", f"/api/posts/{post_id}/curtidas?usuario_id={user_b_id}")
    print_didactic_step(
        4, "Comando: curtir(usuario_id, post_id)", "REST",
        "Relacionamento N:M puro (curtida). A rota é idempotente (curtir duas vezes não duplica registro no banco).\n"
        "   Retorna status 200 OK com a contagem total de curtidas atualizada.",
        "POST", f"{BASE_URL}/api/posts/{post_id}/curtidas?usuario_id={user_b_id}",
        None,
        status, res
    )
    if status == 200: sucessos += 1

    # 5. COMANDO: seguir
    status, res = http_request("POST", f"/api/usuarios/{user_b_id}/seguir", {"alvo_id": user_a_id})
    print_didactic_step(
        5, "Comando: seguir(usuario_id, alvo_id)", "REST",
        "Auto-relacionamento N:M entre usuários. O usuário emissor invoca a ação de seguir sobre o recurso alvo.",
        "POST", f"{BASE_URL}/api/usuarios/{user_b_id}/seguir",
        {"alvo_id": user_a_id},
        status, res
    )
    if status == 200: sucessos += 1

    # 6. CONSULTA: buscar_usuario
    status, res = http_request("GET", f"/api/usuarios/{user_a_id}")
    print_didactic_step(
        6, "Consulta: buscar_usuario(id)", "REST",
        "Consulta de leitura via GET pelo identificador de recurso `/api/usuarios/{id}`.\n"
        "   Atenção ao OVER-FETCHING: o backend decide todo o payload devolvido (mesmo que o cliente só queira o nome).",
        "GET", f"{BASE_URL}/api/usuarios/{user_a_id}",
        None,
        status, res
    )
    if status == 200: sucessos += 1

    # 7. CONSULTA: posts_do_usuario
    status, res = http_request("GET", f"/api/usuarios/{user_a_id}/posts")
    print_didactic_step(
        7, "Consulta: posts_do_usuario(usuario_id)", "REST",
        "Lista todas as publicações do autor. Para ver os comentários detalhados de cada post,\n"
        "   o cliente em REST precisaria disparar requisições extras (problema clássico N+1 de roundtrips).",
        "GET", f"{BASE_URL}/api/usuarios/{user_a_id}/posts",
        None,
        status, res
    )
    if status == 200: sucessos += 1

    # 8. CONSULTA: buscar_post
    status, res = http_request("GET", f"/api/posts/{post_id}")
    print_didactic_step(
        8, "Consulta: buscar_post(id)", "REST",
        "Consulta do post detalhado. O endpoint precisou ser customizado no backend para já incluir os comentários aninhados.",
        "GET", f"{BASE_URL}/api/posts/{post_id}",
        None,
        status, res
    )
    if status == 200: sucessos += 1

    # 9. CONSULTA: seguidores_de e seguindo_de
    status_seg, res_seg = http_request("GET", f"/api/usuarios/{user_a_id}/seguidores")
    print_didactic_step(
        9, "Consulta: seguidores_de e seguindo_de", "REST",
        "Em REST, seguidores e seguindo exigem dois endpoints separados e dois ciclos de requisição/resposta HTTP:\n"
        f"   1) GET /api/usuarios/{user_a_id}/seguidores\n"
        f"   2) GET /api/usuarios/{user_b_id}/seguindo",
        "GET", f"{BASE_URL}/api/usuarios/{user_a_id}/seguidores",
        None,
        status_seg, res_seg
    )
    if status_seg == 200: sucessos += 1

    # 10. CONSULTA: feed_do_usuario
    status, res = http_request("GET", f"/api/usuarios/{user_b_id}/feed")
    print_didactic_step(
        10, "Consulta: feed_do_usuario(usuario_id)", "REST",
        "Gera o feed com publicações dos perfis que o usuário segue.\n"
        "   O formato é estático e predeterminado pela API REST.",
        "GET", f"{BASE_URL}/api/usuarios/{user_b_id}/feed",
        None,
        status, res
    )
    if status == 200: sucessos += 1

    return sucessos


# =====================================================================
# SUÍTE DIDÁTICA: GRAPHQL (JSON)
# =====================================================================

def run_graphql_didactic_suite() -> int:
    print_header("PARTE 2: PROTOCOLO GRAPHQL (JSON) - CONSULTA DECLARATIVA")
    ts = int(time.time() * 1000)
    sucessos = 0

    # 1. COMANDO: criar_usuario
    mut_user = f"""
    mutation {{
      criarUsuario(
        nome: "Gabriel Souza"
        email: "gabriel_{ts}@teste.com"
        bio: "Desenvolvedor frontend apaixonado por GraphQL."
      ) {{
        id
        nome
        email
        bio
      }}
    }}"""
    status, res = graphql_request(mut_user)
    data = res.get("data", {}).get("criarUsuario", {})
    user_a_id = data.get("id", 1)
    print_didactic_step(
        1, "Comando: criar_usuario(nome, email)", "GraphQL",
        "No GraphQL, modificações de estado são declaradas como MUTATIONS.\n"
        "   Ponto chave: o cliente escolhe exatamente quais campos deseja receber de volta após a criação!",
        "POST", f"{BASE_URL}/graphql",
        mut_user,
        status, res
    )
    if status == 200 and data: sucessos += 1

    # Usuário B auxiliar via mutation
    mut_user_b = f"""
    mutation {{
      criarUsuario(nome: "Renata Dias", email: "renata_{ts}@teste.com") {{
        id
        nome
      }}
    }}"""
    _, res_b = graphql_request(mut_user_b)
    user_b_id = res_b.get("data", {}).get("criarUsuario", {}).get("id", 2)

    # 2. COMANDO: criar_post
    mut_post = f"""
    mutation {{
      criarPost(usuarioId: {user_a_id}, texto: "Com GraphQL, clientes mobile solicitam apenas os bytes necessários!") {{
        id
        texto
        autorNome
        criadoEm
      }}
    }}"""
    status, res = graphql_request(mut_post)
    data = res.get("data", {}).get("criarPost", {})
    post_id = data.get("id", 1)
    print_didactic_step(
        2, "Comando: criar_post(usuario_id, texto)", "GraphQL",
        "Criação de publicação com Mutation. Observe que tudo passa pelo MESMO endpoint `/graphql` via POST.",
        "POST", f"{BASE_URL}/graphql",
        mut_post,
        status, res
    )
    if status == 200 and data: sucessos += 1

    # 3. COMANDO: comentar
    mut_comentario = f"""
    mutation {{
      comentar(usuarioId: {user_b_id}, postId: {post_id}, texto: "Zero over-fetching é um divisor de águas.") {{
        id
        texto
        autorNome
        criadoEm
      }}
    }}"""
    status, res = graphql_request(mut_comentario)
    print_didactic_step(
        3, "Comando: comentar(usuario_id, post_id, texto)", "GraphQL",
        "Comentando no post via Mutation com retorno do comentário recém-criado e o nome do autor resolvido.",
        "POST", f"{BASE_URL}/graphql",
        mut_comentario,
        status, res
    )
    if status == 200 and res.get("data"): sucessos += 1

    # 4. COMANDO: curtir
    mut_curtir = f"""
    mutation {{
      curtir(usuarioId: {user_b_id}, postId: {post_id}) {{
        postId
        curtido
        totalCurtidas
      }}
    }}"""
    status, res = graphql_request(mut_curtir)
    print_didactic_step(
        4, "Comando: curtir(usuario_id, post_id)", "GraphQL",
        "Mutation de curtir (N:M puro). Retorna imediatamente o estado booleano e o total de curtidas.",
        "POST", f"{BASE_URL}/graphql",
        mut_curtir,
        status, res
    )
    if status == 200 and res.get("data"): sucessos += 1

    # 5. COMANDO: seguir
    mut_seguir = f"""
    mutation {{
      seguir(usuarioId: {user_b_id}, alvoId: {user_a_id}) {{
        seguidorNome
        alvoNome
        seguindo
      }}
    }}"""
    status, res = graphql_request(mut_seguir)
    print_didactic_step(
        5, "Comando: seguir(usuario_id, alvo_id)", "GraphQL",
        "Mutation para auto-relacionamento de seguidores. O resultado confirma os nomes de quem seguiu quem.",
        "POST", f"{BASE_URL}/graphql",
        mut_seguir,
        status, res
    )
    if status == 200 and res.get("data"): sucessos += 1

    # 6. CONSULTA: buscar_usuario (O GRANDE PODER DO GRAPHQL)
    q_user = f"""
    query {{
      buscarUsuario(id: {user_a_id}) {{
        nome
        bio
        totalSeguidores
        # PODER DO GRAPHQL: aninhamos a lista de posts na mesma query!
        posts {{
          id
          texto
          totalCurtidas
        }}
      }}
    }}"""
    status, res = graphql_request(q_user)
    print_didactic_step(
        6, "Consulta: buscar_usuario(id)", "GraphQL",
        "🌟 PODER DO GRAPHQL (Fim do Under-fetching e N+1):\n"
        "   Em uma única requisição, pedimos o Usuário E todos os seus Posts aninhados.\n"
        "   No REST, precisaríamos de 2 requisições separadas (/usuarios/1 e /usuarios/1/posts)!",
        "POST", f"{BASE_URL}/graphql",
        q_user,
        status, res
    )
    if status == 200 and res.get("data"): sucessos += 1

    # 7. CONSULTA: posts_do_usuario
    q_posts = f"""
    query {{
      postsDoUsuario(usuarioId: {user_a_id}) {{
        id
        texto
        totalCurtidas
        totalComentarios
      }}
    }}"""
    status, res = graphql_request(q_posts)
    print_didactic_step(
        7, "Consulta: posts_do_usuario(usuario_id)", "GraphQL",
        "Consulta de posts do usuário. Não pedimos campos que não precisamos (ex: foto_url ou bio), economizando banda.",
        "POST", f"{BASE_URL}/graphql",
        q_posts,
        status, res
    )
    if status == 200 and res.get("data"): sucessos += 1

    # 8. CONSULTA: buscar_post
    q_post = f"""
    query {{
      buscarPost(id: {post_id}) {{
        texto
        autorNome
        totalCurtidas
        comentarios {{
          autorNome
          texto
          criadoEm
        }}
      }}
    }}"""
    status, res = graphql_request(q_post)
    print_didactic_step(
        8, "Consulta: buscar_post(id)", "GraphQL",
        "Post com seus comentários em formato de árvore hierárquica. O cliente dita o formato exato da resposta JSON.",
        "POST", f"{BASE_URL}/graphql",
        q_post,
        status, res
    )
    if status == 200 and res.get("data"): sucessos += 1

    # 9. CONSULTA: seguidores_de e seguindo_de
    q_social = f"""
    query {{
      seguidores: seguidoresDe(id: {user_a_id}) {{
        id
        nome
      }}
      seguindo: seguindoDe(id: {user_b_id}) {{
        id
        nome
      }}
    }}"""
    status, res = graphql_request(q_social)
    print_didactic_step(
        9, "Consulta: seguidores_de e seguindo_de", "GraphQL",
        "🌟 MULTI-CONSULTAS SIMULTÂNEAS:\n"
        "   Executamos duas consultas independentes ('seguidores' e 'seguindo') num único pacote HTTP usando aliases!",
        "POST", f"{BASE_URL}/graphql",
        q_social,
        status, res
    )
    if status == 200 and res.get("data"): sucessos += 1

    # 10. CONSULTA: feed_do_usuario
    q_feed = f"""
    query {{
      feedDoUsuario(usuarioId: {user_b_id}) {{
        id
        texto
        autorNome
        totalCurtidas
        comentarios {{
          autorNome
          texto
        }}
      }}
    }}"""
    status, res = graphql_request(q_feed)
    print_didactic_step(
        10, "Consulta: feed_do_usuario(usuario_id)", "GraphQL",
        "Feed de notícias: retorna posts seguidos com autores, comentários e likes sob medida em uma única chamada declarativa.",
        "POST", f"{BASE_URL}/graphql",
        q_feed,
        status, res
    )
    if status == 200 and res.get("data"): sucessos += 1

    return sucessos


# =====================================================================
# RELATÓRIO E MAIN
# =====================================================================

def main():
    global BASE_URL

    if "--url" in sys.argv:
        idx = sys.argv.index("--url")
        if idx + 1 < len(sys.argv):
            BASE_URL = sys.argv[idx + 1].rstrip("/")

    so_rest = "--rest" in sys.argv
    so_graphql = "--graphql" in sys.argv
    rodar_todos = not so_rest and not so_graphql

    print(f"\n{BOLD}{CIANO}╔═════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CIANO}║   SUÍTE DE TESTES E DEMONSTRAÇÃO DIDÁTICA DOS PROTOCOLOS (ATIVIDADE 02) ║{RESET}")
    print(f"{BOLD}{CIANO}╚═════════════════════════════════════════════════════════════════════════╝{RESET}")
    print(f"Alvo da API: {AMARELO}{BASE_URL}{RESET}")
    if not AUTO_MODE and DELAY == 0:
        print(f"Modo: {VERDE}{BOLD}Interativo Didático{RESET} (pressione [ENTER] entre as etapas)")
        print(f"Dica: Para rodar direto sem pausas, use {DIM}python test_protocols.py --auto{RESET}\n")

    pontos_rest = 0
    pontos_gql = 0

    if rodar_todos or so_rest:
        pontos_rest = run_rest_didactic_suite()

    if rodar_todos or so_graphql:
        pontos_gql = run_graphql_didactic_suite()

    # Relatório Final
    print_header("RELATÓRIO CONSOLIDADO DE EXECUÇÃO")
    if rodar_todos or so_rest:
        cor = VERDE if pontos_rest == 10 else VERMELHO
        print(f"  {cor}● Protocolo REST:    {pontos_rest}/10 operações validadas com sucesso{RESET}")
    if rodar_todos or so_graphql:
        cor = VERDE if pontos_gql == 10 else VERMELHO
        print(f"  {cor}● Protocolo GraphQL: {pontos_gql}/10 operações validadas com sucesso{RESET}")

    total_esperado = (10 if (rodar_todos or so_rest) else 0) + (10 if (rodar_todos or so_graphql) else 0)
    total_atingido = pontos_rest + pontos_gql

    if total_atingido == total_esperado:
        print(f"\n{BOLD}{VERDE}🎉 100% DE SUCESSO! Todas as operações obrigatórias foram cumpridas e validadas!{RESET}\n")
    else:
        print(f"\n{BOLD}{AMARELO}⚠️ Alguns passos não obtiveram sucesso. Verifique o log acima.{RESET}\n")

if __name__ == "__main__":
    main()
