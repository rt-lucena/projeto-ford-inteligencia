from unittest.mock import MagicMock, patch

from app.services.fipe_service import FipeService


def resposta(status_code, payload):
    mock = MagicMock()

    mock.status_code = status_code
    mock.json.return_value = payload

    return mock


def test_normalizar_remove_acentos_e_espacos():
    assert (
        FipeService._normalizar("  São Paulo ")
        == "sao paulo"
    )

    assert FipeService._normalizar("") == ""
    assert FipeService._normalizar(None) == ""


def test_buscar_preco_fipe_sucesso():
    respostas = [
        resposta(
            200,
            [
                {
                    "nome": "Ford",
                    "valor": "1",
                }
            ],
        ),
        resposta(
            200,
            {
                "modelos": [
                    {
                        "nome": "Ranger Raptor 3.0",
                        "codigo": "123",
                    }
                ]
            },
        ),
        resposta(
            200,
            [
                {
                    "anoModelo": 2025,
                    "valor": "R$ 500.000",
                }
            ],
        ),
    ]

    with patch(
        "app.services.fipe_service.requests.get",
        side_effect=respostas,
    ) as mock_get:

        resultado = FipeService.buscar_preco_fipe(
            "Ford",
            "Ranger",
            "Raptor",
            2025,
        )

    assert resultado == "R$ 500.000"
    assert mock_get.call_count == 3


def test_buscar_preco_fipe_marca_nao_encontrada():
    with patch(
        "app.services.fipe_service.requests.get",
        return_value=resposta(
            200,
            [
                {
                    "nome": "Toyota",
                    "valor": "2",
                }
            ],
        ),
    ):
        resultado = FipeService.buscar_preco_fipe(
            "Ford",
            "Ranger",
            "Raptor",
            2025,
        )

    assert resultado is None


def test_buscar_preco_fipe_api_marca_falha():
    with patch(
        "app.services.fipe_service.requests.get",
        return_value=resposta(500, {}),
    ):
        resultado = FipeService.buscar_preco_fipe(
            "Ford",
            "Ranger",
            "Raptor",
            2025,
        )

    assert resultado is None


def test_buscar_preco_fipe_modelo_nao_encontrado():
    respostas = [
        resposta(
            200,
            [
                {
                    "nome": "Ford",
                    "valor": "1",
                }
            ],
        ),
        resposta(
            200,
            {
                "modelos": [
                    {
                        "nome": "Mustang GT",
                        "codigo": "456",
                    }
                ]
            },
        ),
    ]

    with patch(
        "app.services.fipe_service.requests.get",
        side_effect=respostas,
    ):
        resultado = FipeService.buscar_preco_fipe(
            "Ford",
            "Ranger",
            "Raptor",
            2025,
        )

    assert resultado is None


def test_buscar_preco_fipe_ano_nao_encontrado():
    respostas = [
        resposta(
            200,
            [
                {
                    "nome": "Ford",
                    "valor": "1",
                }
            ],
        ),
        resposta(
            200,
            {
                "modelos": [
                    {
                        "nome": "Ranger Raptor",
                        "codigo": "123",
                    }
                ]
            },
        ),
        resposta(
            200,
            [
                {
                    "anoModelo": 2024,
                    "valor": "R$ 450.000",
                }
            ],
        ),
    ]

    with patch(
        "app.services.fipe_service.requests.get",
        side_effect=respostas,
    ):
        resultado = FipeService.buscar_preco_fipe(
            "Ford",
            "Ranger",
            "Raptor",
            2025,
        )

    assert resultado is None


def test_buscar_preco_fipe_trata_excecao():
    with patch(
        "app.services.fipe_service.requests.get",
        side_effect=Exception("API indisponível"),
    ):
        resultado = FipeService.buscar_preco_fipe(
            "Ford",
            "Ranger",
            "Raptor",
            2025,
        )

    assert resultado is None