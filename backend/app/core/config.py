# app/core/config.py
import os
from pathlib import Path

from dotenv import load_dotenv

# Define a raiz do projeto (backend/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    # JWT
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "ALTERAR_NO_PROD")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'fichas.db'}"

    # Ollama (LLM local)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # 📁 Caminhos para Scrapy e YouTube
    SCRAPY_SETTINGS_MODULE: str = "app.scraping.settings"
    DATA_RAW_DIR: Path = BASE_DIR / "data" / "raw"

    @property
    def YOUTUBE_CLIENT_CONFIG(self) -> dict:
        """
        Gera a estrutura do OAuth Client Secrets dinamicamente a partir do .env.
        """
        return {
            "installed": {
                "client_id": os.getenv("YOUTUBE_CLIENT_ID", ""),
                "project_id": os.getenv("YOUTUBE_PROJECT_ID", ""),
                "auth_uri": os.getenv(
                    "YOUTUBE_AUTH_URI",
                    "https://accounts.google.com/o/oauth2/auth",
                ),
                "token_uri": os.getenv(
                    "YOUTUBE_TOKEN_URI",
                    "https://oauth2.googleapis.com/token",
                ),
                "auth_provider_x509_cert_url": os.getenv(
                    "YOUTUBE_AUTH_PROVIDER_CERT_URL",
                    "https://www.googleapis.com/oauth2/v1/certs",
                ),
                "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET", ""),
                "redirect_uris": ["http://localhost"],
            },
        }


settings = Settings()
