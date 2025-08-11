import os
import sqlite3
import pandas as pd

# Caminho do banco
DB_PATH = "data/books.db"

# Dados iniciais (mock)
initial_books = [
    {"title": "Book A", "category": "Fiction", "price": 10.99, "rating": 4.5},
    {"title": "Book B", "category": "Travel", "price": 15.50, "rating": 4.7},
    {"title": "Book C", "category": "Science", "price": 8.99, "rating": 4.2}
]

def init_db():
    # Garante que a pasta data/ existe
    os.makedirs("data", exist_ok=True)

    # Cria conexão
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Cria tabela
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            rating REAL NOT NULL
        )
    """)

    # Verifica se já tem dados
    cursor.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]

    if count == 0:
        # Insere dados iniciais
        df = pd.DataFrame(initial_books)
        df.to_sql("books", conn, if_exists="append", index=False)
        print("📚 Banco criado e populado com dados iniciais.")
    else:
        print("✅ Banco já possui dados, nenhuma inserção feita.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
