import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import sqlite3
import logging

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

# --- Scraping ---

def get_all_categories():
    """
    Coleta os nomes e URLs de todas as categorias na barra lateral da pagina principal.
    """
    base_url = "https://books.toscrape.com/"
    categories_data = []
    
    logging.info("Iniciando a raspagem das categorias...")
    try:
        response = requests.get(base_url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        side_categories_ul = soup.find('div', class_='side_categories')
        if side_categories_ul:
            nested_ul = side_categories_ul.find('ul', class_='nav').find('ul')
            if nested_ul:
                for li in nested_ul.find_all('li'):
                    a_tag = li.find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        category_name = a_tag.text.strip()
                        category_relative_url = a_tag['href']
                        category_full_url = requests.compat.urljoin(base_url, category_relative_url)
                        categories_data.append({
                            'name': category_name,
                            'url': category_full_url
                        })
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao recuperar a página principal para raspar categorias: {e}")
    
    logging.info(f"Raspagem de categorias concluída. Encontradas {len(categories_data)} categorias.")
    return categories_data

def get_book_details(book_article, category_name):
    """
    Extrai detalhes de cada livro a partir de um elemento <article>.
    """
    try:
        title = book_article.h3.a['title']
        price_str = book_article.find('p', class_='price_color').text
        price = float(price_str.replace('£', ''))
        rating_class = book_article.find('p', class_='star-rating')['class'][1]
        rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
        rating = rating_map.get(rating_class, 0)
        availability_tag = book_article.find('p', class_='instock availability')
        availability_text = availability_tag.text.strip() if availability_tag else "N/A"
        is_in_stock = "In stock" in availability_text
        image_url_relative = book_article.find('img')['src']
        base_image_url = "https://books.toscrape.com/"
        image_url = requests.compat.urljoin(base_image_url, image_url_relative)
        book_relative_url = book_article.h3.a['href']
        base_catalogue_url = "https://books.toscrape.com/catalogue/"
        book_full_url = requests.compat.urljoin(base_catalogue_url, book_relative_url)

        return {
            'title': title,
            'price': price,
            'rating': rating,
            'availability_text': availability_text,
            'is_in_stock': is_in_stock,
            'image_url': image_url,
            'book_page_url': book_full_url,
            'category': category_name
        }
    except Exception as e:
        logging.error(f"Erro ao extrair detalhes de um livro: {e}. Problema em: {book_article}")
        return None

def scrape_all_books_by_category():
    """
    Orquestra o processo de scraping, descobrindo categorias e depois
    visitando cada página de categoria para extrair os livros.
    """
    all_books_data = []
    categories = get_all_categories()
    if not categories:
        logging.error("Nenhuma categoria válida encontrada. Encerrando o scraping.")
        return []

    processed_book_urls = set()

    for category_info in categories:
        category_name = category_info['name']
        initial_category_url = category_info['url']
        logging.info(f"Iniciando scraping da categoria: '{category_name}'")

        current_category_page_url = initial_category_url
        page_num = 1
        has_next_page = True

        while has_next_page:
            logging.info(f"Scrapping pagina {page_num} da categoria '{category_name}'")
            try:
                response = requests.get(current_category_page_url, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')
                books_on_page = soup.find_all('article', class_='product_pod')

                if not books_on_page:
                    has_next_page = False
                    break

                for book_article in books_on_page:
                    details = get_book_details(book_article, category_name)
                    if details and details['book_page_url'] not in processed_book_urls:
                        all_books_data.append(details)
                        processed_book_urls.add(details['book_page_url'])
                    
                next_button = soup.find('li', class_='next')
                if next_button and next_button.find('a'):
                    next_relative_url = next_button.find('a')['href']
                    current_category_page_url = requests.compat.urljoin(current_category_page_url, next_relative_url)
                    page_num += 1
                else:
                    has_next_page = False
                
                time.sleep(0.1)

            except requests.exceptions.RequestException as e:
                logging.error(f"Erro ao recuperar a página de categoria {current_category_page_url}: {e}. Pulando para a próxima categoria.")
                has_next_page = False

    return all_books_data

# --- Funções de Banco de Dados ---

def init_books_db():
    """
    Inicializa o banco de dados 'books.db', cria a tabela se ela não existir.
    """
    DB_FILE = 'data/books.db'
    if not os.path.exists('data'):
        os.makedirs('data')

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Cria a tabela de livros se ela não existir
    cursor.execute('''
         CREATE TABLE IF NOT EXISTS books (
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
    ''')
    conn.commit()
    conn.close()
    logging.info(f"Banco de dados '{DB_FILE}' e tabela 'books' prontos.")

def insert_books_into_db(books_data):
    """
    Insere os dados dos livros coletados no banco de dados.
    """
    DB_FILE = 'data/books.db'
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    logging.info(f"Iniciando a inserção de {len(books_data)} livros no banco de dados...")
    for book in books_data:
        try:
           
            is_in_stock_int = 1 if book['is_in_stock'] else 0
            cursor.execute('''
                INSERT OR IGNORE INTO books (
                    id, title, category, price, rating, is_in_stock, availability_text, image_url, book_page_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                book['id'],
                book['title'],
                book['category'],
                book['price'],
                book['rating'],
                is_in_stock_int,
                book['availability_text'],
                book['image_url'],
                book['book_page_url']
            ))
        except sqlite3.IntegrityError as e:
            logging.warning(f"Livro com URL duplicada '{book['book_page_url']}' ignorado. Erro: {e}")
        except Exception as e:
            logging.error(f"Erro ao inserir o livro '{book['title']}': {e}")
            
    conn.commit()
    conn.close()
    logging.info("Inserção de dados concluída.")

# --- Bloco Principal de Execução ---

if __name__ == "__main__":
    logging.info("Iniciando o Tech Challenge: Extração de dados de livros.")
    
   
    init_books_db()
    
    
    all_collected_books = scrape_all_books_by_category()
    
    if not all_collected_books:
        logging.warning("Nenhum dado de livro foi coletado. Verifique os logs de erro.")
    else:
        
        for i, book in enumerate(all_collected_books):
            book['id'] = i + 1
        
        
        insert_books_into_db(all_collected_books)
        
        logging.info("Scraping e armazenamento de dados concluídos com sucesso.")
