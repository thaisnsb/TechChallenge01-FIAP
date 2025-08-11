from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional
import pandas as pd
import sqlite3
from api.routers.auth import get_current_user

router = APIRouter()

# ===============================
# Função de conexão com o banco
# ===============================
def get_db_connection():
    conn = sqlite3.connect("data/books.db")
    conn.row_factory = sqlite3.Row
    return conn

# ===============================
# Endpoints Core
# ===============================

# 🔹 Endpoints com caminho fixo primeiro para evitar conflito
@router.get("/books/search", tags=["Endpoints Core"])
def search_books(
    title: Optional[str] = Query(None, description="Título do livro"),
    category: Optional[str] = Query(None, description="Categoria do livro")
):
    if title is None and category is None:
        raise HTTPException(status_code=422, detail="Informe ao menos um parâmetro de busca (title ou category)")

    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM books", conn)
    conn.close()

    if title:
        df = df[df["title"].str.contains(title, case=False, na=False)]
    if category:
        df = df[df["category"].str.contains(category, case=False, na=False)]

    return df.to_dict(orient="records")

@router.get("/books/top-rated", tags=["Endpoints de Insights"])
def top_rated_books(
    limit: int = Query(..., ge=1, description="Número de livros a retornar")
):
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT * FROM books ORDER BY rating DESC, price DESC LIMIT ?",
        conn,
        params=(limit,)
    )
    conn.close()
    return df.to_dict(orient="records")

@router.get("/books/price-range", tags=["Endpoints de Insights"])
def books_by_price_range(
    min: float = Query(..., description="Preço mínimo"),
    max: float = Query(..., description="Preço máximo")
):
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT * FROM books WHERE price >= ? AND price <= ?",
        conn,
        params=(min, max)
    )
    conn.close()
    return df.to_dict(orient="records")

@router.get("/books", tags=["Endpoints Core"])
def list_books():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM books", conn)
    conn.close()
    return df.to_dict(orient="records")

@router.get("/books/{book_id}", tags=["Endpoints Core"])
def get_book_by_id(book_id: int):
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM books WHERE id = ?", conn, params=(book_id,))
    conn.close()
    if df.empty:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return df.to_dict(orient="records")[0]

@router.get("/categories", tags=["Endpoints Core"])
def list_categories():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT DISTINCT category FROM books", conn)
    conn.close()
    return sorted(df["category"].dropna().tolist())

# ===============================
# Endpoints de Estatísticas
# ===============================
@router.get("/stats/overview", tags=["Endpoints de Insights"])
def stats_overview():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM books", conn)
    conn.close()
    return {
        "total_books": len(df),
        "avg_price": round(df["price"].mean(), 2) if not df.empty else 0,
        "rating_distribution": df["rating"].value_counts().to_dict()
    }

@router.get("/stats/categories", tags=["Endpoints de Insights"])
def stats_by_category():
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT category, COUNT(*) as count, ROUND(AVG(price),2) as avg_price FROM books GROUP BY category",
        conn
    )
    conn.close()
    return df.to_dict(orient="records")

# ===============================
# Endpoint Protegido — Trigger Scraping
# ===============================
@router.post("/scraping/trigger", tags=["Scraping"])
def trigger_scraping(current_user: dict = Depends(get_current_user)):
    """
    Endpoint protegido para disparar scraping manualmente.
    """
    try:
        from scripts import scrape_books
        scrape_books.run_scraping()
        return {"message": "Scraping executado com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
