from contextlib import asynccontextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.models.user_model import User


# ============================================================
# BANCO DE DADOS DE TESTES
# ============================================================

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


# ============================================================
# LIFESPAN DE TESTES
# ============================================================

@asynccontextmanager
async def test_lifespan(_app):
    """
    Lifespan utilizado durante os testes.

    Não executa o lifespan real da aplicação.
    Portanto:
    - não chama init_db()
    - não cria o usuário administrador
    - não inicializa serviços externos
    - não acessa o banco de produção
    """

    yield


# ============================================================
# FIXTURE DO BANCO
# ============================================================

@pytest.fixture(scope="function")
def db():
    """
    Cria um banco SQLite em memória para cada teste.
    """

    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


# ============================================================
# FIXTURE DO CLIENTE
# ============================================================

@pytest.fixture(scope="function")
def client(db, monkeypatch):
    """
    Cria um TestClient utilizando:

    - banco de testes
    - lifespan de testes
    - dependência get_db sobrescrita
    """

    # Substitui o lifespan real pelo lifespan de testes.
    monkeypatch.setattr(
        app.router,
        "lifespan_context",
        test_lifespan,
    )

    # Substitui o banco da aplicação pelo banco de testes.
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


# ============================================================
# USUÁRIO DE TESTE
# ============================================================

@pytest.fixture
def usuario(db):
    """
    Cria um usuário comum exclusivamente no banco de testes.
    """

    usuario = User(
        nome="Usuário Teste",
        email="teste@teste.com",
        senha_hash=get_password_hash("12345678"),
        role="user",
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario

# ============================================================
# ADMIN DE TESTE
# ============================================================

@pytest.fixture
def admin(db):
    """
    Cria um usuário administrador exclusivamente no banco de testes.
    """
    admin = User(
        nome="Administrador Teste",
        email="admin@teste.com",
        senha_hash=get_password_hash("12345678"),
        role="admin",
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin