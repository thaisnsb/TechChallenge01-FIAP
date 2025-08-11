import sqlite3
import os
import logging
import pandas as pd

# --- Configuração de Logging ---
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%m/%d/%Y %I:%M:%S %p',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("tech_challenge.log")
    ]
)

# --- Funções de Inicialização de Banco de Dados ---
def init_db():
    """
    Inicializa todos os bancos de dados e tabelas necessários para o projeto.
    Cria 'books.db' com a tabela 'books' e 'users.db' com a tabela 'users'.
    """
    if not os.path.exists('data'):
        os.makedirs('data')

    # Inicializa o banco de dados de livros
    DB_BOOKS_FILE = 'data/books.db'
    conn_books = sqlite3.connect(DB_BOOKS_FILE)
    cursor_books = conn_books.cursor()
    
    logging.info(f"Conectando ao banco de dados de livros: {DB_BOOKS_FILE}")
    cursor_books.execute('''
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
    conn_books.commit()
    conn_books.close()
    logging.info(f"Tabela 'books' criada ou já existe em {DB_BOOKS_FILE}.")

    # Inicializa o banco de dados de usuários
    DB_USERS_FILE = 'data/users.db'
    conn_users = sqlite3.connect(DB_USERS_FILE)
    cursor_users = conn_users.cursor()
    
    logging.info(f"Conectando ao banco de dados de usuários: {DB_USERS_FILE}")
    cursor_users.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    
    # Adiciona um usuário de teste se a tabela estiver vazia
    cursor_users.execute("SELECT COUNT(*) FROM users")
    if cursor_users.fetchone()[0] == 0:
        # A senha não está criptografada para simplicidade do exemplo.
        # Em um projeto real, você deve sempre usar hashing de senha (ex: bcrypt).
        cursor_users.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'senha123'))
        logging.info("Usuário de teste 'admin' adicionado.")

    conn_users.commit()
    conn_users.close()
    logging.info(f"Tabela 'users' criada ou já existe em {DB_USERS_FILE}.")

if __name__ == '__main__':
    logging.info("Executando a inicialização de bancos de dados.")
    init_db()
