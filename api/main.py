from fastapi import FastAPI
from api.routers import auth as auth_router, books as books_router

app = FastAPI(
    title="TechChallenge API",
    version="1.0.0",
    description="API do TechChallenge para gerenciamento de livros, autenticação e estatísticas.",
    openapi_tags=[
        {
            "name": "Autenticação",
            "description": "🔑 Endpoints para cadastro e login de usuários"
        },
        {
            "name": "Endpoints Core",
            "description": "📚 Endpoints principais para consulta de livros e categorias"
        },
        {
            "name": "Endpoints de Insights",
            "description": "📊 Estatísticas e relatórios sobre os livros"
        },
        {
            "name": "Scraping",
            "description": "⚙️ Coleta e atualização de dados via scraping"
        }
    ]
)

app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Autenticação"])
app.include_router(books_router.router, prefix="/api/v1", tags=["Endpoints Core"])
