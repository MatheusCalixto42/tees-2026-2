# Atividade 02 - protocolos - Tópicos Especiais em Engenharia de Software


## Enunciado da atividade

Escolher dois protocolos entre REST, SOAP, GraphQL, gRPC e WebSockets, e expor o mesmo domínio nos dois. Pode ser em dois projetos separados, um para cada protocolo, ou num único projeto que fala os dois, a escolha é sua. A linguagem de programação também é livre, e pode ser diferente entre os dois protocolos.


| Protocolo | Formato | Modelo |
| --- | --- | --- |
| SOAP | XML | Requisição/resposta |
| **REST** | JSON | Requisição/resposta |
| **GraphQL** | JSON | Consulta declarativa |
| gRPC | Binário | Chamada de procedimento |
| WebSockets | Livre | Canal permanente |


### O Domínio: Rede Social

| Comandos | Consultas |
| --- | --- |
| criar_usuario(nome, email) | buscar_usuario(id) |
| criar_post(usuario_id, texto) | posts_do_usuario(usuario_id) |
| comentar(usuario_id, post_id, texto) | buscar_post(id) |
| curtir(usuario_id, post_id) | seguidores_de(id) / seguindo_de(id) |
| seguir(usuario_id, alvo_id) | feed_do_usuario(usuario_id) |

Os cinco comandos e as cinco consultas são obrigatórios nos dois protocolos escolhidos.

#### Modelagem do Banco de Dados (ER)

```mermaid
erDiagram
    USUARIO ||--|| PERFIL : "1 : 1"
    USUARIO ||--o{ POST : "1 : N (autor)"
    USUARIO }o--o{ USUARIO : "N : M auto (segue)"
    USUARIO ||--o{ COMENTARIO : "escreve"
    POST ||--o{ COMENTARIO : "recebe (N:M com atributo)"
    USUARIO ||--o{ CURTIDA : "curte"
    POST ||--o{ CURTIDA : "recebe (N:M puro)"

    USUARIO {
        int id PK
        string nome
        string email UK
        datetime criado_em
    }

    PERFIL {
        int id PK
        int usuario_id FK,UK "1:1 exclusivo"
        string bio
        string foto_url
    }

    POST {
        int id PK
        int usuario_id FK "autor"
        text texto
        datetime criado_em
    }

    SEGUE {
        int seguidor_id FK,PK "quem segue"
        int seguido_id FK,PK "alvo seguido"
        datetime criado_em
    }

    COMENTARIO {
        int id PK
        int usuario_id FK
        int post_id FK
        text texto "atributo do N:M"
        datetime criado_em
    }

    CURTIDA {
        int usuario_id FK,PK
        int post_id FK,PK
        datetime criado_em
    }
```


### Requisitos

1. Os cinco comandos e as consultas buscar_usuario, posts_do_usuario, buscar_post e seguidores_de/seguindo_de, ou o equivalente no protocolo.
2. Exemplo de requisição e de resposta, copiável, para cada operação.
3. Instruções para executar, do zero.
4. Uma linha dizendo o que esse protocolo faz melhor que o outro escolhido, nesse domínio.


### Entrega

```bash
tees-2026-2-unidade-1/ 
└── exercicio-2-protocolos/ 
    ├── README.md visão geral + a comparação final 
    ├── <protocolo-a>/ README próprio 
    └── <protocolo-b>/ README próprio
```

Nome da pasta conforme o protocolo, por exemplo rest-json/, soap-xml/, graphql/, grpc/ ou websockets/. Essa é a estrutura para dois projetos separados, num projeto único adapte as pastas, mas mantenha os dois protocolos separados e identificáveis, e o README.md continua trazendo a comparação final.


## O que foi feito

### Escolha de Protocolos

#### REST - JSON

#### GraphQL - JSON

### Estrutura de Pastas

