# app/routes/vehicle_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth_dependencies import get_current_active_user
from app.models.user_model import User
from app.schemas.vehicle_schema import VeiculoCompareResponse, VeiculoResponse
from app.services.scraper_service import get_blog_scrapy
from app.services.vehicle_service import (
    VehicleService,
    create_veiculo,
    gerar_hash_busca,
    get_veiculo_by_hash,
    update_veiculo,
)
from app.utils.helpers import limiter, logger

router = APIRouter(prefix="/veiculos", tags=["Veículos"])


def _obter_ou_processar_veiculo(
    db: Session,
    current_user: User,
    marca: str,
    modelo: str,
    versao: str,
    ano: int,
    fonte: str,
    bypass_cache: bool,
):
    """Função interna para buscar no cache ou processar via IA."""
    hash_busca = gerar_hash_busca(marca, modelo, versao, ano)
    veiculo_db = get_veiculo_by_hash(db, hash_busca)

    if veiculo_db and not bypass_cache:
        return veiculo_db

    carro_query = f"{marca} {modelo} {versao}"
    logger.info("scraping_started", user_id=current_user.id, carro=carro_query)

    try:
        # 1. Scraping
        resultados_scrapy = get_blog_scrapy(carro_query)

        # 🔥 ECONOMIA DE TOKENS: Aborta a requisição se o Scrapy falhar ou vier vazio
        if not resultados_scrapy:
            logger.warning(f"Scraping vazio para {carro_query}. Abortando IA.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Não foi possível coletar dados na internet para {marca} {modelo}. A extração via IA foi cancelada para poupar tokens.",
            )

        # 2. IA e Consenso
        ai_service = VehicleService()
        
        especs = ai_service.processar_veiculo_com_ia(
            marca=marca,
            modelo=modelo,
            versao=versao,
            ano=ano,
        )

        # 🔥 BARREIRA DE QUALIDADE: Impede salvar lixo no Banco de Dados
        termos_invalidos = ["não disponível", "nao disponivel", "", "verificar fontes"]
        indisponiveis = sum(
            1 for v in especs.values() if str(v).strip().lower() in termos_invalidos
        )
        taxa_falha = indisponiveis / len(especs)

        if taxa_falha >= 0.7:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Não foram encontradas informações suficientes para {marca} {modelo}. A extração falhou ou o veículo é muito recente.",
            )

        # 3. Salvar no Banco
        if veiculo_db and bypass_cache:
            return update_veiculo(db, veiculo_db, especs, fonte)
        else:
            return create_veiculo(db, marca, modelo, versao, ano, fonte, especs)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("scraping_failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Falha ao processar {marca} {modelo}: {str(e)}",
        )


@router.get("/busca", response_model=VeiculoResponse)
@limiter.limit("10/minute")
async def buscar_veiculo(
    request: Request,
    marca: str = Query(..., min_length=2, max_length=50),
    modelo: str = Query(..., min_length=1, max_length=50),
    versao: str = Query(..., min_length=1, max_length=100),
    ano: int = Query(..., ge=1886, le=2027),
    fonte: str = Query("scrapy_ia_consenso", max_length=50),
    bypass_cache: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Busca a ficha técnica de um veículo individual."""
    return _obter_ou_processar_veiculo(
        db,
        current_user,
        marca,
        modelo,
        versao,
        ano,
        fonte,
        bypass_cache,
    )


@router.get("/comparar", response_model=VeiculoCompareResponse)
@limiter.limit("5/minute")
async def comparar_veiculos(
    request: Request,
    # Veículo 1
    marca1: str = Query(..., description="Marca do veículo 1"),
    modelo1: str = Query(..., description="Modelo do veículo 1"),
    versao1: str = Query(..., description="Versão do veículo 1"),
    ano1: int = Query(..., description="Ano do veículo 1"),
    # Veículo 2
    marca2: str = Query(..., description="Marca do veículo 2"),
    modelo2: str = Query(..., description="Modelo do veículo 2"),
    versao2: str = Query(..., description="Versão do veículo 2"),
    ano2: int = Query(..., description="Ano do veículo 2"),
    # Configurações globais
    fonte: str = Query("scrapy_ia_consenso", max_length=50),
    bypass_cache: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Processa e retorna as fichas técnicas de dois veículos simultaneamente para comparação."""
    veiculo_1 = _obter_ou_processar_veiculo(
        db,
        current_user,
        marca1,
        modelo1,
        versao1,
        ano1,
        fonte,
        bypass_cache,
    )
    veiculo_2 = _obter_ou_processar_veiculo(
        db,
        current_user,
        marca2,
        modelo2,
        versao2,
        ano2,
        fonte,
        bypass_cache,
    )

    return VeiculoCompareResponse(veiculo1=veiculo_1, veiculo2=veiculo_2)
