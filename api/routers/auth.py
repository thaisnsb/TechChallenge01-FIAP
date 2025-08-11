from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import sqlite3
import os
import bcrypt

router = APIRouter(tags=["JWT Authentication"])

# ===============================
# Configurações JWT
# ===============================
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "chave-super-secreta")  # Em produção, use variável de ambiente
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DB_USERS_FILE = os.path.join("data", "users.db")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ===============================
# Banco de usuários
# ===============================
def get_user_db_connection():
    try:
        if not os.path.exists("data"):
            os.makedirs("data")
        conn = sqlite3.connect(DB_USERS_FILE)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar com o banco de usuários: {e}")
        return None

# ===============================
# Funções auxiliares
# ===============================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(username: str, password: str):
    conn = get_user_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    stored_hash = row[1]
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return {"username": row[0]}
    return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
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

# ===============================
# Endpoints de Autenticação
# ===============================
@router.post("/auth/register")
def register_user(username: str, password: str):
    conn = get_user_db_connection()
    cursor = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        return {"message": "Usuário registrado com sucesso."}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Nome de usuário já existe.")
    finally:
        conn.close()

@router.post("/auth/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/refresh")
def refresh_access_token(current_user: dict = Depends(get_current_user)):
    new_access_token = create_access_token(
        data={"sub": current_user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": new_access_token, "token_type": "bearer"}
