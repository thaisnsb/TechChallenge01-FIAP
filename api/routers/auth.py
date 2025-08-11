from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import sqlite3
import os


router = APIRouter(tags=["JWT Authentication"])
# Define o caminho para o arquivo do banco de dados de usuários.
DB_USERS_FILE = os.path.join("data", "users.db")
# Configurações do JWT
SECRET_KEY = "sua-chave-secreta-muito-segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Configura as autenticação OAuth2 com o fluxo de senha.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- Funções de Banco de Dados de Usuários ---
def get_user_db_connection():
    """Retorna uma conexão com o banco de dados de usuários."""
    try:
        conn = sqlite3.connect(DB_USERS_FILE)
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar com o banco de dados de usuários: {e}")
        return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Funções de Autenticação (Consulta ao DB) ---
def authenticate_user(username: str, password: str):
    """
    Autentica um usuário consultando o banco de dados.
    """
    conn = get_user_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {"username": user[0]}
    return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"username": username}

# --- Endpoints de Autenticação ---
@router.post("/auth/register")
def register_user(username: str, password: str):
    """
    Endpoint para registrar um novo usuário.
    """
    conn = get_user_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")
    cursor = conn.cursor()
    
    try:
       
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return {"message": "Usuário registrado com sucesso."}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Nome de usuário já existe.")
    finally:
        conn.close()

@router.post("/auth/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint para obter token de acesso JWT.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/refresh")
def refresh_access_token(current_user: dict = Depends(get_current_user)):
    """
    Endpoint para renovar o token de acesso.
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": current_user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": new_access_token, "token_type": "bearer"}
