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

```mermaid
graph LR
    A[Web Scraping] -->|BeautifulSoup| B[CSV + SQLite]
    B --> C[API FastAPI]
    C --> D[Endpoints Públicos]
    D --> E[Clientes / Cientistas de Dados / ML Models]
