import json

from app.services.data_loader_service import DataLoaderService


def test_data_loader_retorna_lista_vazia_quando_diretorio_nao_existe(
    tmp_path,
):
    service = DataLoaderService(
        tmp_path / "nao_existe"
    )

    assert service.carregar_artigos() == []


def test_data_loader_carrega_lista_de_artigos(tmp_path):
    arquivo = tmp_path / "motor1.json"

    arquivo.write_text(
        json.dumps(
            [
                {
                    "titulo": "Ranger",
                    "conteudo": "Motor 3.0 V6",
                    "url": "https://exemplo.com",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    artigos = DataLoaderService(
        tmp_path
    ).carregar_artigos()

    assert len(artigos) == 1
    assert artigos[0]["titulo"] == "Ranger"
    assert artigos[0]["conteudo"] == "Motor 3.0 V6"
    assert artigos[0]["fonte"] == "motor1"


def test_data_loader_carrega_objeto_json(tmp_path):
    arquivo = tmp_path / "site_oficial.json"

    arquivo.write_text(
        json.dumps(
            {
                "titulo": "Ford Ranger",
                "conteudo": "Informações técnicas",
                "url": "https://exemplo.com/ranger",
            }
        ),
        encoding="utf-8",
    )

    artigos = DataLoaderService(
        tmp_path
    ).carregar_artigos()

    assert len(artigos) == 1
    assert artigos[0]["fonte"] == "site_oficial"


def test_data_loader_ignora_artigo_sem_conteudo(tmp_path):
    arquivo = tmp_path / "teste.json"

    arquivo.write_text(
        json.dumps(
            [
                {
                    "titulo": "Sem conteúdo",
                    "conteudo": "",
                },
                {
                    "titulo": "Válido",
                    "conteudo": "Conteúdo válido",
                },
            ]
        ),
        encoding="utf-8",
    )

    artigos = DataLoaderService(
        tmp_path
    ).carregar_artigos()

    assert len(artigos) == 1
    assert artigos[0]["titulo"] == "Válido"


def test_data_loader_ignora_json_invalido(tmp_path):
    arquivo = tmp_path / "quebrado.json"

    arquivo.write_text(
        "{ json inválido",
        encoding="utf-8",
    )

    assert (
        DataLoaderService(tmp_path).carregar_artigos()
        == []
    )


def test_data_loader_normaliza_espacos(tmp_path):
    arquivo = tmp_path / "teste.json"

    arquivo.write_text(
        json.dumps(
            {
                "titulo": "  Ranger  ",
                "conteudo": "  Motor V6  ",
                "url": "  https://exemplo.com  ",
            }
        ),
        encoding="utf-8",
    )

    artigo = DataLoaderService(
        tmp_path
    ).carregar_artigos()[0]

    assert artigo == {
        "titulo": "Ranger",
        "conteudo": "Motor V6",
        "url": "https://exemplo.com",
        "fonte": "teste",
    }