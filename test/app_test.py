import pytest
from fastapi.testclient import TestClient
import os
import sqlite3
import pandas as pd
import sys


# Adiciona o diretório raiz do projeto ao PYTHONPATH para resolver a importação
# O diretório-mãe do diretório atual ('test') é o raiz do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.main import app

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    DB_BOOKS_FILE = os.path.join("data", "books.db")
    if not os.path.exists(DB_BOOKS_FILE):
        # Se o banco de dados não existir, crie-o.
        from scripts.scrape_books import init_books_db, scrape_all_books_by_category, insert_books_into_db
        init_books_db()
        books = scrape_all_books_by_category()
        if books:
            insert_books_into_db(books)
   
    yield

# --- Testes para Endpoints Não Protegidos ---

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API está no ar e os dados estão acessíveis."}

def test_list_all_books():
    response = client.get("/api/v1/books")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_book_by_id():
    # Supondo que o livro com id=1 exista
    response = client.get("/api/v1/books/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert "title" in response.json()

def test_get_book_by_invalid_id():
    # Teste para um ID que não existe
    response = client.get("/api/v1/books/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Livro não encontrado."

def test_search_books_by_title():
    response = client.get("/api/v1/books/search", params={"title": "Light"})
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_search_books_by_category():
    response = client.get("/api/v1/books/search", params={"category": "Travel"})
    assert response.status_code == 200
    assert len(response.json()) > 0

# --- Testes para Endpoints Protegidos ---

def test_trigger_scraping_unauthorized():
    # Teste que a rota protegida retorna 401 sem token
    response = client.post("/api/v1/scraping/trigger")
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas"

def test_auth_login():
    # Teste para obter o token de acesso
    response = client.post("/api/v1/auth/login", data={"username": "admin", "password": "senha123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
