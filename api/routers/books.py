from fastapi import APIRouter, HTTPException, Query, Depends
import pandas as pd
import os
import sqlite3
from typing import Optional
from api.routers.auth import get_current_user 


from scripts.scrape_books import scrape_all_books_by_category, init_books_db, insert_books_into_db


router = APIRouter()

# Define o caminho para o arquivo do banco de dados de livros.
DB_BOOKS_FILE = os.path.join("data", "books.db")

# Função auxiliar para estabelecer a conexão com o banco de dados.
def get_db_connection():
    try:
        conn = sqlite3.connect(DB_BOOKS_FILE)
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar com o banco de dados: {e}")
        return None

# Endpoint: GET /books
@router.get("/books", tags=["Endpoints Core"])
def list_all_books():
    """
    Retorna uma lista de todos os livros disponíveis no banco de dados.
    """
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados.")

    try:
        books_df = pd.read_sql_query("SELECT * FROM books", conn)
        if books_df.empty:
            raise HTTPException(status_code=404, detail="Nenhum livro encontrado.")
        
        return books_df.to_dict('records')
    finally:
        conn.close()

# Endpoint: GET /books/{id}
@router.get("/books/{id}", tags=["Endpoints Core"])
def get_book_by_id(id: int):
    """
    Retorna os detalhes completos de um livro específico pelo seu ID.
    A busca é feita diretamente no banco de dados, o que é mais eficiente.
    """
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados.")

    try:
       
        book_df = pd.read_sql_query(f"SELECT * FROM books WHERE id = {id}", conn)
        if book_df.empty:
            raise HTTPException(status_code=404, detail="Livro não encontrado.")
        
        return book_df.iloc[0].to_dict()
    finally:
        conn.close()

# Endpoint: GET /books/search
@router.get("/books/search", tags=["Endpoints Core"])
def search_books(title: Optional[str] = None, category: Optional[str] = None):
    """
    Busca livros por título e/ou categoria. 
    """
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados.")

    query = "SELECT * FROM books WHERE 1=1"
    params = {}
    
    if title:
        query += " AND title LIKE :title"
        params['title'] = f"%{title}%"
    
    if category:
        query += " AND category LIKE :category"
        params['category'] = f"%{category}%"
    
    try:
        filtered_books_df = pd.read_sql_query(query, conn, params=params)
        if filtered_books_df.empty:
            raise HTTPException(status_code=404, detail="Nenhum livro encontrado.")
            
        return filtered_books_df.to_dict('records')
    finally:
        conn.close()

# Endpoint: GET /categories
@router.get("/categories", tags=["Endpoints Core"])
def get_all_categories():
    """
    Lista todas as categorias de livros únicas disponíveis.
    """
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Erro de conexão.")

    try:
        categories_df = pd.read_sql_query("SELECT DISTINCT category FROM books WHERE category IS NOT NULL", conn)
        if categories_df.empty:
            raise HTTPException(status_code=404, detail="Nenhuma categoria encontrada.")
        
        return categories_df['category'].tolist()
    finally:
        conn.close()

# Endpoint disparar o web scraping
@router.post("/scraping/trigger", tags=["Endpoints de Admin"])
def trigger_scraping(current_user: dict = Depends(get_current_user)):
    """
    Endpoint para disparar o web scraping.
    """
    print(f"Scraping disparado pelo usuário: {current_user['username']}")

    # Coleta os dados dos livros
    books_to_insert = scrape_all_books_by_category()

    if not books_to_insert:
        return {"message": "Scraping concluído, mas nenhum livro novo foi encontrado."}

    # Insere os dados no banco de dados
    insert_books_into_db(books_to_insert)

    return {"message": f"Scraping concluído. Foram inseridos ou atualizados {len(books_to_insert)} livros."}

