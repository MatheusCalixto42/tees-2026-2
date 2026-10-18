# Protocolo REST (JSON)

Implementação do protocolo **REST** utilizando o formato **JSON** e transporte HTTP/1.1 para o domínio de Rede Social.

> **O que o REST faz melhor que o GraphQL neste domínio:**  
> O REST oferece simplicidade arquitetural máxima, padronização universal com verbos HTTP e se beneficia nativamente do ecossistema de **cache HTTP na borda** para recursos que mudam pouco (como fotos de perfil e dados cadastrais), sem necessidade de interpretar parsers de consultas.

* **Base URL:** `http://localhost:8000/api`
* **Swagger UI Interativo:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 1. Comandos (Escrita)

> Caso queira executar esses testes automaticamente, use o comando:

```bash
python test_protocols.py --rest
```

### 1.1 `criar_usuario(nome, email)`
Cria um novo usuário e inicializa seu perfil 1:1.

* **Requisição:**
```bash
curl -X POST "http://localhost:8000/api/usuarios" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Mariana Lima",
    "email": "mariana@teste.com",
    "bio": "Entusiasta de arquitetura de software e APIs REST.",
    "foto_url": "https://avatar.com/mariana"
  }'
```

* **Resposta (`201 Created`):**
```json
{
  "id": 1,
  "nome": "Mariana Lima",
  "email": "mariana@teste.com",
  "criado_em": "2026-10-18 12:00:00",
  "bio": "Entusiasta de arquitetura de software e APIs REST.",
  "foto_url": "https://avatar.com/mariana",
  "total_seguidores": 0,
  "total_seguindo": 0,
  "total_posts": 0
}
```

---

### 1.2 `criar_post(usuario_id, texto)`
Cria uma nova publicação vinculada ao autor (relação 1:N).

* **Requisição:**
```bash
curl -X POST "http://localhost:8000/api/posts" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 1,
    "texto": "Explorando as diferenças entre verbos HTTP e modelos declarativos!"
  }'
```

* **Resposta (`201 Created`):**
```json
{
  "id": 1,
  "usuario_id": 1,
  "texto": "Explorando as diferenças entre verbos HTTP e modelos declarativos!",
  "criado_em": "2026-10-18 12:05:00",
  "autor_nome": "Mariana Lima",
  "total_curtidas": 0,
  "total_comentarios": 0,
  "comentarios": []
}
```

---

### 1.3 `comentar(usuario_id, post_id, texto)`
Adiciona um comentário a uma publicação (relacionamento N:M com atributo).

* **Requisição:**
```bash
curl -X POST "http://localhost:8000/api/posts/1/comentarios" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 2,
    "texto": "Excelente discussão! REST padroniza muito bem o ciclo de vida dos recursos."
  }'
```

* **Resposta (`201 Created`):**
```json
{
  "id": 1,
  "usuario_id": 2,
  "post_id": 1,
  "texto": "Excelente discussão! REST padroniza muito bem o ciclo de vida dos recursos.",
  "criado_em": "2026-10-18 12:10:00",
  "autor_nome": "Lucas Ferreira"
}
```

---

### 1.4 `curtir(usuario_id, post_id)`
Registra uma curtida em uma publicação (relacionamento N:M puro, idempotente).

* **Requisição:**
```bash
curl -X POST "http://localhost:8000/api/posts/1/curtidas?usuario_id=2"
```

* **Resposta (`200 OK`):**
```json
{
  "post_id": 1,
  "usuario_id": 2,
  "curtido": true,
  "total_curtidas": 1
}
```

---

### 1.5 `seguir(usuario_id, alvo_id)`
Cria uma relação de seguidor/seguido entre usuários (relacionamento N:M auto).

* **Requisição:**
```bash
curl -X POST "http://localhost:8000/api/usuarios/2/seguir" \
  -H "Content-Type: application/json" \
  -d '{
    "alvo_id": 1
  }'
```

* **Resposta (`200 OK`):**
```json
{
  "seguidor_id": 2,
  "seguidor_nome": "Lucas Ferreira",
  "alvo_id": 1,
  "alvo_nome": "Mariana Lima",
  "seguindo": true
}
```

---

## 2. Consultas (Leitura)

### 2.1 `buscar_usuario(id)`
Recupera os dados completos do usuário, seu perfil 1:1 e contadores.

* **Requisição:**
```bash
curl -X GET "http://localhost:8000/api/usuarios/1"
```

* **Resposta (`200 OK`):**
```json
{
  "id": 1,
  "nome": "Mariana Lima",
  "email": "mariana@teste.com",
  "criado_em": "2026-10-18 12:00:00",
  "bio": "Entusiasta de arquitetura de software e APIs REST.",
  "foto_url": "https://avatar.com/mariana",
  "total_seguidores": 1,
  "total_seguindo": 0,
  "total_posts": 1
}
```

---

### 2.2 `posts_do_usuario(usuario_id)`
Lista todas as publicações de um determinado usuário autor.

* **Requisição:**
```bash
curl -X GET "http://localhost:8000/api/usuarios/1/posts"
```

* **Resposta (`200 OK`):**
```json
[
  {
    "id": 1,
    "usuario_id": 1,
    "texto": "Explorando as diferenças entre verbos HTTP e modelos declarativos!",
    "criado_em": "2026-10-18 12:05:00",
    "autor_nome": "Mariana Lima",
    "total_curtidas": 1,
    "total_comentarios": 1
  }
]
```

---

### 2.3 `buscar_post(id)`
Consulta uma publicação específica com lista de comentários e contagem de curtidas.

* **Requisição:**
```bash
curl -X GET "http://localhost:8000/api/posts/1"
```

* **Resposta (`200 OK`):**
```json
{
  "id": 1,
  "usuario_id": 1,
  "texto": "Explorando as diferenças entre verbos HTTP e modelos declarativos!",
  "criado_em": "2026-10-18 12:05:00",
  "autor_nome": "Mariana Lima",
  "total_curtidas": 1,
  "total_comentarios": 1,
  "comentarios": [
    {
      "id": 1,
      "usuario_id": 2,
      "post_id": 1,
      "texto": "Excelente discussão! REST padroniza muito bem o ciclo de vida dos recursos.",
      "criado_em": "2026-10-18 12:10:00",
      "autor_nome": "Lucas Ferreira"
    }
  ]
}
```

---

### 2.4 `seguidores_de(id)` e `seguindo_de(id)`
Lista quem segue o usuário e quem o usuário está seguindo.

* **Requisição (Seguidores de 1):**
```bash
curl -X GET "http://localhost:8000/api/usuarios/1/seguidores"
```
* **Resposta (`200 OK`):**
```json
[
  {
    "id": 2,
    "nome": "Lucas Ferreira",
    "email": "lucas@teste.com",
    "bio": "",
    "seguido_desde": "2026-10-18 12:15:00"
  }
]
```

* **Requisição (Quem 2 está seguindo):**
```bash
curl -X GET "http://localhost:8000/api/usuarios/2/seguindo"
```
* **Resposta (`200 OK`):**
```json
[
  {
    "id": 1,
    "nome": "Mariana Lima",
    "email": "mariana@teste.com",
    "bio": "Entusiasta de arquitetura de software e APIs REST.",
    "seguido_desde": "2026-10-18 12:15:00"
  }
]
```

---

### 2.5 `feed_do_usuario(usuario_id)`
Gera o feed cronológico composto pelas publicações dos perfis seguidos.

* **Requisição:**
```bash
curl -X GET "http://localhost:8000/api/usuarios/2/feed"
```

* **Resposta (`200 OK`):**
```json
[
  {
    "id": 1,
    "usuario_id": 1,
    "texto": "Explorando as diferenças entre verbos HTTP e modelos declarativos!",
    "criado_em": "2026-10-18 12:05:00",
    "autor_nome": "Mariana Lima",
    "total_curtidas": 1,
    "total_comentarios": 1
  }
]
```
