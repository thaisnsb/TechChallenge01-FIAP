# 📚 Tech Challenge Fase 1 — API Pública de Livros

## 📖 Sobre o Projeto
Este projeto implementa um pipeline completo para extração, transformação e disponibilização de dados de livros a partir do site [Books to Scrape](https://books.toscrape.com/).  
O objetivo é fornecer uma **API RESTful pública** para consulta dos dados, permitindo que cientistas de dados e sistemas de recomendação utilizem as informações com facilidade.

---

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python 3.13.4
- **Framework Web:** FastAPI
- **Servidor:** Uvicorn + Gunicorn (deploy no Render)
- **Scraping:** BeautifulSoup4, Requests
- **Banco de Dados:** SQLite
- **Manipulação de Dados:** Pandas
- **Validação:** Pydantic
- **Autenticação:** JWT
- **Testes:** Pytest
- **Outros:** bcrypt, dotenv, lxml

---

## 🚀 Deploy
API hospedada em produção:  
**[https://techchallengefase1-1.onrender.com](https://techchallengefase1-1.onrender.com)**  

Documentação Swagger:  
**[https://techchallengefase1-1.onrender.com/docs](https://techchallengefase1-1.onrender.com/docs)**  

---

## 📊 Arquitetura do Projeto




# 🧠 Projeto TechChallenge - Fase 1 — API de Livros

## ✅ Sobre

Este projeto implementa um pipeline completo para extração, transformação e disponibilização de dados de livros a partir do site [Books to Scrape](https://books.toscrape.com/).  
O objetivo é fornecer uma **API RESTful pública** para consulta dos dados, permitindo que cientistas de dados e sistemas de recomendação utilizem as informações com facilidade.


---

## ⚙️ Stack utilizada

- **Linguagem:** Python 3.13  
- **Framework Web:** FastAPI  
- **Servidor:** Gunicorn + Uvicorn (deploy via Render)  
- **Gerenciador de pacotes:** pip + requirements.txt  
- **Testes:** pytest  
- **Scraping:** BeautifulSoup, requests  
- **Banco de dados:** SQLite (via sqlite3)  
- **DataFrame:** pandas  
- **Validação:** Pydantic  
- **Autenticação:** python-jose, passlib[bcrypt]  
- **Outros:** openpyxl, lxml, bcrypt, certifi, charset-normalizer, click, ecdsa, anyio, annotated-types  

---

## 🚀 Deploy

- **URL Produção:** https://techchallenge01-fiap.onrender.com  
- **Documentação Swagger:** https://techchallenge01-fiap.onrender.com/docs  

---

## 📌 Arquitetura do Projeto

```plaintext
api/
 ├── main.py              # Configuração principal da API
 ├── routers/
 │    ├── auth.py         # Endpoints de autenticação
 │    └── books.py        # Endpoints de livros e estatísticas
 ├── data/
 │    └── books.db        # Banco de dados SQLite
 └── scripts/
      └── scrape_books.py # Script de scraping

```

---

## 💻 Como rodar localmente

### 1️⃣ Clone o repositório
```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
```

### 2️⃣ Crie o ambiente virtual e instale dependências
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 3️⃣ Inicialize o banco de dados
(Opcional, caso não exista `data/books.db` ou queira recriar)  
```bash
python scripts/init_db.py
```

### 4️⃣ Execute o servidor localmente
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5️⃣ Acesse as rotas
- Swagger: http://127.0.0.1:8000/docs  
- Redirecionamento automático do `/` para `/docs` já configurado.

---

## 🔑 Fluxo de Autenticação

1. **Cadastro:** `POST /api/v1/auth/register`  
2. **Login:** `POST /api/v1/auth/login` (gera token JWT)  
3. **Acesso protegido:** Enviar token no `Authorization: Bearer <token>`  

---

## 🧪 Testes
Para rodar os testes:
```bash
pytest -v
```

---

```mermaid
graph LR
    A[Web Scraping] -->|BeautifulSoup| B[CSV + SQLite]
    B --> C[API FastAPI]
    C --> D[Endpoints Públicos]
    D --> E[Clientes / Cientistas de Dados / ML Models]