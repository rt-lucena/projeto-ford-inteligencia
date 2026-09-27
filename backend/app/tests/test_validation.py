def obter_token(client, email="teste@teste.com", senha="12345678"):
    response = client.post(
        "/auth/token",
        data={
            "username": email,
            "password": senha,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def headers_autenticacao(client):
    token = obter_token(client)

    return {
        "Authorization": f"Bearer {token}",
    }


# ============================================================
# AUTENTICAÇÃO
# ============================================================

def test_login_sem_username(client):
    response = client.post(
        "/auth/token",
        data={
            "password": "12345678",
        },
    )

    assert response.status_code == 422


def test_login_sem_password(client):
    response = client.post(
        "/auth/token",
        data={
            "username": "teste@teste.com",
        },
    )

    assert response.status_code == 422


def test_login_com_senha_inferior_ao_esperado(
    client,
    usuario,
):
    response = client.post(
        "/auth/token",
        data={
            "username": "teste@teste.com",
            "password": "123",
        },
    )

    assert response.status_code == 401


# ============================================================
# BUSCA DE VEÍCULO
# ============================================================

def test_busca_veiculo_sem_autenticacao(client):
    response = client.get(
        "/veiculos/busca",
        params={
            "marca": "Ford",
            "modelo": "Ranger",
            "versao": "Raptor",
            "ano": 2025,
        },
    )

    assert response.status_code == 401


def test_busca_veiculo_sem_marca(
    client,
    usuario,
):
    response = client.get(
        "/veiculos/busca",
        params={
            "modelo": "Ranger",
            "versao": "Raptor",
            "ano": 2025,
        },
        headers=headers_autenticacao(client),
    )

    assert response.status_code == 422


def test_busca_veiculo_marca_muito_curta(
    client,
    usuario,
):
    response = client.get(
        "/veiculos/busca",
        params={
            "marca": "F",
            "modelo": "Ranger",
            "versao": "Raptor",
            "ano": 2025,
        },
        headers=headers_autenticacao(client),
    )

    assert response.status_code == 422


def test_busca_veiculo_ano_menor_que_1886(
    client,
    usuario,
):
    response = client.get(
        "/veiculos/busca",
        params={
            "marca": "Ford",
            "modelo": "Ranger",
            "versao": "Raptor",
            "ano": 1885,
        },
        headers=headers_autenticacao(client),
    )

    assert response.status_code == 422


def test_busca_veiculo_ano_maior_que_2027(
    client,
    usuario,
):
    response = client.get(
        "/veiculos/busca",
        params={
            "marca": "Ford",
            "modelo": "Ranger",
            "versao": "Raptor",
            "ano": 2028,
        },
        headers=headers_autenticacao(client),
    )

    assert response.status_code == 422


# ============================================================
# COMPARAÇÃO
# ============================================================

def test_comparacao_sem_autenticacao(client):
    response = client.get(
        "/veiculos/comparar",
        params={
            "marca1": "Ford",
            "modelo1": "Ranger",
            "versao1": "Raptor",
            "ano1": 2025,
            "marca2": "Ford",
            "modelo2": "Mustang",
            "versao2": "GT",
            "ano2": 2025,
        },
    )

    assert response.status_code == 401


def test_comparacao_sem_marca1(
    client,
    usuario,
):
    response = client.get(
        "/veiculos/comparar",
        params={
            "modelo1": "Ranger",
            "versao1": "Raptor",
            "ano1": 2025,
            "marca2": "Ford",
            "modelo2": "Mustang",
            "versao2": "GT",
            "ano2": 2025,
        },
        headers=headers_autenticacao(client),
    )

    assert response.status_code == 422


def test_comparacao_sem_modelo2(
    client,
    usuario,
):
    response = client.get(
        "/veiculos/comparar",
        params={
            "marca1": "Ford",
            "modelo1": "Ranger",
            "versao1": "Raptor",
            "ano1": 2025,
            "marca2": "Ford",
            "versao2": "GT",
            "ano2": 2025,
        },
        headers=headers_autenticacao(client),
    )

    assert response.status_code == 422


# ============================================================
# HISTÓRICO
# ============================================================

def test_criar_historico_sem_autenticacao(client):
    response = client.post(
        "/historico/",
        json={
            "tipo": "individual",
            "id_veiculo": 1,
        },
    )

    assert response.status_code == 401


def test_criar_historico_tipo_invalido(
    client,
    usuario,
):
    response = client.post(
        "/historico/",
        json={
            "tipo": "invalido",
            "id_veiculo": 1,
        },
        headers=headers_autenticacao(client),
    )

    assert response.status_code == 422


def test_criar_historico_sem_tipo(
    client,
    usuario,
):
    response = client.post(
        "/historico/",
        json={
            "id_veiculo": 1,
        },
        headers=headers_autenticacao(client),
    )

    assert response.status_code == 422


def test_listar_historico_sem_autenticacao(client):
    response = client.get("/historico/")

    assert response.status_code == 401
