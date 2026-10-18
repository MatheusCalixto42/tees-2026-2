import importlib
from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa o banco de dados e cria as tabelas DDL no startup
    init_db()
    yield

app = FastAPI(
    title="Rede Social API - Atividade 02",
    description="Comparação de protocolos (REST e GraphQL) expondo o mesmo domínio de Rede Social.",
    version="1.0.0",
    lifespan=lifespan
)

# Registro do Protocolo REST
rest_module = importlib.import_module("protocolo-rest.routes")
app.include_router(rest_module.router)

# Registro do Protocolo GraphQL
graphql_module = importlib.import_module("protocolo-graphql.schema")
app.include_router(graphql_module.graphql_app, prefix="/graphql")

@app.get("/", tags=["Root"])
def root():
    return {
        "mensagem": "API de Rede Social ativa!",
        "documentacao_rest": "/docs",
        "interface_graphql": "/graphql"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
