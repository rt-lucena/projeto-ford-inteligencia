from unittest.mock import MagicMock, patch

from app.services.vehicle_service import (
    VehicleService,
    create_veiculo,
    gerar_hash_busca,
    get_veiculo_by_hash,
    update_veiculo,
)


def criar_vehicle_service():
    """
    Cria um VehicleService sem inicializar os serviços reais.
    """
    with patch(
        "app.services.vehicle_service.DataLoaderService"
    ) as mock_data_loader, patch(
        "app.services.vehicle_service.LLMService"
    ) as mock_llm:

        service = VehicleService()

    return service, mock_data_loader, mock_llm


def test_gerar_hash_busca_mesma_busca_gera_mesmo_hash():
    hash_1 = gerar_hash_busca(
        "Ford",
        "Ranger",
        "Raptor",
        2025,
    )

    hash_2 = gerar_hash_busca(
        "Ford",
        "Ranger",
        "Raptor",
        2025,
    )

    assert hash_1 == hash_2


def test_gerar_hash_busca_diferencia_veiculos():
    hash_ranger = gerar_hash_busca(
        "Ford",
        "Ranger",
        "Raptor",
        2025,
    )

    hash_mustang = gerar_hash_busca(
        "Ford",
        "Mustang",
        "GT",
        2025,
    )

    assert hash_ranger != hash_mustang


def test_gerar_hash_busca_ignora_espacos_e_maiusculas():
    hash_1 = gerar_hash_busca(
        " Ford ",
        "RANGER",
        " Raptor ",
        2025,
    )

    hash_2 = gerar_hash_busca(
        "ford",
        "ranger",
        "raptor",
        2025,
    )

    assert hash_1 == hash_2
    
def test_processar_veiculo_sem_artigos():
    service, mock_data_loader, mock_llm = criar_vehicle_service()

    mock_data_loader.return_value.carregar_artigos.return_value = []

    resultado = service.processar_veiculo_com_ia(
        marca="Ford",
        modelo="Ranger",
        versao="Raptor",
        ano=2025,
    )

    assert resultado["motor"] == "não disponível"
    assert resultado["potencia"] == "não disponível"
    assert resultado["preco"] == "não disponível"

    mock_data_loader.return_value.carregar_artigos.assert_called_once()

    mock_llm.return_value.processar_artigos.assert_not_called()
    
@patch(
    "app.services.vehicle_service.FipeService.buscar_preco_fipe"
)
@patch(
    "app.services.vehicle_service.ConsensusService.combinar_por_votacao"
)
def test_processar_veiculo_com_ia(
    mock_consenso,
    mock_fipe,
):
    service, mock_data_loader, mock_llm = criar_vehicle_service()

    artigos = [
        {
            "titulo": "Ford Ranger Raptor",
            "conteudo": "Motor 3.0 V6 biturbo com 397 cv.",
            "fonte": "site-teste",
            "url": "https://exemplo.com/ranger",
        },
        {
            "titulo": "Ranger Raptor 2025",
            "conteudo": "Câmbio automático de 10 marchas.",
            "fonte": "site-teste-2",
            "url": "https://exemplo.com/ranger-2",
        },
    ]

    resultados_ia = [
        {
            "motor": "3.0 V6 biturbo",
            "potencia": "397 cv",
            "torque": "59,4 kgfm",
            "preco": "R$ 500.000",
            "fonte": "site-teste",
        },
        {
            "motor": "3.0 V6 biturbo",
            "potencia": "397 cv",
            "torque": "59,4 kgfm",
            "preco": "R$ 500.000",
            "fonte": "site-teste-2",
        },
    ]

    resultado_final = {
        "motor": "3.0 V6 biturbo",
        "potencia": "397 cv",
        "torque": "59,4 kgfm",
        "preco": "R$ 500.000",
    }

    mock_data_loader.return_value.carregar_artigos.return_value = artigos

    mock_llm.return_value.processar_artigos.return_value = resultados_ia

    mock_consenso.return_value = resultado_final

    mock_fipe.return_value = None

    resultado = service.processar_veiculo_com_ia(
        marca="Ford",
        modelo="Ranger",
        versao="Raptor",
        ano=2025,
    )

    assert resultado == resultado_final

    mock_data_loader.return_value.carregar_artigos.assert_called_once()

    mock_llm.return_value.processar_artigos.assert_called_once_with(
        artigos=artigos,
        atributos=service.atributos_esperados,
        marca="Ford",
        modelo="Ranger",
        versao="Raptor",
        ano=2025,
    )

    mock_consenso.assert_called_once()

    mock_fipe.assert_called_once_with(
        "Ford",
        "Ranger",
        "Raptor",
        2025,
    )
    
@patch(
    "app.services.vehicle_service.FipeService.buscar_preco_fipe"
)
@patch(
    "app.services.vehicle_service.ConsensusService.combinar_por_votacao"
)
def test_processar_veiculo_sanitiza_listas(
    mock_consenso,
    mock_fipe,
):
    service, mock_data_loader, mock_llm = criar_vehicle_service()

    mock_data_loader.return_value.carregar_artigos.return_value = [
        {
            "titulo": "Ford Ranger",
            "conteudo": "Dados do veículo",
            "fonte": "teste",
        }
    ]

    mock_llm.return_value.processar_artigos.return_value = [
        {
            "motor": "3.0 V6",
            "modos_de_conducao": [
                "Normal",
                "Sport",
                "Off-road",
            ],
        }
    ]

    mock_fipe.return_value = None

    mock_consenso.return_value = {
        "motor": "3.0 V6",
        "modos_de_conducao": "Normal, Sport, Off-road",
    }

    resultado = service.processar_veiculo_com_ia(
        marca="Ford",
        modelo="Ranger",
        versao="Raptor",
        ano=2025,
    )

    assert resultado["modos_de_conducao"] == "Normal, Sport, Off-road"

    argumentos = mock_consenso.call_args.kwargs

    resultados = argumentos["resultados"]

    assert resultados[0]["modos_de_conducao"] == (
        "Normal, Sport, Off-road"
    )
    
@patch(
    "app.services.vehicle_service.FipeService.buscar_preco_fipe"
)
@patch(
    "app.services.vehicle_service.ConsensusService.combinar_por_votacao"
)
def test_processar_veiculo_atualiza_preco_com_fipe(
    mock_consenso,
    mock_fipe,
):
    service, mock_data_loader, mock_llm = criar_vehicle_service()

    mock_data_loader.return_value.carregar_artigos.return_value = [
        {
            "titulo": "Ford Ranger",
            "conteudo": "Dados do veículo",
            "fonte": "teste",
        }
    ]

    mock_llm.return_value.processar_artigos.return_value = [
        {
            "motor": "3.0 V6",
            "preco": "R$ 480.000",
        }
    ]

    mock_consenso.return_value = {
        "motor": "3.0 V6",
        "preco": "R$ 480.000",
    }

    mock_fipe.return_value = "R$ 500.000"

    resultado = service.processar_veiculo_com_ia(
        marca="Ford",
        modelo="Ranger",
        versao="Raptor",
        ano=2025,
    )

    assert resultado["preco"] == "R$ 500.000"

    mock_fipe.assert_called_once_with(
        "Ford",
        "Ranger",
        "Raptor",
        2025,
    )
    
def test_create_veiculo(db):
    especificacoes = {
        "motor": "3.0 V6",
        "potencia": "397 cv",
        "preco": "R$ 500.000",
    }

    veiculo = create_veiculo(
        db=db,
        marca="Ford",
        modelo="Ranger",
        versao="Raptor",
        ano=2025,
        fonte="teste",
        especificacoes=especificacoes,
    )

    assert veiculo.id is not None
    assert veiculo.marca == "Ford"
    assert veiculo.modelo == "Ranger"
    assert veiculo.versao == "Raptor"
    assert veiculo.ano == 2025
    assert veiculo.fonte == "teste"
    assert veiculo.hash_busca == gerar_hash_busca(
        "Ford",
        "Ranger",
        "Raptor",
        2025,
    )
    
def test_get_veiculo_by_hash(db):
    veiculo = create_veiculo(
        db=db,
        marca="Ford",
        modelo="Ranger",
        versao="Raptor",
        ano=2025,
        fonte="teste",
        especificacoes={
            "motor": "3.0 V6",
        },
    )

    resultado = get_veiculo_by_hash(
        db,
        veiculo.hash_busca,
    )

    assert resultado is not None
    assert resultado.id == veiculo.id
    assert resultado.modelo == "Ranger"
    
def test_update_veiculo(db):
    veiculo = create_veiculo(
        db=db,
        marca="Ford",
        modelo="Ranger",
        versao="Raptor",
        ano=2025,
        fonte="teste",
        especificacoes={
            "motor": "3.0 V6",
            "potencia": "397 cv",
        },
    )

    atualizado = update_veiculo(
        db=db,
        veiculo=veiculo,
        especificacoes={
            "motor": "3.0 V6 Biturbo",
            "potencia": "397 cv",
        },
        fonte="teste_atualizado",
    )

    assert atualizado.motor == "3.0 V6 Biturbo"
    assert atualizado.potencia == "397 cv"
    assert atualizado.fonte == "teste_atualizado"