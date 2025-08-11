from fastapi import FastAPI, HTTPException
from api.routers import books as books_router, auth as auth_router
import os
import sqlite3
import uvicorn



# Define o caminho para o arquivo do banco de dados SQLite.
DB_BOOKS_FILE = os.path.join("data", "books.db")

# Função auxiliar para inicializar o banco de dados e criar a tabela de livros.
def init_books_db():
    if not os.path.exists('data'):
        os.makedirs('data')
    conn = sqlite3.connect(DB_BOOKS_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT,
            category TEXT,
            price REAL,
            rating INTEGER,
            is_in_stock BOOLEAN,
            availability_text TEXT,
            image_url TEXT,
            book_page_url TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

# Inicializa o banco de dados de livros.
init_books_db()

# Cria a instância principal da aplicação FastAPI.
app = FastAPI(
    title="Books API",
    description="API pública para consulta de livros, criada para o Tech Challenge.",
    version="1.0.0"
)


app.include_router(books_router.router, prefix="/api/v1")
app.include_router(books_router.router, prefix="/api/v1")
app.include_router(auth_router.router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["Endpoints Core"])
def health_check():
    """
    Verifica o status da API e a disponibilidade dos dados.
    """
    try:
        conn = sqlite3.connect(DB_BOOKS_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM books LIMIT 1")
        cursor.fetchone()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API está no ar, mas houve um erro ao acessar os dados: {e}")

    return {"status": "ok", "message": "API está no ar e os dados estão acessíveis."}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

