from app.services.consensus_service import ConsensusService


def test_consenso_escolhe_valor_com_maior_peso():
    resultados = [
        {
            "fonte": "site_oficial",
            "motor": "3.0 V6",
        },
        {
            "fonte": "youtube",
            "motor": "2.0 Turbo",
        },
        {
            "fonte": "youtube",
            "motor": "2.0 Turbo",
        },
    ]

    resultado = ConsensusService.combinar_por_votacao(
        resultados,
        {"motor": ""},
    )

    assert resultado["motor"] == "3.0 V6"


def test_consenso_ignora_valores_nao_disponiveis():
    resultados = [
        {
            "fonte": "site_oficial",
            "motor": "não disponível",
        },
        {
            "fonte": "youtube",
            "motor": "3.0 V6",
        },
    ]

    resultado = ConsensusService.combinar_por_votacao(
        resultados,
        {"motor": ""},
    )

    assert resultado["motor"] == "3.0 V6"


def test_consenso_retorna_nao_disponivel_sem_valores_validos():
    resultados = [
        {
            "fonte": "site_oficial",
            "motor": "não disponível",
        },
    ]

    resultado = ConsensusService.combinar_por_votacao(
        resultados,
        {"motor": ""},
    )

    assert resultado["motor"] == "não disponível"


def test_consenso_aplica_pesos_personalizados():
    resultados = [
        {
            "fonte": "a",
            "motor": "3.0 V6",
        },
        {
            "fonte": "b",
            "motor": "2.0 Turbo",
        },
    ]

    resultado = ConsensusService.combinar_por_votacao(
        resultados,
        {"motor": ""},
        pesos_por_fonte={
            "a": 1.0,
            "b": 3.0,
        },
    )

    assert resultado["motor"] == "2.0 Turbo"


def test_consenso_processa_varios_atributos():
    resultados = [
        {
            "fonte": "site_oficial",
            "motor": "3.0 V6",
            "potencia": "397 cv",
        },
        {
            "fonte": "youtube",
            "motor": "2.0 Turbo",
            "potencia": "397 cv",
        },
    ]

    resultado = ConsensusService.combinar_por_votacao(
        resultados,
        {
            "motor": "",
            "potencia": "",
            "torque": "",
        },
    )

    assert resultado["motor"] == "3.0 V6"
    assert resultado["potencia"] == "397 cv"
    assert resultado["torque"] == "não disponível"