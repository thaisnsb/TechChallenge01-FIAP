from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from api.routers import auth, books

app = FastAPI(
    title="Tech Challenge - API Livros",
    description=(
        "API para gerenciamento e consulta de livros.\n\n"
        "🔹 **Passo 1**: Registre-se em `/auth/register`\n"
        "🔹 **Passo 2**: Faça login em `/auth/login`\n"
        "🔹 **Passo 3**: Use o token para acessar endpoints protegidos."
    ),
    version="1.0.0"
)

# 🚀 Redireciona a raiz para /docs
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

# 1️⃣ Autenticação primeiro
app.include_router(auth.router, prefix="/api/v1", tags=["01 - Autenticação"])

# 2️⃣ Depois os livros
app.include_router(books.router, prefix="/api/v1", tags=["02 - Livros"])
