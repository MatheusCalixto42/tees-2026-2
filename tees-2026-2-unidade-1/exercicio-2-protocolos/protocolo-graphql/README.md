# Protocolo GraphQL (JSON)

Implementação do protocolo **GraphQL** utilizando formato **JSON** e transporte HTTP/1.1 para o domínio de Rede Social.

> **O que o GraphQL faz melhor que o REST neste domínio:**  
> O GraphQL permite que o cliente declare em **uma única requisição** exatamente a árvore de dados relacional necessária (ex: post, autor, contagem de curtidas e comentários com seus respectivos autores), **eliminando completamente o problema de under-fetching (N+1 roundtrips) e o over-fetching** de dados no feed da rede social.

* **Endpoint Único:** `http://localhost:8000/graphql`
* **GraphiQL Playground Interativo:** [http://localhost:8000/graphql](http://localhost:8000/graphql)

---

## 1. Comandos (Mutações)

> Caso queira executar esses testes automaticamente, use o comando:

```bash
python test_protocols.py --graphql
```

### 1.1 `criar_usuario(nome, email)`
Cria um novo usuário e inicializa seu perfil 1:1, permitindo escolher os campos de retorno.

* **Requisição (GraphQL):**
```graphql
mutation {
  criarUsuario(
    nome: "Gabriel Souza"
    email: "gabriel@teste.com"
    bio: "Desenvolvedor frontend apaixonado por GraphQL."
  ) {
    id
    nome
    email
    bio
  }
}
```

* **Exemplo via cURL:**
```bash
curl -X POST "http://localhost:8000/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { criarUsuario(nome: \"Gabriel Souza\", email: \"gabriel@teste.com\", bio: \"Desenvolvedor frontend apaixonado por GraphQL.\") { id nome email bio } }"}'
```

* **Resposta (`200 OK`):**
```json
{
  "data": {
    "criarUsuario": {
      "id": 1,
      "nome": "Gabriel Souza",
      "email": "gabriel@teste.com",
      "bio": "Desenvolvedor frontend apaixonado por GraphQL."
    }
  }
}
```

---

### 1.2 `criar_post(usuario_id, texto)`
Cria uma nova publicação vinculada ao autor (relação 1:N).

* **Requisição (GraphQL):**
```graphql
mutation {
  criarPost(
    usuarioId: 1
    texto: "Com GraphQL, clientes mobile solicitam apenas os bytes necessários!"
  ) {
    id
    texto
    autorNome
    criadoEm
  }
}
```

* **Exemplo via cURL:**
```bash
curl -X POST "http://localhost:8000/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { criarPost(usuarioId: 1, texto: \"Com GraphQL, clientes mobile solicitam apenas os bytes necessários!\") { id texto autorNome criadoEm } }"}'
```

* **Resposta (`200 OK`):**
```json
{
  "data": {
    "criarPost": {
      "id": 1,
      "texto": "Com GraphQL, clientes mobile solicitam apenas os bytes necessários!",
      "autorNome": "Gabriel Souza",
      "criadoEm": "2026-10-18 12:05:00"
    }
  }
}
```

---

### 1.3 `comentar(usuario_id, post_id, texto)`
Adiciona um comentário a uma publicação (relacionamento N:M com atributo).

* **Requisição (GraphQL):**
```graphql
mutation {
  comentar(
    usuarioId: 2
    postId: 1
    texto: "Zero over-fetching é um divisor de águas."
  ) {
    id
    texto
    autorNome
    criadoEm
  }
}
```

* **Exemplo via cURL:**
```bash
curl -X POST "http://localhost:8000/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { comentar(usuarioId: 2, postId: 1, texto: \"Zero over-fetching é um divisor de águas.\") { id texto autorNome criadoEm } }"}'
```

* **Resposta (`200 OK`):**
```json
{
  "data": {
    "comentar": {
      "id": 1,
      "texto": "Zero over-fetching é um divisor de águas.",
      "autorNome": "Renata Dias",
      "criadoEm": "2026-10-18 12:10:00"
    }
  }
}
```

---

### 1.4 `curtir(usuario_id, post_id)`
Registra uma curtida em uma publicação (relacionamento N:M puro, idempotente).

* **Requisição (GraphQL):**
```graphql
mutation {
  curtir(usuarioId: 2, postId: 1) {
    postId
    curtido
    totalCurtidas
  }
}
```

* **Exemplo via cURL:**
```bash
curl -X POST "http://localhost:8000/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { curtir(usuarioId: 2, postId: 1) { postId curtido totalCurtidas } }"}'
```

* **Resposta (`200 OK`):**
```json
{
  "data": {
    "curtir": {
      "postId": 1,
      "curtido": true,
      "totalCurtidas": 1
    }
  }
}
```

---

### 1.5 `seguir(usuario_id, alvo_id)`
Cria uma relação de seguidor/seguido entre usuários (relacionamento N:M auto).

* **Requisição (GraphQL):**
```graphql
mutation {
  seguir(usuarioId: 2, alvoId: 1) {
    seguidorNome
    alvoNome
    seguindo
  }
}
```

* **Exemplo via cURL:**
```bash
curl -X POST "http://localhost:8000/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { seguir(usuarioId: 2, alvoId: 1) { seguidorNome alvoNome seguindo } }"}'
```

* **Resposta (`200 OK`):**
```json
{
  "data": {
    "seguir": {
      "seguidorNome": "Renata Dias",
      "alvoNome": "Gabriel Souza",
      "seguindo": true
    }
  }
}
```

---

## 2. Consultas (Leitura)

### 2.1 `buscar_usuario(id)`
Recupera dados do usuário, perfil 1:1 e permite aninhar seus posts em uma única requisição.

* **Requisição (GraphQL):**
```graphql
query {
  buscarUsuario(id: 1) {
    nome
    bio
    totalSeguidores
    posts {
      id
      texto
      totalCurtidas
    }
  }
}
```

* **Exemplo via cURL:**
```bash
curl -X POST "http://localhost:8000/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "query { buscarUsuario(id: 1) { nome bio totalSeguidores posts { id texto totalCurtidas } } }"}'
```

* **Resposta (`200 OK`):**
```json
{
  "data": {
    "buscarUsuario": {
      "nome": "Gabriel Souza",
      "bio": "Desenvolvedor frontend apaixonado por GraphQL.",
      "totalSeguidores": 1,
      "posts": [
        {
          "id": 1,
          "texto": "Com GraphQL, clientes mobile solicitam apenas os bytes necessários!",
          "totalCurtidas": 1
        }
      ]
    }
  }
}
```

---

### 2.2 `posts_do_usuario(usuario_id)`
Lista todas as publicações de um autor específico selecionando apenas os campos desejados.

* **Requisição (GraphQL):**
```graphql
query {
  postsDoUsuario(usuarioId: 1) {
    id
    texto
    totalCurtidas
    totalComentarios
  }
}
```

* **Exemplo via cURL:**
```bash
curl -X POST "http://localhost:8000/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "query { postsDoUsuario(usuarioId: 1) { id texto totalCurtidas totalComentarios } }"}'
```

* **Resposta (`200 OK`):**
```json
{
  "data": {
    "postsDoUsuario": [
      {
        "id": 1,
        "texto": "Com GraphQL, clientes mobile solicitam apenas os bytes necessários!",
        "totalCurtidas": 1,
        "totalComentarios": 1
      }
    ]
  }
}
```

---

### 2.3 `buscar_post(id)`
Consulta uma publicação específica trazendo comentários e autores aninhados em formato de árvore.

* **Requisição (GraphQL):**
```graphql
query {
  buscarPost(id: 1) {
    texto
    autorNome
    totalCurtidas
    comentarios {
      autorNome
      texto
      criadoEm
    }
  }
}
```

* **Exemplo via cURL:**
```bash
curl -X POST "http://localhost:8000/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "query { buscarPost(id: 1) { texto autorNome totalCurtidas comentarios { autorNome texto criadoEm } } }"}'
```

* **Resposta (`200 OK`):**
```json
{
  "data": {
    "buscarPost": {
      "texto": "Com GraphQL, clientes mobile solicitam apenas os bytes necessários!",
      "autorNome": "Gabriel Souza",
      "totalCurtidas": 1,
      "comentarios": [
        {
          "autorNome": "Renata Dias",
          "texto": "Zero over-fetching é um divisor de águas.",
          "criadoEm": "2026-10-18 12:10:00"
        }
      ]
    }
  }
}
```

---

### 2.4 `seguidores_de(id)` e `seguindo_de(id)`
Executa duas consultas distintas em **uma única requisição HTTP** utilizando aliases.

* **Requisição (GraphQL):**
```graphql
query {
  seguidores: seguidoresDe(id: 1) {
    id
    nome
  }
  seguindo: seguindoDe(id: 2) {
    id
    nome
  }
}
```

* **Exemplo via cURL:**
```bash
curl -X POST "http://localhost:8000/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "query { seguidores: seguidoresDe(id: 1) { id nome } seguindo: seguindoDe(id: 2) { id nome } }"}'
```

* **Resposta (`200 OK`):**
```json
{
  "data": {
    "seguidores": [
      {
        "id": 2,
        "nome": "Renata Dias"
      }
    ],
    "seguindo": [
      {
        "id": 1,
        "nome": "Gabriel Souza"
      }
    ]
  }
}
```

---

### 2.5 `feed_do_usuario(usuario_id)`
Gera o feed sob medida com publicações dos perfis seguidos, autor e comentários em um só payload.

* **Requisição (GraphQL):**
```graphql
query {
  feedDoUsuario(usuarioId: 2) {
    id
    texto
    autorNome
    totalCurtidas
    comentarios {
      autorNome
      texto
    }
  }
}
```

* **Exemplo via cURL:**
```bash
curl -X POST "http://localhost:8000/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "query { feedDoUsuario(usuarioId: 2) { id texto autorNome totalCurtidas comentarios { autorNome texto } } }"}'
```

* **Resposta (`200 OK`):**
```json
{
  "data": {
    "feedDoUsuario": [
      {
        "id": 1,
        "texto": "Com GraphQL, clientes mobile solicitam apenas os bytes necessários!",
        "autorNome": "Gabriel Souza",
        "totalCurtidas": 1,
        "comentarios": [
          {
            "autorNome": "Renata Dias",
            "texto": "Zero over-fetching é um divisor de águas."
          }
        ]
      }
    ]
  }
}
```
