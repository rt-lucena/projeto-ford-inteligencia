# app/routes/history_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth_dependencies import (get_current_active_user, get_current_admin_user)
from app.models.user_model import User
from app.schemas.history_schema import HistoricoCreate, HistoricoResponse
from app.services.history_service import (
    anonimize_old_history,
    create_history,
    get_user_history,
)

router = APIRouter(prefix="/historico", tags=["Histórico"])


@router.post("/", response_model=HistoricoResponse, status_code=status.HTTP_201_CREATED)
async def criar_historico(
    historico_in: HistoricoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return create_history(db, current_user.id, historico_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar histórico. Verifique os IDs dos veículos.",
        )


@router.get("/")
async def listar_meu_historico(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return get_user_history(db, current_user.id)


@router.delete("/limpeza-antigos")
async def limpar_historico_antigo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    anonimize_old_history(db)

    return {
        "message": "Registros antigos anonimizados com sucesso."
    }
