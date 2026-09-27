# app/main.py
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user_model import User
from app.routes import auth_routes, history_routes, user_routes, vehicle_routes

load_dotenv()


# --- Inicialização do BD e Admin (movido para cá ou para um script separado) ---
def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "ford@ci.com").first()
        if not existing:
            admin = User(
                nome="Administrador Ford",
                email="ford@ci.com",
                senha_hash=get_password_hash("ford123"),
                role="admin",
            )
            db.add(admin)
            db.commit()
            print("Usuário admin criado!")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Ford Commercial Intelligence", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rotas
app.include_router(auth_routes.router)
app.include_router(history_routes.router)
app.include_router(user_routes.router)
app.include_router(vehicle_routes.router)
