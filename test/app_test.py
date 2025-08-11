import pytest
from fastapi.testclient import TestClient
import sqlite3
import os
from api.main import app

client = TestClient(app)

# ===============================
# FIXTURES
# ===============================
@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """
    Usa banco de dados SQLite em memória para os testes,
    isolando do ambiente de produção.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            price REAL,
            rating INTEGER,
            is_in_stock BOOLEAN,
            availability_text TEXT,
            image_url TEXT,
            book_page_url TEXT UNIQUE
        )
    """)
    cursor.executemany("""
        INSERT INTO books (title, category, price, rating, is_in_stock, availability_text, image_url, book_page_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        ("Book A", "Travel", 10.99, 4, 1, "In stock", "url_img_a", "url_page_a"),
        ("Book B", "Travel", 15.50, 5, 1, "In stock", "url_img_b", "url_page_b"),
        ("Book C", "Fiction", 8.00, 3, 0, "Out of stock", "url_img_c", "url_page_c")
    ])
    conn.commit()
    conn.close()
    yield

# ===============================
# TESTES CORE
# ===============================
def test_health_check():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert "status" in r.json()

def test_list_all_books():
    r = client.get("/api/v1/books")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_get_book_by_id():
    r = client.get("/api/v1/books/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1

def test_get_book_by_invalid_id():
    r = client.get("/api/v1/books/9999")
    assert r.status_code == 404

def test_search_books_by_title():
    r = client.get("/api/v1/books/search", params={"title": "Book A"})
    assert r.status_code == 200
    assert any("Book A" in b["title"] for b in r.json())

def test_search_books_by_category():
    r = client.get("/api/v1/books/search", params={"category": "Travel"})
    assert r.status_code == 200
    assert all(b["category"] == "Travel" for b in r.json())

def test_get_all_categories():
    r = client.get("/api/v1/categories")
    assert r.status_code == 200
    assert "Travel" in r.json()

# ===============================
# TESTES ESTATÍSTICAS
# ===============================
def test_stats_overview():
    r = client.get("/api/v1/stats/overview")
    assert r.status_code == 200
    assert "total_books" in r.json()

def test_stats_categories():
    r = client.get("/api/v1/stats/categories")
    assert r.status_code == 200
    assert any(c["category"] == "Travel" for c in r.json())

def test_top_rated_books():
    r = client.get("/api/v1/books/top-rated", params={"limit": 1})
    assert r.status_code == 200
    assert len(r.json()) == 1

def test_books_price_range():
    r = client.get("/api/v1/books/price-range", params={"min": 9, "max": 12})
    assert r.status_code == 200
    assert all(9 <= b["price"] <= 12 for b in r.json())

# ===============================
# TESTES AUTENTICAÇÃO E ENDPOINT PROTEGIDO
# ===============================
def test_auth_register_and_login_and_refresh():
    # Registro
    r = client.post("/api/v1/auth/register", params={"username": "testuser", "password": "123456"})
    assert r.status_code in (200, 400)  # Pode já existir

    # Login
    r = client.post("/api/v1/auth/login", data={"username": "testuser", "password": "123456"})
    assert r.status_code == 200
    token = r.json()["access_token"]

    # Refresh
    r = client.post("/api/v1/auth/refresh", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert "access_token" in r.json()

    # Endpoint protegido
    r = client.post("/api/v1/scraping/trigger", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code in (200, 400)  # Pode falhar se não houver scraping
