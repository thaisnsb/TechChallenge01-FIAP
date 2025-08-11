# Tech Challenge - Fase 1: API de Consulta de Livros

[cite_start]Este projeto é a resposta ao Tech Challenge da Fase 1 do curso de Machine Learning Engineering[cite: 4]. [cite_start]O objetivo principal é a criação de um pipeline de dados completo, desde a extração de informações de um site de e-commerce de livros até a disponibilização desses dados por meio de uma API RESTful pública[cite: 11, 12].

## 📋 Índice

- [Descrição do Projeto](#-descrição-do-projeto)
- [Arquitetura do Sistema](#-arquitetura-do-sistema)
- [Estrutura de Pastas](#-estrutura-de-pastas)
- [Instalação e Configuração](#-instalação-e-configuração)
- [Instruções de Execução](#-instruções-de-execução)
- [Documentação da API (Endpoints)](#-documentação-da-api-endpoints)
- [Autor](#-autor)

## 📝 Descrição do Projeto

[cite_start]Como parte de um desafio para a posição de Engenheiro(a) de Machine Learning, este projeto visa construir a infraestrutura de dados fundamental para um futuro sistema de recomendação de livros[cite: 9]. A solução envolve:

1.  [cite_start]**Web Scraping**: Um script automatizado para extrair dados de todos os livros do site `https://books.toscrape.com/`[cite: 23, 24].
2.  [cite_start]**Armazenamento de Dados**: Os dados coletados são armazenados localmente em um arquivo CSV[cite: 25].
3.  [cite_start]**API RESTful**: Uma API desenvolvida com FastAPI que serve os dados coletados, permitindo consultas e análises[cite: 28].
4.  [cite_start]**Deploy**: A API é disponibilizada publicamente através de um serviço de cloud[cite: 32].

## 🏗️ Arquitetura do Sistema

[cite_start]A arquitetura foi pensada para ser modular e escalável, seguindo um pipeline de dados claro[cite: 37, 38, 39, 40].

**Fluxo de Dados:**